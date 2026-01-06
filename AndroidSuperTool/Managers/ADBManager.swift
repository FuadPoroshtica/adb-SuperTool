//
//  ADBManager.swift
//  AndroidSuperTool
//

import Foundation

/// Manager for ADB (Android Debug Bridge) operations
class ADBManager {
    private let adbPath: String
    private var currentDevice: String?

    init(adbPath: String) {
        self.adbPath = adbPath
        startServer()
    }

    /// Set the current device to operate on
    func setDevice(_ serial: String) {
        currentDevice = serial
    }

    /// Run an ADB command
    @discardableResult
    private func runADB(_ args: [String]) -> (output: String, success: Bool) {
        var allArgs = [String]()

        if let device = currentDevice {
            allArgs.append(contentsOf: ["-s", device])
        }

        allArgs.append(contentsOf: args)

        let process = Process()
        process.executableURL = URL(fileURLWithPath: adbPath)
        process.arguments = allArgs

        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = pipe

        do {
            try process.run()
            process.waitUntilExit()

            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            let output = String(data: data, encoding: .utf8) ?? ""

            return (output.trimmingCharacters(in: .whitespacesAndNewlines), process.terminationStatus == 0)
        } catch {
            return ("Error: \(error.localizedDescription)", false)
        }
    }

    /// Run a shell command on the device
    private func runShell(_ command: String) -> String {
        let result = runADB(["shell", command])
        return result.output
    }

    /// Start the ADB server
    func startServer() {
        runADB(["start-server"])
    }

    /// Kill the ADB server
    func killServer() {
        runADB(["kill-server"])
    }

    /// Restart the ADB server
    func restartServer() {
        killServer()
        Thread.sleep(forTimeInterval: 0.5)
        startServer()
    }

    /// Get list of connected devices
    func getDevices() -> [DeviceInfo] {
        let result = runADB(["devices", "-l"])
        var devices = [DeviceInfo]()

        let lines = result.output.components(separatedBy: .newlines)
        for line in lines.dropFirst() {
            let trimmed = line.trimmingCharacters(in: .whitespaces)
            if trimmed.isEmpty { continue }

            let parts = trimmed.components(separatedBy: .whitespaces).filter { !$0.isEmpty }
            guard parts.count >= 2 else { continue }

            let serial = parts[0]
            let statusStr = parts[1]

            let status: DeviceStatus
            switch statusStr {
            case "device": status = .online
            case "offline": status = .offline
            case "unauthorized": status = .unauthorized
            case "recovery": status = .recovery
            case "sideload": status = .sideload
            default: status = .unknown
            }

            // Get device details
            let model = getPropertyForDevice(serial, "ro.product.model") ?? "Unknown"
            let manufacturer = getPropertyForDevice(serial, "ro.product.manufacturer") ?? "Unknown"
            let androidVersion = getPropertyForDevice(serial, "ro.build.version.release") ?? "Unknown"
            let sdkVersion = getPropertyForDevice(serial, "ro.build.version.sdk") ?? "Unknown"

            devices.append(DeviceInfo(
                serial: serial,
                model: model,
                manufacturer: manufacturer,
                androidVersion: androidVersion,
                sdkVersion: sdkVersion,
                status: status
            ))
        }

        return devices
    }

    /// Get a property for a specific device
    private func getPropertyForDevice(_ serial: String, _ prop: String) -> String? {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: adbPath)
        process.arguments = ["-s", serial, "shell", "getprop", prop]

        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = pipe

        do {
            try process.run()
            process.waitUntilExit()

            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            let output = String(data: data, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines)
            return output?.isEmpty == false ? output : nil
        } catch {
            return nil
        }
    }

    /// Get a system property
    func getProperty(_ prop: String) -> String? {
        let result = runShell("getprop \(prop)")
        return result.isEmpty ? nil : result
    }

    /// Get list of installed packages
    func getPackages(includeSystem: Bool = false) -> [PackageInfo] {
        let cmd = includeSystem ? "pm list packages -f" : "pm list packages -f -3"
        let output = runShell(cmd)
        var packages = [PackageInfo]()

        for line in output.components(separatedBy: .newlines) {
            guard line.hasPrefix("package:") else { continue }
            let pkg = String(line.dropFirst(8))

            if let eqPos = pkg.lastIndex(of: "=") {
                let packageName = String(pkg[pkg.index(after: eqPos)...])
                let path = String(pkg[..<eqPos])
                let isSystem = path.hasPrefix("/system/") || path.hasPrefix("/product/")

                packages.append(PackageInfo(
                    packageName: packageName,
                    isSystem: isSystem,
                    isDisabled: false
                ))
            }
        }

        return packages
    }

    /// Get third-party packages only
    func getThirdPartyPackages() -> [PackageInfo] {
        return getPackages(includeSystem: false)
    }

    /// Uninstall a package (for current user)
    @discardableResult
    func uninstallPackage(_ package: String) -> Bool {
        let result = runADB(["shell", "pm", "uninstall", "-k", "--user", "0", package])
        return result.output.contains("Success")
    }

    /// Disable a package
    @discardableResult
    func disablePackage(_ package: String) -> Bool {
        let result = runADB(["shell", "pm", "disable-user", "--user", "0", package])
        return result.output.contains("disabled") || result.output.contains("new state")
    }

    /// Enable a package
    @discardableResult
    func enablePackage(_ package: String) -> Bool {
        let result = runADB(["shell", "pm", "enable", package])
        return result.output.contains("enabled") || result.output.contains("new state")
    }

    /// Reboot device
    func reboot() {
        runADB(["reboot"])
    }

    /// Reboot to recovery mode
    func rebootRecovery() {
        runADB(["reboot", "recovery"])
    }

    /// Reboot to bootloader
    func rebootBootloader() {
        runADB(["reboot", "bootloader"])
    }

    /// Reboot to download mode (Samsung)
    func rebootDownload() {
        runADB(["reboot", "download"])
    }

    /// Factory reset
    func factoryReset() {
        runShell("am broadcast -a android.intent.action.FACTORY_RESET")
    }
}
