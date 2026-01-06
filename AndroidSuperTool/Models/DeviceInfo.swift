//
//  DeviceInfo.swift
//  AndroidSuperTool
//

import Foundation

/// Status of a connected device
enum DeviceStatus: String {
    case online = "device"
    case offline = "offline"
    case unauthorized = "unauthorized"
    case recovery = "recovery"
    case sideload = "sideload"
    case unknown = "unknown"

    var displayName: String {
        switch self {
        case .online: return "Online"
        case .offline: return "Offline"
        case .unauthorized: return "Unauthorized"
        case .recovery: return "Recovery"
        case .sideload: return "Sideload"
        case .unknown: return "Unknown"
        }
    }
}

/// Information about a connected Android device
struct DeviceInfo: Identifiable, Hashable {
    let id = UUID()
    let serial: String
    var model: String
    var manufacturer: String
    var androidVersion: String
    var sdkVersion: String
    var status: DeviceStatus

    var displayName: String {
        "\(manufacturer) \(model)"
    }

    static func == (lhs: DeviceInfo, rhs: DeviceInfo) -> Bool {
        lhs.serial == rhs.serial
    }

    func hash(into hasher: inout Hasher) {
        hasher.combine(serial)
    }
}

/// Information about an installed package
struct PackageInfo: Identifiable {
    let id = UUID()
    let packageName: String
    var versionName: String?
    var versionCode: String?
    var isSystem: Bool
    var isDisabled: Bool
    var installer: String?
}
