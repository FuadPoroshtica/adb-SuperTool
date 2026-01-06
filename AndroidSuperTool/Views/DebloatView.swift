//
//  DebloatView.swift
//  AndroidSuperTool
//

import SwiftUI

struct DebloatView: View {
    @EnvironmentObject var appState: AppState
    @State private var debloatLevel: DebloatLevel = .medium
    @State private var packages: [DebloatPackage] = []
    @State private var isLoading = false
    @State private var statusMessage = ""
    @State private var isEntryLevel = false

    var selectedCount: Int {
        packages.filter { $0.isSelected }.count
    }

    var body: some View {
        VStack(spacing: 0) {
            // Toolbar
            HStack {
                if isEntryLevel {
                    Label("Entry-level Samsung detected!", systemImage: "checkmark.circle.fill")
                        .foregroundColor(.green)
                }

                Spacer()

                Picker("Debloat Level", selection: $debloatLevel) {
                    ForEach(DebloatLevel.allCases, id: \.self) { level in
                        Text(level.rawValue).tag(level)
                    }
                }
                .frame(width: 150)
                .onChange(of: debloatLevel) { _, _ in
                    loadPackages()
                }

                Button(action: { loadPackages() }) {
                    Label("Refresh", systemImage: "arrow.clockwise")
                }

                Button(action: selectAll) {
                    Label("Select All", systemImage: "checkmark.square")
                }

                Button(action: deselectAll) {
                    Label("Deselect All", systemImage: "square")
                }

                Button(action: removeSelected) {
                    Label("Remove Selected", systemImage: "trash")
                }
                .disabled(selectedCount == 0)
            }
            .padding()

            // Level description
            Text(debloatLevel.description)
                .font(.caption)
                .foregroundColor(.secondary)
                .padding(.horizontal)
                .padding(.bottom, 8)

            Divider()

            // Package list grouped by category
            if isLoading {
                VStack {
                    Spacer()
                    ProgressView()
                    Text("Loading packages...")
                        .foregroundColor(.secondary)
                    Spacer()
                }
            } else if packages.isEmpty {
                VStack {
                    Spacer()
                    Image(systemName: "checkmark.circle")
                        .font(.system(size: 48))
                        .foregroundColor(.green)
                    Text("No bloatware packages found")
                        .foregroundColor(.secondary)
                    Spacer()
                }
            } else {
                List {
                    ForEach(DebloatCategory.allCases, id: \.self) { category in
                        let categoryPackages = packages.filter { $0.category == category }
                        if !categoryPackages.isEmpty {
                            Section(header: Text(category.rawValue)) {
                                ForEach(categoryPackages) { pkg in
                                    DebloatPackageRow(package: pkg)
                                }
                            }
                        }
                    }
                }
            }

            // Status bar
            HStack {
                Text("\(selectedCount) packages selected")
                Spacer()
                Text(statusMessage)
                    .foregroundColor(.secondary)
            }
            .padding(8)
            .background(Color(NSColor.controlBackgroundColor))
        }
        .onAppear {
            loadPackages()
        }
    }

    private func loadPackages() {
        guard let adb = appState.adbManager else { return }

        isLoading = true
        statusMessage = "Loading..."

        DispatchQueue.global(qos: .userInitiated).async {
            let debloater = Debloater(adb: adb)
            let isEntry = debloater.isEntryLevelSamsung()
            let allPackages = Debloater.getPackagesForLevel(debloatLevel)
            let installed = debloater.getInstalledPackages(allPackages)

            DispatchQueue.main.async {
                self.isEntryLevel = isEntry
                self.packages = installed
                self.isLoading = false
                self.statusMessage = "Found \(installed.count) removable packages"
            }
        }
    }

    private func selectAll() {
        for pkg in packages {
            pkg.isSelected = true
        }
    }

    private func deselectAll() {
        for pkg in packages {
            pkg.isSelected = false
        }
    }

    private func removeSelected() {
        guard let adb = appState.adbManager else { return }

        let selected = packages.filter { $0.isSelected }
        if selected.isEmpty { return }

        statusMessage = "Removing \(selected.count) packages..."

        DispatchQueue.global(qos: .userInitiated).async {
            let debloater = Debloater(adb: adb)
            var success = 0
            var failed = 0

            for pkg in selected {
                if debloater.debloatPackage(pkg.packageName) {
                    success += 1
                } else {
                    failed += 1
                }
            }

            DispatchQueue.main.async {
                self.statusMessage = "Removed: \(success), Failed: \(failed)"
                // Remove successful ones from list
                self.packages.removeAll { $0.isSelected }
            }
        }
    }
}

struct DebloatPackageRow: View {
    @ObservedObject var package: DebloatPackage

    var body: some View {
        HStack {
            Toggle("", isOn: $package.isSelected)
                .labelsHidden()

            VStack(alignment: .leading, spacing: 2) {
                Text(package.name)
                    .fontWeight(.medium)
                Text(package.packageName)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Spacer()

            Text(package.description)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding(.vertical, 2)
    }
}

#Preview {
    DebloatView()
        .environmentObject(AppState())
}
