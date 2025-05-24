---
applyTo: '**'
---
Project Context: PeerChat Group Chat Application
---

- This project implements a group chat system with both client-server and peer-to-peer communication.
- All protocol messages must use the helpers defined in `network/protocol.py` (e.g., `make_error`, `make_nickname_taken`, etc.).
- The server must respond with `NICKNAME_TAKEN` if a nickname is already in use, and with `ERROR <reason>` for malformed or unexpected messages.
- The client must handle `NICKNAME_TAKEN` and `ERROR` messages appropriately, triggering the correct UI callbacks.
- All new protocol features or changes must be reflected in `network/protocol.py` and documented in `network/README.md`.
- Follow Python best practices and keep code modular and well-commented.