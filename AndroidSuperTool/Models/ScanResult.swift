//
//  ScanResult.swift
//  AndroidSuperTool
//

import SwiftUI

/// Risk level for detected apps
enum RiskLevel: Int, Comparable, CaseIterable {
    case safe = 0
    case low = 1
    case medium = 2
    case high = 3
    case critical = 4

    static func < (lhs: RiskLevel, rhs: RiskLevel) -> Bool {
        lhs.rawValue < rhs.rawValue
    }

    var displayName: String {
        switch self {
        case .safe: return "SAFE"
        case .low: return "LOW"
        case .medium: return "MEDIUM"
        case .high: return "HIGH"
        case .critical: return "CRITICAL"
        }
    }

    var color: Color {
        switch self {
        case .safe: return .green
        case .low: return .blue
        case .medium: return .orange
        case .high: return .red
        case .critical: return .purple
        }
    }

    var icon: String {
        switch self {
        case .safe: return "checkmark.shield"
        case .low: return "info.circle"
        case .medium: return "exclamationmark.triangle"
        case .high: return "xmark.shield"
        case .critical: return "exclamationmark.shield"
        }
    }
}

/// Result of scanning an app
class ScanResult: Identifiable, ObservableObject {
    let id = UUID()
    let package: PackageInfo
    let riskLevel: RiskLevel
    let category: String
    let description: String
    @Published var isSelected: Bool = false

    init(package: PackageInfo, riskLevel: RiskLevel, category: String, description: String) {
        self.package = package
        self.riskLevel = riskLevel
        self.category = category
        self.description = description
    }
}

/// Summary of scan results
struct ThreatSummary {
    var total: Int = 0
    var critical: Int = 0
    var high: Int = 0
    var medium: Int = 0
    var low: Int = 0
    var safe: Int = 0

    var threats: Int {
        critical + high + medium
    }

    static func from(_ results: [ScanResult]) -> ThreatSummary {
        var summary = ThreatSummary()
        summary.total = results.count

        for result in results {
            switch result.riskLevel {
            case .critical: summary.critical += 1
            case .high: summary.high += 1
            case .medium: summary.medium += 1
            case .low: summary.low += 1
            case .safe: summary.safe += 1
            }
        }

        return summary
    }
}
