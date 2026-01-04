# Android SuperTool - Mobile Shop Edition

A powerful, easy-to-use TUI (Terminal User Interface) tool for cleaning Android phones using ADB. Designed specifically for mobile shops and repair technicians who need to quickly remove viruses, adware, and bloatware from customer devices.

```
╔═══════════════════════════════════════════════════════════════╗
║     _   _   _ ___  ___  ___ ___ ___    _____  ___  _          ║
║    /_\ | \ | |   \| _ \/ _ \_ _|   \  |_   _|/ _ \| |         ║
║   / _ \|  \| | |) |   / (_) | || |) |   | | | (_) | |__       ║
║  /_/ \_\_|\__|___/|_|_\\___/___|___/    |_|  \___/|____|      ║
║                                                               ║
║           SUPER TOOL - Mobile Shop Edition v1.0               ║
╚═══════════════════════════════════════════════════════════════╝
```

## Features

- **Auto-installs ADB** - Downloads Android Platform Tools automatically on first run
- **AI-Powered Scanning** - Identifies malware, adware, and bloatware using pattern matching and optional AI analysis
- **One-Click Cleaning** - Remove all detected threats with a single command
- **Popup Ad Catcher** - Identify which app is causing fullscreen popup ads
- **Comprehensive Database** - Contains hundreds of known malicious and bloatware packages
- **Easy TUI Interface** - No need to memorize ADB commands
- **Batch Operations** - Uninstall or disable multiple apps at once
- **Permission Management** - Revoke dangerous permissions from apps

## Quick Start

### Option 1: Run Setup Script (Recommended)
```bash
python setup.py
```
This will:
1. Create a virtual environment
2. Install all dependencies
3. Download ADB tools automatically

Then run:
```bash
# On Linux/Mac:
./venv/bin/python supertool.py

# On Windows:
.\venv\Scripts\python.exe supertool.py
```

### Option 2: Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run the tool (will download ADB automatically)
python supertool.py
```

## Usage

### Interactive Mode (TUI)
```bash
python supertool.py
```
This launches the full interactive interface with menus for all features.

### Command Line Mode
```bash
# Quick scan
python supertool.py --scan

# Scan and auto-remove all threats
python supertool.py --clean

# List all third-party apps
python supertool.py --list

# Catch popup ad source (run when popup is visible)
python supertool.py --catch

# Uninstall specific package
python supertool.py --uninstall com.example.malware

# Target specific device
python supertool.py --device SERIAL_NUMBER --scan
```

## Menu Options

| Key | Option | Description |
|-----|--------|-------------|
| 1 | Scan Device | Full scan for malware, adware, and bloatware |
| 2 | Quick Clean | One-click remove all detected threats |
| 3 | View Installed Apps | List all apps with risk assessment |
| 4 | Catch Popup Ad | Identify app causing popup ads |
| 5 | Device Info | View device information |
| 6 | Manual Uninstall | Manually remove specific apps |
| 7 | Disable System Apps | Disable bloatware without removing |
| 8 | Revoke Permissions | Remove dangerous permissions |
| 9 | ADB Shell | Run custom ADB commands |
| **D** | **Samsung Debloat** | **Make Samsung phone minimal & fast** |
| 0 | Settings | Configure tool settings |

## Risk Levels

| Level | Color | Description |
|-------|-------|-------------|
| CRITICAL | Red | Confirmed malware, spyware, ransomware |
| HIGH | Orange | Aggressive adware, data harvesters, trojans |
| MEDIUM | Yellow | Bloatware, intrusive ads, trackers |
| LOW | Cyan | Mild bloatware, unnecessary pre-installed apps |
| SAFE | Green | Known safe apps |

## Common Threat Categories

- **Fake Cleaners** - Apps that claim to "clean" or "boost" your phone
- **Fake Antivirus** - Fake security apps that show false virus warnings
- **Popup Ads** - Apps that display fullscreen ads over other apps
- **Battery Savers** - Fake battery optimization apps
- **Loan Sharks** - Predatory lending apps
- **Spyware/Stalkerware** - Apps that track user activity
- **Data Harvesters** - Apps that collect and sell user data

## Samsung Debloat (Entry-Level Devices)

Special feature for making Samsung phones minimal and lightweight. Optimized for entry-level devices like:

**Supported Models:**
- Galaxy A05, A05s, A06, A07
- Galaxy A14, A16, A17
- Galaxy A22, A23, A24
- Galaxy M05, M14, M15
- And other budget Samsung devices

### Debloat Levels

| Level | What it removes |
|-------|-----------------|
| **Light** | Microsoft apps, Facebook, Amazon, Netflix, AR Emoji, Games |
| **Medium** | Light + Bixby, Themes, Edge panels, Samsung Cloud, Pass |
| **Aggressive** | Maximum removal - Near stock Android experience |
| **Custom** | Choose specific categories |

### Categories Available for Removal

- **Microsoft Apps** - Office, Outlook, OneDrive, LinkedIn
- **Facebook/Meta** - Facebook, Instagram, Messenger
- **Bixby & AI** - Bixby Voice, Vision, Routines
- **AR Emoji** - AR Zone, Avatar Stickers, Live Stickers
- **Game Launcher** - Game Booster, Game Tools, Game Optimizing Service
- **Themes** - Galaxy Themes, Dynamic Wallpapers
- **Knox Security** - Enterprise security (not needed for consumers)
- **Samsung DeX** - Desktop mode (not available on entry-level)
- **Samsung Health** - Fitness tracking
- **Samsung Pay** - Mobile payments
- **Samsung Cloud** - Cloud backup
- **Edge Panels** - Edge screen shortcuts
- **Sharing Features** - Quick Share, Smart View
- **Google Bloat** - YouTube Music, Play Books, etc.
- **Amazon** - Shopping, Prime Video, Kindle
- **Netflix** - Netflix app
- **Other Bloat** - Booking.com, Flipboard, etc.

### Usage

1. Press **D** in the main menu
2. Select debloat level (Light/Medium/Aggressive/Custom)
3. Review packages to be removed
4. Confirm removal
5. Optionally reboot device

### Package Sources

Based on community research from:
- [khlam/debloat-samsung-android](https://github.com/khlam/debloat-samsung-android)
- [Universal Android Debloater](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation)
- [Achno/debloat-samsung-ADB-shizuku](https://github.com/Achno/debloat-samsung-ADB-shizuku)

## For Mobile Shops

### Typical Workflow

1. Connect customer phone via USB
2. Enable USB debugging on the phone (Settings > Developer Options > USB Debugging)
3. Accept the USB debugging authorization prompt on the phone
4. Run: `python supertool.py`
5. Select "Quick Clean" (option 2) for fast virus removal
6. Review results and confirm removal
7. Optionally run full scan (option 1) for deeper analysis

### Handling Common Issues

**"Permission denied" errors:**
- Some phones (especially Xiaomi/MIUI) restrict uninstalling certain apps
- Try using "Disable System Apps" option instead

**"Unknown package" errors:**
- The app may already be uninstalled
- Try with --user 0 option (the tool does this automatically)

**Device not detected:**
- Ensure USB debugging is enabled
- Try a different USB cable
- Restart ADB server (Settings > Restart ADB server)

## AI Analysis (Optional)

For enhanced threat detection, you can enable AI-powered analysis:

1. Get an API key from [Anthropic](https://console.anthropic.com/)
2. Set the environment variable:
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   ```
3. Enable AI analysis in Settings

## Requirements

- Python 3.8 or higher
- USB cable for device connection
- USB debugging enabled on target device

## Dependencies

- `rich` - Beautiful terminal formatting
- `requests` - HTTP library for downloading ADB
- `anthropic` - Optional, for AI analysis

## Project Structure

```
adb-SuperTool/
├── supertool.py          # Main entry point
├── setup.py              # Setup script
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── run.sh / run.bat      # Platform launchers
├── android-tools/        # ADB tools (auto-downloaded)
└── src/
    ├── __init__.py
    ├── installer.py      # ADB auto-installer
    ├── adb_manager.py    # ADB wrapper
    ├── database.py       # Threat database
    ├── debloater.py      # Samsung debloat module
    ├── scanner.py        # App scanner
    └── tui.py            # Terminal UI
```

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### Adding New Threats to Database

Edit `src/database.py` and add entries to the appropriate dictionary:

```python
"com.example.malware": AppInfo(
    "com.example.malware",
    "Malware App Name",
    RiskLevel.HIGH,
    AppCategory.ADWARE,
    "Description of the threat",
    True  # Safe to remove
),
```

## License

MIT License - See LICENSE file for details.

## Disclaimer

This tool is designed for authorized use by device owners and repair technicians. Always ensure you have proper authorization before modifying a device. The authors are not responsible for any damage caused by improper use of this tool.
