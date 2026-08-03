# MyPass Desktop Application Architecture

## Overview
MyPass is a local-first, privacy-focused native desktop password manager. It features a modern, high-performance desktop presentation layer built with **Tauri 2.0 + React 19 + TypeScript + Tailwind CSS + shadcn/ui + Framer Motion**, backed by a production-grade **Python Cryptographic Engine**.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Tauri WebView UI                     │
│  (React 19, TypeScript, Tailwind, Framer Motion, Zustand) │
└────────────────────────────┬────────────────────────────┘
                             │  Tauri IPC (Commands)
┌────────────────────────────▼────────────────────────────┐
│                    Tauri Core (Rust)                    │
│   (Process Supervision, OS Integrations, Window Shell)  │
└────────────────────────────┬────────────────────────────┘
                             │  Local Subprocess IPC (STDIN/STDOUT)
┌────────────────────────────▼────────────────────────────┐
│                 Python Backend Engine                   │
│   (Cryptography, Vault Repositories, Security Audit)    │
└────────────────────────────┬────────────────────────────┘
                             │  AES-256-GCM / Argon2id
┌────────────────────────────▼────────────────────────────┐
│                Encrypted SQLite Vault DB                │
└─────────────────────────────────────────────────────────┘
```

---

## Security Boundaries & Cryptographic Model

1. **Local-First & Offline**: All master password key derivations (Argon2id) and vault encryptions (AES-256-GCM) take place locally. No sensitive data ever leaves the local machine.
2. **IPC Security**: Sensitive payload transfers across the IPC bridge are encrypted in memory or handled via ephemeral memory buffers. Passwords in memory are wiped upon session lock.
3. **Session Lifecycle**:
   - `LOCKED`: Memory buffers cleared, master key purged, UI displays UnlockScreen.
   - `UNLOCKING`: Argon2id key derivation runs in background thread.
   - `UNLOCKED`: Vault service loaded; auto-lock timer active (clears memory after idle timeout).

---

## Repository Layout

```
Password-Manager-App/
├── ARCHITECTURE.md           # This document
├── main.py                   # Python backend entry point / IPC runner
├── database/                 # SQLite schema, connection pool & repositories
├── services/                 # Cryptography, VaultService, MasterPasswordService, TOTP, BreachDetection
├── crypto/                   # Encryption primitives (AES-256-GCM, Argon2id)
├── security/                 # Security audit, clipboard manager, session lock
├── utils/                    # Constants, logging, path helpers
├── frontend/                 # Tauri + React 19 Desktop UI
│   ├── src-tauri/            # Rust Tauri 2.0 configuration & command handlers
│   └── src/                  # React + TypeScript source
│       ├── app/              # Application bootstrap & providers
│       ├── components/       # Storybook UI component library
│       ├── features/         # Auth, Vault, Search, Settings domains
│       ├── stores/           # Zustand state management
│       ├── api/              # Decoupled IPC API adapter
│       └── styles/           # Design tokens & CSS custom properties
└── tests/                    # Pytest backend test suite
```

---

## Data Flow Pipeline

1. **User Input / Action**: User performs an action in React UI (e.g. unlocks vault, searches entries, copies password).
2. **Zustand Store**: Feature component calls Zustand store method.
3. **Frontend API Adapter**: Store invokes `src/api/` adapter method.
4. **Tauri IPC**: Tauri command invokes Rust handler asynchronously.
5. **Python Backend**: Rust handler executes request against Python backend process.
6. **Database / Crypto**: Python backend reads/decrypts SQLite vault data.
7. **Response Flow**: Decrypted response is returned back through IPC adapter to Zustand store and rendered in React UI at 60fps.
