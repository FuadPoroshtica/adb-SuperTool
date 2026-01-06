//
//  AppScanner.swift
//  AndroidSuperTool
//

import Foundation

/// Scanner for analyzing apps on a device
class AppScanner {
    private let adb: ADBManager
    private let database = ThreatDatabase.shared

    init(adb: ADBManager) {
        self.adb = adb
    }

    /// Scan all third-party apps on the device
    func scanDevice() -> [ScanResult] {
        let packages = adb.getThirdPartyPackages()
        var results = [ScanResult]()

        for pkg in packages {
            let (riskLevel, description) = database.analyze(pkg.packageName)
            let category = categorize(pkg.packageName, risk: riskLevel)

            results.append(ScanResult(
                package: pkg,
                riskLevel: riskLevel,
                category: category,
                description: description
            ))
        }

        // Sort by risk level (highest first)
        results.sort { $0.riskLevel > $1.riskLevel }

        return results
    }

    /// Scan all apps including system apps
    func scanAll() -> [ScanResult] {
        let packages = adb.getPackages(includeSystem: true)
        var results = [ScanResult]()

        for pkg in packages {
            let (riskLevel, description) = database.analyze(pkg.packageName)
            let category = categorize(pkg.packageName, risk: riskLevel)

            results.append(ScanResult(
                package: pkg,
                riskLevel: riskLevel,
                category: category,
                description: description
            ))
        }

        results.sort { $0.riskLevel > $1.riskLevel }

        return results
    }

    /// Categorize an app based on its package name and risk level
    private func categorize(_ packageName: String, risk: RiskLevel) -> String {
        switch risk {
        case .critical:
            return "Malware"
        case .high:
            return "Adware/PUP"
        case .medium:
            return "Bloatware"
        case .low:
            return "Optional"
        case .safe:
            if packageName.contains("google") {
                return "Google"
            } else if packageName.contains("samsung") || packageName.contains("sec.") {
                return "Samsung"
            } else if packageName.contains("miui") || packageName.contains("xiaomi") {
                return "Xiaomi"
            } else if packageName.contains("huawei") {
                return "Huawei"
            } else {
                return "User App"
            }
        }
    }

    /// Quick scan - only high risk and critical
    func quickScan() -> [ScanResult] {
        scanDevice().filter { $0.riskLevel >= .high }
    }
}
