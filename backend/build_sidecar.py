import os
import subprocess
import sys
import shutil

def get_target_triple():
    # Use rustc to get the host target triple
    try:
        result = subprocess.run(["rustc", "-vV"], capture_output=True, text=True, check=True)
        for line in result.stdout.split('\n'):
            if line.startswith("host:"):
                return line.split(":")[1].strip()
    except Exception as e:
        print(f"Failed to get target triple from rustc: {e}")
        # Fallback to standard apple silicon if rustc fails
        return "aarch64-apple-darwin"

def main():
    target = get_target_triple()
    print(f"Determined host target triple: {target}")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    entry_point = os.path.join(base_dir, "ipc_bridge.py")
    
    # Target directory for Tauri resources
    resources_dir = os.path.join(base_dir, "..", "frontend", "src-tauri", "resources")
    os.makedirs(resources_dir, exist_ok=True)
    final_resource_path = os.path.join(resources_dir, "ipc_bridge_app")

    print(f"Building {entry_point} with PyInstaller...")

    # Run PyInstaller
    # --onedir to make a folder instead of unpacking on launch
    pyinstaller_cmd = [
        "pyinstaller",
        "--onedir",
        "--name", "ipc_bridge",
        "--distpath", os.path.join(base_dir, "dist"),
        "--clean",
        "--noconfirm",
        entry_point
    ]
    
    # We must ensure we're using the pyinstaller from our venv
    venv_pyinstaller = os.path.join(base_dir, "venv", "bin", "pyinstaller")
    if os.path.exists(venv_pyinstaller):
        pyinstaller_cmd[0] = venv_pyinstaller
        
    try:
        subprocess.run(pyinstaller_cmd, check=True, cwd=base_dir)
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller failed with code {e.returncode}")
        sys.exit(1)
        
    # Copy to tauri resources dir
    built_dir = os.path.join(base_dir, "dist", "ipc_bridge")
    if os.path.exists(built_dir):
        if os.path.exists(final_resource_path):
            shutil.rmtree(final_resource_path)
        shutil.copytree(built_dir, final_resource_path)
        print(f"Successfully copied sidecar folder to: {final_resource_path}")
    else:
        print(f"Error: Could not find built directory at {built_dir}")
        sys.exit(1)

if __name__ == "__main__":
    main()
