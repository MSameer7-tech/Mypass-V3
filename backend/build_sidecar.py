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
    
    # Target directory for Tauri binaries
    binaries_dir = os.path.join(base_dir, "..", "frontend", "src-tauri", "binaries")
    os.makedirs(binaries_dir, exist_ok=True)
    
    # Expected filename by Tauri (e.g., ipc_bridge-aarch64-apple-darwin)
    final_binary_name = f"ipc_bridge-{target}"
    final_binary_path = os.path.join(binaries_dir, final_binary_name)

    print(f"Building {entry_point} with PyInstaller...")

    # Run PyInstaller
    # --onefile to make a single binary
    # --name ipc_bridge to set the output name
    # --distpath to set output folder
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
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
        
    # Copy to tauri binaries dir with correct name
    built_binary = os.path.join(base_dir, "dist", "ipc_bridge")
    if os.path.exists(built_binary):
        shutil.copy2(built_binary, final_binary_path)
        print(f"Successfully copied sidecar to: {final_binary_path}")
    else:
        print(f"Error: Could not find built binary at {built_binary}")
        sys.exit(1)

if __name__ == "__main__":
    main()
