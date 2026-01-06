//
//  ScanView.swift
//  AndroidSuperTool
//

import SwiftUI

struct ScanView: View {
    @EnvironmentObject var appState: AppState
    @State private var showSafeApps = false
    @State private var selectAll = false

    var filteredResults: [ScanResult] {
        if showSafeApps {
            return appState.scanResults
        } else {
            return appState.scanResults.filter { $0.riskLevel != .safe }
        }
    }

    var summary: ThreatSummary {
        ThreatSummary.from(appState.scanResults)
    }

    var body: some View {
        VStack(spacing: 0) {
            // Toolbar
            HStack {
                Button(action: { appState.startScan() }) {
                    Label("Scan Device", systemImage: "magnifyingglass")
                }
                .disabled(appState.isScanning || appState.selectedDevice == nil)

                if appState.isScanning {
                    ProgressView()
                        .scaleEffect(0.7)
                        .padding(.leading, 8)
                }

                Spacer()

                if !appState.scanResults.isEmpty {
                    Button(action: { appState.removeSelected() }) {
                        Label("Remove Selected", systemImage: "trash")
                    }
                    .disabled(appState.scanResults.filter { $0.isSelected }.isEmpty)

                    Toggle("Show Safe Apps", isOn: $showSafeApps)
                        .toggleStyle(.checkbox)
                        .padding(.leading)
                }
            }
            .padding()

            // Summary bar
            if !appState.scanResults.isEmpty {
                HStack(spacing: 20) {
                    Text("Total: \(summary.total)")
                    SummaryBadge(label: "Critical", count: summary.critical, color: .purple)
                    SummaryBadge(label: "High", count: summary.high, color: .red)
                    SummaryBadge(label: "Medium", count: summary.medium, color: .orange)
                    SummaryBadge(label: "Low", count: summary.low, color: .blue)
                    Spacer()
                }
                .padding(.horizontal)
                .padding(.bottom, 8)
            }

            Divider()

            // Results table
            if appState.scanResults.isEmpty {
                VStack {
                    Spacer()
                    if appState.isScanning {
                        VStack(spacing: 16) {
                            ProgressView()
                            Text("Scanning device...")
                                .foregroundColor(.secondary)
                        }
                    } else {
                        VStack(spacing: 16) {
                            Image(systemName: "magnifyingglass")
                                .font(.system(size: 48))
                                .foregroundColor(.secondary)
                            Text("Click 'Scan Device' to start")
                                .foregroundColor(.secondary)
                        }
                    }
                    Spacer()
                }
            } else {
                Table(filteredResults) {
                    TableColumn("") { result in
                        Toggle("", isOn: Binding(
                            get: { result.isSelected },
                            set: { result.isSelected = $0 }
                        ))
                        .labelsHidden()
                    }
                    .width(30)

                    TableColumn("Package") { result in
                        Text(result.package.packageName)
                            .font(.system(.body, design: .monospaced))
                    }
                    .width(min: 200, ideal: 300)

                    TableColumn("Risk") { result in
                        HStack {
                            Image(systemName: result.riskLevel.icon)
                                .foregroundColor(result.riskLevel.color)
                            Text(result.riskLevel.displayName)
                                .foregroundColor(result.riskLevel.color)
                                .fontWeight(.semibold)
                        }
                    }
                    .width(100)

                    TableColumn("Category") { result in
                        Text(result.category)
                    }
                    .width(100)

                    TableColumn("Description") { result in
                        Text(result.description)
                            .foregroundColor(.secondary)
                    }
                }
            }

            // Status bar
            HStack {
                Text(appState.statusMessage)
                    .foregroundColor(.secondary)
                Spacer()
            }
            .padding(8)
            .background(Color(NSColor.controlBackgroundColor))
        }
    }
}

struct SummaryBadge: View {
    let label: String
    let count: Int
    let color: Color

    var body: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(color)
                .frame(width: 8, height: 8)
            Text("\(label): \(count)")
                .font(.caption)
        }
    }
}

#Preview {
    ScanView()
        .environmentObject(AppState())
}
