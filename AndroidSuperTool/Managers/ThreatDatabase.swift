//
//  ThreatDatabase.swift
//  AndroidSuperTool
//

import Foundation

/// Information about a known threat
struct ThreatInfo {
    let packageName: String
    let riskLevel: RiskLevel
    let category: String
    let description: String
}

/// Database of known malware, adware, and bloatware packages
class ThreatDatabase {
    static let shared = ThreatDatabase()

    private var threats: [String: ThreatInfo] = [:]
    private var patterns: [(NSRegularExpression, RiskLevel, String)] = []

    private init() {
        loadThreats()
        loadPatterns()
    }

    private func loadThreats() {
        // CRITICAL - Known malware, banking trojans, spyware
        let critical: [(String, String, String)] = [
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
            ("com.cerberus.rat", "RAT", "Cerberus banking trojan"),
            ("com.flubot.sms", "SMS Malware", "FluBot SMS stealer"),
            ("com.teabot.banking", "Banking Trojan", "TeaBot banking trojan"),
        ]

        for (pkg, cat, desc) in critical {
            threats[pkg] = ThreatInfo(packageName: pkg, riskLevel: .critical, category: cat, description: desc)
        }

        // HIGH RISK - Aggressive adware, popup generators
        let highRisk: [(String, String, String)] = [
            ("wht.water.habit.tracker", "Popup Adware", "Generates fullscreen popup ads"),
            ("com.adsapp.notification", "Notification Spam", "Spams notification ads"),
            ("com.applovin.sdk", "Aggressive Ads", "Aggressive ad SDK"),
            ("com.startapp.android", "Adware SDK", "StartApp aggressive ads"),
            ("com.airpush.android", "Push Ads", "AirPush notification ads"),
            ("cn.wps.moffice_eng", "Bloatware", "WPS Office with heavy ads"),
            ("com.uc.browser", "Privacy Risk", "UC Browser - known privacy issues"),
            ("com.apus.launcher", "Adware Launcher", "APUS Launcher with ads"),
            ("com.cleanmaster.mguard", "Fake Cleaner", "Clean Master - aggressive ads"),
            ("com.qihoo.security", "Bloatware", "360 Security - heavy bloatware"),
            ("com.duapps.cleaner", "Adware", "DU Cleaner - aggressive ads"),
            ("com.nqmobile.antivirus", "Fake AV", "NQ Mobile fake antivirus"),
        ]

        for (pkg, cat, desc) in highRisk {
            threats[pkg] = ThreatInfo(packageName: pkg, riskLevel: .high, category: cat, description: desc)
        }

        // MEDIUM RISK - Bloatware, carrier apps
        let mediumRisk: [(String, String, String)] = [
            // Samsung
            ("com.samsung.android.app.tips", "Bloatware", "Samsung Tips"),
            ("com.samsung.android.game.gamehome", "Bloatware", "Samsung Game Hub"),
            ("com.samsung.android.arzone", "Bloatware", "Samsung AR Zone"),
            ("com.samsung.android.aremoji", "Bloatware", "Samsung AR Emoji"),
            ("com.samsung.android.bixby.agent", "Bloatware", "Bixby Voice"),
            ("com.samsung.android.visionintelligence", "Bloatware", "Bixby Vision"),
            ("com.samsung.android.app.spage", "Bloatware", "Bixby Home/Samsung Free"),
            ("com.sec.android.app.sbrowser", "Bloatware", "Samsung Browser"),
            ("com.samsung.android.themestore", "Bloatware", "Samsung Themes"),
            // Xiaomi
            ("com.miui.analytics", "Telemetry", "Xiaomi Analytics"),
            ("com.xiaomi.mipicks", "Bloatware", "Xiaomi GetApps"),
            ("com.miui.hybrid", "Bloatware", "Xiaomi Quick Apps"),
            ("com.miui.videoplayer", "Bloatware", "Mi Video"),
            ("com.xiaomi.glgm", "Bloatware", "Xiaomi Games"),
            // Huawei
            ("com.huawei.appmarket", "Bloatware", "Huawei AppGallery"),
            ("com.huawei.himovie", "Bloatware", "Huawei Video"),
            ("com.huawei.gameassistant", "Bloatware", "Huawei Game Center"),
            // Facebook
            ("com.facebook.katana", "Privacy Risk", "Facebook - high data collection"),
            ("com.facebook.orca", "Privacy Risk", "Facebook Messenger"),
            ("com.facebook.appmanager", "Bloatware", "Facebook App Manager"),
            ("com.facebook.system", "Bloatware", "Facebook Services"),
        ]

        for (pkg, cat, desc) in mediumRisk {
            threats[pkg] = ThreatInfo(packageName: pkg, riskLevel: .medium, category: cat, description: desc)
        }

        // LOW RISK - Microsoft apps, Google extras
        let lowRisk: [(String, String, String)] = [
            ("com.microsoft.office.outlook", "Optional", "Microsoft Outlook"),
            ("com.microsoft.office.word", "Optional", "Microsoft Word"),
            ("com.microsoft.office.excel", "Optional", "Microsoft Excel"),
            ("com.microsoft.skydrive", "Optional", "Microsoft OneDrive"),
            ("com.microsoft.appmanager", "Bloatware", "Microsoft Apps Manager"),
            ("com.linkedin.android", "Optional", "LinkedIn"),
            ("com.google.android.apps.magazines", "Optional", "Google News"),
            ("com.google.android.videos", "Optional", "Google Play Movies"),
            ("com.netflix.mediaclient", "Optional", "Netflix"),
            ("com.spotify.music", "Optional", "Spotify"),
        ]

        for (pkg, cat, desc) in lowRisk {
            threats[pkg] = ThreatInfo(packageName: pkg, riskLevel: .low, category: cat, description: desc)
        }
    }

    private func loadPatterns() {
        let patternData: [(String, RiskLevel, String)] = [
            // Critical
            ("(?i)(trojan|malware|virus|banker|stealer|keylog|ransom)", .critical, "Malware-related package"),
            // High
            ("(?i)(adware|popup|push\\.ad|notification\\.ad|spam)", .high, "Adware-related package"),
            ("(?i)(cleaner|booster|battery\\.saver|speed\\.up|optimizer)", .high, "Likely fake utility"),
            ("(?i)(free\\.vpn|vpn\\.free|turbo\\.vpn)", .high, "Suspicious free VPN"),
            // Medium
            ("^com\\.(samsung|sec)\\.android\\.(ar|bixby|game)", .medium, "Samsung bloatware"),
            ("^com\\.miui\\.|^com\\.xiaomi\\.", .medium, "Xiaomi system app"),
            ("^com\\.huawei\\.|^com\\.hicloud\\.", .medium, "Huawei system app"),
        ]

        for (pattern, level, desc) in patternData {
            if let regex = try? NSRegularExpression(pattern: pattern, options: []) {
                patterns.append((regex, level, desc))
            }
        }
    }

    /// Look up a package in the database
    func lookup(_ packageName: String) -> ThreatInfo? {
        return threats[packageName]
    }

    /// Check if a package matches suspicious patterns
    func checkPatterns(_ packageName: String) -> (RiskLevel, String)? {
        let range = NSRange(packageName.startIndex..., in: packageName)

        for (regex, level, desc) in patterns {
            if regex.firstMatch(in: packageName, options: [], range: range) != nil {
                return (level, desc)
            }
        }

        return nil
    }

    /// Analyze a package and return its risk assessment
    func analyze(_ packageName: String) -> (RiskLevel, String) {
        // Check exact matches first
        if let threat = lookup(packageName) {
            return (threat.riskLevel, threat.description)
        }

        // Check patterns
        if let (level, desc) = checkPatterns(packageName) {
            return (level, desc)
        }

        // Unknown - assume safe
        return (.safe, "Unknown package")
    }
}
