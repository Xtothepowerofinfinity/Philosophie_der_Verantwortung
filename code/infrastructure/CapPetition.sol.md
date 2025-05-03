# Dokumentation: CapPetition Smart Contract (`CapPetition.sol`)

## Übersicht

Der `CapPetition.sol` Smart Contract ist eine Kernkomponente des X^∞-Systems zur Verwaltung von **Bedürfnisäußerungen** (Petitionen). Er ermöglicht es Akteuren im System, proaktiv auf Mängel oder Bedarfe in bestimmten Domänen hinzuweisen ("Wozu?"), ohne eine Lösung ("Wie?") vorzuschreiben. Andere Akteure können diese Petitionen unterstützen. Die Legitimität und Dringlichkeit einer Petition wird durch einen **gewichteten Score** repräsentiert, der auf dem `Cap_Potential` der Unterstützer basiert (Berechnung erfolgt off-chain). Der Contract gewährleistet Transparenz, Auditierbarkeit und Zugangskontrolle basierend auf dem Domain Cap der Teilnehmer.

## Abhängigkeiten

* **`ICapLedger` Interface:** Der Contract benötigt die Adresse eines kompatiblen `CapLedger`-Contracts, der das Interface `ICapLedger` implementiert und insbesondere die Funktion `getCapPotential(address account, bytes32 domain) returns (uint256)` bereitstellt. Diese Funktion wird zur Überprüfung der Teilnahmeberechtigung verwendet.
* **OpenZeppelin Contracts:** Nutzt `Ownable.sol` für einfache Zugriffsrechte auf administrative Funktionen (`@openzeppelin/contracts/access/Ownable.sol`).

## State Variablen

* `capLedger`: `ICapLedger` - Die Adresse des verknüpften `CapLedger`-Contracts.
* `_petitionCounter`: `uint256` - Ein interner Zähler zur Vergabe eindeutiger Petitions-IDs.
* `petitions`: `mapping(uint256 => Petition)` - Speichert die Daten jeder Petition, zugreifbar über ihre ID.
* `owner`: `address` (via `Ownable`) - Die Adresse, die administrative Rechte hat (z.B. `setCapLedgerAddress`).

## Structs

* **`Petition`:**
    * `id`: `uint256` - Eindeutige ID der Petition.
    * `creator`: `address` - Adresse des Erstellers.
    * `domain`: `bytes32` - Die Domäne, auf die sich die Petition bezieht.
    * `descriptionHash`: `string` - Hash (z.B. IPFS CID) der detaillierten Bedürfnisbeschreibung ("Wozu?"). Der Inhalt selbst wird off-chain gespeichert.
    * `supporters`: `address[]` - Dynamisches Array der Adressen, die diese Petition unterstützen.
    * `hasSupported`: `mapping(address => bool)` - Effiziente Prüfung, ob eine Adresse bereits unterstützt hat.
    * `creationTimestamp`: `uint256` - Zeitstempel der Erstellung.
    * `isOpen`: `bool` - Flag, ob die Petition noch unterstützt werden kann.

## Events

* `PetitionCreated(uint256 indexed petitionId, address indexed creator, bytes32 indexed domain, string descriptionHash, uint256 timestamp)`: Wird ausgelöst, wenn eine neue Petition erstellt wird.
* `PetitionSupported(uint256 indexed petitionId, address indexed supporter, uint256 timestamp)`: Wird ausgelöst, wenn eine Adresse eine Petition unterstützt.
* `CapLedgerAddressSet(address indexed newCapLedgerAddress)`: Wird ausgelöst, wenn die Adresse des `CapLedger` aktualisiert wird.

## Kernfunktionen

* **`createPetition(bytes32 domain, string calldata descriptionHash)`:**
    * Ermöglicht das Erstellen einer neuen Petition.
    * **Zugangskontrolle:** Prüft via `_canParticipate`, ob der `msg.sender` eine Berechtigung (>0 `Cap_Potential` laut `CapLedger`) für die angegebene `domain` hat (basierend auf `Cap_Base`/`BGE` oder spezifischerem Cap).
    * **Wozu/Wie-Trennung:** Speichert nur den `descriptionHash` (Verweis auf das "Wozu?"), keine Lösungsdetails.
    * Der Ersteller wird automatisch als erster Unterstützer hinzugefügt.
    * Löst `PetitionCreated` und `PetitionSupported` Events aus.
* **`supportPetition(uint256 petitionId)`:**
    * Ermöglicht das Unterstützen einer bestehenden, offenen Petition.
    * **Zugangskontrolle:** Prüft via `_canParticipate`, ob der `msg.sender` eine Berechtigung für die `domain` der Petition hat.
    * Verhindert doppelte Unterstützung durch denselben Account.
    * Fügt den `msg.sender` zur `supporters`-Liste hinzu und setzt `hasSupported`.
    * Löst `PetitionSupported` Event aus.
* **`getPetitionCount() view returns (uint256)`:**
    * Gibt die Gesamtzahl der erstellten Petitionen zurück.
* **`getSupporters(uint256 petitionId) view returns (address[] memory)`:**
    * Gibt die Liste der Unterstützeradressen für eine Petition zurück. Primär für Off-Chain-Nutzung (Score-Berechnung) gedacht.

## Administrative Funktionen (nur `owner`)

* **`setCapLedgerAddress(address newCapLedgerAddress)`:** Aktualisiert die Adresse des `CapLedger`-Contracts.
* **`closePetition(uint256 petitionId)`:** Schließt eine Petition für weitere Unterstützung.
* **`reopenPetition(uint256 petitionId)`:** Öffnet eine geschlossene Petition wieder für Unterstützung.

## Off-Chain Aspekte

* **Gewichtete Score-Berechnung:** Die Berechnung des Scores ($Score = \sum (1 / \text{Cap\_Potential})$) muss off-chain erfolgen, indem die `supporters`-Liste gelesen und für jeden Unterstützer das `Cap_Potential` sicher vom `capLedger`-Contract abgefragt wird.
* **Beschreibungsinhalt:** Der Inhalt der Bedürfnisbeschreibung ("Wozu?") muss über den `descriptionHash` (z.B. via IPFS Gateway) off-chain abgerufen werden.

## Sicherheitshinweise

* Die Sicherheit des Systems hängt von der Korrektheit und Sicherheit des `CapLedger`-Contracts ab.
* Die `Ownable`-Rechte sollten sicher verwaltet werden.
* Bei sehr vielen Unterstützern können die Gas-Kosten für das Hinzufügen zum `supporters`-Array ansteigen. Alternative Datenstrukturen könnten erwogen werden, erschweren aber die Off-Chain-Verarbeitung.