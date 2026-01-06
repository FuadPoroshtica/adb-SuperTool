//
//  AndroidSuperToolApp.swift
//  AndroidSuperTool
//
//  Mobile Shop Edition - Native macOS App
//

import SwiftUI

@main
struct AndroidSuperToolApp: App {
    @StateObject private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .frame(minWidth: 900, minHeight: 600)
        }
        .windowStyle(.hiddenTitleBar)
        .commands {
            CommandGroup(replacing: .newItem) { }
            CommandGroup(after: .appSettings) {
                Button("Select ADB Directory...") {
                    appState.showADBPicker = true
                }
                .keyboardShortcut(",", modifiers: [.command, .shift])
            }
        }

        Settings {
            SettingsView()
                .environmentObject(appState)
        }
    }
}

/// Global application state
class AppState: ObservableObject {
    @Published var adbManager: ADBManager?
    @Published var selectedDevice: DeviceInfo?
    @Published var devices: [DeviceInfo] = []
    @Published var scanResults: [ScanResult] = []
    @Published var isScanning = false
    @Published var statusMessage = ""
    @Published var showADBPicker = false
    @Published var adbPath: String = ""

    init() {
        // Try to find ADB automatically
        if let path = ADBInstaller.findADB() {
            self.adbPath = path
            self.adbManager = ADBManager(adbPath: path)
            refreshDevices()
        }
    }

    func setADBPath(_ path: String) {
        self.adbPath = path
        self.adbManager = ADBManager(adbPath: path)
        UserDefaults.standard.set(path, forKey: "adbPath")
        refreshDevices()
    }

    func refreshDevices() {
        guard let adb = adbManager else { return }
        devices = adb.getDevices()
        if selectedDevice == nil, let first = devices.first {
            selectedDevice = first
        }
    }

    func selectDevice(_ device: DeviceInfo) {
        selectedDevice = device
        adbManager?.setDevice(device.serial)
        scanResults = []
    }

    func startScan() {
        guard let adb = adbManager, selectedDevice != nil else { return }
        isScanning = true
        statusMessage = "Scanning device..."

        DispatchQueue.global(qos: .userInitiated).async {
            let scanner = AppScanner(adb: adb)
            let results = scanner.scanDevice()

            DispatchQueue.main.async {
                self.scanResults = results
                self.isScanning = false
                self.statusMessage = "Found \(results.count) apps"
            }
        }
    }

    func removeSelected() {
        guard let adb = adbManager else { return }
        let selected = scanResults.filter { $0.isSelected }

        var removed = 0
        var failed = 0

        for result in selected {
            if adb.uninstallPackage(result.package.packageName) {
                removed += 1
            } else if adb.disablePackage(result.package.packageName) {
                removed += 1
            } else {
                failed += 1
            }
        }

        statusMessage = "Removed: \(removed), Failed: \(failed)"
        scanResults.removeAll { $0.isSelected }
    }
}
