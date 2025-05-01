
import 'dart:convert';
import 'dart:io';

class GateSync {
  final String syncFile = "synced_seen_log.json";

  // Placeholder für Domain-Wallets (im echten System durch KeyVault ersetzt)
  Map<String, String> domainWallets = {
    "infra": "0xGATEWALLET123...",
    "social": "0xGATEWALLET456..."
  };

  String getWalletForDomain(String domain) {
    return domainWallets[domain] ?? "0xUNKNOWN";
  }

  String fakeSign(String jsonData, String domain) {
    final wallet = getWalletForDomain(domain);
    return "signed_by:$wallet"; // placeholder for cryptographic signature
  }

  void sendSyncData(String domain, List<dynamic> seenLog) {
    final String wallet = getWalletForDomain(domain);
    final String payload = json.encode({
      "gate_wallet": wallet,
      "timestamp": DateTime.now().millisecondsSinceEpoch ~/ 1000,
      "seen": seenLog,
    });

    final String signature = fakeSign(payload, domain);
    final syncPackage = {
      "gate_wallet": wallet,
      "timestamp": DateTime.now().millisecondsSinceEpoch ~/ 1000,
      "seen": seenLog,
      "signature": signature
    };

    File("last_sync_out.json").writeAsStringSync(json.encode(syncPackage), flush: true);
  }

  void receiveSyncData(String jsonString) {
    final incoming = json.decode(jsonString);
    final file = File(syncFile);
    List<dynamic> existing = [];

    if (file.existsSync()) {
      existing = json.decode(file.readAsStringSync());
    }

    existing.add(incoming);
    file.writeAsStringSync(json.encode(existing), flush: true);
  }
}
