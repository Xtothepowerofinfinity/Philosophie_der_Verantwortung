import os
from decimal import Decimal, getcontext

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from web3 import Web3
from web3.exceptions import ContractLogicError

# --- Konfiguration & Initialisierung ---

load_dotenv() # Lädt Variablen aus .env Datei

# Set Decimal precision (important for division)
getcontext().prec = 50 # Set precision higher if needed

app = Flask(__name__)

# Load Config
NODE_URL = os.getenv("NODE_URL")
CAP_PETITION_ADDRESS = os.getenv("CAP_PETITION_ADDRESS")
CAP_LEDGER_ADDRESS = os.getenv("CAP_LEDGER_ADDRESS")

# Basic Input Validation
if not all([NODE_URL, CAP_PETITION_ADDRESS, CAP_LEDGER_ADDRESS]):
    raise ValueError("Environment variables NODE_URL, CAP_PETITION_ADDRESS, CAP_LEDGER_ADDRESS must be set.")

if not Web3.is_checksum_address(CAP_PETITION_ADDRESS):
     raise ValueError(f"Invalid CAP_PETITION_ADDRESS: {CAP_PETITION_ADDRESS}")
if not Web3.is_checksum_address(CAP_LEDGER_ADDRESS):
     raise ValueError(f"Invalid CAP_LEDGER_ADDRESS: {CAP_LEDGER_ADDRESS}")

# Load ABIs (assuming JSON files are in the same directory)
try:
    with open("CapPetition.json", "r") as f:
        CAP_PETITION_ABI = f.read()
    with open("CapLedger.json", "r") as f:
        CAP_LEDGER_ABI = f.read()
except FileNotFoundError as e:
    raise FileNotFoundError(f"ABI file not found. Make sure CapPetition.json and CapLedger.json are present. Details: {e}")


# Web3 Connection
w3 = Web3(Web3.HTTPProvider(NODE_URL))
if not w3.is_connected():
    raise ConnectionError(f"Failed to connect to Ethereum node at {NODE_URL}")

# Contract Instances
try:
    cap_petition_contract = w3.eth.contract(address=CAP_PETITION_ADDRESS, abi=CAP_PETITION_ABI)
    cap_ledger_contract = w3.eth.contract(address=CAP_LEDGER_ADDRESS, abi=CAP_LEDGER_ABI)
except Exception as e:
    raise RuntimeError(f"Failed to instantiate contracts: {e}")


# --- Kernlogik ---

def get_cap_potential_securely(account: str, domain: bytes) -> Decimal | None:
    """
    Fetches Cap Potential securely from the CapLedger contract.
    Handles potential errors and zero potential.

    Returns:
        Decimal: The Cap Potential if > 0.
        None: If potential is 0 or an error occurred during fetch.
    """
    try:
        # Ensure checksum address
        checksum_account = Web3.to_checksum_address(account)
        # Call the CapLedger contract
        potential_wei = cap_ledger_contract.functions.getCapPotential(checksum_account, domain).call()

        # Convert from Wei (uint256) to Decimal. Assuming potential is stored as integer.
        # Adjust unit conversion if Cap Potential uses decimals on-chain.
        potential_dec = Decimal(potential_wei)

        if potential_dec > 0:
            return potential_dec
        else:
            # Potential is zero, cannot contribute weight (avoid division by zero)
            app.logger.warning(f"Account {account} has zero Cap Potential in domain {domain.hex()}. Skipping for score.")
            return None
    except ContractLogicError as e:
        # Contract reverted (e.g., account doesn't exist, invalid domain)
        app.logger.error(f"Contract logic error getting potential for {account} in domain {domain.hex()}: {e}")
        return None
    except Exception as e:
        # Other errors (RPC, connection, invalid address format before checksum etc.)
        app.logger.error(f"Error fetching Cap Potential for {account} in domain {domain.hex()}: {e}")
        return None

def calculate_weighted_score(petition_id: int) -> Decimal | None:
    """
    Calculates the weighted support score for a given petition.
    Fetches supporter potentials securely from CapLedger.
    Score = Sum(1 / Cap_Potential) for supporters with Potential > 0.

    Returns:
         Decimal: The calculated weighted score.
         None: If petition not found or score calculation failed.
    """
    try:
        # 1. Get Petition Data (including domain and supporters)
        petition_data = cap_petition_contract.functions.petitions(petition_id).call()
        # petition_data indices based on struct order: 0:id, 1:creator, 2:domain, 3:descHash, 4:supporters_ref?, 5:hasSupported_ref?, 6:timestamp, 7:isOpen
        if petition_data[1] == '0x0000000000000000000000000000000000000000': # Check if creator is zero address (petition doesn't exist)
            app.logger.error(f"Petition with ID {petition_id} not found.")
            return None

        domain = petition_data[2] # bytes32
        # Fetch supporters list separately as it's dynamic array
        supporters = cap_petition_contract.functions.getSupporters(petition_id).call()

        if not supporters:
            return Decimal(0) # No supporters, score is 0

        # 2. Calculate Score
        total_weighted_score = Decimal(0)
        valid_supporters_count = 0
        for supporter_address in supporters:
            potential = get_cap_potential_securely(supporter_address, domain)
            if potential is not None and potential > 0: # Ensure potential is valid and non-zero
                 # Ensure precision for division
                 try:
                     total_weighted_score += (Decimal(1) / potential)
                     valid_supporters_count += 1
                 except Exception as e: # Catch potential division issues if potential is somehow zero despite check
                     app.logger.error(f"Division error for supporter {supporter_address} potential {potential}: {e}")

        app.logger.info(f"Calculated score for petition {petition_id}: {total_weighted_score} from {valid_supporters_count}/{len(supporters)} supporters.")
        return total_weighted_score

    except ContractLogicError as e:
        app.logger.error(f"Contract logic error fetching data for petition {petition_id}: {e}")
        return None
    except Exception as e:
        app.logger.error(f"Error calculating score for petition {petition_id}: {e}")
        return None


# --- API Endpunkte (Beispiele mit Flask) ---

@app.route('/petition/<int:petition_id>/score', methods=['GET'])
def get_petition_score(petition_id):
    """API endpoint to get the calculated weighted score for a petition."""
    app.logger.info(f"Received request for score of petition ID: {petition_id}")
    score = calculate_weighted_score(petition_id)
    if score is not None:
        # Convert Decimal to string for JSON compatibility
        return jsonify({"petition_id": petition_id, "weighted_score": str(score)})
    else:
        return jsonify({"error": f"Could not calculate score for petition {petition_id}. Petition might not exist or data unavailable."}), 404

@app.route('/petition/<int:petition_id>', methods=['GET'])
def get_petition_details(petition_id):
    """API endpoint to get petition details (excluding supporters list for brevity)."""
    try:
        petition_data = cap_petition_contract.functions.petitions(petition_id).call()
        if petition_data[1] == '0x0000000000000000000000000000000000000000':
             return jsonify({"error": f"Petition {petition_id} not found."}), 404

        # Fetch description from IPFS using petition_data[3] (descriptionHash) - IMPLEMENTATION NEEDED
        # description = fetch_from_ipfs(petition_data[3]) # Placeholder

        details = {
            "petition_id": int(petition_data[0]), # Solidity uint256 -> Python int
            "creator": petition_data[1],
            "domain": petition_data[2].hex(), # bytes32 -> hex string
            "descriptionHash": petition_data[3],
            # "description_content": description, # Add fetched content here
            "creationTimestamp": int(petition_data[6]),
            "isOpen": petition_data[7],
            # Score calculation can be added here too
            # "weighted_score": str(calculate_weighted_score(petition_id))
        }
        return jsonify(details)
    except Exception as e:
         app.logger.error(f"Error getting details for petition {petition_id}: {e}")
         return jsonify({"error": "Failed to retrieve petition details."}), 500


# --- Potentielle Integrationsfunktion ---

def find_and_forward_prioritized_needs(threshold: Decimal = Decimal('10.0')):
    """
    Finds petitions exceeding a certain weighted score threshold and forwards
    them to the strategy/resource allocation mechanism (placeholder).
    This represents the "Wozu?" -> "Wie?" link.
    """
    prioritized_petitions = []
    try:
        total_petitions = cap_petition_contract.functions.getPetitionCount().call()
        app.logger.info(f"Checking {total_petitions} petitions for prioritization...")

        for i in range(1, total_petitions + 1):
            score = calculate_weighted_score(i)
            if score is not None and score >= threshold:
                 # Get details to forward (e.g., ID, domain, description hash)
                 petition_data = cap_petition_contract.functions.petitions(i).call()
                 # Basic check if petition exists
                 if petition_data[1] != '0x0000000000000000000000000000000000000000':
                    details = {
                        "petition_id": i,
                        "domain": petition_data[2].hex(),
                        "descriptionHash": petition_data[3],
                        "weighted_score": str(score)
                    }
                    prioritized_petitions.append(details)
                    app.logger.info(f"Petition {i} meets threshold with score {score}.")

        # TODO: Implement forwarding logic here
        if prioritized_petitions:
            app.logger.info(f"Forwarding {len(prioritized_petitions)} prioritized petitions to strategy module...")
            # forward_to_strategy_module(prioritized_petitions) # Placeholder call
        else:
             app.logger.info("No petitions met the prioritization threshold.")

        return prioritized_petitions # Or return status

    except Exception as e:
        app.logger.error(f"Error during need prioritization: {e}")
        return None


# --- Main Execution ---
if __name__ == '__main__':
    # Example: Run a check for prioritized needs on startup (optional)
    # find_and_forward_prioritized_needs(Decimal('5.0')) # Set your threshold

    # Start Flask server
    # Use host='0.0.0.0' to make it accessible on your network if needed
    # Use debug=True only for development, set to False for production
    app.run(host='127.0.0.1', port=5001, debug=True)