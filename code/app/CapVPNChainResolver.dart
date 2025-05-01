
import 'package:web3dart/web3dart.dart';
import 'package:http/http.dart';

class CapVPNChainResolver {
  final String rpcUrl;
  final String contractAddress;
  final String abiJson;
  late Web3Client _client;
  late DeployedContract _contract;

  CapVPNChainResolver(this.rpcUrl, this.contractAddress, this.abiJson) {
    _client = Web3Client(rpcUrl, Client());
    _contract = DeployedContract(
      ContractAbi.fromJson(abiJson, 'CapVPNRegistry'),
      EthereumAddress.fromHex(contractAddress),
    );
  }

  Future<List<String>> getAllNodes(String domain) async {
    final func = _contract.function('getAllNodes');
    final result = await _client.call(
      contract: _contract,
      function: func,
      params: [domain],
    );
    return (result[0] as List).map((e) => e.toString()).toList();
  }

  Future<String> getNodeByIndex(String domain, int index) async {
    final func = _contract.function('getNode');
    final result = await _client.call(
      contract: _contract,
      function: func,
      params: [domain, BigInt.from(index)],
    );
    return result.first.toString();
  }

  Future<int> getNodeCount(String domain) async {
    final func = _contract.function('getNodeCount');
    final result = await _client.call(
      contract: _contract,
      function: func,
      params: [domain],
    );
    return (result.first as BigInt).toInt();
  }
}
