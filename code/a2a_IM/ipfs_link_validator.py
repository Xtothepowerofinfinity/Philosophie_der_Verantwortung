
import requests
import argparse

def validate_ipfs_hash(ipfs_hash, gateway="https://ipfs.io/ipfs/"):
    if ipfs_hash in ["", "N/A", None]:
        return {"valid": False, "reason": "Empty or placeholder hash"}

    url = gateway + ipfs_hash
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return {"valid": True, "status": res.status_code, "size": len(res.content)}
        else:
            return {"valid": False, "status": res.status_code, "reason": "Not 200"}
    except requests.RequestException as e:
        return {"valid": False, "error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ipfs", required=True, help="IPFS CID")
    parser.add_argument("--gateway", default="https://ipfs.io/ipfs/")
    args = parser.parse_args()

    result = validate_ipfs_hash(args.ipfs, args.gateway)
    print(result)
