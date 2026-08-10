<p align="center">
  <img src="assets/logo.png" alt="MyPass" width="120" />
</p>

<h1 align="center">MyPass</h1>

<p align="center">
  <strong>A local-first desktop password manager built with Tauri, React, and Python.</strong><br/>
  Your credentials never leave your machine.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-3.0.0-blue?style=flat-square" alt="Version" />
  <img src="https://img.shields.io/badge/platform-macOS-lightgrey?style=flat-square&logo=apple" alt="macOS" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License" />
  <img src="https://img.shields.io/badge/encryption-AES--256--GCM-orange?style=flat-square" alt="Encryption" />
  <img src="https://img.shields.io/badge/Tauri-v2-blue?style=flat-square&logo=tauri" alt="Tauri v2" />
</p>

---

## Why MyPass?

Most password managers store your vault on someone else's server. MyPass keeps everything on your local machine — encrypted at rest, unlocked only when you need it, and never transmitted anywhere.

It's a native desktop app — not Electron, not a web wrapper. The frontend is rendered by the system's native WebView via [Tauri](https://tauri.app/), the UI is built with React, and the cryptographic backend runs as a bundled Python process communicating over stdio IPC.

---

## Features

<table>
<tr>
<td width="50%" valign="top">

### 🔐 Security
- **AES-256-GCM** encryption for passwords and notes
- **Argon2id** key derivation from master password
- **Touch ID** biometric unlock on macOS
- Platform credential storage via OS keychain
- Auto-lock on inactivity (configurable timer)
- Clipboard auto-clear after 30 seconds
- No network access — fully offline

</td>
<td width="50%" valign="top">

### 🗝️ Vault Management
- Create, edit, and delete credential entries
- Organize by category: Passwords, Secure Notes, Developer Keys, Work, Personal, Finance, Social
- Mark entries as favorites
- Real-time search and filtering
- Password history tracking per entry

</td>
</tr>
<tr>
<td width="50%" valign="top">

### ⚡ Productivity
- Secure password generator
- Password strength indicator (Very Weak → Very Strong)
- One-click copy to clipboard
- Command palette (`⌘K`)
- Keyboard shortcuts: `⌘N` new entry, `⌘F` search, `⌘L` lock, `⌘,` settings

</td>
<td width="50%" valign="top">

### 💾 Backup & Security Auditing
- Encrypted `.mypass` backup export (AES-256-GCM)
- Plaintext JSON export (with warnings)
- Import and merge from backup files
- **Security Center** dashboard with vault health score
- Detects weak passwords, reused credentials, and breached entries

</td>
</tr>
<tr>
<td colspan="2" valign="top">

### 🎨 Experience
- Dark, Light, and System theme modes
- Smooth animations powered by Framer Motion
- Compact mode for dense layouts
- Optional website favicon display
- Native `.mypass` file association — double-click to import
- Resizable panel layout

</td>
</tr>
</table>

---

## Architecture

MyPass uses a hybrid architecture: a Tauri + React frontend handles the UI and user interaction, while a Python backend manages all cryptographic operations, database access, and platform authentication.

The two layers communicate over **stdin/stdout IPC** using a JSON-RPC protocol — no local network ports are opened.

```
┌─────────────────────────────────────────────────┐
│                   MyPass.app                    │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │           React + TypeScript              │  │
│  │     Tailwind CSS · Framer Motion          │  │
│  │     Zustand · React Query · Zod           │  │
│  └──────────────────┬────────────────────────┘  │
│                     │  invoke("python_ipc")      │
│  ┌──────────────────▼────────────────────────┐  │
│  │              Tauri v2 (Rust)              │  │
│  │        stdin/stdout IPC bridge            │  │
│  └──────────────────┬────────────────────────┘  │
│                     │  JSON-RPC over stdio       │
│  ┌──────────────────▼────────────────────────┐  │
│  │          Python Backend (bundled)         │  │
│  │                                           │  │
│  │  ┌─────────┐ ┌────────────┐ ┌──────────┐ │  │
│  │  │ Crypto  │ │  Services  │ │ Platform │ │  │
│  │  │AES-256  │ │   Vault    │ │  Auth    │ │  │
│  │  │Argon2id │ │  Backup    │ │ Keychain │ │  │
│  │  │         │ │  Search    │ │ Touch ID │ │  │
│  │  └────┬────┘ └─────┬──────┘ └──────────┘ │  │
│  │       │            │                      │  │
│  │  ┌────▼────────────▼──────────────────┐   │  │
│  │  │          SQLite Database           │   │  │
│  │  │   (per-field AES-256-GCM at rest)  │   │  │
│  │  └────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology |
| :--- | :--- |
| Frontend | React 19, TypeScript 5.7, Vite 6 |
| Styling | Tailwind CSS v4 |
| Animations | Framer Motion |
| State | Zustand + TanStack React Query |
| Icons | Lucide React |
| Desktop Shell | Tauri v2 (Rust) |
| Backend | Python 3.11+ |
| Encryption | `cryptography` (AES-256-GCM) |
| KDF | Argon2id (64 MB memory, 3 iterations, 4 lanes) |
| Database | SQLite 3 |
| Platform Auth | macOS Keychain, Touch ID (`LocalAuthentication`) |
| Sidecar Packaging | PyInstaller (`--onedir`) |

---

## Security Model

MyPass is a password manager, so the security implementation matters. Here is exactly what is implemented — no exaggeration.

### What is encrypted

| Data | Method | Notes |
| :--- | :--- | :--- |
| Passwords | AES-256-GCM | Encrypted per-entry with unique nonces |
| Notes | AES-256-GCM | Encrypted per-entry with unique nonces |
| Backup files (`.mypass`) | AES-256-GCM | Key derived from master password |
| Biometric key wrapping | AES-256-GCM | Master key wrapped with keychain secret |

### What is NOT encrypted

| Data | Storage |
| :--- | :--- |
| Entry titles, usernames, URLs, categories, tags | Plaintext in SQLite |
| SQLite database file | Not full-disk encrypted by the app |

This is a deliberate trade-off: plaintext metadata enables fast search and filtering without decrypting every entry. Sensitive fields (passwords, notes) are always encrypted at rest.

### Key Derivation

The master password is processed through **Argon2id** with these parameters:

- Memory: 64 MB (`memory_cost=65536`)
- Iterations: 3
- Parallelism: 4 lanes
- Output: 256-bit key
- Salt: 16 bytes (random, per-vault)

### Biometric Authentication

When Touch ID is enabled:
1. A random 32-byte secret is generated and stored in the macOS Keychain
2. The derived master key is wrapped (encrypted) using that secret
3. On biometric unlock, the secret is retrieved from the Keychain, and the master key is unwrapped
4. The master password itself is never stored

### Session Security

- The derived encryption key exists only in the `VaultService` instance in memory
- Locking the vault destroys the service instance and the key reference
- Auto-lock is triggered by frontend inactivity detection (mouse, keyboard, visibility)
- Clipboard is automatically cleared after a configurable timeout (default: 30 seconds)

---

## Installation

### Download

Grab the latest `.dmg` from the [Releases](https://github.com/MSameer7-tech/Mypass-V3/releases) page.

**Requirements:**
- macOS 10.15 (Catalina) or later
- Apple Silicon (arm64)

> **Note:** The app is not yet code-signed or notarized. On first launch, you may need to right-click → Open, or allow it in System Preferences → Security & Privacy.

---

## Development Setup

### Prerequisites

| Tool | Version |
| :--- | :--- |
| Node.js | 20+ |
| pnpm | 11+ |
| Python | 3.11+ |
| Rust | Latest stable |

### 1. Clone the repository

```bash
git clone https://github.com/MSameer7-tech/Mypass-V3.git
cd Mypass-V3
```

### 2. Set up the Python backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Build the Python sidecar

```bash
python build_sidecar.py
```

This runs PyInstaller in `--onedir` mode and copies the output to `frontend/src-tauri/resources/ipc_bridge_app/`.

### 4. Set up the frontend

```bash
cd ../frontend
pnpm install
```

### 5. Run in development mode

```bash
pnpm tauri dev
```

### 6. Build for production

```bash
pnpm tauri build
```

The production `.dmg` will be generated in `frontend/src-tauri/target/release/bundle/dmg/`.

---

## Project Structure

```
MyPass/
├── backend/                    # Python backend
│   ├── ipc_bridge.py           # JSON-RPC stdin/stdout bridge
│   ├── app.py                  # Application entry point
│   ├── config.py               # Configuration
│   ├── build_sidecar.py        # PyInstaller build script
│   ├── crypto/                 # AES-256-GCM, Argon2id, clipboard
│   ├── database/               # SQLite schema and operations
│   ├── services/               # Vault, auth, backup, generator
│   ├── platform_auth/          # macOS Touch ID, Windows Hello
│   ├── utils/                  # Shared utilities
│   └── tests/                  # pytest test suite
├── frontend/                   # Tauri + React frontend
│   ├── src/                    # React components, hooks, stores
│   │   ├── features/           # Auth, vault, settings, security
│   │   ├── stores/             # Zustand state stores
│   │   ├── api/                # Tauri IPC client
│   │   └── queries/            # React Query hooks
│   ├── src-tauri/              # Tauri/Rust shell
│   │   ├── src/lib.rs          # IPC bridge, process management
│   │   ├── tauri.conf.json     # App config, bundle settings
│   │   └── resources/          # Bundled Python sidecar (generated)
│   └── package.json
├── contracts/                  # IPC schema definitions
├── docs/                       # Architecture and design docs
├── assets/                     # Icons and branding
└── .github/workflows/ci.yml    # CI: pytest + TypeScript checks
```

---

## CI/CD

GitHub Actions runs on every push and pull request:

- **Backend:** Python 3.11 + `pytest` (excluding GUI tests)
- **Frontend:** Node 20 + pnpm 11 + TypeScript type checking

---

## Roadmap

- [ ] Apple code signing and notarization
- [ ] Master password change
- [ ] Windows support
- [ ] Linux support
- [ ] Browser extension integration

---

## License

[MIT](LICENSE) — © 2026 Mohammad Sameer
