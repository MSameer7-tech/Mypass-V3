# MyPass: Premium Password Vault

MyPass is an ultra-premium, state-based, AES-encrypted password manager designed to mirror the aesthetics of top-tier desktop utility apps (like Linear, Raycast, and Arc). Built entirely with Python and CustomTkinter, it features a seamless, minimalist matte-dark card UI, real-time dynamic password strength validation, and instantaneous search interactions.

## 🚀 Features
- **Military-Grade Encryption:** Local AES encryption powered by `cryptography`. Your passwords are mathematically secured before they ever touch the SQLite database.
- **Dynamic State UX:** Fluid UI with real-time border highlights, empty-state detection, and subtle fading toast notifications (e.g., `✓ Password Copied`).
- **Live Password Strength Meter:** Evaluates password entropy dynamically based on length, symbols, caps, and digits.
- **Power User Shortcuts:** 
  - `Cmd+S` to Save
  - `Cmd+F` to Search
  - `Cmd+G` to Auto-Generate strong credentials
- **Standalone DMG:** Pre-packaged into a lightweight native `.dmg` file for seamless macOS installation—complete with a custom disk icon.

## 📥 Download & Install
1. Navigate to the `dist/` folder in this repository.
2. Download `MyPass.dmg`.
3. Double-click the `.dmg` and drag the `MyPass.app` into your Applications folder.

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

## 🔒 Security
All vault data is stored safely in `~/.password_manager_data/` on your local machine. No data is transmitted to the cloud. Do not lose your `vault.key`, or your data will be permanently irretrievable.

---
*Built with Python, CustomTkinter, and 🩵.*
