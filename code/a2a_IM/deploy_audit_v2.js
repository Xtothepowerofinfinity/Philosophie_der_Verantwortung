
const fs = require('fs');
const { Web3Storage, File } = require('web3.storage');
const { ethers } = require('hardhat');

const AUDIT_FILE = './cap_chain_audit_log.json';
const INCIDENT_FILE = './incident_hid_record.json';
const CAP_ID = 'Z-001';

async function uploadToIPFS(path, apiToken) {
    const fileBuffer = fs.readFileSync(path);
    const files = [new File([fileBuffer], path.split('/').pop())];
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

    const auditJson = fs.readFileSync(AUDIT_FILE, 'utf8');
    const auditHash = sha256(auditJson);
    const auditCid = await uploadToIPFS(AUDIT_FILE, web3Token);

    const incidentJson = fs.readFileSync(INCIDENT_FILE, 'utf8');
    const incidentData = JSON.parse(incidentJson);
    const incidentHash = sha256(incidentJson);
    const incidentCid = await uploadToIPFS(INCIDENT_FILE, web3Token);

    const [deployer] = await ethers.getSigners();
    const Contract = await ethers.getContractFactory('CapAuditStorageV2');
    const contract = await Contract.deploy();
    await contract.deployed();
    console.log("✅ Contract deployed to:", contract.address);

    const tx1 = await contract.storeAudit(CAP_ID, auditHash, auditCid);
    await tx1.wait();
    console.log("📦 Audit stored:", CAP_ID);

    const tx2 = await contract.storeIncident(
        incidentData.task_id || "INC-001",
        CAP_ID,
        incidentData.agent || "anonymous",
        incidentData.severity || "normal",
        incidentHash,
        incidentCid
    );
    await tx2.wait();
    console.log("⚠️ Incident stored.");
}

main().catch((e) => {
    console.error(e);
    process.exit(1);
});
