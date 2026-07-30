import os
import sys

def load_gui_preference() -> str:
    # 1. CLI argument
    if "--gui" in sys.argv:
        try:
            idx = sys.argv.index("--gui")
            return sys.argv[idx + 1].lower()
        except (ValueError, IndexError):
            pass

    # 2. Environment variable
    env_gui = os.environ.get("MYPASS_UI")
    if env_gui:
        return env_gui.lower()

    # 3. Configuration file config.json
    try:
        from utils.helpers import build_data_path
        from utils.constants import DATA_DIR_NAME
        import json
        config_path = build_data_path(DATA_DIR_NAME, "config.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "ui" in data:
                    return str(data["ui"]).lower()
    except Exception:
        pass

    # 4. Legacy default
    return "legacy"

def main() -> None:
    gui_type = load_gui_preference()
            
    if gui_type == "qt":
        from app_qt import main as qt_main
        qt_main()
    else:
        from app_legacy import main as legacy_main
        legacy_main()

if __name__ == "__main__":
    main()
