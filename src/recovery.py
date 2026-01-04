"""
Recovery and Firmware Module
Handles factory reset, recovery mode, download mode, and firmware operations
"""

import os
import re
import json
import platform
import subprocess
import zipfile
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple, Callable
from enum import Enum

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class DeviceMode(Enum):
    """Device boot modes."""
    NORMAL = "normal"
    RECOVERY = "recovery"
    DOWNLOAD = "download"       # Samsung Odin mode
    FASTBOOT = "fastboot"       # Generic Android fastboot
    SIDELOAD = "sideload"
    EDL = "edl"                 # Qualcomm Emergency Download


@dataclass
class FirmwareInfo:
    """Information about available firmware."""
    model: str
    region: str
    version: str
    android_version: str
    build_date: str
    filename: str
    size: int
    download_url: str = ""
    changelog: str = ""


class RecoveryManager:
    """Manages recovery operations and device modes."""

    def __init__(self, adb_manager):
        """
        Initialize with ADB manager.

        Args:
            adb_manager: Instance of ADBManager
        """
        self.adb = adb_manager

    # ========================================================================
    # Factory Reset Operations
    # ========================================================================

    def factory_reset_adb(self) -> Tuple[bool, str]:
        """
        Perform factory reset via ADB (requires device to be on).
        This will wipe all user data!

        Returns:
            Tuple of (success, message)
        """
        # First, try the recovery command approach
        ret, stdout, stderr = self.adb.shell("am broadcast -a android.intent.action.MASTER_CLEAR")

        if ret == 0:
            return True, "Factory reset initiated. Device will reboot and wipe data."

        # Alternative method using recovery command
        ret, stdout, stderr = self.adb.shell("recovery --wipe_data")

        if ret == 0:
            return True, "Factory reset command sent."

        return False, f"Factory reset failed: {stderr or stdout}"

    def wipe_data_recovery(self) -> Tuple[bool, str]:
        """
        Wipe data by rebooting to recovery and issuing wipe command.
        Works on most devices with stock recovery.

        Returns:
            Tuple of (success, message)
        """
        # Reboot to recovery
        success = self.reboot_recovery()
        if not success:
            return False, "Failed to reboot to recovery"

        return True, "Device rebooting to recovery. Manually select 'Wipe data/factory reset' from recovery menu."

    def wipe_cache(self) -> Tuple[bool, str]:
        """
        Wipe the cache partition.

        Returns:
            Tuple of (success, message)
        """
        ret, stdout, stderr = self.adb.shell("rm -rf /data/dalvik-cache/*")
        ret2, stdout2, stderr2 = self.adb.shell("rm -rf /cache/*")

        if ret == 0 or ret2 == 0:
            return True, "Cache wiped. Reboot recommended."

        return False, "Cache wipe failed (may need root)"

    # ========================================================================
    # Boot Mode Operations
    # ========================================================================

    def reboot_recovery(self) -> bool:
        """Reboot device into recovery mode."""
        return self.adb.reboot("recovery")

    def reboot_bootloader(self) -> bool:
        """Reboot device into bootloader/fastboot mode."""
        return self.adb.reboot("bootloader")

    def reboot_download(self) -> bool:
        """
        Reboot Samsung device into Download/Odin mode.
        Uses the 'download' reboot target.
        """
        # Try Samsung-specific download mode
        result = self.adb.reboot("download")
        if result:
            return True

        # Alternative: use key combo simulation (requires root)
        ret, stdout, stderr = self.adb.shell(
            "reboot download"
        )
        return ret == 0

    def reboot_edl(self) -> Tuple[bool, str]:
        """
        Reboot into EDL (Emergency Download) mode.
        Only works on Qualcomm devices, may require root.

        Returns:
            Tuple of (success, message)
        """
        # Try direct EDL reboot
        ret, stdout, stderr = self.adb.shell("reboot edl")

        if ret == 0:
            return True, "Rebooting to EDL mode..."

        # Alternative method
        ret, stdout, stderr = self.adb.shell(
            "echo 1 > /sys/bus/platform/drivers/diag/smd_diag/modem_efs_dump"
        )

        if ret == 0:
            return True, "EDL mode triggered"

        return False, "EDL mode not supported or requires root"

    def reboot_normal(self) -> bool:
        """Reboot device normally."""
        return self.adb.reboot()

    def shutdown(self) -> bool:
        """Shutdown the device."""
        ret, stdout, stderr = self.adb.shell("reboot -p")
        return ret == 0

    def get_current_mode(self) -> DeviceMode:
        """
        Detect current device mode.

        Returns:
            Current DeviceMode
        """
        # Check ADB devices output
        devices = self.adb.get_devices()

        for device in devices:
            if device.serial == self.adb.get_current_device():
                state = device.state.value.lower()

                if state == "recovery":
                    return DeviceMode.RECOVERY
                elif state == "sideload":
                    return DeviceMode.SIDELOAD
                elif state == "device":
                    return DeviceMode.NORMAL

        # Check fastboot
        try:
            result = subprocess.run(
                ["fastboot", "devices"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if self.adb.get_current_device() in result.stdout:
                return DeviceMode.FASTBOOT
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        return DeviceMode.NORMAL

    # ========================================================================
    # Recovery Commands (when in recovery mode)
    # ========================================================================

    def recovery_wipe_data(self) -> Tuple[bool, str]:
        """
        Execute wipe data command in recovery mode.
        Device must be in recovery mode with ADB enabled.
        """
        ret, stdout, stderr = self.adb.shell("recovery --wipe_data")

        if ret == 0:
            return True, "Wipe data initiated in recovery"

        # Try twrp command if available
        ret, stdout, stderr = self.adb.shell("twrp wipe data")

        if ret == 0:
            return True, "TWRP wipe data initiated"

        return False, "Wipe command failed. Use recovery menu manually."

    def recovery_wipe_cache(self) -> Tuple[bool, str]:
        """Execute wipe cache command in recovery mode."""
        ret, stdout, stderr = self.adb.shell("recovery --wipe_cache")

        if ret == 0:
            return True, "Wipe cache initiated"

        ret, stdout, stderr = self.adb.shell("twrp wipe cache")

        if ret == 0:
            return True, "TWRP wipe cache initiated"

        return False, "Wipe cache failed. Use recovery menu manually."

    def sideload_zip(self, zip_path: Path) -> Tuple[bool, str]:
        """
        Sideload a ZIP file (ROM, update, etc.) via ADB sideload.
        Device must be in sideload mode.

        Args:
            zip_path: Path to the ZIP file

        Returns:
            Tuple of (success, message)
        """
        if not zip_path.exists():
            return False, f"File not found: {zip_path}"

        # Device should be in sideload mode
        try:
            result = subprocess.run(
                [self.adb.adb_path, "sideload", str(zip_path)],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for large files
            )

            if result.returncode == 0:
                return True, "Sideload completed successfully"

            return False, result.stderr or "Sideload failed"

        except subprocess.TimeoutExpired:
            return False, "Sideload timed out"
        except Exception as e:
            return False, f"Sideload error: {str(e)}"


class SamsungFirmwareDownloader:
    """
    Downloads Samsung firmware using FUS (Firmware Update Server) protocol.
    Based on Frija/SamFirm approach.
    """

    FUS_URL = "https://fota-cloud-dn.ospserver.net/firmware/"
    NONCE_URL = "https://neofussvr.sslcs.cdngc.net/NF_DownloadGenerateNonce.do"

    # Known Samsung region codes
    REGIONS = {
        "XEU": "Europe (Unlocked)",
        "BTU": "UK",
        "DBT": "Germany",
        "XEF": "France",
        "ITV": "Italy",
        "ESP": "Spain",
        "PHE": "Netherlands",
        "XEZ": "Czech Republic",
        "ROM": "Romania",
        "SEE": "Serbia",
        "SER": "Russia",
        "AUT": "Austria",
        "EUX": "Hungary/Poland/Nordic",
        "OXX": "Latin America",
        "TPA": "Panama",
        "TMB": "T-Mobile USA",
        "ATT": "AT&T",
        "VZW": "Verizon",
        "SPR": "Sprint",
        "USC": "US Cellular",
        "XAA": "USA (Unlocked)",
        "XAR": "USA (Unlocked AT&T)",
        "KOO": "South Korea",
        "SKC": "South Korea (SK Telecom)",
        "KTC": "South Korea (KT)",
        "LUC": "South Korea (LG U+)",
        "INS": "India",
        "XSA": "Australia",
        "XSP": "Singapore",
        "THL": "Thailand",
        "XXV": "Vietnam",
        "XME": "Malaysia",
        "XID": "Indonesia",
        "PHH": "Philippines",
        "BRI": "Taiwan",
        "TGY": "Hong Kong",
        "ZTA": "Taiwan",
        "CHC": "China",
    }

    def __init__(self, download_dir: Optional[Path] = None):
        """
        Initialize the firmware downloader.

        Args:
            download_dir: Directory to save firmware files
        """
        self.download_dir = download_dir or Path.cwd() / "firmware"
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def get_latest_firmware(
        self,
        model: str,
        region: str = "XEU"
    ) -> Optional[FirmwareInfo]:
        """
        Get information about the latest firmware for a device.

        Args:
            model: Device model (e.g., SM-A055F)
            region: Region code (e.g., XEU for Europe)

        Returns:
            FirmwareInfo or None if not found
        """
        if not REQUESTS_AVAILABLE:
            return None

        try:
            # Check firmware version using Samsung's version check
            url = f"https://fota-cloud-dn.ospserver.net/firmware/{region}/{model}/version.xml"

            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                return None

            # Parse version info from XML
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)

            version_elem = root.find(".//latest")
            if version_elem is None:
                return None

            version = version_elem.text

            return FirmwareInfo(
                model=model,
                region=region,
                version=version,
                android_version="",  # Would need additional parsing
                build_date="",
                filename=f"{model}_{region}_{version}.zip",
                size=0
            )

        except Exception:
            return None

    def check_firmware_exists(self, model: str, region: str) -> bool:
        """Check if firmware is available for download."""
        info = self.get_latest_firmware(model, region)
        return info is not None

    def get_common_regions(self) -> Dict[str, str]:
        """Get dictionary of common region codes."""
        return self.REGIONS

    def search_firmware_online(
        self,
        model: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> List[FirmwareInfo]:
        """
        Search for available firmware across multiple regions.

        Args:
            model: Device model
            progress_callback: Optional callback for progress updates

        Returns:
            List of available FirmwareInfo
        """
        available = []
        checked = 0
        total = len(self.REGIONS)

        for region_code, region_name in self.REGIONS.items():
            checked += 1
            if progress_callback:
                progress_callback(f"Checking {region_name} ({checked}/{total})...")

            info = self.get_latest_firmware(model, region_code)
            if info:
                available.append(info)

        return available


class GenericFirmwareHelper:
    """
    Helper for generic Android firmware operations.
    Provides links and instructions for various manufacturers.
    """

    FIRMWARE_SOURCES = {
        "samsung": {
            "name": "Samsung",
            "tools": ["Odin (Windows)", "Heimdall (Linux/Mac)"],
            "websites": [
                ("SamMobile", "https://www.sammobile.com/firmwares/"),
                ("SamFw", "https://samfw.com/"),
                ("Frija Tool", "https://github.com/SlackingVeteran/frija"),
            ],
            "instructions": """
1. Download firmware from SamMobile or use Frija
2. Extract the firmware ZIP
3. Boot device into Download mode (Vol Down + Power while connecting USB)
4. Use Odin (Windows) or Heimdall (Linux/Mac) to flash
5. Select BL, AP, CP, CSC files in Odin
6. Click Start to flash
            """
        },
        "xiaomi": {
            "name": "Xiaomi/Redmi/POCO",
            "tools": ["MiFlash Tool", "Fastboot"],
            "websites": [
                ("MIUI Downloads", "https://c.mi.com/global/miuidownload/"),
                ("XiaomiFirmware", "https://xiaomifirmwareupdater.com/"),
            ],
            "instructions": """
1. Download ROM from official MIUI site
2. Boot into Fastboot mode (Vol Down + Power)
3. Use MiFlash tool or fastboot commands
4. For Recovery ROM: boot to Recovery, select Install
5. For Fastboot ROM: use MiFlash or 'fastboot flash' commands
            """
        },
        "oneplus": {
            "name": "OnePlus",
            "tools": ["MSM Tool", "Fastboot"],
            "websites": [
                ("OnePlus Support", "https://www.oneplus.com/support/softwareupgrade"),
            ],
            "instructions": """
1. Download OxygenOS from OnePlus
2. For local upgrade: place in root of storage, update via Settings
3. For fastboot: extract and use flash scripts
4. For MSM tool: boot to EDL mode and use MSM Download Tool
            """
        },
        "google": {
            "name": "Google Pixel",
            "tools": ["Android Flash Tool", "Fastboot"],
            "websites": [
                ("Factory Images", "https://developers.google.com/android/images"),
                ("OTA Images", "https://developers.google.com/android/ota"),
                ("Android Flash Tool", "https://flash.android.com/"),
            ],
            "instructions": """
1. Use Android Flash Tool (web-based) - easiest method
2. Or download factory image from Google
3. Unlock bootloader if needed
4. Extract and run flash-all script
5. Or use fastboot to flash individual partitions
            """
        },
        "huawei": {
            "name": "Huawei/Honor",
            "tools": ["HiSuite", "Huawei Multi-Tool"],
            "websites": [
                ("HiSuite", "https://consumer.huawei.com/en/support/hisuite/"),
                ("Firmware Finder", "https://professorjtj.github.io/"),
            ],
            "instructions": """
1. Use HiSuite for official updates
2. For manual: download update.app
3. Place in dload folder on SD card
4. Boot to eRecovery (Vol Up + Power)
5. Select install from SD card
            """
        },
        "motorola": {
            "name": "Motorola",
            "tools": ["Rescue and Smart Assistant", "Fastboot"],
            "websites": [
                ("Motorola Support", "https://motorola-global-portal.custhelp.com/"),
                ("Lenovo Support", "https://support.lenovo.com/"),
            ],
            "instructions": """
1. Use Rescue and Smart Assistant for recovery
2. For fastboot: unlock bootloader first
3. Download stock firmware
4. Use fastboot flash commands
            """
        },
        "realme": {
            "name": "Realme",
            "tools": ["Realme Flash Tool", "MSM Tool"],
            "websites": [
                ("Realme Support", "https://www.realme.com/support/"),
            ],
            "instructions": """
1. Download firmware from Realme support
2. For OTA: place in root storage
3. Go to Settings > Software Update > Local Install
4. For deep flash: use MSM tool in EDL mode
            """
        },
        "oppo": {
            "name": "OPPO",
            "tools": ["MSM Download Tool", "ColorOS Recovery"],
            "websites": [
                ("OPPO Support", "https://support.oppo.com/"),
            ],
            "instructions": """
1. Download ColorOS firmware
2. For recovery: place ofp file in storage
3. Boot to Recovery, select Install from storage
4. For MSM: boot to EDL mode
            """
        },
        "vivo": {
            "name": "Vivo",
            "tools": ["AFT Tool", "QFIL"],
            "websites": [
                ("Vivo Support", "https://www.vivo.com/support"),
            ],
            "instructions": """
1. Download firmware from Vivo support
2. Use AFT (Android Flash Tool) for flashing
3. For Qualcomm devices: use QFIL in EDL mode
            """
        },
    }

    @classmethod
    def get_manufacturer_info(cls, manufacturer: str) -> Optional[Dict]:
        """Get firmware info for a manufacturer."""
        mfr_lower = manufacturer.lower()

        for key, info in cls.FIRMWARE_SOURCES.items():
            if key in mfr_lower or mfr_lower in info["name"].lower():
                return info

        return None

    @classmethod
    def get_supported_manufacturers(cls) -> List[str]:
        """Get list of supported manufacturers."""
        return [info["name"] for info in cls.FIRMWARE_SOURCES.values()]

    @classmethod
    def detect_manufacturer(cls, model: str, manufacturer: str) -> str:
        """Detect manufacturer from model or manufacturer string."""
        combined = f"{model} {manufacturer}".lower()

        if "sm-" in combined or "samsung" in combined:
            return "samsung"
        elif "redmi" in combined or "poco" in combined or "xiaomi" in combined or "mi " in combined:
            return "xiaomi"
        elif "oneplus" in combined or "le2" in combined or "kb2" in combined:
            return "oneplus"
        elif "pixel" in combined or "google" in combined:
            return "google"
        elif "huawei" in combined or "honor" in combined:
            return "huawei"
        elif "moto" in combined or "motorola" in combined:
            return "motorola"
        elif "rmx" in combined or "realme" in combined:
            return "realme"
        elif "cph" in combined or "oppo" in combined:
            return "oppo"
        elif "vivo" in combined or "v20" in combined:
            return "vivo"

        return "unknown"


class HeimdallHelper:
    """
    Helper for Heimdall - cross-platform Samsung flashing tool.
    """

    HEIMDALL_RELEASES = "https://api.github.com/repos/Benjamin-Dobell/Heimdall/releases/latest"

    @staticmethod
    def is_installed() -> bool:
        """Check if Heimdall is installed."""
        try:
            result = subprocess.run(
                ["heimdall", "version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    @staticmethod
    def get_version() -> Optional[str]:
        """Get installed Heimdall version."""
        try:
            result = subprocess.run(
                ["heimdall", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        return None

    @staticmethod
    def detect_device() -> bool:
        """Detect if a Samsung device is connected in Download mode."""
        try:
            result = subprocess.run(
                ["heimdall", "detect"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    @staticmethod
    def flash_partition(
        partition: str,
        file_path: Path,
        no_reboot: bool = False
    ) -> Tuple[bool, str]:
        """
        Flash a partition using Heimdall.

        Args:
            partition: Partition name (e.g., BOOT, RECOVERY, SYSTEM)
            file_path: Path to the image file
            no_reboot: Don't reboot after flashing

        Returns:
            Tuple of (success, message)
        """
        if not file_path.exists():
            return False, f"File not found: {file_path}"

        cmd = ["heimdall", "flash", f"--{partition}", str(file_path)]

        if no_reboot:
            cmd.append("--no-reboot")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                return True, f"Flashed {partition} successfully"

            return False, result.stderr or "Flash failed"

        except subprocess.TimeoutExpired:
            return False, "Flash operation timed out"
        except Exception as e:
            return False, f"Error: {str(e)}"

    @staticmethod
    def print_pit() -> Tuple[bool, str]:
        """Print the device's PIT (Partition Information Table)."""
        try:
            result = subprocess.run(
                ["heimdall", "print-pit"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return True, result.stdout

            return False, result.stderr or "Failed to read PIT"

        except Exception as e:
            return False, f"Error: {str(e)}"
