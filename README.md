<h1 align="center">MyPass</h1>

<p align="center">
  Premium AES-Encrypted Password Vault for macOS & Windows
</p>

<p align="center">
  Built with Python, CustomTkinter & SQLite
</p>

<p align="center">
<img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python">
<img src="https://img.shields.io/badge/CustomTkinter-Modern_UI-black?style=for-the-badge">
<img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-black?style=for-the-badge">
<img src="https://img.shields.io/badge/Encryption-AES256-success?style=for-the-badge">
</p>

<p align="center">
  <img src="assets/preview.png" width="900">
</p>

## Features

- 🔐 **AES-encrypted local password vault**
- ⚡ **Real-time password strength analysis**
- 🎨 **Premium SaaS-inspired matte UI**
- 📋 **One-click password copy**
- 👁️ **Show / hide password toggle**
- ⌨️ **Keyboard shortcuts for power users**
- 💾 **SQLite-backed secure local storage**
- 📦 **Native macOS DMG packaging**

## Screenshots

| Vault UI | Password Strength |
|---|---|
| ![](assets/ui.png) | ![](assets/strength.png) |


## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| CustomTkinter | Modern desktop UI |
| SQLite | Local database |
| Cryptography | AES encryption |
| PyInstaller | Desktop packaging |
| create-dmg | macOS installer generation |

## Architecture

```plaintext
UI Layer (CustomTkinter)
        ↓
Encryption Layer (cryptography)
        ↓
SQLite Secure Vault
```

## 📥 Download & Install

1. Navigate to the `dist/` folder in this repository.
2. Download `MyPass.dmg`.
3. Double-click the `.dmg` and drag `MyPass.app` into your Applications folder.

*(Note: As this is an indie unsigned utility, you may need to Right-Click -> Open the app the first time to bypass macOS Gatekeeper, or run `xattr -cr /Applications/MyPass.app` in your terminal).*

## 🛠️ Build it Yourself

### Prerequisites
- Python 3.10+
- macOS (for `.app` and `.dmg` generation) or Windows.

### Setup
```bash
# Clone the repo
git clone https://github.com/MSameer7-tech/Password-Manager-App.git
cd Password-Manager-App

# Install requirements
pip install -r requirements.txt

# Run locally
python main.py
```

### Packaging for macOS
We use PyInstaller and `create-dmg`:
```bash
pyinstaller --windowed --name "MyPass" --icon assets/icon.icns --add-data "assets:assets" --hidden-import=PIL --hidden-import=customtkinter --hidden-import=cryptography -y main.py

# Fix gatekeeper flags and permissions
xattr -cr dist/MyPass.app
codesign --force --deep -s - dist/MyPass.app

# Create DMG
cd dist
create-dmg --volname "MyPass" --volicon "../assets/icon.icns" --window-pos 200 120 --window-size 800 400 --icon-size 100 --icon "MyPass.app" 200 190 --hide-extension "MyPass.app" --app-drop-link 600 185 "MyPass.dmg" "MyPass.app/"
```

## 🔒 Security Notes
All vault data is stored safely in `~/.password_manager_data/` on your local machine. No data is transmitted to the cloud. Do not lose your `vault.key`, or your data will be permanently irretrievable.

## Roadmap

- [ ] Biometric unlock
- [ ] Cloud sync
- [ ] Browser extension
- [ ] Password categories
- [ ] Secure notes
- [ ] TOTP / 2FA support

---
*Built with Python, CustomTkinter, and 🩵.*
