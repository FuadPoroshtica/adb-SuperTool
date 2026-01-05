//! Samsung device debloater for entry-level phones

use crate::adb::AdbManager;
use std::sync::Arc;

/// Debloat intensity level
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DebloatLevel {
    Light,      // Only obvious bloatware
    Medium,     // + AR, Games, Themes
    Aggressive, // + Knox, Health, Pay, most Samsung apps
    Custom,     // User-selected packages
}

impl DebloatLevel {
    pub fn description(&self) -> &'static str {
        match self {
            DebloatLevel::Light => "Safe - Remove obvious bloatware only",
            DebloatLevel::Medium => "Moderate - Remove AR, Games, Themes",
            DebloatLevel::Aggressive => "Maximum - Remove most Samsung apps",
            DebloatLevel::Custom => "Custom - Select packages manually",
        }
    }
}

/// Category of bloatware package
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DebloatCategory {
    Bixby,
    ArEmoji,
    Games,
    Themes,
    Knox,
    Health,
    Pay,
    Microsoft,
    Facebook,
    Google,
    SamsungApps,
    Carrier,
    Other,
}

impl DebloatCategory {
    pub fn name(&self) -> &'static str {
        match self {
            DebloatCategory::Bixby => "Bixby",
            DebloatCategory::ArEmoji => "AR Emoji",
            DebloatCategory::Games => "Games",
            DebloatCategory::Themes => "Themes",
            DebloatCategory::Knox => "Knox",
            DebloatCategory::Health => "Health",
            DebloatCategory::Pay => "Samsung Pay",
            DebloatCategory::Microsoft => "Microsoft",
            DebloatCategory::Facebook => "Facebook",
            DebloatCategory::Google => "Google",
            DebloatCategory::SamsungApps => "Samsung Apps",
            DebloatCategory::Carrier => "Carrier",
            DebloatCategory::Other => "Other",
        }
    }
}

/// A package that can be debloated
#[derive(Debug, Clone)]
pub struct DebloatPackage {
    pub package: String,
    pub name: String,
    pub category: DebloatCategory,
    pub description: String,
    pub is_selected: bool,
}

/// Samsung Debloater
pub struct Debloater {
    adb: Arc<AdbManager>,
}

impl Debloater {
    pub fn new(adb: Arc<AdbManager>) -> Self {
        Self { adb }
    }

    /// Check if device is a Samsung entry-level device
    pub fn is_entry_level_samsung(&self) -> bool {
        if let Ok(model) = self.adb.get_prop("ro.product.model") {
            let model = model.to_uppercase();
            // Entry-level A series
            model.contains("SM-A055") || // A05
            model.contains("SM-A065") || // A06
            model.contains("SM-A075") || // A07
            model.contains("SM-A165") || // A16
            model.contains("SM-A175") || // A17
            model.contains("SM-A135") || // A13
            model.contains("SM-A145") || // A14
            model.contains("SM-A155") || // A15
            model.contains("SM-A045") || // A04
            model.contains("SM-A046") || // A04s
            model.contains("SM-A035") || // A03
            model.contains("SM-A037") || // A03s
            model.contains("SM-A032") || // A03 Core
            // Entry-level M series
            model.contains("SM-M135") || // M13
            model.contains("SM-M145") || // M14
            model.contains("SM-M155")    // M15
        } else {
            false
        }
    }

    /// Get all debloatable packages with their categories
    pub fn get_all_packages() -> Vec<DebloatPackage> {
        let mut packages = Vec::new();

        // Bixby
        for (pkg, name, desc) in BIXBY_PACKAGES {
            packages.push(DebloatPackage {
                package: pkg.to_string(),
                name: name.to_string(),
                category: DebloatCategory::Bixby,
                description: desc.to_string(),
                is_selected: false,
            });
        }

        // AR Emoji
        for (pkg, name, desc) in AR_EMOJI_PACKAGES {
            packages.push(DebloatPackage {
                package: pkg.to_string(),
                name: name.to_string(),
                category: DebloatCategory::ArEmoji,
                description: desc.to_string(),
                is_selected: false,
            });
        }

        // Games
        for (pkg, name, desc) in GAMES_PACKAGES {
            packages.push(DebloatPackage {
                package: pkg.to_string(),
                name: name.to_string(),
                category: DebloatCategory::Games,
                description: desc.to_string(),
                is_selected: false,
            });
        }

        // Themes
        for (pkg, name, desc) in THEMES_PACKAGES {
            packages.push(DebloatPackage {
                package: pkg.to_string(),
                name: name.to_string(),
                category: DebloatCategory::Themes,
                description: desc.to_string(),
                is_selected: false,
            });
        }

        // Knox
        for (pkg, name, desc) in KNOX_PACKAGES {
            packages.push(DebloatPackage {
                package: pkg.to_string(),
                name: name.to_string(),
                category: DebloatCategory::Knox,
                description: desc.to_string(),
                is_selected: false,
            });
        }

        // Health
        for (pkg, name, desc) in HEALTH_PACKAGES {
            packages.push(DebloatPackage {
                package: pkg.to_string(),
                name: name.to_string(),
                category: DebloatCategory::Health,
                description: desc.to_string(),
                is_selected: false,
            });
        }

        // Samsung Pay
        for (pkg, name, desc) in PAY_PACKAGES {
            packages.push(DebloatPackage {
                package: pkg.to_string(),
                name: name.to_string(),
                category: DebloatCategory::Pay,
                description: desc.to_string(),
                is_selected: false,
            });
        }

        // Microsoft
        for (pkg, name, desc) in MICROSOFT_PACKAGES {
            packages.push(DebloatPackage {
                package: pkg.to_string(),
                name: name.to_string(),
                category: DebloatCategory::Microsoft,
                description: desc.to_string(),
                is_selected: false,
            });
        }

        // Facebook
        for (pkg, name, desc) in FACEBOOK_PACKAGES {
            packages.push(DebloatPackage {
                package: pkg.to_string(),
                name: name.to_string(),
                category: DebloatCategory::Facebook,
                description: desc.to_string(),
                is_selected: false,
            });
        }

        // Samsung Apps
        for (pkg, name, desc) in SAMSUNG_APPS_PACKAGES {
            packages.push(DebloatPackage {
                package: pkg.to_string(),
                name: name.to_string(),
                category: DebloatCategory::SamsungApps,
                description: desc.to_string(),
                is_selected: false,
            });
        }

        packages
    }

    /// Get packages for a specific debloat level
    pub fn get_packages_for_level(level: DebloatLevel) -> Vec<DebloatPackage> {
        let all = Self::get_all_packages();

        match level {
            DebloatLevel::Light => {
                all.into_iter()
                    .filter(|p| matches!(p.category,
                        DebloatCategory::Facebook |
                        DebloatCategory::Games))
                    .collect()
            }
            DebloatLevel::Medium => {
                all.into_iter()
                    .filter(|p| matches!(p.category,
                        DebloatCategory::Facebook |
                        DebloatCategory::Games |
                        DebloatCategory::ArEmoji |
                        DebloatCategory::Themes |
                        DebloatCategory::Bixby))
                    .collect()
            }
            DebloatLevel::Aggressive => all,
            DebloatLevel::Custom => all,
        }
    }

    /// Debloat a single package (uninstall for user 0)
    pub fn debloat_package(&self, package: &str) -> anyhow::Result<bool> {
        // Try uninstall first
        if self.adb.uninstall_package(package)? {
            return Ok(true);
        }

        // Fall back to disable
        self.adb.disable_package(package)
    }

    /// Debloat multiple packages
    pub fn debloat_packages(&self, packages: &[String]) -> Vec<(String, bool)> {
        packages.iter()
            .map(|pkg| {
                let success = self.debloat_package(pkg).unwrap_or(false);
                (pkg.clone(), success)
            })
            .collect()
    }

    /// Get which packages from the list are actually installed
    pub fn get_installed_packages(&self, packages: &[DebloatPackage]) -> anyhow::Result<Vec<DebloatPackage>> {
        let installed = self.adb.get_packages(true)?;
        let installed_names: std::collections::HashSet<_> = installed
            .iter()
            .map(|p| p.package_name.as_str())
            .collect();

        Ok(packages.iter()
            .filter(|p| installed_names.contains(p.package.as_str()))
            .cloned()
            .collect())
    }
}

// Package lists
const BIXBY_PACKAGES: &[(&str, &str, &str)] = &[
    ("com.samsung.android.bixby.agent", "Bixby Voice", "Voice assistant"),
    ("com.samsung.android.bixby.service", "Bixby Service", "Background service"),
    ("com.samsung.android.visionintelligence", "Bixby Vision", "Camera AI features"),
    ("com.samsung.android.bixby.wakeup", "Bixby Wakeup", "Voice activation"),
    ("com.samsung.android.app.spage", "Samsung Free", "News/content feed"),
    ("com.samsung.android.app.routines", "Bixby Routines", "Automation"),
    ("com.samsung.android.bixbyvision.framework", "Bixby Vision Framework", "Vision core"),
];

const AR_EMOJI_PACKAGES: &[(&str, &str, &str)] = &[
    ("com.samsung.android.aremoji", "AR Emoji", "Create AR emoji"),
    ("com.samsung.android.arzone", "AR Zone", "AR features hub"),
    ("com.samsung.android.ardrawing", "AR Doodle", "Draw in AR"),
    ("com.samsung.android.aremojieditor", "AR Emoji Editor", "Edit emoji"),
    ("com.sec.android.mimage.avatarstickers", "Avatar Stickers", "Emoji stickers"),
    ("com.samsung.android.app.camera.sticker.facearavatar.preload", "AR Stickers", "Camera stickers"),
];

const GAMES_PACKAGES: &[(&str, &str, &str)] = &[
    ("com.samsung.android.game.gamehome", "Game Home", "Game launcher"),
    ("com.samsung.android.game.gametools", "Game Tools", "Game overlay"),
    ("com.samsung.android.game.gos", "Game Optimizing", "Game performance"),
    ("com.enhance.gameservice", "Game Service", "Gaming features"),
    ("com.samsung.android.game.gameService", "Game Service", "Gaming backend"),
];

const THEMES_PACKAGES: &[(&str, &str, &str)] = &[
    ("com.samsung.android.themestore", "Galaxy Themes", "Theme store"),
    ("com.samsung.android.themecenter", "Theme Center", "Theme manager"),
    ("com.samsung.android.app.dressroom", "Wallpapers", "Wallpaper app"),
];

const KNOX_PACKAGES: &[(&str, &str, &str)] = &[
    ("com.samsung.android.knox.containercore", "Knox Container", "Secure folder core"),
    ("com.samsung.android.knox.analytics.uploader", "Knox Analytics", "Enterprise analytics"),
    ("com.samsung.android.knox.pushmanager", "Knox Push", "Enterprise push"),
    ("com.samsung.android.knox.kpu", "Knox Platform", "Enterprise platform"),
    ("com.sec.enterprise.knox.attestation", "Knox Attestation", "Security verification"),
    ("com.samsung.knox.securefolder", "Secure Folder", "Private space"),
    ("com.samsung.android.appseparation", "App Separation", "Knox isolation"),
];

const HEALTH_PACKAGES: &[(&str, &str, &str)] = &[
    ("com.samsung.android.forest", "Digital Wellbeing", "Screen time"),
    ("com.samsung.android.app.parentalcare", "Parental Controls", "Family features"),
    ("com.sec.android.app.shealth", "Samsung Health", "Health tracking"),
    ("com.samsung.android.service.health", "Health Service", "Health backend"),
];

const PAY_PACKAGES: &[(&str, &str, &str)] = &[
    ("com.samsung.android.spay", "Samsung Pay", "Mobile payments"),
    ("com.samsung.android.spayfw", "Samsung Pay Framework", "Payment core"),
    ("com.samsung.android.samsungpass", "Samsung Pass", "Password manager"),
    ("com.samsung.android.samsungpassautofill", "Pass Autofill", "Autofill service"),
    ("com.samsung.android.authfw", "Auth Framework", "Authentication"),
];

const MICROSOFT_PACKAGES: &[(&str, &str, &str)] = &[
    ("com.microsoft.appmanager", "MS App Manager", "Microsoft installer"),
    ("com.microsoft.office.outlook", "Outlook", "Email client"),
    ("com.microsoft.office.officehubrow", "Office Hub", "Office suite"),
    ("com.microsoft.skydrive", "OneDrive", "Cloud storage"),
    ("com.linkedin.android", "LinkedIn", "Professional network"),
    ("com.microsoft.office.word", "Word", "Document editor"),
    ("com.microsoft.office.excel", "Excel", "Spreadsheets"),
    ("com.microsoft.office.powerpoint", "PowerPoint", "Presentations"),
];

const FACEBOOK_PACKAGES: &[(&str, &str, &str)] = &[
    ("com.facebook.katana", "Facebook", "Social network"),
    ("com.facebook.orca", "Messenger", "Chat app"),
    ("com.facebook.system", "Facebook Services", "Background service"),
    ("com.facebook.appmanager", "FB App Manager", "Facebook installer"),
    ("com.facebook.services", "FB Services", "Facebook backend"),
    ("com.instagram.android", "Instagram", "Photo sharing"),
];

const SAMSUNG_APPS_PACKAGES: &[(&str, &str, &str)] = &[
    ("com.sec.android.app.sbrowser", "Samsung Browser", "Web browser"),
    ("com.samsung.android.app.tips", "Samsung Tips", "Tips and tricks"),
    ("com.samsung.android.mobileservice", "Samsung Experience", "Samsung services"),
    ("com.samsung.android.app.watchmanagerstub", "Galaxy Wearable", "Watch app stub"),
    ("com.samsung.android.voc", "Samsung Members", "Support app"),
    ("com.samsung.android.app.social", "Samsung Social", "What's New feed"),
    ("com.samsung.android.app.reminder", "Reminder", "Tasks app"),
    ("com.samsung.android.calendar", "Samsung Calendar", "Calendar app"),
    ("com.samsung.android.email.provider", "Email", "Email client"),
    ("com.samsung.android.app.notes", "Samsung Notes", "Note taking"),
    ("com.samsung.android.svoiceime", "Samsung Voice Input", "Voice typing"),
    ("com.samsung.android.kidsinstaller", "Kids Mode", "Parental mode"),
    ("com.samsung.android.app.sharelive", "Quick Share", "File sharing"),
    ("com.samsung.android.smartsuggestions", "Smart Suggestions", "AI suggestions"),
    ("com.samsung.android.privateshare", "Private Share", "Secure sharing"),
];
