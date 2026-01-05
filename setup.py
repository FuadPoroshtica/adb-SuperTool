#!/usr/bin/env python3
"""
Setup script for Android SuperTool
Creates virtual environment, installs dependencies, and sets up the tool
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def main():
    """Main setup function."""
    print("=" * 60)
    print("  Android SuperTool - Setup")
    print("  Mobile Shop Edition")
    print("=" * 60)
    print()

    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return 1

    print(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}")

    # Get script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)

    # Check if in virtual environment
    in_venv = sys.prefix != sys.base_prefix

    if not in_venv:
        venv_dir = script_dir / "venv"

        if not venv_dir.exists():
            print("\nCreating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
            print("[OK] Virtual environment created")

        # Get the correct pip path
        if platform.system() == "Windows":
            pip_path = venv_dir / "Scripts" / "pip.exe"
            python_path = venv_dir / "Scripts" / "python.exe"
        else:
            pip_path = venv_dir / "bin" / "pip"
            python_path = venv_dir / "bin" / "python"

        print("\nInstalling dependencies...")
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("[OK] Dependencies installed")

        # Download ADB
        print("\nDownloading Android Platform Tools...")
        result = subprocess.run(
            [str(python_path), "supertool.py", "--install-adb"],
            capture_output=False
        )

        if result.returncode == 0:
            print("[OK] ADB tools ready")
        else:
            print("[WARNING] ADB installation may have issues")

        print("\n" + "=" * 60)
        print("  Setup Complete!")
        print("=" * 60)
        print()
        print("To run Android SuperTool:")
        print()

        if platform.system() == "Windows":
            print(f"  .\\venv\\Scripts\\python.exe supertool.py")
            print()
            print("Or activate the virtual environment first:")
            print(f"  .\\venv\\Scripts\\activate")
            print("  python supertool.py")
        else:
            print(f"  ./venv/bin/python supertool.py")
            print()
            print("Or activate the virtual environment first:")
            print(f"  source venv/bin/activate")
            print("  python supertool.py")

        print()
        print("Quick commands:")
        print("  python supertool.py --scan   # Quick scan")
        print("  python supertool.py --clean  # Scan and clean")
        print()

    else:
        # Already in virtual environment
        print("\nInstalling dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("[OK] Dependencies installed")

        print("\nDownloading Android Platform Tools...")
        import importlib.util
        spec = importlib.util.spec_from_file_location("supertool", script_dir / "supertool.py")
        module = importlib.util.module_from_spec(spec)

        from src.installer import ADBInstaller
        installer = ADBInstaller()

        if not installer.is_installed() and not installer.is_system_adb_available():
            def progress(status, downloaded, total):
                if total > 0:
                    pct = (downloaded / total) * 100
                    print(f"\r{status} {pct:.1f}%", end="", flush=True)

            if installer.install(progress):
                print("\n[OK] ADB tools ready")
            else:
                print("\n[WARNING] ADB installation may have issues")
        else:
            print("[OK] ADB already available")

        print("\n" + "=" * 60)
        print("  Setup Complete!")
        print("=" * 60)
        print()
        print("Run: python supertool.py")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
