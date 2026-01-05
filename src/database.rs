//! Threat database for known malware, adware, and bloatware packages

use std::collections::HashMap;

/// Risk level for detected apps
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum RiskLevel {
    Safe,
    Low,
    Medium,
    High,
    Critical,
}

impl RiskLevel {
    pub fn as_str(&self) -> &'static str {
        match self {
            RiskLevel::Safe => "SAFE",
            RiskLevel::Low => "LOW",
            RiskLevel::Medium => "MEDIUM",
            RiskLevel::High => "HIGH",
            RiskLevel::Critical => "CRITICAL",
        }
    }

    pub fn color(&self) -> &'static str {
        match self {
            RiskLevel::Safe => "green",
            RiskLevel::Low => "blue",
            RiskLevel::Medium => "yellow",
            RiskLevel::High => "red",
            RiskLevel::Critical => "magenta",
        }
    }
}

/// Information about a known threat
#[derive(Debug, Clone)]
pub struct ThreatInfo {
    pub package: String,
    pub risk_level: RiskLevel,
    pub category: String,
    pub description: String,
}

/// Threat database containing known malicious and bloatware packages
pub struct ThreatDatabase {
    threats: HashMap<String, ThreatInfo>,
    patterns: Vec<(regex::Regex, RiskLevel, String)>,
}

impl ThreatDatabase {
    pub fn new() -> Self {
        let mut db = Self {
            threats: HashMap::new(),
            patterns: Vec::new(),
        };
        db.load_threats();
        db.load_patterns();
        db
    }

    fn load_threats(&mut self) {
        // CRITICAL - Known malware, banking trojans, spyware
        let critical = vec![
            ("com.android.syskeeper", "Banking Trojan", "Anubis banking trojan variant"),
            ("com.android.providers.system", "Spyware", "System-disguised spyware"),
            ("com.android.system.service", "Malware", "Fake system service malware"),
            ("com.update.system.app", "Trojan", "Fake update trojan"),
            ("com.android.playstore", "Fake App", "Fake Play Store (real is com.android.vending)"),
            ("com.secure.vpn.free", "Data Theft", "VPN that steals data"),
            ("com.battery.saver.pro", "Adware/Spyware", "Fake battery saver with spyware"),
            ("com.speed.booster.master", "Adware", "Fake speed booster full of ads"),
            ("com.cleaner.super.fast", "Adware", "Fake cleaner with aggressive ads"),
            ("com.joker.malware", "Premium SMS", "Joker malware family"),
            ("com.hiddad.adware", "Adware", "HiddenAd malware family"),
            ("com.alien.spy", "Spyware", "AlienSpy RAT"),
            ("com.cerberus.rat", "RAT", "Cerberus banking trojan"),
            ("com.eventbot.trojan", "Banking Trojan", "EventBot banking trojan"),
            ("com.flubot.sms", "SMS Malware", "FluBot SMS stealer"),
            ("com.teabot.banking", "Banking Trojan", "TeaBot banking trojan"),
        ];

        for (pkg, cat, desc) in critical {
            self.threats.insert(pkg.to_string(), ThreatInfo {
                package: pkg.to_string(),
                risk_level: RiskLevel::Critical,
                category: cat.to_string(),
                description: desc.to_string(),
            });
        }

        // HIGH RISK - Aggressive adware, popup generators, known problematic apps
        let high_risk = vec![
            ("wht.water.habit.tracker", "Popup Adware", "Generates fullscreen popup ads"),
            ("com.adsapp.notification", "Notification Spam", "Spams notification ads"),
            ("com.applovin.sdk", "Aggressive Ads", "Aggressive ad SDK"),
            ("com.startapp.android", "Adware SDK", "StartApp aggressive ads"),
            ("com.airpush.android", "Push Ads", "AirPush notification ads"),
            ("com.leadbolt.android", "Adware", "LeadBolt ad network"),
            ("com.mobvista.msdk", "Adware SDK", "Mobvista aggressive ads"),
            ("com.inmobi.androidsdk", "Adware", "InMobi aggressive variant"),
            ("cn.wps.moffice_eng", "Bloatware", "WPS Office with heavy ads"),
            ("com.uc.browser", "Privacy Risk", "UC Browser - known privacy issues"),
            ("com.apus.launcher", "Adware Launcher", "APUS Launcher with ads"),
            ("com.cleanmaster.mguard", "Fake Cleaner", "Clean Master - aggressive ads"),
            ("com.cmcm.whatscall", "Data Mining", "CMC data mining app"),
            ("com.qihoo.security", "Bloatware", "360 Security - heavy bloatware"),
            ("com.duapps.cleaner", "Adware", "DU Cleaner - aggressive ads"),
            ("com.dianxinos.optimizer", "Adware", "DU Speed Booster"),
            ("com.nqmobile.antivirus", "Fake AV", "NQ Mobile fake antivirus"),
            ("com.piriform.ccleaner", "Unnecessary", "CCleaner - not useful on Android"),
            ("com.avast.android.cleaner", "Adware", "Avast Cleanup with ads"),
        ];

        for (pkg, cat, desc) in high_risk {
            self.threats.insert(pkg.to_string(), ThreatInfo {
                package: pkg.to_string(),
                risk_level: RiskLevel::High,
                category: cat.to_string(),
                description: desc.to_string(),
            });
        }

        // MEDIUM RISK - Bloatware, carrier apps, manufacturer junk
        let medium_risk = vec![
            // Samsung bloatware
            ("com.samsung.android.app.tips", "Bloatware", "Samsung Tips"),
            ("com.samsung.android.game.gamehome", "Bloatware", "Samsung Game Hub"),
            ("com.samsung.android.game.gametools", "Bloatware", "Samsung Game Tools"),
            ("com.samsung.android.arzone", "Bloatware", "Samsung AR Zone"),
            ("com.samsung.android.aremoji", "Bloatware", "Samsung AR Emoji"),
            ("com.samsung.android.ardrawing", "Bloatware", "Samsung AR Doodle"),
            ("com.samsung.android.bixby.agent", "Bloatware", "Bixby Voice"),
            ("com.samsung.android.visionintelligence", "Bloatware", "Bixby Vision"),
            ("com.samsung.android.bixby.service", "Bloatware", "Bixby Service"),
            ("com.samsung.android.app.spage", "Bloatware", "Bixby Home/Samsung Free"),
            ("com.sec.android.app.sbrowser", "Bloatware", "Samsung Browser"),
            ("com.samsung.android.themestore", "Bloatware", "Samsung Themes"),
            ("com.samsung.android.mobileservice", "Bloatware", "Samsung Experience Service"),
            ("com.samsung.android.forest", "Bloatware", "Samsung Digital Wellbeing"),
            // Xiaomi bloatware
            ("com.miui.analytics", "Telemetry", "Xiaomi Analytics"),
            ("com.xiaomi.mipicks", "Bloatware", "Xiaomi GetApps"),
            ("com.miui.hybrid", "Bloatware", "Xiaomi Quick Apps"),
            ("com.miui.videoplayer", "Bloatware", "Mi Video"),
            ("com.miui.player", "Bloatware", "Mi Music"),
            ("com.mi.globalminusscreen", "Bloatware", "Mi App Vault"),
            ("com.miui.cloudservice", "Telemetry", "Xiaomi Cloud"),
            ("com.xiaomi.glgm", "Bloatware", "Xiaomi Games"),
            ("com.miui.cleanmaster", "Bloatware", "Xiaomi Cleaner"),
            // Huawei bloatware
            ("com.huawei.appmarket", "Bloatware", "Huawei AppGallery"),
            ("com.huawei.himovie", "Bloatware", "Huawei Video"),
            ("com.huawei.music", "Bloatware", "Huawei Music"),
            ("com.huawei.gameassistant", "Bloatware", "Huawei Game Center"),
            ("com.huawei.hwid", "Telemetry", "Huawei Mobile Services"),
            // Facebook
            ("com.facebook.katana", "Privacy Risk", "Facebook - high data collection"),
            ("com.facebook.orca", "Privacy Risk", "Facebook Messenger"),
            ("com.facebook.appmanager", "Bloatware", "Facebook App Manager"),
            ("com.facebook.system", "Bloatware", "Facebook Services"),
            ("com.facebook.services", "Bloatware", "Facebook Services"),
        ];

        for (pkg, cat, desc) in medium_risk {
            self.threats.insert(pkg.to_string(), ThreatInfo {
                package: pkg.to_string(),
                risk_level: RiskLevel::Medium,
                category: cat.to_string(),
                description: desc.to_string(),
            });
        }

        // LOW RISK - Microsoft apps, Google extras, optional services
        let low_risk = vec![
            ("com.microsoft.office.outlook", "Optional", "Microsoft Outlook"),
            ("com.microsoft.office.word", "Optional", "Microsoft Word"),
            ("com.microsoft.office.excel", "Optional", "Microsoft Excel"),
            ("com.microsoft.office.powerpoint", "Optional", "Microsoft PowerPoint"),
            ("com.microsoft.skydrive", "Optional", "Microsoft OneDrive"),
            ("com.microsoft.appmanager", "Bloatware", "Microsoft Apps Manager"),
            ("com.linkedin.android", "Optional", "LinkedIn"),
            ("com.google.android.apps.magazines", "Optional", "Google News"),
            ("com.google.android.videos", "Optional", "Google Play Movies"),
            ("com.google.android.music", "Optional", "Google Play Music"),
            ("com.google.android.apps.tachyon", "Optional", "Google Duo/Meet"),
            ("com.google.android.youtube.music", "Optional", "YouTube Music"),
            ("com.netflix.mediaclient", "Optional", "Netflix"),
            ("com.spotify.music", "Optional", "Spotify"),
            ("com.amazon.kindle", "Optional", "Kindle"),
        ];

        for (pkg, cat, desc) in low_risk {
            self.threats.insert(pkg.to_string(), ThreatInfo {
                package: pkg.to_string(),
                risk_level: RiskLevel::Low,
                category: cat.to_string(),
                description: desc.to_string(),
            });
        }
    }

    fn load_patterns(&mut self) {
        // Critical patterns
        self.patterns.push((
            regex::Regex::new(r"(?i)(trojan|malware|virus|banker|stealer|keylog|ransom)").unwrap(),
            RiskLevel::Critical,
            "Malware-related package name".to_string(),
        ));

        // High risk patterns
        self.patterns.push((
            regex::Regex::new(r"(?i)(adware|popup|push\.ad|notification\.ad|spam)").unwrap(),
            RiskLevel::High,
            "Adware-related package".to_string(),
        ));
        self.patterns.push((
            regex::Regex::new(r"(?i)(cleaner|booster|battery\.saver|speed\.up|optimizer)").unwrap(),
            RiskLevel::High,
            "Likely fake utility app".to_string(),
        ));
        self.patterns.push((
            regex::Regex::new(r"(?i)(free\.vpn|vpn\.free|turbo\.vpn)").unwrap(),
            RiskLevel::High,
            "Suspicious free VPN".to_string(),
        ));

        // Medium risk patterns
        self.patterns.push((
            regex::Regex::new(r"^com\.(samsung|sec)\.android\.(ar|bixby|game)").unwrap(),
            RiskLevel::Medium,
            "Samsung bloatware".to_string(),
        ));
        self.patterns.push((
            regex::Regex::new(r"^com\.miui\.|^com\.xiaomi\.").unwrap(),
            RiskLevel::Medium,
            "Xiaomi system app".to_string(),
        ));
        self.patterns.push((
            regex::Regex::new(r"^com\.huawei\.|^com\.hicloud\.").unwrap(),
            RiskLevel::Medium,
            "Huawei system app".to_string(),
        ));
    }

    /// Look up a package in the database
    pub fn lookup(&self, package: &str) -> Option<&ThreatInfo> {
        self.threats.get(package)
    }

    /// Check if a package matches any suspicious patterns
    pub fn check_patterns(&self, package: &str) -> Option<(RiskLevel, String)> {
        for (regex, level, desc) in &self.patterns {
            if regex.is_match(package) {
                return Some((*level, desc.clone()));
            }
        }
        None
    }

    /// Analyze a package and return its risk level and description
    pub fn analyze(&self, package: &str) -> (RiskLevel, String) {
        // First check exact matches
        if let Some(threat) = self.lookup(package) {
            return (threat.risk_level, threat.description.clone());
        }

        // Then check patterns
        if let Some((level, desc)) = self.check_patterns(package) {
            return (level, desc);
        }

        // Unknown package
        (RiskLevel::Safe, "Unknown package".to_string())
    }

    /// Get all packages of a specific risk level
    pub fn get_by_risk(&self, level: RiskLevel) -> Vec<&ThreatInfo> {
        self.threats.values().filter(|t| t.risk_level == level).collect()
    }
}

impl Default for ThreatDatabase {
    fn default() -> Self {
        Self::new()
    }
}
