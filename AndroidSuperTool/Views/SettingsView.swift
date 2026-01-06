//
//  SettingsView.swift
//  AndroidSuperTool
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var appState: AppState
    @State private var isInstalling = false
    @State private var installProgress: Double = 0
    @State private var installMessage = ""

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                // ADB Settings
                GroupBox("ADB Configuration") {
                    VStack(alignment: .leading, spacing: 16) {
                        HStack {
                            Text("ADB Path:")
                                .fontWeight(.medium)

                            if appState.adbPath.isEmpty {
                                Text("Not configured")
                                    .foregroundColor(.red)
                            } else {
                                Text(appState.adbPath)
                                    .font(.system(.body, design: .monospaced))
                                    .foregroundColor(.secondary)
                            }

                            Spacer()

                            Button("Browse...") {
                                selectADBPath()
                            }
                        }

                        HStack {
                            Button("Auto-detect ADB") {
                                autoDetect()
                            }

                            Button("Download ADB") {
                                downloadADB()
                            }
                            .disabled(isInstalling)

                            if isInstalling {
                                ProgressView(value: installProgress)
                                    .frame(width: 100)
                                Text(installMessage)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }

                        if !appState.adbPath.isEmpty {
                            Button("Restart ADB Server") {
                                appState.adbManager?.restartServer()
                                appState.refreshDevices()
                            }
                        }
                    }
                    .padding()
                }

                // About
                GroupBox("About") {
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Image(systemName: "wrench.and.screwdriver")
                                .font(.largeTitle)
                                .foregroundColor(.accentColor)

                            VStack(alignment: .leading) {
                                Text("Android SuperTool")
                                    .font(.headline)
                                Text("Version 1.0.0 - Mobile Shop Edition")
                                    .foregroundColor(.secondary)
                            }
                        }

                        Divider()

                        Text("Features:")
                            .fontWeight(.medium)

                        VStack(alignment: .leading, spacing: 4) {
                            FeatureRow(text: "Scan for malware, adware, and bloatware")
                            FeatureRow(text: "Samsung device debloating")
                            FeatureRow(text: "Recovery and firmware tools")
                            FeatureRow(text: "Native macOS app - no dependencies")
                        }
                    }
                    .padding()
                }

                Spacer()
            }
            .padding()
        }
    }

    private func selectADBPath() {
        let panel = NSOpenPanel()
        panel.title = "Select ADB Executable"
        panel.canChooseFiles = true
        panel.canChooseDirectories = false
        panel.allowsMultipleSelection = false
        panel.directoryURL = URL(fileURLWithPath: "/usr/local/bin")

        if panel.runModal() == .OK, let url = panel.url {
            if ADBInstaller.validateADBPath(url.path) {
                appState.setADBPath(url.path)
            } else {
                // Show error
                let alert = NSAlert()
                alert.messageText = "Invalid ADB Path"
                alert.informativeText = "The selected file is not a valid ADB executable."
                alert.alertStyle = .warning
                alert.runModal()
            }
        }
    }

    private func autoDetect() {
        if let path = ADBInstaller.findADB() {
            appState.setADBPath(path)
        } else {
            let alert = NSAlert()
            alert.messageText = "ADB Not Found"
            alert.informativeText = "Could not find ADB. Please download it or select the path manually."
            alert.alertStyle = .informational
            alert.runModal()
        }
    }

    private func downloadADB() {
        isInstalling = true
        installProgress = 0
        installMessage = "Starting..."

        ADBInstaller.installADB(
            progress: { progress, message in
                DispatchQueue.main.async {
                    self.installProgress = progress
                    self.installMessage = message
                }
            },
            completion: { result in
                DispatchQueue.main.async {
                    self.isInstalling = false

                    switch result {
                    case .success(let path):
                        self.appState.setADBPath(path)
                    case .failure(let error):
                        let alert = NSAlert()
                        alert.messageText = "Download Failed"
                        alert.informativeText = error.localizedDescription
                        alert.alertStyle = .critical
                        alert.runModal()
                    }
                }
            }
        )
    }
}

struct FeatureRow: View {
    let text: String

    var body: some View {
        HStack {
            Image(systemName: "checkmark")
                .foregroundColor(.green)
            Text(text)
        }
        .font(.caption)
    }
}

/// ADB picker sheet that can be shown modally
struct ADBPickerSheet: View {
    @EnvironmentObject var appState: AppState
    @Environment(\.dismiss) var dismiss
    @State private var isInstalling = false
    @State private var installProgress: Double = 0
    @State private var installMessage = ""

    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "wrench.and.screwdriver")
                .font(.system(size: 48))
                .foregroundColor(.accentColor)

            Text("Configure ADB")
                .font(.title)
                .fontWeight(.bold)

            Text("Android SuperTool needs ADB to communicate with devices.")
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)

            VStack(spacing: 12) {
                Button(action: autoDetect) {
                    Label("Auto-detect ADB", systemImage: "magnifyingglass")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)

                Button(action: selectPath) {
                    Label("Select ADB Path...", systemImage: "folder")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)

                Button(action: downloadADB) {
                    Label("Download ADB", systemImage: "arrow.down.circle")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
                .disabled(isInstalling)
            }
            .frame(width: 250)

            if isInstalling {
                VStack {
                    ProgressView(value: installProgress)
                    Text(installMessage)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .frame(width: 250)
            }

            Button("Cancel") {
                dismiss()
            }
            .buttonStyle(.link)
        }
        .padding(40)
        .frame(width: 400)
    }

    private func autoDetect() {
        if let path = ADBInstaller.findADB() {
            appState.setADBPath(path)
            dismiss()
        }
    }

    private func selectPath() {
        let panel = NSOpenPanel()
        panel.title = "Select ADB Executable"
        panel.canChooseFiles = true
        panel.canChooseDirectories = false

        if panel.runModal() == .OK, let url = panel.url {
            if ADBInstaller.validateADBPath(url.path) {
                appState.setADBPath(url.path)
                dismiss()
            }
        }
    }

    private func downloadADB() {
        isInstalling = true

        ADBInstaller.installADB(
            progress: { progress, message in
                DispatchQueue.main.async {
                    self.installProgress = progress
                    self.installMessage = message
                }
            },
            completion: { result in
                DispatchQueue.main.async {
                    self.isInstalling = false

                    if case .success(let path) = result {
                        self.appState.setADBPath(path)
                        self.dismiss()
                    }
                }
            }
        )
    }
}

#Preview {
    SettingsView()
        .environmentObject(AppState())
}
