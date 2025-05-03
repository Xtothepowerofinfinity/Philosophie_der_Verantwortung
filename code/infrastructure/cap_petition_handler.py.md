# Dokumentation: CapPetition Backend Handler (`cap_petition_handler.py`)

## Übersicht

Dieses Python-Modul dient als Backend-Service für das "CapPetition System" innerhalb der X^∞-Architektur. Seine Hauptaufgaben sind:

1.  Sichere Interaktion mit den Smart Contracts `CapPetition.sol` und `CapLedger.sol` auf der Blockchain.
2.  Die **Off-Chain-Berechnung des gewichteten Unterstützungsscores** für Petitionen. Hierbei wird sichergestellt, dass die `Cap_Potential`-Werte der Unterstützer *direkt und ausschließlich* aus dem vertrauenswürdigen `CapLedger`-Contract bezogen werden.
3.  Bereitstellung einer einfachen API (hier beispielhaft mit Flask) zum Abrufen von Petitionsdaten und Scores.
4.  Bildung der Schnittstelle zur Weiterleitung priorisierter Bedarfe ("Wozu?") an nachgelagerte Strategie- oder Ressourcen-Allokations-Prozesse ("Wie?").

## Setup & Konfiguration

1.  **Bibliotheken installieren:**
    ```bash
    pip install Flask python-dotenv web3
    ```
    (Optional: `pip install requests` für IPFS-Abfragen)
2.  **ABI-Dateien:** Die JSON-ABI-Dateien der kompilierten Smart Contracts (`CapPetition.json`, `CapLedger.json`) müssen im selben Verzeichnis wie das Skript oder einem konfigurierten Pfad vorhanden sein.
3.  **Umgebungsvariablen (`.env`-Datei):** Erstelle eine `.env`-Datei im selben Verzeichnis mit folgendem Inhalt:
    ```dotenv
    # URL deines Ethereum Nodes (z.B. Infura, Alchemy, Lokaler Node)
    NODE_URL=[https://goerli.infura.io/v3/DEIN_PROJEKT_ID](https://goerli.infura.io/v3/DEIN_PROJEKT_ID)

    # Deployed Adresse des CapPetition Contracts
    CAP_PETITION_ADDRESS=0x...

    # Deployed Adresse des CapLedger Contracts
    CAP_LEDGER_ADDRESS=0x...
    ```

## Architektur

* **Web Framework:** Nutzt Flask für die Bereitstellung von API-Endpunkten. (Kann durch FastAPI oder andere ersetzt werden).
* **Blockchain-Anbindung:** Verwendet `web3.py` zur Kommunikation mit der Ethereum-Blockchain über die konfigurierte `NODE_URL`.
* **Contract-Instanzen:** Erstellt `web3.eth.contract`-Instanzen für `CapPetition` und `CapLedger` unter Verwendung der Adressen und ABIs.
* **Präzision:** Nutzt Pythons `Decimal`-Typ für die Score-Berechnung, um Rundungsfehler zu vermeiden.

## Kernfunktionen

* **`get_cap_potential_securely(account: str, domain: bytes) -> Decimal | None`:**
    * Fragt das `Cap_Potential` eines Accounts für eine Domain sicher vom `CapLedger`-Contract ab.
    * Gibt den Wert als `Decimal` zurück oder `None` bei Fehler oder Potential von 0.
* **`calculate_weighted_score(petition_id: int) -> Decimal | None`:**
    * **Sicherheitskritisch:** Berechnet den gewichteten Score.
    * Holt die Liste der `supporters` vom `CapPetition`-Contract.
    * Ruft für JEDEN `supporter` die Funktion `get_cap_potential_securely` auf, um den *verifizierten* Wert vom `CapLedger` zu erhalten.
    * Summiert die Kehrwerte (`1 / potential`) nur für Unterstützer mit `potential > 0`.
    * Gibt den Gesamtscore als `Decimal` zurück oder `None` bei Fehlern.
* **`get_petition_details_with_score(petition_id: int)`:** (Beispielimplementierung im Code)
    * Kombiniert Daten aus `CapPetition.sol` mit dem berechneten Score.
    * *Hinweis:* Das Abrufen des Beschreibungsinhalts vom IPFS-Hash (`descriptionHash`) ist hier noch nicht implementiert.
* **`find_and_forward_prioritized_needs(threshold: Decimal)`:** (Beispielimplementierung im Code)
    * Identifiziert Petitionen, deren gewichteter Score einen Schwellenwert überschreitet.
    * **Integrationspunkt:** Hier muss die Logik eingefügt werden, um diese priorisierten Bedarfe ("Wozu?") an das Modul weiterzuleiten, das für die Initiierung des "Wie?" (Strategie, Ressourcen-Allokation) zuständig ist.

## API Endpunkte (Beispiele mit Flask)

* **`GET /petition/<int:petition_id>/score`:**
    * Gibt den berechneten, gewichteten Score für die angegebene Petitions-ID zurück.
    * Antwort: `{"petition_id": ID, "weighted_score": "SCORE_ALS_STRING"}` oder Fehler (404, 500).
* **`GET /petition/<int:petition_id>`:**
    * Gibt grundlegende Details der Petition zurück (ohne Unterstützerliste, ohne IPFS-Inhalt).
    * Antwort: JSON mit Petitionsdetails oder Fehler (404, 500).
* *(Weitere Endpunkte, z.B. zum Auflisten von Petitionen pro Domain, können hinzugefügt werden.)*

## Ausführen des Service

Starte den Flask-Entwicklungsserver (für Testzwecke):

```bash
python cap_petition_handler.py