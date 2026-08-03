# MyPass Comprehensive UI & Component Inventory (`UI_INVENTORY.md`)

## 1. Authentication Screens & Overlays
- [ ] **UnlockScreen**: Master password prompt, biometric trigger button, lock status indicator, error shake animation.
- [ ] **CreateVaultScreen**: First-time vault setup screen with master password creation, strength meter, and confirmation field.
- [ ] **LockOverlay**: Instant blur overlay with quick unlock password input.

---

## 2. Main Workspace Layout
- [ ] **Sidebar**: Navigation menu, Vault category items (All, Favorites, Passwords, Secure Notes, Credit Cards, Developer Keys), Tag list, Security Health badge, Lock button.
- [ ] **Toolbar / HeaderBar**: Mac window control buttons, Search Bar (⌘K trigger), Quick Add button (+), View Toggle, Sort selector.
- [ ] **VaultList**: Card list rendering title, username, website favicon, favorite star badge, and last modified timestamp.
- [ ] **Inspector (Details Pane)**: Header Card (56px icon, Title, Security Badge), Credentials Card (Username, Password reveal/copy, TOTP ring), Notes Card, Metadata Card (Created, Modified, Security Audit).

---

## 3. Dialogs & Modals
- [ ] **NewEntryModal**: Tabbed form for creating Password, Credit Card, or Secure Note entries.
- [ ] **EditEntryModal**: In-place editing form with password generator integration.
- [ ] **PasswordGeneratorModal**: Standalone password generator with length slider, character toggles, entropy meter, and copy button.
- [ ] **SettingsModal**: App preferences (Theme, Idle Timeout, Clipboard Auto-Clear, Biometrics, Keyring Integration).
- [ ] **AboutModal**: App version, security architecture summary, license metadata.

---

## 4. Feedback & Status Components
- [ ] **ToastNotification**: Auto-dismissing toast alerts (e.g. "Password copied! Auto-clears in 45s").
- [ ] **ConfirmDialog**: Action confirmation modal (e.g. "Delete Vault Entry?").
- [ ] **EmptyState**: Visual empty placeholder when no passwords exist or search returns 0 matches.
- [ ] **ErrorState / ErrorBoundary**: Zone fallback card when a component error occurs.
- [ ] **LoadingState / Skeleton**: Card shimmer placeholder while loading vault data.

---

## 5. Utilities & Command Palette
- [ ] **CommandPalette (⌘K)**: Raycast-style instant launcher for searching passwords, filtering categories, and executing quick actions (Copy Password, Lock Vault, New Entry).
- [ ] **ContextMenu**: Right-click menu for Vault Cards (Copy Username, Copy Password, Toggle Favorite, Edit, Delete).
- [ ] **DropdownMenu**: Select menu for sort criteria and filters.
