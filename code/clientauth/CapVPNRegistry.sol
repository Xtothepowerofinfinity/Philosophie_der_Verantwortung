
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @title CapVPNRegistry - Decentralized Registry for CapOS VPN Exit Nodes
contract CapVPNRegistry {
    mapping(string => address[]) private vpnNodes; // domain => list of node IP holders
    mapping(address => bool) public approved;

    event NodeAdded(string domain, address node);
    event NodeRemoved(string domain, address node);

    modifier onlyApproved() {
        require(approved[msg.sender], "Not approved");
        _;
    }

    constructor() {
        approved[msg.sender] = true;
    }

    function approve(address node) public onlyApproved {
        approved[node] = true;
    }

    function revoke(address node) public onlyApproved {
        approved[node] = false;
    }

    function addNode(string memory domain, address node) public onlyApproved {
        vpnNodes[domain].push(node);
        emit NodeAdded(domain, node);
    }

    function removeNode(string memory domain, address node) public onlyApproved {
        address[] storage list = vpnNodes[domain];
        for (uint i = 0; i < list.length; i++) {
            if (list[i] == node) {
                list[i] = list[list.length - 1];
                list.pop();
                emit NodeRemoved(domain, node);
                break;
            }
        }
    }

    function getNodeCount(string memory domain) public view returns (uint) {
        return vpnNodes[domain].length;
    }

    function getNode(string memory domain, uint index) public view returns (address) {
        address[] storage list = vpnNodes[domain];
        require(index < list.length, "Index out of bounds");
        return list[index];
    }

    function getAllNodes(string memory domain) public view returns (address[] memory) {
        return vpnNodes[domain];
    }
}
