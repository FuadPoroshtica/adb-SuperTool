# Android SuperTool - Mobile Shop Edition

A powerful, native GUI tool for managing Android phones using ADB. Built in Rust for maximum performance and a single executable with no dependencies. Designed specifically for mobile shops and repair technicians.

![Screenshot](screenshot.png)

## Features

- **Single Executable** - Just one 12MB binary, no Python or dependencies needed
- **Cross-Platform** - Runs on Windows, Linux, and macOS
- **Auto-Installs ADB** - Downloads Android Platform Tools automatically on first run
- **Threat Scanning** - Identifies malware, adware, and bloatware with a comprehensive database
- **One-Click Cleaning** - Remove all detected threats with a single click
- **Samsung Debloat** - Make entry-level Samsung phones minimal and fast
- **Recovery Tools** - Factory reset, recovery mode, firmware download links
- **Native GUI** - Fast, responsive interface built with egui

## Quick Start

### Download & Run

1. Download the appropriate binary for your OS from the [Releases](../../releases) page
2. Run the executable - that's it!

### Build from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/adb-SuperTool.git
cd adb-SuperTool

# Build release version
cargo build --release

# Run
./target/release/android-supertool
```

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
| CRITICAL | Magenta | Confirmed malware, spyware, banking trojans |
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

## Building

### Prerequisites

- [Rust](https://rustup.rs/) 1.70 or higher
- On Linux: `libgtk-3-dev libxcb-render0-dev libxcb-shape0-dev libxcb-xfixes0-dev`

### Build Commands

```bash
# Debug build
cargo build

# Release build (optimized, 12MB)
cargo build --release

# Run directly
cargo run --release
```

### Cross-Compilation

```bash
# For Windows (from Linux)
cargo build --release --target x86_64-pc-windows-gnu

# For macOS (requires cross-compilation toolchain)
cargo build --release --target x86_64-apple-darwin
```

## Project Structure

```
android-supertool/
├── Cargo.toml          # Rust dependencies
├── README.md           # This file
└── src/
    ├── main.rs         # Entry point & GUI window
    ├── app.rs          # Main application state & UI
    ├── adb.rs          # ADB command wrapper
    ├── database.rs     # Threat database
    ├── scanner.rs      # App scanner
    ├── debloater.rs    # Samsung debloat module
    ├── recovery.rs     # Recovery & firmware tools
    └── installer.rs    # ADB auto-installer
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

**ADB not installing:**
- Check your internet connection
- The tool downloads ADB from Google's servers

## For Mobile Shops

### Typical Workflow

1. Connect customer phone via USB
2. Enable USB debugging if not already enabled
3. Launch SuperTool and select the device
4. Go to **Scan Device** → Review threats → Remove Selected
5. For Samsung phones: Go to **Samsung Debloat** → Select level → Remove
6. Hand back a clean, fast phone to the customer

### Tips

- Keep the tool on a USB drive for quick access
- The aggressive debloat level is great for entry-level Samsung phones
- Always ask customer permission before removing apps
- Recovery tools require the phone to already have USB debugging enabled

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### Adding New Threats

Edit `src/database.rs` and add entries to the appropriate category:

```rust
("com.example.malware", "Malware Category", "Description of threat"),
```

## License

MIT License - See LICENSE file for details.

## Disclaimer

This tool is designed for authorized use by device owners and repair technicians. Always ensure you have proper authorization before modifying a device. The authors are not responsible for any damage caused by improper use of this tool.
