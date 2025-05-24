# PeerChat Protokoll

## Nachrichtenformate

### Client → Server

- `REGISTER <nickname> <udp_port>`
    - Registriert einen neuen Benutzer.
    - Antwort: `NICKNAME_TAKEN` oder `JOINED ...` oder `ERROR <reason>`

### Server → Client

- `NICKNAME_TAKEN`
    - Nickname ist bereits vergeben.
- `ERROR <reason>`
    - Bei falsch formatierten oder unerwarteten Nachrichten.
- `JOINED <nickname> <ip> <udp_port> <tcp_port>`
    - Ein Benutzer ist dem Chat beigetreten.
- `LEFT <nickname>`
    - Ein Benutzer hat den Chat verlassen.

## Fehlerfälle

- Bei falsch formatierten Nachrichten:
  `ERROR Invalid <command> format`
- Bei unbekannten Nachrichten:
  `ERROR Unknown command`
- Bei Nickname-Konflikt:
  `NICKNAME_TAKEN`

## UDP Hinweise

- UDP-Nachrichten können verloren gehen. Kritische Nachrichten sollten ggf. wiederholt oder bestätigt werden (ACK/NACK Mechanismus ist optional und aktuell nicht implementiert).
- Für Peer-Discovery und nicht-kritische Nachrichten wird Paketverlust toleriert.
- Für kritische Nachrichten (z.B. Chat-Anfragen) empfiehlt sich eine Wiederholung nach Timeout, falls keine Antwort empfangen wird.

## Timeouts und Verbindungsabbrüche

- Wenn nach einer Anfrage (z.B. CHAT_REQUEST) innerhalb eines definierten Zeitraums keine Antwort (ACCEPT/REJECT) empfangen wird, sollte der Client den Benutzer informieren und die Anfrage als fehlgeschlagen betrachten.
- Bei Verbindungsabbruch (z.B. keine Daten mehr über TCP, oder explizite Fehlermeldung) wird der Benutzer informiert und die Verbindung geschlossen.
- Es werden keine expliziten Keepalive/Heartbeat-Nachrichten gesendet, aber dies kann für eine robustere Implementierung ergänzt werden.

## Zustandsautomat (State Machine)

- Ein Client muss sich zuerst mit REGISTER anmelden und auf JOINED warten, bevor weitere Nachrichten gesendet werden.
- Erst nach erfolgreicher Registrierung dürfen BROADCAST, PORT und andere Nachrichten gesendet werden.
- Der Server akzeptiert keine weiteren REGISTER-Nachrichten nach erfolgreicher Anmeldung.
- Nachrichten, die nicht zum aktuellen Zustand passen (z.B. BROADCAST vor Registrierung), werden mit ERROR beantwortet.
- Peer-to-peer: CHAT_REQUEST darf nur gesendet werden, wenn eine TCP-Verbindung zu einem Peer besteht.
- Nach einem LEFT_CHAT oder Verbindungsabbruch ist keine weitere Kommunikation erlaubt.

## Beispiel für erlaubte Nachrichtenreihenfolge

1. Client → Server: REGISTER <nickname> <udp_port>
2. Server → Client: JOINED ...
3. Client → Server: PORT <nickname> <tcp_port>
4. Server → Client: JOINED ... (für andere Peers)
5. Client → Server: BROADCAST <message>
6. Peer-to-peer: CHAT_REQUEST <nickname>
7. Peer-to-peer: CHAT_ACCEPT/CHAT_REJECT <nickname>
8. Peer-to-peer: LEFT_CHAT <nickname>

---

*Letzte Aktualisierung: 2025-05-24*