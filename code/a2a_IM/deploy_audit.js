
const fs = require('fs');
const { Web3Storage, File } = require('web3.storage');
const { ethers } = require('hardhat');

const FILE_PATH = './cap_chain_audit_log.json';
const CAP_ID = 'Z-001';

async function uploadToIPFS(apiToken) {
    const fileBuffer = fs.readFileSync(FILE_PATH);
    const files = [new File([fileBuffer], 'cap_chain_audit_log.json')];
    const client = new Web3Storage({ token: apiToken });
    const cid = await client.put(files);
    return cid;
}

function sha256(data) {
    return ethers.utils.sha256(ethers.utils.toUtf8Bytes(data));
}

async function main() {
    const web3Token = process.env.WEB3_STORAGE_TOKEN;
    if (!web3Token) {
        throw new Error('WEB3_STORAGE_TOKEN env var required');
    }

    const auditJson = fs.readFileSync(FILE_PATH, 'utf8');
    const auditHash = sha256(auditJson);
    const ipfsHash = await uploadToIPFS(web3Token);
    console.log("📦 IPFS Hash:", ipfsHash);
    console.log("🔐 Audit Hash:", auditHash);

    const [deployer] = await ethers.getSigners();
    const Audit = await ethers.getContractFactory('CapAuditStorage');
    const contract = await Audit.deploy();
    await contract.deployed();
    console.log("✅ Contract deployed to:", contract.address);

    const tx = await contract.storeAudit(CAP_ID, auditHash, ipfsHash);
    await tx.wait();
    console.log("📝 Audit record stored.");
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
