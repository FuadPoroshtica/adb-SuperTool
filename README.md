# Android SuperTool - Mobile Shop Edition

A powerful, native macOS app for managing Android phones using ADB. Built in Swift with SwiftUI for a beautiful, responsive interface. Designed specifically for mobile shops and repair technicians.

![Screenshot](screenshot.png)

## Features

- **Native macOS App** - Single .app bundle, no dependencies needed
- **SwiftUI Interface** - Modern, beautiful design that follows macOS guidelines
- **Auto-detects ADB** - Finds ADB from common locations or downloads it
- **Manual ADB Selection** - Choose your own ADB directory if needed
- **Threat Scanning** - Identifies malware, adware, and bloatware
- **One-Click Cleaning** - Remove all detected threats with a single click
- **Samsung Debloat** - Make entry-level Samsung phones minimal and fast
- **Recovery Tools** - Factory reset, recovery mode, firmware download links

## Requirements

- macOS 13.0 (Ventura) or later
- Xcode 15+ (for building from source)

## Quick Start

### Option 1: Download Pre-built App

1. Download `AndroidSuperTool.app` from the [Releases](../../releases) page
2. Move to Applications folder
3. Double-click to run

### Option 2: Build from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/adb-SuperTool.git
cd adb-SuperTool

# Open in Xcode
open AndroidSuperTool.xcodeproj

# Or build from command line
xcodebuild -project AndroidSuperTool.xcodeproj -scheme AndroidSuperTool -configuration Release build
```

The built `.app` will be in `build/Release/AndroidSuperTool.app`

## ADB Configuration

On first launch, the app will try to find ADB automatically in these locations:

1. Previously saved path (from Settings)
2. `~/Library/Application Support/AndroidSuperTool/platform-tools/adb`
3. `/usr/local/bin/adb`
4. `/opt/homebrew/bin/adb`
5. `~/Library/Android/sdk/platform-tools/adb`
6. Android Studio SDK location

**If ADB is not found:**

- Click **Settings** → **Browse...** to select your ADB executable
- Or click **Download ADB** to automatically download from Google

## Usage

1. Connect your Android device via USB
2. Enable USB debugging on the phone (Settings > Developer Options > USB Debugging)
3. Accept the USB debugging authorization prompt on the phone
4. Launch Android SuperTool
5. Your device should appear in the device dropdown

## Main Features

### Scan Device

Scans all installed apps and categorizes them by risk level:

| Level | Color | Description |
|-------|-------|-------------|
| CRITICAL | Purple | Confirmed malware, spyware, banking trojans |
| HIGH | Red | Aggressive adware, fake cleaners, data harvesters |
| MEDIUM | Orange | Bloatware, intrusive trackers |
| LOW | Blue | Optional apps, mild bloatware |
| SAFE | Green | Known safe apps |

Select apps and click "Remove Selected" to uninstall them.

### Samsung Debloat

Optimizes Samsung devices by removing bloatware. Perfect for entry-level phones like:
- Galaxy A05, A06, A07, A14, A16, A17
- Galaxy M14, M15

**Debloat Levels:**

| Level | Description |
|-------|-------------|
| Light | Only obvious bloatware - Facebook, Games |
| Medium | + Bixby, AR Emoji, Themes |
| Aggressive | Maximum removal - near stock Android |
| Custom | Select specific packages |

**Categories:**
- Bixby (Voice, Vision, Routines)
- AR Emoji & Stickers
- Game Launcher & Tools
- Samsung Themes
- Knox Security (enterprise features)
- Samsung Health & Pay
- Microsoft Apps
- Facebook Apps

### Recovery & Firmware

Tools for device recovery and firmware management:

**Reboot Options:**
- Normal reboot
- Recovery mode
- Download/Odin mode (Samsung)
- Bootloader/Fastboot mode

**Factory Reset:**
- Triple confirmation required to prevent accidents
- Complete data wipe

**Firmware Sources:**
- Samsung: SamFw, SamMobile, Frija
- Xiaomi: XiaomiFirmwareUpdater, MIUI Download
- OnePlus: Official support
- Google Pixel: Android Flash Tool
- Huawei, Motorola, Realme, OPPO, Vivo

## Project Structure

```
AndroidSuperTool/
├── AndroidSuperTool.xcodeproj/
├── AndroidSuperTool/
│   ├── AndroidSuperToolApp.swift    # App entry point
│   ├── Views/
│   │   ├── ContentView.swift        # Main navigation
│   │   ├── ScanView.swift           # Device scanner
│   │   ├── DebloatView.swift        # Samsung debloater
│   │   ├── RecoveryView.swift       # Recovery tools
│   │   └── SettingsView.swift       # ADB configuration
│   ├── Models/
│   │   ├── DeviceInfo.swift         # Device data model
│   │   └── ScanResult.swift         # Scan result model
│   ├── Managers/
│   │   ├── ADBManager.swift         # ADB command wrapper
│   │   ├── ADBInstaller.swift       # ADB auto-installer
│   │   ├── ThreatDatabase.swift     # Malware database
│   │   ├── AppScanner.swift         # App analyzer
│   │   ├── Debloater.swift          # Samsung debloater
│   │   └── RecoveryManager.swift    # Recovery tools
│   └── Resources/
│       ├── Info.plist
│       └── AndroidSuperTool.entitlements
└── README.md
```

## Common Issues

**Device not detected:**
- Ensure USB debugging is enabled
- Accept the USB debugging prompt on your phone
- Try a different USB cable
- Click the Refresh button

**"Permission denied" errors:**
- Some devices (especially Xiaomi) restrict uninstalling certain apps
- Try disabling the app instead of uninstalling

**ADB not found:**
- Go to Settings and click "Browse..." to select your ADB
- Or click "Download ADB" to install it automatically

## For Mobile Shops

### Typical Workflow

1. Connect customer phone via USB
2. Enable USB debugging if not already enabled
3. Launch SuperTool and select the device
4. Go to **Scan Device** → Review threats → Remove Selected
5. For Samsung phones: Go to **Samsung Debloat** → Select level → Remove
6. Hand back a clean, fast phone to the customer

### Tips

- Keep the app in your Dock for quick access
- The aggressive debloat level is great for entry-level Samsung phones
- Always ask customer permission before removing apps
- Recovery tools require the phone to already have USB debugging enabled

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### Adding New Threats

Edit `Managers/ThreatDatabase.swift` and add entries to the appropriate array:

```swift
("com.example.malware", "Category", "Description"),
```

## License

MIT License - See LICENSE file for details.

## Disclaimer

This tool is designed for authorized use by device owners and repair technicians. Always ensure you have proper authorization before modifying a device. The authors are not responsible for any damage caused by improper use of this tool.
