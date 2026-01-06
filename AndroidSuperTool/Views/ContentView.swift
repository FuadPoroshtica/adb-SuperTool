//
//  ContentView.swift
//  AndroidSuperTool
//

import SwiftUI

/// Navigation tabs
enum NavigationTab: String, CaseIterable {
    case home = "Home"
    case scan = "Scan Device"
    case debloat = "Samsung Debloat"
    case recovery = "Recovery"
    case settings = "Settings"

    var icon: String {
        switch self {
        case .home: return "house"
        case .scan: return "magnifyingglass"
        case .debloat: return "iphone"
        case .recovery: return "wrench"
        case .settings: return "gear"
        }
    }
}

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @State private var selectedTab: NavigationTab = .home

    var body: some View {
        NavigationSplitView {
            // Sidebar
            List(NavigationTab.allCases, id: \.self, selection: $selectedTab) { tab in
                Label(tab.rawValue, systemImage: tab.icon)
                    .tag(tab)
            }
            .listStyle(.sidebar)
            .frame(minWidth: 180)
        } detail: {
            VStack(spacing: 0) {
                // Top bar with device selector
                TopBarView()

                Divider()

                // Main content
                switch selectedTab {
                case .home:
                    HomeView()
                case .scan:
                    ScanView()
                case .debloat:
                    DebloatView()
                case .recovery:
                    RecoveryView()
                case .settings:
                    SettingsView()
                }
            }
        }
        .sheet(isPresented: $appState.showADBPicker) {
            ADBPickerSheet()
        }
    }
}

/// Top bar with device selector
struct TopBarView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        HStack {
            Text("Android SuperTool")
                .font(.title2)
                .fontWeight(.semibold)

            Spacer()

            if !appState.devices.isEmpty {
                Picker("Device", selection: Binding(
                    get: { appState.selectedDevice },
                    set: { if let device = $0 { appState.selectDevice(device) } }
                )) {
                    ForEach(appState.devices) { device in
                        Text("\(device.displayName) (\(device.serial))")
                            .tag(device as DeviceInfo?)
                    }
                }
                .frame(width: 300)
            } else {
                Text("No devices connected")
                    .foregroundColor(.secondary)
            }

            Button(action: { appState.refreshDevices() }) {
                Image(systemName: "arrow.clockwise")
            }
            .help("Refresh devices")
        }
        .padding()
        .background(Color(NSColor.windowBackgroundColor))
    }
}

/// Home view with overview
struct HomeView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // Hero
                VStack(spacing: 8) {
                    Image(systemName: "wrench.and.screwdriver")
                        .font(.system(size: 60))
                        .foregroundColor(.accentColor)

                    Text("Android SuperTool")
                        .font(.largeTitle)
                        .fontWeight(.bold)

                    Text("Mobile Shop Edition")
                        .font(.title3)
                        .foregroundColor(.secondary)
                }
                .padding(.top, 40)

                // Feature cards
                HStack(spacing: 20) {
                    FeatureCard(icon: "magnifyingglass", title: "Scan Device", description: "Find malware & bloatware")
                    FeatureCard(icon: "iphone", title: "Samsung Debloat", description: "Optimize entry-level phones")
                    FeatureCard(icon: "wrench", title: "Recovery", description: "Reset & firmware tools")
                }
                .padding(.horizontal, 40)

                // Device info
                if let device = appState.selectedDevice {
                    GroupBox("Connected Device") {
                        VStack(alignment: .leading, spacing: 8) {
                            InfoRow(label: "Model", value: device.model)
                            InfoRow(label: "Manufacturer", value: device.manufacturer)
                            InfoRow(label: "Android", value: device.androidVersion)
                            InfoRow(label: "Serial", value: device.serial)
                        }
                        .padding()
                    }
                    .frame(maxWidth: 400)
                } else {
                    Text("Connect an Android device with USB debugging enabled")
                        .foregroundColor(.secondary)
                        .padding()
                }

                Spacer()
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(NSColor.textBackgroundColor))
    }
}

struct FeatureCard: View {
    let icon: String
    let title: String
    let description: String

    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 36))
                .foregroundColor(.accentColor)

            Text(title)
                .font(.headline)

            Text(description)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(width: 160, height: 140)
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }
}

struct InfoRow: View {
    let label: String
    let value: String

    var body: some View {
        HStack {
            Text(label + ":")
                .foregroundColor(.secondary)
            Text(value)
                .fontWeight(.medium)
            Spacer()
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(AppState())
}
