//
//  RecoveryManager.swift
//  AndroidSuperTool
//

import Foundation

/// Device manufacturer
enum Manufacturer: String, CaseIterable {
    case samsung = "Samsung"
    case xiaomi = "Xiaomi"
    case oneplus = "OnePlus"
    case google = "Google"
    case huawei = "Huawei"
    case motorola = "Motorola"
    case realme = "Realme"
    case oppo = "OPPO"
    case vivo = "Vivo"
    case other = "Other"

    static func detect(from manufacturerString: String) -> Manufacturer {
        let lower = manufacturerString.lowercased()

        if lower.contains("samsung") { return .samsung }
        if lower.contains("xiaomi") || lower.contains("redmi") || lower.contains("poco") { return .xiaomi }
        if lower.contains("oneplus") { return .oneplus }
        if lower.contains("google") { return .google }
        if lower.contains("huawei") || lower.contains("honor") { return .huawei }
        if lower.contains("motorola") || lower.contains("lenovo") { return .motorola }
        if lower.contains("realme") { return .realme }
        if lower.contains("oppo") { return .oppo }
        if lower.contains("vivo") { return .vivo }

        return .other
    }
}

/// Firmware source information
struct FirmwareSource: Identifiable {
    let id = UUID()
    let name: String
    let url: String
    let description: String
}

/// Flashing tool information
struct FlashingTool: Identifiable {
    let id = UUID()
    let name: String
    let description: String
    let downloadURL: String
    let instructions: [String]
}

/// Recovery and firmware management
class RecoveryManager {
    private let adb: ADBManager

    init(adb: ADBManager) {
        self.adb = adb
    }

    /// Get device manufacturer
    func getManufacturer() -> Manufacturer {
        guard let mfr = adb.getProperty("ro.product.manufacturer") else {
            return .other
        }
        return Manufacturer.detect(from: mfr)
    }

    /// Reboot to recovery mode
    func rebootRecovery() {
        adb.rebootRecovery()
    }

    /// Reboot to bootloader
    func rebootBootloader() {
        adb.rebootBootloader()
    }

    /// Reboot to download mode (Samsung)
    func rebootDownload() {
        adb.rebootDownload()
    }

    /// Normal reboot
    func reboot() {
        adb.reboot()
    }

    /// Factory reset (DANGEROUS!)
    func factoryReset() {
        adb.factoryReset()
    }

    /// Get firmware sources for manufacturer
    static func getFirmwareSources(for manufacturer: Manufacturer) -> [FirmwareSource] {
        switch manufacturer {
        case .samsung:
            return [
                FirmwareSource(name: "SamFw", url: "https://samfw.com", description: "Free Samsung firmware downloads"),
                FirmwareSource(name: "SamMobile", url: "https://www.sammobile.com/firmwares", description: "Official Samsung firmware archive"),
                FirmwareSource(name: "Frija", url: "https://github.com/SlackingVeteran/frija/releases", description: "Download directly from Samsung servers"),
            ]
        case .xiaomi:
            return [
                FirmwareSource(name: "XiaomiFirmwareUpdater", url: "https://xiaomifirmwareupdater.com", description: "Xiaomi/Redmi/POCO firmware archive"),
                FirmwareSource(name: "MIUI Download", url: "https://c.mi.com/global/miuidownload", description: "Official MIUI download page"),
            ]
        case .oneplus:
            return [
                FirmwareSource(name: "OnePlus Support", url: "https://service.oneplus.com/global/search/search-detail?id=2096329", description: "Official OnePlus firmware"),
                FirmwareSource(name: "XDA OnePlus", url: "https://www.xda-developers.com/tag/oneplus", description: "Community firmware and guides"),
            ]
        case .google:
            return [
                FirmwareSource(name: "Google Developers", url: "https://developers.google.com/android/images", description: "Official Pixel factory images"),
                FirmwareSource(name: "OTA Images", url: "https://developers.google.com/android/ota", description: "Official Pixel OTA updates"),
            ]
        case .huawei:
            return [
                FirmwareSource(name: "HuaweiROM", url: "https://huaweirom.com", description: "Huawei firmware archive"),
                FirmwareSource(name: "Firmware Finder", url: "https://pro-teammt.ru/firmware-database", description: "Huawei firmware database"),
            ]
        case .motorola:
            return [
                FirmwareSource(name: "Motorola Support", url: "https://motorola-global-portal.custhelp.com/app/software-upgrade", description: "Official Motorola software"),
                FirmwareSource(name: "Lolinet", url: "https://mirrors.lolinet.com/firmware/motorola", description: "Motorola firmware mirror"),
            ]
        case .realme:
            return [
                FirmwareSource(name: "Realme Software Update", url: "https://www.realme.com/global/support/software-update", description: "Official Realme updates"),
            ]
        case .oppo:
            return [
                FirmwareSource(name: "OPPO Support", url: "https://support.oppo.com/en/software-update", description: "Official OPPO software"),
            ]
        case .vivo:
            return [
                FirmwareSource(name: "Vivo Support", url: "https://www.vivo.com/en/support/download", description: "Official Vivo downloads"),
            ]
        case .other:
            return [
                FirmwareSource(name: "XDA Developers", url: "https://www.xda-developers.com", description: "Community forums - search for your device"),
            ]
        }
    }

    /// Get flashing tool for manufacturer
    static func getFlashingTool(for manufacturer: Manufacturer) -> FlashingTool? {
        switch manufacturer {
        case .samsung:
            return FlashingTool(
                name: "Odin / Heimdall",
                description: "Odin (Windows) or Heimdall (Cross-platform) for Samsung",
                downloadURL: "https://github.com/Benjamin-Dobell/Heimdall/releases",
                instructions: [
                    "1. Download Odin (Windows) or Heimdall (Mac/Linux)",
                    "2. Put device in Download Mode (Vol Down + Power while off)",
                    "3. Connect USB and select firmware files",
                    "4. Click Start/Flash to begin"
                ]
            )
        case .xiaomi:
            return FlashingTool(
                name: "MiFlash Tool",
                description: "Official Xiaomi flashing tool",
                downloadURL: "https://xiaomiflashtool.com",
                instructions: [
                    "1. Download and install MiFlash",
                    "2. Put device in Fastboot mode (Vol Down + Power)",
                    "3. Select firmware folder in MiFlash",
                    "4. Click Refresh, select device, click Flash"
                ]
            )
        case .google:
            return FlashingTool(
                name: "Android Flash Tool",
                description: "Google's web-based flashing tool",
                downloadURL: "https://flash.android.com",
                instructions: [
                    "1. Visit flash.android.com in Chrome",
                    "2. Enable OEM unlocking in Developer Options",
                    "3. Connect device in Fastboot mode",
                    "4. Follow on-screen instructions"
                ]
            )
        default:
            return nil
        }
    }
}
