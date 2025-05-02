
import json
import argparse
import hashlib
from datetime import datetime

def generate_audit_hash(json_path, link_incident=False, incident_id=None):
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Sort for reproducibility
    canonical_data = json.dumps(data, sort_keys=True).encode('utf-8')
    audit_hash = hashlib.sha256(canonical_data).hexdigest()

    metadata = {
        "audit_hash": audit_hash,
        "linked_incident": link_incident,
        "incident_id": incident_id if link_incident else None,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source_file": json_path
    }

    output_file = json_path.replace(".json", "_archived.json")
    with open(output_file, 'w') as f:
        json.dump({
            "metadata": metadata,
            "data": data
        }, f, indent=4)

    print(f"✅ Archived log written to {output_file}")
    return output_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path to original JSON log")
    parser.add_argument("--link", action="store_true", help="Enable incident linking")
    parser.add_argument("--incident", help="Incident ID if linking")
    args = parser.parse_args()

    generate_audit_hash(args.file, link_incident=args.link, incident_id=args.incident)
