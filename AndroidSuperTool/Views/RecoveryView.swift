//
//  RecoveryView.swift
//  AndroidSuperTool
//

import SwiftUI

struct RecoveryView: View {
    @EnvironmentObject var appState: AppState
    @State private var manufacturer: Manufacturer = .other
    @State private var resetConfirmations = 0
    @State private var statusMessage = ""

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                // Manufacturer detection
                if let device = appState.selectedDevice {
                    HStack {
                        Image(systemName: "iphone")
                            .font(.title)
                        VStack(alignment: .leading) {
                            Text("Detected: \(manufacturer.rawValue)")
                                .font(.headline)
                            Text(device.displayName)
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding()
                    .background(Color(NSColor.controlBackgroundColor))
                    .cornerRadius(8)
                }

                // Reboot options
                GroupBox("Reboot Options") {
                    HStack(spacing: 16) {
                        RebootButton(title: "Reboot", icon: "arrow.clockwise", action: reboot)
                        RebootButton(title: "Recovery", icon: "wrench", action: rebootRecovery)
                        RebootButton(title: "Download", icon: "arrow.down.circle", action: rebootDownload)
                        RebootButton(title: "Bootloader", icon: "bolt", action: rebootBootloader)
                    }
                    .padding()
                }

                // Factory reset
                GroupBox("Factory Reset") {
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .foregroundColor(.red)
                            Text("WARNING: This will erase all data!")
                                .foregroundColor(.red)
                                .fontWeight(.semibold)
                        }

                        HStack {
                            Text("Confirmations: \(resetConfirmations)/3")

                            if resetConfirmations < 3 {
                                Button("Confirm") {
                                    resetConfirmations += 1
                                }
                                .buttonStyle(.borderedProminent)
                            } else {
                                Button("FACTORY RESET") {
                                    performFactoryReset()
                                }
                                .buttonStyle(.borderedProminent)
                                .tint(.red)
                            }

                            if resetConfirmations > 0 {
                                Button("Cancel") {
                                    resetConfirmations = 0
                                }
                            }
                        }
                    }
                    .padding()
                }

                // Firmware sources
                GroupBox("Firmware Sources") {
                    VStack(alignment: .leading, spacing: 12) {
                        ForEach(RecoveryManager.getFirmwareSources(for: manufacturer)) { source in
                            HStack {
                                VStack(alignment: .leading) {
                                    Text(source.name)
                                        .fontWeight(.medium)
                                    Text(source.description)
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }

                                Spacer()

                                Button("Open") {
                                    if let url = URL(string: source.url) {
                                        NSWorkspace.shared.open(url)
                                    }
                                }
                            }
                            Divider()
                        }
                    }
                    .padding()
                }

                // Flashing tool
                if let tool = RecoveryManager.getFlashingTool(for: manufacturer) {
                    GroupBox("Flashing Tool") {
                        VStack(alignment: .leading, spacing: 12) {
                            HStack {
                                VStack(alignment: .leading) {
                                    Text(tool.name)
                                        .font(.headline)
                                    Text(tool.description)
                                        .foregroundColor(.secondary)
                                }

                                Spacer()

                                Button("Download") {
                                    if let url = URL(string: tool.downloadURL) {
                                        NSWorkspace.shared.open(url)
                                    }
                                }
                            }

                            Divider()

                            ForEach(tool.instructions, id: \.self) { instruction in
                                Text(instruction)
                                    .font(.caption)
                            }
                        }
                        .padding()
                    }
                }

                // Status
                if !statusMessage.isEmpty {
                    Text(statusMessage)
                        .foregroundColor(.secondary)
                        .padding()
                }

                Spacer()
            }
            .padding()
        }
        .onAppear {
            detectManufacturer()
        }
    }

    private func detectManufacturer() {
        guard let adb = appState.adbManager else { return }
        let rm = RecoveryManager(adb: adb)
        manufacturer = rm.getManufacturer()
    }

    private func reboot() {
        appState.adbManager?.reboot()
        statusMessage = "Rebooting device..."
    }

    private func rebootRecovery() {
        appState.adbManager?.rebootRecovery()
        statusMessage = "Rebooting to recovery mode..."
    }

    private func rebootDownload() {
        appState.adbManager?.rebootDownload()
        statusMessage = "Rebooting to download mode..."
    }

    private func rebootBootloader() {
        appState.adbManager?.rebootBootloader()
        statusMessage = "Rebooting to bootloader..."
    }

    private func performFactoryReset() {
        guard let adb = appState.adbManager else { return }
        let rm = RecoveryManager(adb: adb)
        rm.factoryReset()
        statusMessage = "Factory reset initiated"
        resetConfirmations = 0
    }
}

struct RebootButton: View {
    let title: String
    let icon: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                Text(title)
                    .font(.caption)
            }
            .frame(width: 80, height: 60)
        }
        .buttonStyle(.bordered)
    }
}

#Preview {
    RecoveryView()
        .environmentObject(AppState())
}
