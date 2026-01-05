//! Recovery and firmware management module

use crate::adb::AdbManager;
use std::sync::Arc;

/// Device manufacturer
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Manufacturer {
    Samsung,
    Xiaomi,
    OnePlus,
    Google,
    Huawei,
    Motorola,
    Realme,
    Oppo,
    Vivo,
    Other,
}

impl Manufacturer {
    pub fn from_string(s: &str) -> Self {
        let lower = s.to_lowercase();
        if lower.contains("samsung") {
            Manufacturer::Samsung
        } else if lower.contains("xiaomi") || lower.contains("redmi") || lower.contains("poco") {
            Manufacturer::Xiaomi
        } else if lower.contains("oneplus") {
            Manufacturer::OnePlus
        } else if lower.contains("google") {
            Manufacturer::Google
        } else if lower.contains("huawei") || lower.contains("honor") {
            Manufacturer::Huawei
        } else if lower.contains("motorola") || lower.contains("lenovo") {
            Manufacturer::Motorola
        } else if lower.contains("realme") {
            Manufacturer::Realme
        } else if lower.contains("oppo") {
            Manufacturer::Oppo
        } else if lower.contains("vivo") {
            Manufacturer::Vivo
        } else {
            Manufacturer::Other
        }
    }

    pub fn name(&self) -> &'static str {
        match self {
            Manufacturer::Samsung => "Samsung",
            Manufacturer::Xiaomi => "Xiaomi",
            Manufacturer::OnePlus => "OnePlus",
            Manufacturer::Google => "Google",
            Manufacturer::Huawei => "Huawei",
            Manufacturer::Motorola => "Motorola",
            Manufacturer::Realme => "Realme",
            Manufacturer::Oppo => "OPPO",
            Manufacturer::Vivo => "Vivo",
            Manufacturer::Other => "Other",
        }
    }
}

/// Firmware source information
#[derive(Debug, Clone)]
pub struct FirmwareSource {
    pub name: String,
    pub url: String,
    pub description: String,
}

/// Recovery manager for device recovery operations
pub struct RecoveryManager {
    adb: Arc<AdbManager>,
}

impl RecoveryManager {
    pub fn new(adb: Arc<AdbManager>) -> Self {
        Self { adb }
    }

    /// Get device manufacturer
    pub fn get_manufacturer(&self) -> anyhow::Result<Manufacturer> {
        let mfr = self.adb.get_prop("ro.product.manufacturer")?;
        Ok(Manufacturer::from_string(&mfr))
    }

    /// Reboot to recovery mode
    pub fn reboot_recovery(&self) -> anyhow::Result<()> {
        self.adb.reboot_recovery()
    }

    /// Reboot to bootloader/fastboot
    pub fn reboot_bootloader(&self) -> anyhow::Result<()> {
        self.adb.reboot_bootloader()
    }

    /// Reboot to download mode (Samsung)
    pub fn reboot_download(&self) -> anyhow::Result<()> {
        self.adb.reboot_download()
    }

    /// Normal reboot
    pub fn reboot(&self) -> anyhow::Result<()> {
        self.adb.reboot()
    }

    /// Factory reset (DANGEROUS - wipes all data!)
    pub fn factory_reset(&self) -> anyhow::Result<()> {
        self.adb.factory_reset()
    }

    /// Sideload a zip file in recovery mode
    pub fn sideload(&self, zip_path: &str) -> anyhow::Result<bool> {
        self.adb.sideload(zip_path)
    }

    /// Get firmware download sources for manufacturer
    pub fn get_firmware_sources(manufacturer: Manufacturer) -> Vec<FirmwareSource> {
        match manufacturer {
            Manufacturer::Samsung => vec![
                FirmwareSource {
                    name: "SamFw".to_string(),
                    url: "https://samfw.com".to_string(),
                    description: "Free Samsung firmware downloads".to_string(),
                },
                FirmwareSource {
                    name: "SamMobile".to_string(),
                    url: "https://www.sammobile.com/firmwares".to_string(),
                    description: "Official Samsung firmware archive".to_string(),
                },
                FirmwareSource {
                    name: "Frija".to_string(),
                    url: "https://github.com/SlackingVeteran/frija/releases".to_string(),
                    description: "Tool to download firmware directly from Samsung servers".to_string(),
                },
            ],
            Manufacturer::Xiaomi => vec![
                FirmwareSource {
                    name: "XiaomiFirmwareUpdater".to_string(),
                    url: "https://xiaomifirmwareupdater.com".to_string(),
                    description: "Xiaomi/Redmi/POCO firmware archive".to_string(),
                },
                FirmwareSource {
                    name: "MIUI Download".to_string(),
                    url: "https://c.mi.com/global/miuidownload".to_string(),
                    description: "Official MIUI download page".to_string(),
                },
            ],
            Manufacturer::OnePlus => vec![
                FirmwareSource {
                    name: "OnePlus Support".to_string(),
                    url: "https://service.oneplus.com/global/search/search-detail?id=2096329".to_string(),
                    description: "Official OnePlus firmware".to_string(),
                },
                FirmwareSource {
                    name: "XDA OnePlus".to_string(),
                    url: "https://www.xda-developers.com/tag/oneplus".to_string(),
                    description: "Community firmware and guides".to_string(),
                },
            ],
            Manufacturer::Google => vec![
                FirmwareSource {
                    name: "Google Developers".to_string(),
                    url: "https://developers.google.com/android/images".to_string(),
                    description: "Official Pixel factory images".to_string(),
                },
                FirmwareSource {
                    name: "OTA Images".to_string(),
                    url: "https://developers.google.com/android/ota".to_string(),
                    description: "Official Pixel OTA updates".to_string(),
                },
            ],
            Manufacturer::Huawei => vec![
                FirmwareSource {
                    name: "HuaweiROM".to_string(),
                    url: "https://huaweirom.com".to_string(),
                    description: "Huawei firmware archive".to_string(),
                },
                FirmwareSource {
                    name: "Firmware Finder".to_string(),
                    url: "https://pro-teammt.ru/firmware-database".to_string(),
                    description: "Huawei firmware database".to_string(),
                },
            ],
            Manufacturer::Motorola => vec![
                FirmwareSource {
                    name: "Motorola Support".to_string(),
                    url: "https://motorola-global-portal.custhelp.com/app/software-upgrade".to_string(),
                    description: "Official Motorola software".to_string(),
                },
                FirmwareSource {
                    name: "Lolinet".to_string(),
                    url: "https://mirrors.lolinet.com/firmware/motorola".to_string(),
                    description: "Motorola firmware mirror".to_string(),
                },
            ],
            Manufacturer::Realme => vec![
                FirmwareSource {
                    name: "Realme Software Update".to_string(),
                    url: "https://www.realme.com/global/support/software-update".to_string(),
                    description: "Official Realme updates".to_string(),
                },
            ],
            Manufacturer::Oppo => vec![
                FirmwareSource {
                    name: "OPPO Support".to_string(),
                    url: "https://support.oppo.com/en/software-update".to_string(),
                    description: "Official OPPO software".to_string(),
                },
            ],
            Manufacturer::Vivo => vec![
                FirmwareSource {
                    name: "Vivo Support".to_string(),
                    url: "https://www.vivo.com/en/support/download".to_string(),
                    description: "Official Vivo downloads".to_string(),
                },
            ],
            Manufacturer::Other => vec![
                FirmwareSource {
                    name: "XDA Developers".to_string(),
                    url: "https://www.xda-developers.com".to_string(),
                    description: "Community forums - search for your device".to_string(),
                },
            ],
        }
    }

    /// Get flashing tool info for manufacturer
    pub fn get_flashing_tool(manufacturer: Manufacturer) -> Option<FlashingTool> {
        match manufacturer {
            Manufacturer::Samsung => Some(FlashingTool {
                name: "Odin / Heimdall".to_string(),
                description: "Odin (Windows) or Heimdall (Cross-platform) for Samsung".to_string(),
                download_url: "https://github.com/Benjamin-Dobell/Heimdall/releases".to_string(),
                instructions: vec![
                    "1. Download Odin (Windows) or Heimdall".to_string(),
                    "2. Put device in Download Mode (Vol Down + Power while off)".to_string(),
                    "3. Connect USB and select firmware files".to_string(),
                    "4. Click Start/Flash to begin".to_string(),
                ],
            }),
            Manufacturer::Xiaomi => Some(FlashingTool {
                name: "MiFlash Tool".to_string(),
                description: "Official Xiaomi flashing tool".to_string(),
                download_url: "https://xiaomiflashtool.com".to_string(),
                instructions: vec![
                    "1. Download and install MiFlash".to_string(),
                    "2. Put device in Fastboot mode (Vol Down + Power)".to_string(),
                    "3. Select firmware folder in MiFlash".to_string(),
                    "4. Click Refresh, select device, click Flash".to_string(),
                ],
            }),
            Manufacturer::Google => Some(FlashingTool {
                name: "Android Flash Tool".to_string(),
                description: "Google's web-based flashing tool".to_string(),
                download_url: "https://flash.android.com".to_string(),
                instructions: vec![
                    "1. Visit flash.android.com in Chrome".to_string(),
                    "2. Enable OEM unlocking in Developer Options".to_string(),
                    "3. Connect device in Fastboot mode".to_string(),
                    "4. Follow on-screen instructions".to_string(),
                ],
            }),
            _ => None,
        }
    }
}

/// Information about a flashing tool
#[derive(Debug, Clone)]
pub struct FlashingTool {
    pub name: String,
    pub description: String,
    pub download_url: String,
    pub instructions: Vec<String>,
}

/// Recovery action result
#[derive(Debug)]
pub enum RecoveryResult {
    Success(String),
    Error(String),
    Confirmation(String),
}
