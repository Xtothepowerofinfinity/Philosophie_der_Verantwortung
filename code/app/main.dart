
import 'package:flutter/material.dart';
import 'cap_gate.dart';
import 'wallet_connect.dart';
import 'cap_manager.dart';
import 'feedback_sender.dart';

void main() {
  runApp(const CapDeviceApp());
}

class CapDeviceApp extends StatelessWidget {
  const CapDeviceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'X∞ CapDevice',
      theme: ThemeData.dark(),
      home: const CapGateHome(),
    );
  }
}

class CapGateHome extends StatelessWidget {
  const CapGateHome({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('X^∞ – CapDevice Gateway'),
        centerTitle: true,
      ),
      body: ListView(
        children: [
          ListTile(
            title: const Text('🔐 Cap Management'),
            subtitle: const Text('Verwalte aktives Cap'),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const CapManagerView()),
              );
            },
          ),
          const Divider(),
          ListTile(
            title: const Text('🪙 Wallet Connect'),
            subtitle: const Text('Verknüpfe deine Domänen-Wallet'),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const WalletConnectView()),
              );
            },
          ),
          const Divider(),
          ListTile(
            title: const Text('📡 BLE / RFID Scanner'),
            subtitle: const Text('Umfeld- und Gerätekopplung'),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const CapGateView()),
              );
            },
          ),
          const Divider(),
          ListTile(
            title: const Text('📤 Feedback senden'),
            subtitle: const Text('Sende Rückkopplung ins System'),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const FeedbackSenderView()),
              );
            },
          ),
        ],
      ),
    );
  }
}
