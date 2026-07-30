import urllib.request
import os

icons = [
    "plus", "copy", "x", "edit-2", "eye", "eye-off", "github", 
    "history", "lock", "search", "settings", "shield", "star", 
    "trash", "trash-2", "user", "alert-triangle", "check", "chevron-down"
]

mapping = {
    "plus": "add",
    "x": "delete",
    "edit-2": "edit",
    "trash-2": "trash",
    "alert-triangle": "warning"
}

out_dir = "/Users/sameer/Documents/Password-Manager-App/assets/icons"
os.makedirs(out_dir, exist_ok=True)
os.makedirs("/Users/sameer/Documents/Password-Manager-App/ui/design_system", exist_ok=True)
os.makedirs("/Users/sameer/Documents/Password-Manager-App/ui/components", exist_ok=True)

for icon in icons:
    url = f"https://unpkg.com/lucide-static@latest/icons/{icon}.svg"
    out_name = mapping.get(icon, icon) + ".svg"
    out_path = os.path.join(out_dir, out_name)
    try:
        urllib.request.urlretrieve(url, out_path)
        print(f"Downloaded {out_name}")
    except Exception as e:
        print(f"Failed to download {icon}: {e}")
