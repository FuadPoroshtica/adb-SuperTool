//
//  Debloater.swift
//  AndroidSuperTool
//

import Foundation

/// Debloat intensity level
enum DebloatLevel: String, CaseIterable {
    case light = "Light"
    case medium = "Medium"
    case aggressive = "Aggressive"
    case custom = "Custom"

    var description: String {
        switch self {
        case .light: return "Safe - Remove obvious bloatware only"
        case .medium: return "Moderate - Remove AR, Games, Themes"
        case .aggressive: return "Maximum - Remove most Samsung apps"
        case .custom: return "Custom - Select packages manually"
        }
    }
}

/// Category of bloatware package
enum DebloatCategory: String, CaseIterable {
    case bixby = "Bixby"
    case arEmoji = "AR Emoji"
    case games = "Games"
    case themes = "Themes"
    case knox = "Knox"
    case health = "Health"
    case pay = "Samsung Pay"
    case microsoft = "Microsoft"
    case facebook = "Facebook"
    case samsungApps = "Samsung Apps"
}

/// A package that can be debloated
class DebloatPackage: Identifiable, ObservableObject {
    let id = UUID()
    let packageName: String
    let name: String
    let category: DebloatCategory
    let description: String
    @Published var isSelected: Bool = false

    init(packageName: String, name: String, category: DebloatCategory, description: String) {
        self.packageName = packageName
        self.name = name
        self.category = category
        self.description = description
    }
}

/// Samsung Debloater
class Debloater {
    private let adb: ADBManager

    init(adb: ADBManager) {
        self.adb = adb
    }

    /// Check if device is a Samsung entry-level device
    func isEntryLevelSamsung() -> Bool {
        guard let model = adb.getProperty("ro.product.model")?.uppercased() else {
            return false
        }

        let entryLevelPrefixes = [
            "SM-A055", "SM-A065", "SM-A075", "SM-A165", "SM-A175",
            "SM-A135", "SM-A145", "SM-A155", "SM-A045", "SM-A046",
            "SM-A035", "SM-A037", "SM-A032", "SM-M135", "SM-M145", "SM-M155"
        ]

        return entryLevelPrefixes.contains { model.hasPrefix($0) }
    }

    /// Get all debloatable packages
    static func getAllPackages() -> [DebloatPackage] {
        var packages = [DebloatPackage]()

        // Bixby
        for (pkg, name, desc) in bixbyPackages {
            packages.append(DebloatPackage(packageName: pkg, name: name, category: .bixby, description: desc))
        }

        // AR Emoji
        for (pkg, name, desc) in arEmojiPackages {
            packages.append(DebloatPackage(packageName: pkg, name: name, category: .arEmoji, description: desc))
        }

        // Games
        for (pkg, name, desc) in gamesPackages {
            packages.append(DebloatPackage(packageName: pkg, name: name, category: .games, description: desc))
        }

        // Themes
        for (pkg, name, desc) in themesPackages {
            packages.append(DebloatPackage(packageName: pkg, name: name, category: .themes, description: desc))
        }

        // Knox
        for (pkg, name, desc) in knoxPackages {
            packages.append(DebloatPackage(packageName: pkg, name: name, category: .knox, description: desc))
        }

        // Health
        for (pkg, name, desc) in healthPackages {
            packages.append(DebloatPackage(packageName: pkg, name: name, category: .health, description: desc))
        }

        // Samsung Pay
        for (pkg, name, desc) in payPackages {
            packages.append(DebloatPackage(packageName: pkg, name: name, category: .pay, description: desc))
        }

        // Microsoft
        for (pkg, name, desc) in microsoftPackages {
            packages.append(DebloatPackage(packageName: pkg, name: name, category: .microsoft, description: desc))
        }

        // Facebook
        for (pkg, name, desc) in facebookPackages {
            packages.append(DebloatPackage(packageName: pkg, name: name, category: .facebook, description: desc))
        }

        // Samsung Apps
        for (pkg, name, desc) in samsungAppsPackages {
            packages.append(DebloatPackage(packageName: pkg, name: name, category: .samsungApps, description: desc))
        }

        return packages
    }

    /// Get packages for a specific debloat level
    static func getPackagesForLevel(_ level: DebloatLevel) -> [DebloatPackage] {
        let all = getAllPackages()

        switch level {
        case .light:
            return all.filter { $0.category == .facebook || $0.category == .games }
        case .medium:
            return all.filter {
                [.facebook, .games, .arEmoji, .themes, .bixby].contains($0.category)
            }
        case .aggressive, .custom:
            return all
        }
    }

    /// Debloat a single package
    @discardableResult
    func debloatPackage(_ packageName: String) -> Bool {
        // Try uninstall first
        if adb.uninstallPackage(packageName) {
            return true
        }

        // Fall back to disable
        return adb.disablePackage(packageName)
    }

    /// Debloat multiple packages
    func debloatPackages(_ packages: [String]) -> [(String, Bool)] {
        packages.map { ($0, debloatPackage($0)) }
    }

    /// Get which packages from the list are actually installed
    func getInstalledPackages(_ packages: [DebloatPackage]) -> [DebloatPackage] {
        let installed = Set(adb.getPackages(includeSystem: true).map { $0.packageName })
        return packages.filter { installed.contains($0.packageName) }
    }

    // Package lists
    private static let bixbyPackages: [(String, String, String)] = [
        ("com.samsung.android.bixby.agent", "Bixby Voice", "Voice assistant"),
        ("com.samsung.android.bixby.service", "Bixby Service", "Background service"),
        ("com.samsung.android.visionintelligence", "Bixby Vision", "Camera AI features"),
        ("com.samsung.android.bixby.wakeup", "Bixby Wakeup", "Voice activation"),
        ("com.samsung.android.app.spage", "Samsung Free", "News/content feed"),
        ("com.samsung.android.app.routines", "Bixby Routines", "Automation"),
    ]

    private static let arEmojiPackages: [(String, String, String)] = [
        ("com.samsung.android.aremoji", "AR Emoji", "Create AR emoji"),
        ("com.samsung.android.arzone", "AR Zone", "AR features hub"),
        ("com.samsung.android.ardrawing", "AR Doodle", "Draw in AR"),
        ("com.samsung.android.aremojieditor", "AR Emoji Editor", "Edit emoji"),
        ("com.sec.android.mimage.avatarstickers", "Avatar Stickers", "Emoji stickers"),
    ]

    private static let gamesPackages: [(String, String, String)] = [
        ("com.samsung.android.game.gamehome", "Game Home", "Game launcher"),
        ("com.samsung.android.game.gametools", "Game Tools", "Game overlay"),
        ("com.samsung.android.game.gos", "Game Optimizing", "Game performance"),
        ("com.enhance.gameservice", "Game Service", "Gaming features"),
    ]

    private static let themesPackages: [(String, String, String)] = [
        ("com.samsung.android.themestore", "Galaxy Themes", "Theme store"),
        ("com.samsung.android.themecenter", "Theme Center", "Theme manager"),
        ("com.samsung.android.app.dressroom", "Wallpapers", "Wallpaper app"),
    ]

    private static let knoxPackages: [(String, String, String)] = [
        ("com.samsung.android.knox.containercore", "Knox Container", "Secure folder core"),
        ("com.samsung.android.knox.analytics.uploader", "Knox Analytics", "Enterprise analytics"),
        ("com.samsung.android.knox.pushmanager", "Knox Push", "Enterprise push"),
        ("com.samsung.knox.securefolder", "Secure Folder", "Private space"),
    ]

    private static let healthPackages: [(String, String, String)] = [
        ("com.samsung.android.forest", "Digital Wellbeing", "Screen time"),
        ("com.samsung.android.app.parentalcare", "Parental Controls", "Family features"),
        ("com.sec.android.app.shealth", "Samsung Health", "Health tracking"),
    ]

    private static let payPackages: [(String, String, String)] = [
        ("com.samsung.android.spay", "Samsung Pay", "Mobile payments"),
        ("com.samsung.android.spayfw", "Samsung Pay Framework", "Payment core"),
        ("com.samsung.android.samsungpass", "Samsung Pass", "Password manager"),
    ]

    private static let microsoftPackages: [(String, String, String)] = [
        ("com.microsoft.appmanager", "MS App Manager", "Microsoft installer"),
        ("com.microsoft.office.outlook", "Outlook", "Email client"),
        ("com.microsoft.office.officehubrow", "Office Hub", "Office suite"),
        ("com.microsoft.skydrive", "OneDrive", "Cloud storage"),
        ("com.linkedin.android", "LinkedIn", "Professional network"),
    ]

    private static let facebookPackages: [(String, String, String)] = [
        ("com.facebook.katana", "Facebook", "Social network"),
        ("com.facebook.orca", "Messenger", "Chat app"),
        ("com.facebook.system", "Facebook Services", "Background service"),
        ("com.facebook.appmanager", "FB App Manager", "Facebook installer"),
        ("com.instagram.android", "Instagram", "Photo sharing"),
    ]

    private static let samsungAppsPackages: [(String, String, String)] = [
        ("com.sec.android.app.sbrowser", "Samsung Browser", "Web browser"),
        ("com.samsung.android.app.tips", "Samsung Tips", "Tips and tricks"),
        ("com.samsung.android.mobileservice", "Samsung Experience", "Samsung services"),
        ("com.samsung.android.voc", "Samsung Members", "Support app"),
        ("com.samsung.android.calendar", "Samsung Calendar", "Calendar app"),
        ("com.samsung.android.app.notes", "Samsung Notes", "Note taking"),
    ]
}
