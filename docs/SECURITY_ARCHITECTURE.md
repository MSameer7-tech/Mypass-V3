# MyPass Security & Cryptographic Architecture

## 1. Local-First & Threat Model

MyPass operates strictly as a local-first application. No vault records, master passwords, or encryption keys are transmitted to any cloud servers or third-party APIs.

### Primary Threat Mitigations
- **Memory Inspection**: Master keys derived via Argon2id exist only in volatile memory during `UNLOCKED` state.
- **IPC Sniffing**: Local IPC bridge commands operate over stdin/stdout process channels within local process boundaries. Sensitive inputs (passwords) are transferred using zero-copy byte buffers wiped immediately after processing.
- **Clipboard Leakage**: Passwords copied to system clipboard automatically purge after 45 seconds using `ClipboardService`.
- **Database Compromise**: Database stored on disk (`mypass.db`) is encrypted using AES-256-GCM authenticated encryption.

---

## 2. Session Lifecycle & Key Hierarchy

```
               ┌────────────────────────┐
               │    Master Password     │
               └───────────┬────────────┘
                           │  Argon2id (Salt, Time=3, Mem=64MB)
                           ▼
               ┌────────────────────────┐
               │   Master Encryption    │
               │       Key (256-bit)    │
               └───────────┬────────────┘
                           │  AES-256-GCM
         ┌─────────────────┴─────────────────┐
         ▼                                   ▼
┌─────────────────┐                 ┌─────────────────┐
│ Vault Entry Key │                 │ Vault Database  │
└─────────────────┘                 └─────────────────┘
```

### State Transitions
1. **`LOCKED`**:
   - Master Encryption Key purged from memory (`sys.memzero` / Python string release).
   - Vault DB connection closed.
   - UI displays `UnlockScreen` with zero cached entry records.
2. **`UNLOCKING`**:
   - Master password verified against Argon2id key derivation hash.
   - Key derived asynchronously off main loop.
3. **`UNLOCKED`**:
   - Vault entries loaded into local memory cache.
   - Inactivity idle timer active (triggers auto-lock upon 15 minutes of idle time).

---

## 3. Extensible Auth Provider Model

Authentication flows are abstracted through an `AuthProvider` interface:

```typescript
export interface AuthProvider {
  unlock(masterPassword: string): Promise<UnlockResult>;
  lock(): Promise<void>;
  supportsBiometrics(): Promise<boolean>;
  authenticateBiometrics(): Promise<BiometricResult>;
}
```

Implementations:
- `PasswordAuthProvider` (Primary master password)
- `AppleBiometricsAuthProvider` (macOS Touch ID)
- `PasskeyAuthProvider` (Future expansion)
