# PeerChat

A modern, modular peer-to-peer chat application with a beautiful Catppuccin Mocha-inspired interface.

> **Project for Hochschule Konstanz (HTWG) — Rechnernetze**

---

## Overview

**PeerChat** lets you chat directly with peers on your network, featuring a sleek, themed GUI, real-time peer discovery, and robust, modular code.

---

## Project Structure

- `server/` — Server logic and entry point
- `client/` — Client core logic and entry point
- `network/` — TCP/UDP helpers and protocol definitions
- `gui/` — Modular, class-based GUI (with reusable components)
  - `components/` — Peer list, chat area, message entry, broadcast box, etc.
- `theme/` — Centralized color palette and font management

---

## How to Run

### 1. Start the Server

```bash
python -m server.main
```

### 2. Start the Client (GUI)

```bash
python -m client.main
```

---

## 💡 Features

- **Modern, Themed GUI**: Catppuccin Mocha palette, custom fonts, and smooth layout
- **Login & Peer List**: Register with a nickname, see who's online in real time
- **Direct Peer-to-Peer Chat**: Secure, direct TCP connections for private messaging
- **Broadcast Box**: System messages and announcements
- **Peer Discovery**: Fast, automatic detection via UDP
- **Chat History**: Timestamped, color-coded messages
- **Robust Error Handling**: Friendly feedback for network issues
- **Modular Codebase**: Easy to extend, with reusable GUI components

---

## Screenshots

> ![screenshot-1](assets/screenshot-1.png)

---

## About

This project was developed as part of the Rechnernetze (Computer Networks) course at Hochschule Konstanz (HTWG). It's a hands-on exploration of peer-to-peer networking, GUI design, and clean software architecture.

---

## License

MIT — Free to use, modify, and learn from!
