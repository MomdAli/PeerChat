# PeerChat Protokoll-Spezifikation

## Übersicht
Dieses Dokument beschreibt die Protokolle für die Kommunikation im PeerChat-System:
- **Client-Server-Protokoll** (TCP): Registrierung, Broadcast, Peer-Informationen
- **Peer-to-Peer-Protokoll** (TCP): Chat-Anfragen, Chat-Nachrichten, Verbindungsmanagement
- **UDP-Hinweise**: Peer-Discovery, Paketverlust

Die Protokolle spezifizieren Nachrichtenformate, erlaubte Nachrichtenreihenfolgen und das Verhalten bei Fehlern ("good path" und "bad path").

---

## 1. Client-Server-Protokoll (TCP)

### Nachrichtenformate
- `REGISTER <nickname> <udp_port>`
  → Registrierung eines Clients. Antwort: `NICKNAME_TAKEN`, `JOINED ...` oder `ERROR <reason>`
- `PORT <nickname> <tcp_port>`
  → Übermittlung des eigenen TCP-Ports nach erfolgreicher Registrierung.
- `JOINED <nickname> <ip> <udp_port> <tcp_port>`
  → Ein Peer ist dem Chat beigetreten (Server → Client).
- `LEFT <nickname>`
  → Ein Peer hat den Chat verlassen (Server → Client).
- `BROADCAST <message>`
  → Nachricht an alle Clients (Client → Server → alle Clients).
- `NICKNAME_TAKEN`
  → Nickname ist bereits vergeben (Server → Client).
- `ERROR <reason>`
  → Fehlerhafte, unerwartete oder ungültige Nachricht (Server → Client).

### Ablauf (Reihenfolge)
1. Client → Server: `REGISTER ...`
2. Server → Client: `JOINED ...` (eigene Registrierung und alle anderen Peers)
3. Client → Server: `PORT ...`
4. Danach: `BROADCAST ...` und weitere Nachrichten erlaubt

### Fehlerfälle ("bad path")
- Falsches Format, doppelte Registrierung, unerwartete Nachrichten: `ERROR <reason>`
- Nickname-Konflikt: `NICKNAME_TAKEN`

---

## 2. Peer-to-Peer-Protokoll (TCP)

### Nachrichtenformate
- `CHAT_REQUEST <nickname>`
  → Anfrage, einen privaten Chat zu starten
- `CHAT_ACCEPT <nickname>`
  → Annahme der Chat-Anfrage
- `CHAT_REJECT <nickname>`
  → Ablehnung der Chat-Anfrage
- `LEFT_CHAT <nickname>`
  → Peer verlässt den privaten Chat
- `CHAT_MSG <nickname> <message>`
  → Chat-Nachricht zwischen Peers
- `ERROR <reason>`
  → Fehlerhafte, unerwartete oder ungültige Nachricht

### Ablauf (Reihenfolge)
1. Peer A → Peer B: `CHAT_REQUEST ...`
2. Peer B → Peer A: `CHAT_ACCEPT ...` oder `CHAT_REJECT ...`
3. Nach Annahme: `CHAT_MSG ...` beliebig oft in beide Richtungen
4. Beenden: `LEFT_CHAT ...`

### Fehlerfälle ("bad path")
- Falsches Format, unerwartete Nachrichten: `ERROR <reason>`
- Keine Antwort auf Chat-Anfrage: Timeout, Verbindung wird geschlossen

---

## 3. UDP-Hinweise
- UDP wird für Peer-Discovery oder optionale Nachrichten genutzt.
- **Paketverlust ist möglich!** Kritische Nachrichten sollten ggf. wiederholt oder bestätigt werden (ACK/NACK optional).
- Für nicht-kritische Nachrichten wird Paketverlust toleriert.

---

## 4. TCP-Bytestrom und Nachrichtenextraktion
- Alle TCP-Nachrichten werden mit einer 10-Byte-Längenpräfixierung übertragen, sodass Nachrichten eindeutig aus dem Bytestrom extrahiert werden können.

---

## 5. Zustandsautomat (State Machine)
- Ein Client muss sich zuerst registrieren (`REGISTER`), dann den eigenen Port senden (`PORT`), bevor weitere Nachrichten erlaubt sind.
- Der Server akzeptiert keine weiteren `REGISTER`-Nachrichten nach erfolgreicher Anmeldung.
- Nachrichten, die nicht zum aktuellen Zustand passen, werden mit `ERROR` beantwortet.
- Peer-to-Peer: Erst nach erfolgreichem Handshake (`CHAT_REQUEST`/`CHAT_ACCEPT`) dürfen Chat-Nachrichten gesendet werden.

---

## 6. Fehlerbehandlung
- Jede falsch formatierte, unerwartete oder ausbleibende Nachricht wird mit `ERROR <reason>` beantwortet.
- Bei Verbindungsabbruch oder Timeout wird die Verbindung geschlossen und der Benutzer informiert.

---

*Letzte Aktualisierung: 2025-05-24*