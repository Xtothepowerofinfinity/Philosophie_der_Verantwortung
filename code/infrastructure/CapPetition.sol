// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ICapLedger Interface
 * @dev Interface to interact with the CapLedger contract to get Cap potentials.
 * Needs to be implemented by the actual CapLedger contract.
 */
interface ICapLedger {
    /**
     * @dev Returns the Cap Potential of an account within a specific domain.
     * Assumes Cap Potential > 0 indicates legitimate access/stake (Cap_Base/BGE).
     */
    function getCapPotential(address account, bytes32 domain) external view returns (uint256);
}

/**
 * @title CapPetition Contract
 * @dev Manages the creation and support of petitions (need expressions) within the X-Infinity ecosystem.
 * Enforces the separation of "Wozu?" (the need) from "Wie?" (the solution).
 * Relies on an external CapLedger for Cap Potential checks.
 * Uses Ownable for administrative tasks.
 */
contract CapPetition is Ownable {

    // --- State Variables ---

    ICapLedger public capLedger; // Address of the CapLedger contract

    uint256 private _petitionCounter; // Counter for unique petition IDs

    // Struct to hold petition data
    struct Petition {
        uint256 id;                 // Unique ID
        address creator;            // Address of the petition creator
        bytes32 domain;             // The domain the petition pertains to
        string descriptionHash;     // Hash/CID of the detailed "Wozu?" description (stored off-chain, e.g., IPFS)
        address[] supporters;       // Array of addresses supporting this petition
        mapping(address => bool) hasSupported; // Efficient check if an address has supported
        uint256 creationTimestamp;  // Timestamp of creation
        bool isOpen;                // Flag if petition is still open for support
    }

    // Mapping from petition ID to Petition struct
    mapping(uint256 => Petition) public petitions;

    // --- Events ---

    /**
     * @dev Emitted when a new petition is created.
     */
    event PetitionCreated(
        uint256 indexed petitionId,
        address indexed creator,
        bytes32 indexed domain,
        string descriptionHash,
        uint256 timestamp
    );

    /**
     * @dev Emitted when an address supports a petition.
     */
    event PetitionSupported(
        uint256 indexed petitionId,
        address indexed supporter,
        uint256 timestamp
    );

     /**
     * @dev Emitted when the CapLedger address is updated.
     */
    event CapLedgerAddressSet(address indexed newCapLedgerAddress);


    // --- Errors ---
    error PetitionNotFound(uint256 petitionId);
    error PetitionNotOpen(uint256 petitionId);
    error AlreadySupported(uint256 petitionId, address supporter);
    error CannotParticipate(address account, bytes32 domain);
    error ZeroAddress();


    // --- Constructor ---

    /**
     * @dev Sets the initial CapLedger address during deployment.
     * @param initialOwner The address that will initially own the contract.
     * @param initialCapLedgerAddress The address of the deployed CapLedger contract.
     */
    constructor(address initialOwner, address initialCapLedgerAddress) Ownable(initialOwner) {
        if(initialCapLedgerAddress == address(0)) revert ZeroAddress();
        capLedger = ICapLedger(initialCapLedgerAddress);
        emit CapLedgerAddressSet(initialCapLedgerAddress);
    }

    // --- Functions ---

    /**
     * @dev Creates a new petition for a specific domain.
     * The caller must have a legitimate stake (Cap > 0) in the domain.
     * Only stores a hash of the description ("Wozu?"), not the solution ("Wie?").
     * @param domain The domain the petition relates to.
     * @param descriptionHash Hash (e.g., IPFS CID) of the detailed need description.
     */
    function createPetition(bytes32 domain, string calldata descriptionHash) external {
        if (!_canParticipate(msg.sender, domain)) {
            revert CannotParticipate(msg.sender, domain);
        }

        _petitionCounter++;
        uint256 newPetitionId = _petitionCounter;

        Petition storage newPetition = petitions[newPetitionId];
        newPetition.id = newPetitionId;
        newPetition.creator = msg.sender;
        newPetition.domain = domain;
        newPetition.descriptionHash = descriptionHash;
        newPetition.creationTimestamp = block.timestamp;
        newPetition.isOpen = true;

        // Creator automatically supports their own petition
        newPetition.supporters.push(msg.sender);
        newPetition.hasSupported[msg.sender] = true;

        emit PetitionCreated(
            newPetitionId,
            msg.sender,
            domain,
            descriptionHash,
            block.timestamp
        );
        // Also emit support event for the creator
        emit PetitionSupported(
            newPetitionId,
            msg.sender,
            block.timestamp
        );
    }

    /**
     * @dev Allows an address to support an existing, open petition.
     * The caller must have a legitimate stake (Cap > 0) in the petition's domain.
     * @param petitionId The ID of the petition to support.
     */
    function supportPetition(uint256 petitionId) external {
        Petition storage petition = petitions[petitionId];

        if (petition.creator == address(0)) { // Check if petition exists (creator is mandatory)
            revert PetitionNotFound(petitionId);
        }
        if (!petition.isOpen) {
            revert PetitionNotOpen(petitionId);
        }
        if (petition.hasSupported[msg.sender]) {
            revert AlreadySupported(petitionId, msg.sender);
        }
        if (!_canParticipate(msg.sender, petition.domain)) {
            revert CannotParticipate(msg.sender, petition.domain);
        }

        petition.supporters.push(msg.sender);
        petition.hasSupported[msg.sender] = true;

        emit PetitionSupported(
            petitionId,
            msg.sender,
            block.timestamp
        );
    }

    // --- Internal View Function ---

    /**
     * @dev Internal function to check if an account can participate in a domain.
     * Checks if the account has Cap Potential > 0 in the given domain via the CapLedger.
     * This acts as a proxy for having Cap_Base/BGE or other relevant Cap.
     * @param account The address to check.
     * @param domain The domain to check participation for.
     * @return bool True if the account can participate, false otherwise.
     */
    function _canParticipate(address account, bytes32 domain) internal view returns (bool) {
        // Ensure capLedger address is set
        if (address(capLedger) == address(0)) {
             return false; // Or revert, depending on desired behavior if not configured
        }
        try capLedger.getCapPotential(account, domain) returns (uint256 potential) {
             // Allow participation if potential is greater than zero
             return potential > 0;
        } catch {
             // If the call fails (e.g., ledger not set correctly, or other issue)
             return false;
        }
    }

    // --- Getter Functions ---

    /**
     * @dev Returns the total number of petitions created.
     */
    function getPetitionCount() external view returns (uint256) {
        return _petitionCounter;
    }

    /**
     * @dev Returns the list of supporters for a given petition.
     * Intended for off-chain use (e.g., calculating weighted scores).
     * @param petitionId The ID of the petition.
     * @return address[] Memory array of supporter addresses.
     */
    function getSupporters(uint256 petitionId) external view returns (address[] memory) {
         if (petitions[petitionId].creator == address(0)) {
             revert PetitionNotFound(petitionId);
         }
        return petitions[petitionId].supporters;
    }

    // --- Admin Functions ---

    /**
     * @dev Allows the owner to update the CapLedger contract address.
     * @param newCapLedgerAddress The address of the new CapLedger contract.
     */
    function setCapLedgerAddress(address newCapLedgerAddress) external onlyOwner {
         if(newCapLedgerAddress == address(0)) revert ZeroAddress();
        capLedger = ICapLedger(newCapLedgerAddress);
        emit CapLedgerAddressSet(newCapLedgerAddress);
    }

    /**
     * @dev Allows the owner to close a petition for further support.
     * @param petitionId The ID of the petition to close.
     */
    function closePetition(uint256 petitionId) external onlyOwner {
        if (petitions[petitionId].creator == address(0)) {
             revert PetitionNotFound(petitionId);
         }
        petitions[petitionId].isOpen = false;
        // Optional: Emit an event PetitionClosed(petitionId);
    }

     /**
     * @dev Allows the owner to reopen a petition for further support.
     * @param petitionId The ID of the petition to reopen.
     */
    function reopenPetition(uint256 petitionId) external onlyOwner {
        if (petitions[petitionId].creator == address(0)) {
             revert PetitionNotFound(petitionId);
         }
        petitions[petitionId].isOpen = true;
         // Optional: Emit an event PetitionReopened(petitionId);
    }
}