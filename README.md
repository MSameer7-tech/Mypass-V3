<p align="center">
  <img src="assets/logo.png" alt="MyPass" width="100" />
</p>

<h1 align="center">MyPass</h1>

<p align="center">
  A local-first desktop password manager.<br/>
  Your credentials stay on your machine — encrypted, offline, and under your control.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-3.1.0-0969da?style=flat-square" alt="Version" />
  <img src="https://img.shields.io/badge/macOS-Apple%20Silicon-333?style=flat-square&logo=apple&logoColor=white" alt="macOS Apple Silicon" />
  <img src="https://img.shields.io/badge/Windows-x64%20%7C%20ARM64-0078d4?style=flat-square&logo=windows&logoColor=white" alt="Windows x64 & ARM64" />
  <img src="https://img.shields.io/badge/Tauri-v2-24c8db?style=flat-square&logo=tauri&logoColor=white" alt="Tauri v2" />
  <img src="https://img.shields.io/badge/React-19-61dafb?style=flat-square&logo=react&logoColor=black" alt="React 19" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/license-MIT-22c55e?style=flat-square" alt="MIT License" />
</p>

---

## Overview

MyPass is a desktop password manager that stores everything locally. It does not sync to a cloud, does not phone home, and does not require an account.

Built with a modern hybrid architecture using a **Tauri v2 + React 19** desktop shell and a bundled native **Python cryptographic engine**, MyPass communicates securely over private stdin/stdout IPC without opening any network ports.

**Current release (v3.1.0):** Native installers for **macOS (Apple Silicon)** and **Windows (x64 and ARM64)**.

---

## 🖥️ Interface

<p align="center">
  <img src="docs/screenshots/vault-annotated.jpg" alt="MyPass — Vault" width="800" />
</p>

<p align="center">
  <img src="docs/screenshots/login-annotated.jpg" alt="MyPass — Unlock" width="700" />
</p>

<p align="center">
  <img src="docs/screenshots/security-center-annotated.jpg" alt="MyPass — Security Center" width="800" />
</p>

<p align="center">
  <img src="docs/screenshots/password-details.png" alt="MyPass — Entry Details" width="400" />
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="docs/screenshots/settings.png" alt="MyPass — Settings" width="400" />
</p>

<p align="center">
  <em>Entry inspector with strength analysis &nbsp;·&nbsp; Preferences panel</em>
</p>

---

## ✨ Features

### 🗝️ Vault & Credential Management

- Create, edit, and delete credential entries
- Organize by category — Passwords, Secure Notes, Developer Keys, Work, Personal, Finance, Social
- Mark entries as favorites for quick access
- Real-time search and filtering across titles, usernames, and URLs
- Full password revision history tracked per entry

### 🔐 Security & Cryptography

- **AES-256-GCM** authenticated encryption for passwords and notes
- **Argon2id** key derivation (64 MB memory, 3 iterations, 4 parallel lanes)
- **Hardened Master Password Rotation**: Atomic in-memory pre-validation, full re-encryption, zero-loss rollback guarantee, and clean session boundary locking
- **Biometric Unlock**: Touch ID on macOS and Windows Hello on Windows
- Credential storage via OS-native vaults (macOS Keychain / Windows Credential Manager)
- Auto-lock after inactivity (default: 15 minutes, configurable)
- Clipboard auto-clear after copy (default: 30 seconds, configurable)
- No network access — the app is 100% offline

### ⚡ Productivity

- Secure password generator (configurable length, character sets, exclusion rules)
- Password strength indicator with entropy analysis
- One-click copy for usernames and passwords
- Command palette — `⌘K` / `Ctrl+K`
- Keyboard shortcuts — `⌘N` new entry · `⌘F` search · `⌘L` lock · `⌘,` settings

### 💾 Backup & Auditing

- Encrypted `.mypass` backup export (AES-256-GCM)
- Plaintext JSON export (with explicit user warnings)
- Import and merge from backup files with duplicate detection
- Native `.mypass` file association — double-click to import
- **Security Center** — offline vault health score, weak password detection, reuse detection, breach flagging

### 🎨 Experience

- Dark, Light, and System theme modes
- Smooth layout transitions powered by Framer Motion
- Compact density mode
- Optional website favicon display
- Resizable split-panel layout

---

## 🔐 Security Model

MyPass is designed from the ground up for strict local-first security.

### Encryption

All sensitive fields use **AES-256-GCM** authenticated encryption via Python's `cryptography` library (`cryptography.hazmat.primitives.ciphers.aead.AESGCM`). Each encrypted field is generated with a unique 12-byte cryptographically secure random nonce.

### Key Derivation

The master password is derived using **Argon2id**:

| Parameter | Value |
| :--- | :--- |
| Memory | 64 MB (`memory_cost=65536`) |
| Iterations | 3 |
| Parallelism | 4 lanes |
| Output key length | 256 bits (32 bytes) |
| Salt | 16 bytes, random, per-vault |

### What is encrypted at rest

| Data | Encrypted | Method |
| :--- | :--- | :--- |
| Passwords | ✅ Yes | AES-256-GCM, per-entry |
| Notes | ✅ Yes | AES-256-GCM, per-entry |
| Revision History | ✅ Yes | AES-256-GCM, per-entry |
| Titles | ❌ No | Plaintext in SQLite |
| Usernames | ❌ No | Plaintext in SQLite |
| Website URLs | ❌ No | Plaintext in SQLite |
| Categories / Tags | ❌ No | Plaintext in SQLite |

*Note:* Plaintext metadata enables fast instant search and filtering without decrypting every record on every keypress. The database file resides strictly in your OS user profile.

### Master Password Rotation (Hardened Lifecycle)

Master password change executes under a strict 6-stage lifecycle:
1. **Validation**: Verifies minimum length, enforces difference between old and new passwords, and applies failure rate-limiting.
2. **Zero-Write Pre-Validation**: 100% of all vault entries and historical revisions are decrypted into memory before any database write begins. If any record is corrupt or unreadable, the operation aborts with zero database mutations.
3. **Key Derivation & Self-Test**: Derives the new Argon2id key and performs an encryption/decryption roundtrip check on the vault identifier.
4. **In-Memory Re-Encryption**: Encrypts all vault records and history items with the new key.
5. **Atomic Multi-Table Transaction**: Updates `app_metadata`, `vault_entries`, `password_history`, and biometric flags in a single SQLite connection with automatic rollback on any failure.
6. **Session Boundary & OS Cleanup**: Purges old biometric secrets from the OS credential store and immediately locks the vault.

### Biometric Authentication

When biometrics (Touch ID / Windows Hello) are enabled:
1. A random 32-byte secret is generated and stored securely in the OS credential store (macOS Keychain or Windows Credential Manager).
2. The vault's derived master key is encrypted (wrapped) using AES-256-GCM with this secret.
3. On biometric unlock, the OS authenticates the user, retrieves the secret, and unwraps the master key.
4. The master password itself is never stored anywhere on disk.

### Session & Clipboard Security

- The master encryption key exists only in the active `VaultService` in memory while the vault is unlocked.
- Locking the vault destroys the service instance and zeroizes references.
- Auto-lock is triggered by frontend activity monitoring (mouse, keyboard, focus, visibility events).
- Clipboard contents are cleared automatically after a configurable duration (default: 30 seconds).

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                       MyPass                            │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │               React 19 + TypeScript               │  │
│  │            Tailwind CSS · Framer Motion           │  │
│  │              Zustand · React Query                │  │
│  └─────────────────────────┬─────────────────────────┘  │
│                            │ invoke("python_ipc")       │
│  ┌─────────────────────────▼─────────────────────────┐  │
│  │                  Tauri v2 / Rust                  │  │
│  │            Native Shell · Process Mgmt            │  │
│  └─────────────────────────┬─────────────────────────┘  │
│                            │ stdin/stdout JSON-RPC      │
│  ┌─────────────────────────▼─────────────────────────┐  │
│  │             Python Backend (Sidecar)              │  │
│  │                                                   │  │
│  │   Crypto ────────── Services ────────── Platform  │  │
│  │   AES-256-GCM       Vault               Keychain  │  │
│  │   Argon2id          Backup / Import     Win Hello │  │
│  │   Rotation          Password Generator  Touch ID  │  │
│  └─────────────────────────┬─────────────────────────┘  │
│                            │                            │
│  ┌─────────────────────────▼─────────────────────────┐  │
│  │       SQLite 3 Database + OS Credential Store     │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

The Python backend is packaged via PyInstaller in `--onedir` mode and bundled inside the desktop app as a native resource. It spawns without a console window, communicates strictly over local pipes, and shuts down cleanly with the frontend.

---

## 🧰 Tech Stack

| Layer | Technology |
| :--- | :--- |
| UI Framework | React 19, TypeScript 5.7 |
| Build Tool | Vite 6 |
| Styling | Tailwind CSS v4 |
| State Management | Zustand 5, TanStack React Query 5 |
| Animations | Framer Motion 12 |
| Icons | Lucide React |
| Validation | Zod |
| Desktop Shell | Tauri v2 (Rust 2021 edition) |
| Backend Engine | Python 3.11+ |
| Encryption | AES-256-GCM (`cryptography`) |
| Key Derivation | Argon2id |
| Database | SQLite 3 (WAL Mode) |
| Platform Auth | macOS Keychain (Touch ID), Windows Hello (`WinRT`) |
| Sidecar Packaging | PyInstaller 6 (`--onedir`) |

---

## 📦 Installation

### Pre-Built Binaries

Download the appropriate installer from the [Releases](https://github.com/MSameer7-tech/Mypass-V3/releases) page:

| Platform | Package | Architecture |
| :--- | :--- | :--- |
| **macOS** | `MyPass_3.1.0_aarch64.dmg` | Apple Silicon (M1/M2/M3/M4) |
| **Windows** | `MyPass_3.1.0_x64-setup.exe` | Windows 10/11 (64-bit Intel/AMD) |
| **Windows** | `MyPass_3.1.0_arm64-setup.exe` | Windows 11 (ARM64 Snapdragon/Ampere) |
| **Checksums** | `SHA256SUMS.txt` | Cryptographic file hashes |

> **macOS Gatekeeper Note:** Because MyPass is not code-signed with a paid Apple Developer certificate, macOS will display an unrecognized developer notice on first run.
> 
> To bypass Gatekeeper quarantine, you can either:
> 1. Right-click `MyPass.app` in Finder $\rightarrow$ Click **Open** $\rightarrow$ Click **Open** in the dialog.
> 2. Or run this command in Terminal after moving the app to Applications:
>    ```bash
>    xattr -cr /Applications/MyPass.app
>    ```
>
> **Windows SmartScreen Note:** Windows may prompt a SmartScreen warning for new unsigned installers. Click **More info** $\rightarrow$ **Run anyway**.

---

### Build From Source

**Prerequisites:**
- Node.js 20+ & pnpm 11+
- Python 3.11+
- Rust (Latest stable)

```bash
# 1. Clone the repository
git clone https://github.com/MSameer7-tech/Mypass-V3.git
cd Mypass-V3

# 2. Set up Python virtual environment & build sidecar
cd backend
python -m venv venv
source venv/bin/activate        # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python build_sidecar.py

# 3. Install frontend dependencies
cd ../frontend
pnpm install

# 4. Run in development mode
pnpm tauri dev

# 5. Build production bundle & installer
pnpm tauri build
```

Production installers are generated under `frontend/src-tauri/target/release/bundle/`.

---

## 🧪 Testing & CI

```bash
# Backend unit & crypto test suite (82+ tests)
PYTHONPATH=backend pytest backend/tests -q

# Frontend type checking
cd frontend
pnpm typecheck

# Frontend unit & component tests (30+ tests)
pnpm test

# Frontend production bundle check
pnpm build
```

**Automated CI/CD:** GitHub Actions executes quality gates, native sidecar compilation, PE/Mach-O binary architecture verification, and multi-platform packaging across `macos-14`, `windows-latest` (x64), and `windows-11-arm`.

---

## 🗺️ Roadmap

- [x] Tauri v2 + React 19 desktop rewrite
- [x] Python IPC sidecar architecture (fast launch, hidden console)
- [x] AES-256-GCM encrypted local vault with Argon2id
- [x] macOS Touch ID & Keychain integration
- [x] Windows Hello & Windows Credential Manager integration
- [x] Master Password Rotation with zero-loss rollback guarantee
- [x] Windows native installer support (x64 & ARM64 NSIS)
- [x] Automated multi-platform GitHub Actions release pipeline
- [ ] Apple Developer & Microsoft code signing / notarization
- [ ] Linux packaging (AppImage / Flatpak)
- [ ] Browser extension companion

---

## ⚠️ Security Notice

MyPass uses established, standard cryptographic primitives (AES-256-GCM, Argon2id) and local-first architecture. It is an actively maintained open-source application and has **not undergone an independent third-party security audit**.

If you discover a security issue or vulnerability, please report it via GitHub Issues or contact the maintainer directly.

---

## 📄 License

[MIT](LICENSE) — © 2026 Mohammad Sameer

---

## 👨‍💻 Author

**Sameer** — [github.com/MSameer7-tech](https://github.com/MSameer7-tech)

<p align="center">
  If MyPass is useful to you, consider giving the repository a ⭐
</p>
