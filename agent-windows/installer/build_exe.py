import subprocess
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
DIST_DIR = ROOT / "dist"
BUILD_DIR = ROOT / "build"


def build():
    print("[*] Building standalone FIM Windows Agent executable (fim-agent.exe)...")
    
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--name",
        "fim-agent",
        "--paths",
        str(SRC_DIR),
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(BUILD_DIR),
        "--clean",
        str(SRC_DIR / "main.py"),
    ]

    res = subprocess.run(cmd, cwd=str(ROOT))
    if res.returncode == 0:
        exe_path = DIST_DIR / "fim-agent.exe"
        print("==========================================================")
        print(f"[✓] Successfully compiled: {exe_path}")
        print(f" Size: {exe_path.stat().st_size / (1024*1024):.2f} MB")
        print("==========================================================")
        return True
    else:
        print("[✗] Compilation failed.")
        return False


if __name__ == "__main__":
    build()
