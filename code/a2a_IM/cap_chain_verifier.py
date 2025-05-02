
import json

class CapChainVerifier:
    def __init__(self, chain_file_path):
        with open(chain_file_path, 'r') as f:
            self.data = json.load(f)

    def verify_chain_integrity(self):
        chain = self.data.get("chain", [])
        if not chain or len(chain) < 2:
            return False, "Chain too short or missing"

        for i in range(len(chain) - 1):
            if chain[i]["delegated_to"] != chain[i + 1]["agent"]:
                return False, f"Broken delegation between step {i} and {i+1}"

        return True, "Chain delegation consistent"

    def verify_scope_use(self):
        chain = self.data.get("chain", [])
        for entry in chain:
            if "used_scope" in entry:
                for scope in entry["used_scope"]:
                    if scope not in entry["scope"]:
                        return False, f"Used scope '{scope}' not granted in entry: {entry['agent']}"

        return True, "All used scopes valid"

    def verify_acknowledgements(self):
        ack = self.data.get("acknowledgement")
        final_ack = self.data.get("final_ack")
        if not ack or not final_ack:
            return False, "Missing acknowledgement(s)"
        if not (ack["task_confirmed"] and final_ack["status"] == "task_complete_chain_closed"):
            return False, "ACKs incomplete or incorrect"

        return True, "ACKs valid"

    def run_all_checks(self):
        results = {}
        for name, func in [
            ("chain_integrity", self.verify_chain_integrity),
            ("scope_use", self.verify_scope_use),
            ("acknowledgements", self.verify_acknowledgements)
        ]:
            ok, msg = func()
            results[name] = {"valid": ok, "message": msg}
        return results

# Beispiel:
# verifier = CapChainVerifier("cap_chain_log.json")
# print(verifier.run_all_checks())
