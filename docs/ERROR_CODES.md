# MyPass Error Code Dictionary (`ERROR_CODES.md`)

## Overview
To prevent the frontend from parsing exception strings or stack traces, the backend exposes standardized, strongly typed error codes. The React UI maps these error codes to localized error messages and toast notifications.

---

## Error Code Registry

| Error Code | Category | HTTP Equivalent | Description |
| :--- | :--- | :--- | :--- |
| **`AUTH_INVALID_PASSWORD`** | Auth | `401 Unauthorized` | Master password check failed. |
| **`AUTH_SESSION_LOCKED`** | Auth | `403 Forbidden` | Requested operation requires unlocked session. |
| **`AUTH_VAULT_NOT_FOUND`** | Auth | `404 Not Found` | No vault database file exists at path. |
| **`AUTH_DATABASE_LOCKED`** | Auth | `423 Locked` | Database connection busy or locked by another process. |
| **`VAULT_ENTRY_NOT_FOUND`** | Vault | `404 Not Found` | Requested entry ID does not exist in database. |
| **`VAULT_VALIDATION_FAILED`** | Vault | `422 Unprocessable` | Entry payload missing required fields (e.g. empty title). |
| **`VAULT_CORRUPTED_RECORD`** | Vault | `500 Internal Error` | Decryption failed for target record payload. |
| **`GENERATOR_INVALID_LENGTH`** | Generator | `400 Bad Request` | Password length outside allowed range (8-128). |
| **`CLIPBOARD_UNAVAILABLE`** | System | `503 Service Unavailable` | System OS clipboard access denied or failed. |
| **`SEARCH_TIMEOUT`** | Search | `504 Gateway Timeout` | Vault search query exceeded execution threshold. |
