
import 'dart:convert';
import 'dart:io';

Future<void> main() async {
  final server = await HttpServer.bind(InternetAddress.anyIPv4, 8989);
  print('🚪 CapGate Receiver listening on port 8989');

  await for (HttpRequest request in server) {
    if (request.method == 'POST' && request.uri.path == '/gate_receive') {
      final content = await utf8.decoder.bind(request).join();
      final data = jsonDecode(content);

      final capId = data['cap_id'];
      final signer = request.headers.value('X-Signed-By') ?? 'unknown';
      final severity = data['severity'] ?? 'normal';

      print('✅ Received incident for CapID: \$capId from \$signer (Severity: \$severity)');

      if (severity == 'critical') {
        print('🚨 CRITICAL: Gate escalation triggered for \$capId');
      }

      request.response
        ..statusCode = HttpStatus.ok
        ..write(jsonEncode({'status': 'received', 'cap_id': capId}))
        ..close();
    } else {
      request.response
        ..statusCode = HttpStatus.notFound
        ..write('Not Found')
        ..close();
    }
  }
}
