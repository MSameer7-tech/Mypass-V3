# MyPass IPC Bridge Specification (`IPC_SPEC.md`)

## Overview
This document defines every callable backend method exposed across the local process IPC bridge between the Tauri desktop frontend and the Python backend process.

All IPC calls follow an asynchronous Request / Response protocol.

---

## 1. Authentication & Session Methods

### `auth:unlock`
Unlocks the password vault by deriving the master key via Argon2id.
- **Request**:
  ```json
  {
    "masterPassword": "string"
  }
  ```
- **Response Success**:
  ```json
  {
    "success": true,
    "sessionState": "UNLOCKED",
    "errorMessage": null
  }
  ```
- **Response Failure**:
  ```json
  {
    "success": false,
    "sessionState": "LOCKED",
    "errorCode": "AUTH_INVALID_PASSWORD",
    "errorMessage": "Wrong master password."
  }
  ```

### `auth:lock`
Immediately locks the session, clears memory buffers, and purges keys.
- **Request**: `{}`
- **Response**:
  ```json
  {
    "success": true,
    "sessionState": "LOCKED"
  }
  ```

### `auth:getStatus`
Returns the current session state and auto-lock timeout.
- **Response**:
  ```json
  {
    "sessionState": "UNLOCKED",
    "idleTimeoutSeconds": 900
  }
  ```

---

## 2. Vault Management Methods

### `vault:listEntries`
Lists summary metadata for all entries in the vault.
- **Request**: `{}`
- **Response**:
  ```json
  {
    "entries": [
      {
        "id": 1,
        "title": "GitHub",
        "username": "developer@mypass.app",
        "website": "https://github.com",
        "category": "Work",
        "favorite": true,
        "createdAt": "2026-08-01T12:00:00Z",
        "updatedAt": "2026-08-03T10:00:00Z"
      }
    ]
  }
  ```

### `vault:getEntryDetails`
Fetches full sensitive details (decrypted password, notes, TOTP) for a single entry.
- **Request**:
  ```json
  {
    "id": 1
  }
  ```
- **Response**:
  ```json
  {
    "entry": {
      "id": 1,
      "title": "GitHub",
      "username": "developer@mypass.app",
      "password": "DecryptedPassword123!",
      "website": "https://github.com",
      "notes": "Personal access token stored in notes.",
      "category": "Work",
      "favorite": true,
      "totpSecret": "JBSWY3DPEHPK3PXP",
      "createdAt": "2026-08-01T12:00:00Z",
      "updatedAt": "2026-08-03T10:00:00Z"
    }
  }
  ```

### `vault:createEntry`
Creates a new vault entry.
- **Request**: `VaultCreateDTO`
- **Response**: `VaultEntryDTO`

### `vault:updateEntry`
Updates an existing vault entry.
- **Request**: `VaultUpdateDTO`
- **Response**: `VaultEntryDTO`

### `vault:deleteEntry`
Deletes a vault entry by ID.
- **Request**: `{ "id": 1 }`
- **Response**: `{ "success": true, "deletedId": 1 }`

---

## 3. Password Generator & Clipboard Methods

### `generator:generatePassword`
Generates a cryptographically secure random password.
- **Request**:
  ```json
  {
    "length": 20,
    "useUppercase": true,
    "useLowercase": true,
    "useDigits": true,
    "useSymbols": true
  }
  ```
- **Response**:
  ```json
  {
    "password": "k9#mP2$xL5!vQ8@zW1^n",
    "entropyBits": 128.4
  }
  ```

### `clipboard:copy`
Copies text to system clipboard with a 45-second auto-clear timer.
- **Request**:
  ```json
  {
    "text": "SensitivePassword123!",
    "isSensitive": true,
    "autoClearSeconds": 45
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "clearsAt": "2026-08-03T19:30:45Z"
  }
  ```
