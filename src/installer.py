"""
ADB Tools Auto-Installer Module
Downloads and sets up Android Platform Tools on first run
"""

import os
import sys
import platform
import zipfile
import tarfile
import shutil
import stat
import subprocess
from pathlib import Path
from typing import Optional, Callable

try:
    import requests
    from tqdm import tqdm
except ImportError:
    requests = None
    tqdm = None


class ADBInstaller:
    """Handles automatic download and installation of ADB tools."""

    # Official Google Platform Tools download URLs
    DOWNLOAD_URLS = {
        "Windows": "https://dl.google.com/android/repository/platform-tools-latest-windows.zip",
        "Linux": "https://dl.google.com/android/repository/platform-tools-latest-linux.zip",
        "Darwin": "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip",
    }

    def __init__(self, install_dir: Optional[Path] = None):
        """
        Initialize the installer.

        Args:
            install_dir: Directory to install ADB tools. Defaults to ./android-tools/
        """
        self.system = platform.system()
        self.install_dir = install_dir or Path(__file__).parent.parent / "android-tools"
        self.platform_tools_dir = self.install_dir / "platform-tools"
        self.adb_path = self._get_adb_executable_path()

    def _get_adb_executable_path(self) -> Path:
        """Get the path to the ADB executable based on OS."""
        if self.system == "Windows":
            return self.platform_tools_dir / "adb.exe"
        return self.platform_tools_dir / "adb"

    def is_installed(self) -> bool:
        """Check if ADB is already installed in our directory."""
        return self.adb_path.exists()

    def is_system_adb_available(self) -> bool:
        """Check if ADB is available in system PATH."""
        try:
            result = subprocess.run(
                ["adb", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def get_adb_command(self) -> str:
        """Get the ADB command to use (local or system)."""
        if self.is_installed():
            return str(self.adb_path)
        elif self.is_system_adb_available():
            return "adb"
        return str(self.adb_path)  # Will need to install first

    def download_with_progress(
        self,
        url: str,
        dest: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """
        Download a file with progress tracking.

        Args:
            url: URL to download from
            dest: Destination file path
            progress_callback: Optional callback(downloaded, total) for progress updates

        Returns:
            True if download successful, False otherwise
        """
        if requests is None:
            print("Error: 'requests' library not installed. Run: pip install requests")
            return False

        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            dest.parent.mkdir(parents=True, exist_ok=True)

            with open(dest, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)

            return True

        except requests.RequestException as e:
            print(f"Download error: {e}")
            return False

    def extract_archive(self, archive_path: Path, extract_to: Path) -> bool:
        """
        Extract a zip or tar archive.

        Args:
            archive_path: Path to the archive file
            extract_to: Directory to extract to

        Returns:
            True if extraction successful, False otherwise
        """
        try:
            extract_to.mkdir(parents=True, exist_ok=True)

            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    zf.extractall(extract_to)
            elif archive_path.suffix in ['.tar', '.gz', '.tgz']:
                with tarfile.open(archive_path, 'r:*') as tf:
                    tf.extractall(extract_to)
            else:
                print(f"Unknown archive format: {archive_path.suffix}")
                return False

            return True

        except (zipfile.BadZipFile, tarfile.TarError) as e:
            print(f"Extraction error: {e}")
            return False

    def set_executable_permissions(self) -> None:
        """Set executable permissions on ADB binaries (Linux/macOS)."""
        if self.system == "Windows":
            return

        executables = ["adb", "fastboot", "mke2fs", "e2fsdroid"]
        for exe in executables:
            exe_path = self.platform_tools_dir / exe
            if exe_path.exists():
                current_mode = exe_path.stat().st_mode
                exe_path.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def install(
        self,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> bool:
        """
        Download and install ADB tools.

        Args:
            progress_callback: Optional callback(status, downloaded, total)

        Returns:
            True if installation successful, False otherwise
        """
        if self.is_installed():
            return True

        if self.system not in self.DOWNLOAD_URLS:
            print(f"Unsupported operating system: {self.system}")
            return False

        url = self.DOWNLOAD_URLS[self.system]
        archive_name = f"platform-tools-{self.system.lower()}.zip"
        archive_path = self.install_dir / archive_name

        # Create install directory
        self.install_dir.mkdir(parents=True, exist_ok=True)

        # Download
        def download_progress(downloaded: int, total: int):
            if progress_callback:
                progress_callback("Downloading Android Platform Tools...", downloaded, total)

        if not self.download_with_progress(url, archive_path, download_progress):
            return False

        # Extract
        if progress_callback:
            progress_callback("Extracting...", 0, 0)

        if not self.extract_archive(archive_path, self.install_dir):
            return False

        # Set permissions
        self.set_executable_permissions()

        # Clean up archive
        try:
            archive_path.unlink()
        except OSError:
            pass

        # Verify installation
        if not self.is_installed():
            print("Installation failed: ADB executable not found after extraction")
            return False

        if progress_callback:
            progress_callback("Installation complete!", 100, 100)

        return True

    def uninstall(self) -> bool:
        """Remove installed ADB tools."""
        try:
            if self.install_dir.exists():
                shutil.rmtree(self.install_dir)
            return True
        except OSError as e:
            print(f"Uninstall error: {e}")
            return False

    def get_version(self) -> Optional[str]:
        """Get the installed ADB version."""
        adb_cmd = self.get_adb_command()
        try:
            result = subprocess.run(
                [adb_cmd, "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Parse version from output
                for line in result.stdout.split('\n'):
                    if 'Android Debug Bridge version' in line:
                        return line.split('version')[-1].strip()
            return None
        except (subprocess.SubprocessError, FileNotFoundError):
            return None


def ensure_adb_installed(install_dir: Optional[Path] = None) -> str:
    """
    Convenience function to ensure ADB is installed and return the command path.

    Args:
        install_dir: Optional installation directory

    Returns:
        Path to ADB executable

    Raises:
        RuntimeError: If ADB cannot be installed
    """
    installer = ADBInstaller(install_dir)

    if installer.is_installed() or installer.is_system_adb_available():
        return installer.get_adb_command()

    print("ADB not found. Downloading Android Platform Tools...")

    def progress(status: str, downloaded: int, total: int):
        if total > 0:
            pct = (downloaded / total) * 100
            print(f"\r{status} {pct:.1f}%", end="", flush=True)
        else:
            print(f"\r{status}", end="", flush=True)

    if installer.install(progress):
        print("\nADB installed successfully!")
        return installer.get_adb_command()
    else:
        raise RuntimeError("Failed to install ADB tools")


if __name__ == "__main__":
    # Test installation
    try:
        adb_path = ensure_adb_installed()
        print(f"ADB available at: {adb_path}")

        installer = ADBInstaller()
        version = installer.get_version()
        if version:
            print(f"ADB version: {version}")
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
