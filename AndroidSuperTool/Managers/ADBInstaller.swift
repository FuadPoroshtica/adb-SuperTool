//
//  ADBInstaller.swift
//  AndroidSuperTool
//

import Foundation

/// Handles ADB Platform Tools installation and discovery
class ADBInstaller {
    static let platformToolsURL = "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip"

    /// Get the application support directory for storing ADB
    static var appSupportDir: URL {
        let paths = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)
        let appDir = paths[0].appendingPathComponent("AndroidSuperTool")

        if !FileManager.default.fileExists(atPath: appDir.path) {
            try? FileManager.default.createDirectory(at: appDir, withIntermediateDirectories: true)
        }

        return appDir
    }

    /// Get the expected path for bundled ADB
    static var bundledADBPath: URL {
        appSupportDir.appendingPathComponent("platform-tools/adb")
    }

    /// Find ADB executable - checks multiple locations
    static func findADB() -> String? {
        // 1. Check user defaults for saved path
        if let savedPath = UserDefaults.standard.string(forKey: "adbPath"),
           FileManager.default.isExecutableFile(atPath: savedPath) {
            return savedPath
        }

        // 2. Check bundled location
        if FileManager.default.isExecutableFile(atPath: bundledADBPath.path) {
            return bundledADBPath.path
        }

        // 3. Check common locations
        let commonPaths = [
            "/usr/local/bin/adb",
            "/opt/homebrew/bin/adb",
            "/usr/bin/adb",
            NSHomeDirectory() + "/Library/Android/sdk/platform-tools/adb",
            NSHomeDirectory() + "/Android/Sdk/platform-tools/adb",
            "/Applications/Android Studio.app/Contents/sdk/platform-tools/adb"
        ]

        for path in commonPaths {
            if FileManager.default.isExecutableFile(atPath: path) {
                return path
            }
        }

        // 4. Check PATH
        if let pathEnv = ProcessInfo.processInfo.environment["PATH"] {
            let paths = pathEnv.components(separatedBy: ":")
            for path in paths {
                let adbPath = (path as NSString).appendingPathComponent("adb")
                if FileManager.default.isExecutableFile(atPath: adbPath) {
                    return adbPath
                }
            }
        }

        return nil
    }

    /// Check if ADB is installed in our app support directory
    static func isADBInstalled() -> Bool {
        FileManager.default.isExecutableFile(atPath: bundledADBPath.path)
    }

    /// Download and install ADB Platform Tools
    static func installADB(progress: @escaping (Double, String) -> Void, completion: @escaping (Result<String, Error>) -> Void) {
        progress(0.0, "Starting download...")

        guard let url = URL(string: platformToolsURL) else {
            completion(.failure(NSError(domain: "ADBInstaller", code: 1, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"])))
            return
        }

        let task = URLSession.shared.downloadTask(with: url) { tempURL, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }

            guard let tempURL = tempURL else {
                completion(.failure(NSError(domain: "ADBInstaller", code: 2, userInfo: [NSLocalizedDescriptionKey: "Download failed"])))
                return
            }

            progress(0.7, "Extracting...")

            do {
                // Move to app support and unzip
                let zipPath = appSupportDir.appendingPathComponent("platform-tools.zip")

                // Remove old zip if exists
                try? FileManager.default.removeItem(at: zipPath)
                try FileManager.default.moveItem(at: tempURL, to: zipPath)

                // Remove old platform-tools if exists
                let platformToolsDir = appSupportDir.appendingPathComponent("platform-tools")
                try? FileManager.default.removeItem(at: platformToolsDir)

                // Unzip using ditto (macOS native)
                let process = Process()
                process.executableURL = URL(fileURLWithPath: "/usr/bin/ditto")
                process.arguments = ["-xk", zipPath.path, appSupportDir.path]

                try process.run()
                process.waitUntilExit()

                // Clean up zip
                try? FileManager.default.removeItem(at: zipPath)

                // Make adb executable
                try FileManager.default.setAttributes([.posixPermissions: 0o755], ofItemAtPath: bundledADBPath.path)

                progress(1.0, "Installation complete!")
                completion(.success(bundledADBPath.path))

            } catch {
                completion(.failure(error))
            }
        }

        // Observe progress
        let observation = task.progress.observe(\.fractionCompleted) { progress, _ in
            DispatchQueue.main.async {
                let downloadProgress = progress.fractionCompleted * 0.7
                let mb = Double(task.countOfBytesReceived) / 1_000_000.0
                let totalMB = Double(task.countOfBytesExpectedToReceive) / 1_000_000.0
                let message = String(format: "Downloading... %.1f/%.1f MB", mb, totalMB)
                progress(downloadProgress, message)
            }
        }

        task.resume()

        // Keep observation alive
        DispatchQueue.main.asyncAfter(deadline: .now() + 300) {
            _ = observation
        }
    }

    /// Validate that an ADB path is valid
    static func validateADBPath(_ path: String) -> Bool {
        guard FileManager.default.isExecutableFile(atPath: path) else {
            return false
        }

        // Try to run adb version
        let process = Process()
        process.executableURL = URL(fileURLWithPath: path)
        process.arguments = ["version"]

        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = pipe

        do {
            try process.run()
            process.waitUntilExit()

            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            let output = String(data: data, encoding: .utf8) ?? ""

            return output.contains("Android Debug Bridge")
        } catch {
            return false
        }
    }
}
