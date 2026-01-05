//! ADB (Android Debug Bridge) manager for device communication

use anyhow::{anyhow, Result};
use std::path::PathBuf;
use std::process::{Command, Output};
use std::sync::{Arc, Mutex};

/// Information about a connected Android device
#[derive(Debug, Clone)]
pub struct DeviceInfo {
    pub serial: String,
    pub model: String,
    pub manufacturer: String,
    pub android_version: String,
    pub sdk_version: String,
    pub status: DeviceStatus,
}

#[derive(Debug, Clone, PartialEq)]
pub enum DeviceStatus {
    Online,
    Offline,
    Unauthorized,
    Recovery,
    Sideload,
    Unknown,
}

impl DeviceStatus {
    pub fn as_str(&self) -> &'static str {
        match self {
            DeviceStatus::Online => "Online",
            DeviceStatus::Offline => "Offline",
            DeviceStatus::Unauthorized => "Unauthorized",
            DeviceStatus::Recovery => "Recovery",
            DeviceStatus::Sideload => "Sideload",
            DeviceStatus::Unknown => "Unknown",
        }
    }
}

/// Information about an installed package
#[derive(Debug, Clone)]
pub struct PackageInfo {
    pub package_name: String,
    pub version_name: Option<String>,
    pub version_code: Option<String>,
    pub is_system: bool,
    pub is_disabled: bool,
    pub installer: Option<String>,
}

/// ADB Manager for device operations
pub struct AdbManager {
    adb_path: PathBuf,
    current_device: Arc<Mutex<Option<String>>>,
}

impl AdbManager {
    /// Create a new ADB manager with the given ADB path
    pub fn new(adb_path: PathBuf) -> Self {
        Self {
            adb_path,
            current_device: Arc::new(Mutex::new(None)),
        }
    }

    /// Set the current device to operate on
    pub fn set_device(&self, serial: &str) {
        let mut device = self.current_device.lock().unwrap();
        *device = Some(serial.to_string());
    }

    /// Get the current device serial
    pub fn get_device(&self) -> Option<String> {
        self.current_device.lock().unwrap().clone()
    }

    /// Run an ADB command
    fn run_adb(&self, args: &[&str]) -> Result<Output> {
        let mut cmd = Command::new(&self.adb_path);

        // Add device serial if set
        if let Some(serial) = self.get_device() {
            cmd.arg("-s").arg(&serial);
        }

        cmd.args(args);

        let output = cmd.output()?;
        Ok(output)
    }

    /// Run an ADB shell command
    fn run_shell(&self, shell_cmd: &str) -> Result<String> {
        let output = self.run_adb(&["shell", shell_cmd])?;
        let stdout = String::from_utf8_lossy(&output.stdout).to_string();
        Ok(stdout.trim().to_string())
    }

    /// Get list of connected devices
    pub fn get_devices(&self) -> Result<Vec<DeviceInfo>> {
        let output = Command::new(&self.adb_path)
            .args(["devices", "-l"])
            .output()?;

        let stdout = String::from_utf8_lossy(&output.stdout);
        let mut devices = Vec::new();

        for line in stdout.lines().skip(1) {
            if line.trim().is_empty() {
                continue;
            }

            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() >= 2 {
                let serial = parts[0].to_string();
                let status = match parts[1] {
                    "device" => DeviceStatus::Online,
                    "offline" => DeviceStatus::Offline,
                    "unauthorized" => DeviceStatus::Unauthorized,
                    "recovery" => DeviceStatus::Recovery,
                    "sideload" => DeviceStatus::Sideload,
                    _ => DeviceStatus::Unknown,
                };

                // Get device details
                let model = self.get_prop_for_device(&serial, "ro.product.model")
                    .unwrap_or_else(|_| "Unknown".to_string());
                let manufacturer = self.get_prop_for_device(&serial, "ro.product.manufacturer")
                    .unwrap_or_else(|_| "Unknown".to_string());
                let android_version = self.get_prop_for_device(&serial, "ro.build.version.release")
                    .unwrap_or_else(|_| "Unknown".to_string());
                let sdk_version = self.get_prop_for_device(&serial, "ro.build.version.sdk")
                    .unwrap_or_else(|_| "Unknown".to_string());

                devices.push(DeviceInfo {
                    serial,
                    model,
                    manufacturer,
                    android_version,
                    sdk_version,
                    status,
                });
            }
        }

        Ok(devices)
    }

    /// Get a property for a specific device
    fn get_prop_for_device(&self, serial: &str, prop: &str) -> Result<String> {
        let output = Command::new(&self.adb_path)
            .args(["-s", serial, "shell", "getprop", prop])
            .output()?;

        let value = String::from_utf8_lossy(&output.stdout).trim().to_string();
        if value.is_empty() {
            Err(anyhow!("Property not found"))
        } else {
            Ok(value)
        }
    }

    /// Get a system property
    pub fn get_prop(&self, prop: &str) -> Result<String> {
        self.run_shell(&format!("getprop {}", prop))
    }

    /// Get list of installed packages
    pub fn get_packages(&self, include_system: bool) -> Result<Vec<PackageInfo>> {
        let cmd = if include_system {
            "pm list packages -f"
        } else {
            "pm list packages -f -3"
        };

        let output = self.run_shell(cmd)?;
        let mut packages = Vec::new();

        for line in output.lines() {
            if let Some(pkg) = line.strip_prefix("package:") {
                // Format: /path/to/apk=package.name
                if let Some(eq_pos) = pkg.rfind('=') {
                    let package_name = pkg[eq_pos + 1..].to_string();
                    let is_system = pkg.starts_with("/system/") || pkg.starts_with("/product/");

                    packages.push(PackageInfo {
                        package_name,
                        version_name: None,
                        version_code: None,
                        is_system,
                        is_disabled: false,
                        installer: None,
                    });
                }
            }
        }

        Ok(packages)
    }

    /// Get list of third-party packages only
    pub fn get_third_party_packages(&self) -> Result<Vec<PackageInfo>> {
        self.get_packages(false)
    }

    /// Get list of disabled packages
    pub fn get_disabled_packages(&self) -> Result<Vec<String>> {
        let output = self.run_shell("pm list packages -d")?;
        let mut packages = Vec::new();

        for line in output.lines() {
            if let Some(pkg) = line.strip_prefix("package:") {
                packages.push(pkg.to_string());
            }
        }

        Ok(packages)
    }

    /// Uninstall a package (for current user, keeps data)
    pub fn uninstall_package(&self, package: &str) -> Result<bool> {
        let output = self.run_adb(&["shell", "pm", "uninstall", "-k", "--user", "0", package])?;
        let stdout = String::from_utf8_lossy(&output.stdout);
        Ok(stdout.contains("Success"))
    }

    /// Completely uninstall a package (removes data too)
    pub fn uninstall_package_complete(&self, package: &str) -> Result<bool> {
        let output = self.run_adb(&["shell", "pm", "uninstall", "--user", "0", package])?;
        let stdout = String::from_utf8_lossy(&output.stdout);
        Ok(stdout.contains("Success"))
    }

    /// Disable a package
    pub fn disable_package(&self, package: &str) -> Result<bool> {
        let output = self.run_adb(&["shell", "pm", "disable-user", "--user", "0", package])?;
        let stdout = String::from_utf8_lossy(&output.stdout);
        Ok(stdout.contains("disabled") || stdout.contains("new state"))
    }

    /// Enable a package
    pub fn enable_package(&self, package: &str) -> Result<bool> {
        let output = self.run_adb(&["shell", "pm", "enable", package])?;
        let stdout = String::from_utf8_lossy(&output.stdout);
        Ok(stdout.contains("enabled") || stdout.contains("new state"))
    }

    /// Clear package data
    pub fn clear_package(&self, package: &str) -> Result<bool> {
        let output = self.run_adb(&["shell", "pm", "clear", package])?;
        let stdout = String::from_utf8_lossy(&output.stdout);
        Ok(stdout.contains("Success"))
    }

    /// Force stop an app
    pub fn force_stop(&self, package: &str) -> Result<()> {
        self.run_adb(&["shell", "am", "force-stop", package])?;
        Ok(())
    }

    /// Revoke a permission from a package
    pub fn revoke_permission(&self, package: &str, permission: &str) -> Result<bool> {
        let output = self.run_adb(&["shell", "pm", "revoke", package, permission])?;
        Ok(output.status.success())
    }

    /// Reboot device to recovery mode
    pub fn reboot_recovery(&self) -> Result<()> {
        self.run_adb(&["reboot", "recovery"])?;
        Ok(())
    }

    /// Reboot device to bootloader/fastboot mode
    pub fn reboot_bootloader(&self) -> Result<()> {
        self.run_adb(&["reboot", "bootloader"])?;
        Ok(())
    }

    /// Reboot device to download mode (Samsung)
    pub fn reboot_download(&self) -> Result<()> {
        self.run_adb(&["reboot", "download"])?;
        Ok(())
    }

    /// Normal reboot
    pub fn reboot(&self) -> Result<()> {
        self.run_adb(&["reboot"])?;
        Ok(())
    }

    /// Factory reset via ADB (wipes data)
    pub fn factory_reset(&self) -> Result<()> {
        // This is a dangerous operation - wipes user data!
        self.run_shell("am broadcast -a android.intent.action.FACTORY_RESET")?;
        Ok(())
    }

    /// Install an APK
    pub fn install_apk(&self, apk_path: &str) -> Result<bool> {
        let output = self.run_adb(&["install", "-r", apk_path])?;
        let stdout = String::from_utf8_lossy(&output.stdout);
        Ok(stdout.contains("Success"))
    }

    /// Push a file to the device
    pub fn push_file(&self, local_path: &str, remote_path: &str) -> Result<bool> {
        let output = self.run_adb(&["push", local_path, remote_path])?;
        Ok(output.status.success())
    }

    /// Pull a file from the device
    pub fn pull_file(&self, remote_path: &str, local_path: &str) -> Result<bool> {
        let output = self.run_adb(&["pull", remote_path, local_path])?;
        Ok(output.status.success())
    }

    /// Get battery level
    pub fn get_battery_level(&self) -> Result<i32> {
        let output = self.run_shell("dumpsys battery | grep level")?;
        if let Some(level_str) = output.split(':').nth(1) {
            level_str.trim().parse().map_err(|_| anyhow!("Failed to parse battery level"))
        } else {
            Err(anyhow!("Could not get battery level"))
        }
    }

    /// Get free storage space in bytes
    pub fn get_free_storage(&self) -> Result<u64> {
        let output = self.run_shell("df /data | tail -1")?;
        let parts: Vec<&str> = output.split_whitespace().collect();
        if parts.len() >= 4 {
            // Parse free space (usually in KB or with K/M/G suffix)
            let free_str = parts[3];
            parse_size(free_str)
        } else {
            Err(anyhow!("Could not parse storage info"))
        }
    }

    /// Take a screenshot and save it locally
    pub fn take_screenshot(&self, local_path: &str) -> Result<()> {
        self.run_shell("screencap -p /sdcard/screenshot.png")?;
        self.pull_file("/sdcard/screenshot.png", local_path)?;
        self.run_shell("rm /sdcard/screenshot.png")?;
        Ok(())
    }

    /// Sideload a zip file (for recovery mode)
    pub fn sideload(&self, zip_path: &str) -> Result<bool> {
        let output = self.run_adb(&["sideload", zip_path])?;
        Ok(output.status.success())
    }

    /// Start ADB server
    pub fn start_server(&self) -> Result<()> {
        Command::new(&self.adb_path).arg("start-server").output()?;
        Ok(())
    }

    /// Kill ADB server
    pub fn kill_server(&self) -> Result<()> {
        Command::new(&self.adb_path).arg("kill-server").output()?;
        Ok(())
    }

    /// Restart ADB server
    pub fn restart_server(&self) -> Result<()> {
        self.kill_server()?;
        std::thread::sleep(std::time::Duration::from_millis(500));
        self.start_server()?;
        Ok(())
    }
}

/// Parse a size string like "1.5G" or "500M" to bytes
fn parse_size(s: &str) -> Result<u64> {
    let s = s.trim();
    if s.is_empty() {
        return Err(anyhow!("Empty size string"));
    }

    let (num_str, multiplier) = if s.ends_with('K') || s.ends_with('k') {
        (&s[..s.len()-1], 1024u64)
    } else if s.ends_with('M') || s.ends_with('m') {
        (&s[..s.len()-1], 1024u64 * 1024)
    } else if s.ends_with('G') || s.ends_with('g') {
        (&s[..s.len()-1], 1024u64 * 1024 * 1024)
    } else {
        (s, 1u64)
    };

    let num: f64 = num_str.parse()?;
    Ok((num * multiplier as f64) as u64)
}
