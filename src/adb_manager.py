"""
ADB Manager Module
Handles all ADB operations including device detection, app management, and system commands
"""

import subprocess
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Tuple, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from .installer import ADBInstaller, ensure_adb_installed


class DeviceState(Enum):
    """Device connection states."""
    DEVICE = "device"           # Normal connected state
    OFFLINE = "offline"         # Device offline
    UNAUTHORIZED = "unauthorized"  # USB debugging not authorized
    RECOVERY = "recovery"       # Device in recovery mode
    SIDELOAD = "sideload"       # Device in sideload mode
    BOOTLOADER = "bootloader"   # Device in bootloader/fastboot
    UNKNOWN = "unknown"


class InstallLocation(Enum):
    """App installation locations."""
    SYSTEM = "system"           # /system/app or /system/priv-app
    DATA = "data"               # /data/app (user installed)
    VENDOR = "vendor"           # /vendor/app
    PRODUCT = "product"         # /product/app
    UNKNOWN = "unknown"


@dataclass
class DeviceInfo:
    """Information about a connected Android device."""
    serial: str
    state: DeviceState
    model: str = ""
    manufacturer: str = ""
    android_version: str = ""
    sdk_version: int = 0
    product: str = ""
    device: str = ""
    transport_id: str = ""

    @property
    def display_name(self) -> str:
        """Get a human-readable device name."""
        if self.model:
            return f"{self.manufacturer} {self.model}".strip()
        return self.serial


@dataclass
class PackageInfo:
    """Information about an installed package."""
    package_name: str
    version_name: str = ""
    version_code: int = 0
    install_location: InstallLocation = InstallLocation.UNKNOWN
    is_system: bool = False
    is_enabled: bool = True
    is_suspended: bool = False
    first_install_time: str = ""
    last_update_time: str = ""
    installer: str = ""
    uid: int = 0
    data_dir: str = ""
    apk_path: str = ""
    permissions: List[str] = field(default_factory=list)
    requested_permissions: List[str] = field(default_factory=list)


class ADBManager:
    """Manages ADB operations for Android devices."""

    def __init__(self, adb_path: Optional[str] = None):
        """
        Initialize the ADB Manager.

        Args:
            adb_path: Path to ADB executable. If None, will auto-detect or install.
        """
        self.installer = ADBInstaller()
        self._adb_path = adb_path
        self._current_device: Optional[str] = None

    @property
    def adb_path(self) -> str:
        """Get the ADB executable path, installing if necessary."""
        if self._adb_path:
            return self._adb_path
        return ensure_adb_installed()

    def _run_adb(
        self,
        args: List[str],
        device: Optional[str] = None,
        timeout: int = 30,
        check: bool = True
    ) -> subprocess.CompletedProcess:
        """
        Run an ADB command.

        Args:
            args: Command arguments (after 'adb')
            device: Device serial number (uses current device if None)
            timeout: Command timeout in seconds
            check: Whether to raise exception on non-zero exit

        Returns:
            CompletedProcess result
        """
        cmd = [self.adb_path]

        # Add device specifier
        target_device = device or self._current_device
        if target_device:
            cmd.extend(["-s", target_device])

        cmd.extend(args)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if check and result.returncode != 0:
                # Don't raise for common expected errors
                if "unknown package" not in result.stderr.lower():
                    pass  # We'll handle errors in calling code
            return result
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"ADB command timed out: {' '.join(args)}")

    def start_server(self) -> bool:
        """Start the ADB server."""
        result = self._run_adb(["start-server"], device=None, check=False)
        return result.returncode == 0

    def kill_server(self) -> bool:
        """Kill the ADB server."""
        result = self._run_adb(["kill-server"], device=None, check=False)
        return result.returncode == 0

    def restart_server(self) -> bool:
        """Restart the ADB server."""
        self.kill_server()
        time.sleep(1)
        return self.start_server()

    def get_devices(self) -> List[DeviceInfo]:
        """
        Get list of connected devices.

        Returns:
            List of DeviceInfo objects
        """
        result = self._run_adb(["devices", "-l"], device=None, check=False)
        if result.returncode != 0:
            return []

        devices = []
        for line in result.stdout.strip().split('\n')[1:]:  # Skip header
            if not line.strip():
                continue

            parts = line.split()
            if len(parts) < 2:
                continue

            serial = parts[0]
            state_str = parts[1]

            try:
                state = DeviceState(state_str)
            except ValueError:
                state = DeviceState.UNKNOWN

            device = DeviceInfo(serial=serial, state=state)

            # Parse additional properties
            for part in parts[2:]:
                if ':' in part:
                    key, value = part.split(':', 1)
                    if key == 'model':
                        device.model = value
                    elif key == 'device':
                        device.device = value
                    elif key == 'product':
                        device.product = value
                    elif key == 'transport_id':
                        device.transport_id = value

            # Get additional info for connected devices
            if state == DeviceState.DEVICE:
                device = self._enrich_device_info(device)

            devices.append(device)

        return devices

    def _enrich_device_info(self, device: DeviceInfo) -> DeviceInfo:
        """Add additional properties to device info."""
        props = {
            "ro.product.manufacturer": "manufacturer",
            "ro.product.model": "model",
            "ro.build.version.release": "android_version",
            "ro.build.version.sdk": "sdk_version",
        }

        for prop, attr in props.items():
            result = self._run_adb(
                ["shell", "getprop", prop],
                device=device.serial,
                timeout=5,
                check=False
            )
            if result.returncode == 0:
                value = result.stdout.strip()
                if attr == "sdk_version":
                    try:
                        value = int(value)
                    except ValueError:
                        value = 0
                setattr(device, attr, value)

        return device

    def set_current_device(self, serial: str) -> None:
        """Set the current working device."""
        self._current_device = serial

    def get_current_device(self) -> Optional[str]:
        """Get the current working device serial."""
        return self._current_device

    def wait_for_device(self, timeout: int = 60) -> bool:
        """Wait for a device to connect."""
        try:
            result = self._run_adb(["wait-for-device"], timeout=timeout, check=False)
            return result.returncode == 0
        except TimeoutError:
            return False

    # ========================================================================
    # Package Management
    # ========================================================================

    def get_packages(
        self,
        include_system: bool = True,
        include_disabled: bool = True,
        user_id: Optional[int] = None
    ) -> List[str]:
        """
        Get list of installed packages.

        Args:
            include_system: Include system packages
            include_disabled: Include disabled packages
            user_id: Specific user ID to query

        Returns:
            List of package names
        """
        args = ["shell", "pm", "list", "packages"]

        if not include_system:
            args.append("-3")  # Third-party only
        if include_disabled:
            args.append("-d")  # Include disabled

        if user_id is not None:
            args.extend(["--user", str(user_id)])

        result = self._run_adb(args, check=False)
        if result.returncode != 0:
            return []

        packages = []
        for line in result.stdout.strip().split('\n'):
            if line.startswith('package:'):
                packages.append(line[8:])

        return packages

    def get_third_party_packages(self) -> List[str]:
        """Get only user-installed (third-party) packages."""
        args = ["shell", "pm", "list", "packages", "-3"]
        result = self._run_adb(args, check=False)

        if result.returncode != 0:
            return []

        packages = []
        for line in result.stdout.strip().split('\n'):
            if line.startswith('package:'):
                packages.append(line[8:])

        return packages

    def get_system_packages(self) -> List[str]:
        """Get only system packages."""
        args = ["shell", "pm", "list", "packages", "-s"]
        result = self._run_adb(args, check=False)

        if result.returncode != 0:
            return []

        packages = []
        for line in result.stdout.strip().split('\n'):
            if line.startswith('package:'):
                packages.append(line[8:])

        return packages

    def get_package_info(self, package_name: str) -> Optional[PackageInfo]:
        """
        Get detailed information about a package.

        Args:
            package_name: The package name

        Returns:
            PackageInfo object or None if not found
        """
        result = self._run_adb(
            ["shell", "dumpsys", "package", package_name],
            timeout=10,
            check=False
        )

        if result.returncode != 0 or "Unable to find package" in result.stdout:
            return None

        info = PackageInfo(package_name=package_name)
        output = result.stdout

        # Parse version info
        version_match = re.search(r'versionName=([^\s]+)', output)
        if version_match:
            info.version_name = version_match.group(1)

        version_code_match = re.search(r'versionCode=(\d+)', output)
        if version_code_match:
            info.version_code = int(version_code_match.group(1))

        # Parse install location
        if '/system/priv-app/' in output or '/system/app/' in output:
            info.install_location = InstallLocation.SYSTEM
            info.is_system = True
        elif '/vendor/app/' in output:
            info.install_location = InstallLocation.VENDOR
            info.is_system = True
        elif '/product/app/' in output:
            info.install_location = InstallLocation.PRODUCT
            info.is_system = True
        elif '/data/app/' in output:
            info.install_location = InstallLocation.DATA
            info.is_system = False

        # Parse enabled state
        if 'enabled=' in output:
            enabled_match = re.search(r'enabled=(\d+)', output)
            if enabled_match:
                info.is_enabled = enabled_match.group(1) != '0'

        # Parse installer
        installer_match = re.search(r'installerPackageName=([^\s]+)', output)
        if installer_match:
            info.installer = installer_match.group(1)

        # Parse APK path
        path_match = re.search(r'codePath=([^\s]+)', output)
        if path_match:
            info.apk_path = path_match.group(1)

        # Parse permissions
        perms = re.findall(r'android\.permission\.[A-Z_]+', output)
        info.permissions = list(set(perms))

        return info

    def get_package_path(self, package_name: str) -> Optional[str]:
        """Get the APK path for a package."""
        result = self._run_adb(
            ["shell", "pm", "path", package_name],
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            path = result.stdout.strip()
            if path.startswith('package:'):
                return path[8:]
            return path
        return None

    def uninstall_package(
        self,
        package_name: str,
        keep_data: bool = False,
        user_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Uninstall a package.

        Args:
            package_name: Package to uninstall
            keep_data: Keep app data after uninstall
            user_id: Uninstall for specific user only

        Returns:
            Tuple of (success, message)
        """
        args = ["shell", "pm", "uninstall"]

        if keep_data:
            args.append("-k")

        if user_id is not None:
            args.extend(["--user", str(user_id)])

        args.append(package_name)

        result = self._run_adb(args, timeout=30, check=False)

        if result.returncode == 0 and "Success" in result.stdout:
            return True, "Package uninstalled successfully"

        # Handle common errors
        stderr = result.stderr.lower() + result.stdout.lower()

        if "unknown package" in stderr:
            return False, "Package not found"
        elif "permission denied" in stderr:
            return False, "Permission denied - try with user 0"
        elif "device policy" in stderr:
            return False, "Package protected by device policy"

        return False, result.stderr or result.stdout or "Unknown error"

    def disable_package(
        self,
        package_name: str,
        user_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Disable a package (doesn't remove, just disables).

        Args:
            package_name: Package to disable
            user_id: Disable for specific user

        Returns:
            Tuple of (success, message)
        """
        args = ["shell", "pm", "disable-user"]

        if user_id is not None:
            args.extend(["--user", str(user_id)])

        args.append(package_name)

        result = self._run_adb(args, check=False)

        if result.returncode == 0:
            return True, "Package disabled"

        return False, result.stderr or result.stdout or "Failed to disable"

    def enable_package(self, package_name: str) -> Tuple[bool, str]:
        """Enable a disabled package."""
        result = self._run_adb(
            ["shell", "pm", "enable", package_name],
            check=False
        )
        if result.returncode == 0:
            return True, "Package enabled"
        return False, result.stderr or "Failed to enable"

    def clear_package_data(self, package_name: str) -> Tuple[bool, str]:
        """Clear all data for a package."""
        result = self._run_adb(
            ["shell", "pm", "clear", package_name],
            check=False
        )
        if result.returncode == 0 and "Success" in result.stdout:
            return True, "Data cleared"
        return False, result.stderr or result.stdout or "Failed to clear data"

    def force_stop_package(self, package_name: str) -> bool:
        """Force stop a running package."""
        result = self._run_adb(
            ["shell", "am", "force-stop", package_name],
            check=False
        )
        return result.returncode == 0

    # ========================================================================
    # Permission Management
    # ========================================================================

    def revoke_permission(
        self,
        package_name: str,
        permission: str
    ) -> Tuple[bool, str]:
        """
        Revoke a permission from a package.

        Args:
            package_name: The package
            permission: Permission to revoke (e.g., android.permission.CAMERA)

        Returns:
            Tuple of (success, message)
        """
        result = self._run_adb(
            ["shell", "pm", "revoke", package_name, permission],
            check=False
        )
        if result.returncode == 0:
            return True, f"Revoked {permission}"
        return False, result.stderr or "Failed to revoke permission"

    def revoke_overlay_permission(self, package_name: str) -> Tuple[bool, str]:
        """Revoke draw over other apps permission (blocks popup ads)."""
        result = self._run_adb(
            ["shell", "appops", "set", package_name, "SYSTEM_ALERT_WINDOW", "deny"],
            check=False
        )
        if result.returncode == 0:
            return True, "Overlay permission revoked"
        return False, result.stderr or "Failed to revoke overlay permission"

    def get_running_packages(self) -> List[str]:
        """Get list of currently running packages."""
        result = self._run_adb(
            ["shell", "ps", "-A", "-o", "NAME"],
            check=False
        )
        if result.returncode != 0:
            return []

        packages = []
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if line.startswith('com.') or line.startswith('org.'):
                packages.append(line)

        return list(set(packages))

    def get_foreground_package(self) -> Optional[str]:
        """Get the currently focused/foreground package."""
        result = self._run_adb(
            ["shell", "dumpsys", "window", "windows"],
            check=False
        )
        if result.returncode != 0:
            return None

        # Look for mCurrentFocus or mFocusedApp
        match = re.search(r'mCurrentFocus.*?([a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z][a-zA-Z0-9_]*)+)', result.stdout)
        if match:
            return match.group(1)

        match = re.search(r'mFocusedApp.*?([a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z][a-zA-Z0-9_]*)+)', result.stdout)
        if match:
            return match.group(1)

        return None

    # ========================================================================
    # Batch Operations
    # ========================================================================

    def batch_uninstall(
        self,
        packages: List[str],
        progress_callback: Optional[Callable[[str, bool, str], None]] = None,
        user_id: Optional[int] = 0
    ) -> Dict[str, Tuple[bool, str]]:
        """
        Uninstall multiple packages.

        Args:
            packages: List of package names
            progress_callback: Callback(package, success, message) for progress
            user_id: User ID for uninstall (0 for main user)

        Returns:
            Dict mapping package name to (success, message)
        """
        results = {}

        for package in packages:
            success, message = self.uninstall_package(package, user_id=user_id)
            results[package] = (success, message)

            if progress_callback:
                progress_callback(package, success, message)

            # Small delay to avoid overwhelming the device
            time.sleep(0.1)

        return results

    def batch_disable(
        self,
        packages: List[str],
        progress_callback: Optional[Callable[[str, bool, str], None]] = None
    ) -> Dict[str, Tuple[bool, str]]:
        """
        Disable multiple packages.

        Args:
            packages: List of package names
            progress_callback: Callback(package, success, message)

        Returns:
            Dict mapping package name to (success, message)
        """
        results = {}

        for package in packages:
            success, message = self.disable_package(package)
            results[package] = (success, message)

            if progress_callback:
                progress_callback(package, success, message)

            time.sleep(0.1)

        return results

    # ========================================================================
    # Device Operations
    # ========================================================================

    def reboot(self, mode: Optional[str] = None) -> bool:
        """
        Reboot the device.

        Args:
            mode: Optional mode (recovery, bootloader, etc.)
        """
        args = ["reboot"]
        if mode:
            args.append(mode)

        result = self._run_adb(args, check=False)
        return result.returncode == 0

    def get_battery_info(self) -> Dict[str, str]:
        """Get battery information."""
        result = self._run_adb(["shell", "dumpsys", "battery"], check=False)
        if result.returncode != 0:
            return {}

        info = {}
        for line in result.stdout.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip()] = value.strip()

        return info

    def get_storage_info(self) -> Dict[str, str]:
        """Get storage information."""
        result = self._run_adb(["shell", "df", "-h", "/data"], check=False)
        if result.returncode != 0:
            return {}

        lines = result.stdout.strip().split('\n')
        if len(lines) >= 2:
            parts = lines[1].split()
            if len(parts) >= 4:
                return {
                    "total": parts[1],
                    "used": parts[2],
                    "available": parts[3],
                    "use_percent": parts[4] if len(parts) > 4 else "N/A"
                }
        return {}

    def take_screenshot(self, output_path: Path) -> bool:
        """Take a screenshot and save it locally."""
        remote_path = "/sdcard/screenshot.png"

        # Take screenshot on device
        result = self._run_adb(
            ["shell", "screencap", "-p", remote_path],
            check=False
        )
        if result.returncode != 0:
            return False

        # Pull to local
        result = self._run_adb(
            ["pull", remote_path, str(output_path)],
            check=False
        )

        # Clean up
        self._run_adb(["shell", "rm", remote_path], check=False)

        return result.returncode == 0

    def shell(self, command: str, timeout: int = 30) -> Tuple[int, str, str]:
        """
        Run a shell command on the device.

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        result = self._run_adb(
            ["shell", command],
            timeout=timeout,
            check=False
        )
        return result.returncode, result.stdout, result.stderr


# Convenience function
def get_adb_manager(adb_path: Optional[str] = None) -> ADBManager:
    """Get an ADB manager instance."""
    return ADBManager(adb_path)
