#!/usr/bin/env python3
"""
Android SuperTool - Mobile Shop Edition
A comprehensive ADB-based Android cleaning and management tool

Usage:
    python supertool.py          # Launch TUI
    python supertool.py --scan   # Quick scan only
    python supertool.py --clean  # Scan and clean
    python supertool.py --help   # Show help
"""

import sys
import os
import argparse

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []

    try:
        import rich
    except ImportError:
        missing.append("rich")

    try:
        import requests
    except ImportError:
        missing.append("requests")

    if missing:
        print("Missing required dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nInstall with:")
        print(f"  pip install {' '.join(missing)}")
        print("\nOr install all dependencies:")
        print("  pip install -r requirements.txt")
        return False

    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Android SuperTool - Mobile Shop Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python supertool.py              Launch interactive TUI
  python supertool.py --scan       Quick scan connected device
  python supertool.py --clean      Scan and remove all threats
  python supertool.py --list       List all installed packages
  python supertool.py --catch      Identify popup ad source

For mobile shop use:
  1. Connect customer phone via USB
  2. Enable USB debugging on phone
  3. Run: python supertool.py
  4. Select 'Quick Clean' for fast virus removal
        """
    )

    parser.add_argument(
        "--scan", "-s",
        action="store_true",
        help="Quick scan and show results"
    )

    parser.add_argument(
        "--clean", "-c",
        action="store_true",
        help="Scan and remove all threats automatically"
    )

    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all third-party packages"
    )

    parser.add_argument(
        "--catch",
        action="store_true",
        help="Identify current foreground app (for catching popup ads)"
    )

    parser.add_argument(
        "--uninstall", "-u",
        metavar="PACKAGE",
        help="Uninstall a specific package"
    )

    parser.add_argument(
        "--device", "-d",
        metavar="SERIAL",
        help="Target specific device by serial number"
    )

    parser.add_argument(
        "--install-adb",
        action="store_true",
        help="Download and install ADB tools"
    )

    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show version information"
    )

    args = parser.parse_args()

    # Version info
    if args.version:
        from src import __version__
        print(f"Android SuperTool v{__version__}")
        print("Mobile Shop Edition")
        return 0

    # Check dependencies
    if not check_dependencies():
        return 1

    # Install ADB only
    if args.install_adb:
        from src.installer import ADBInstaller
        installer = ADBInstaller()

        if installer.is_installed():
            print(f"ADB already installed at: {installer.adb_path}")
            version = installer.get_version()
            if version:
                print(f"Version: {version}")
        else:
            print("Downloading Android Platform Tools...")

            def progress(status, downloaded, total):
                if total > 0:
                    pct = (downloaded / total) * 100
                    print(f"\r{status} {pct:.1f}%", end="", flush=True)

            if installer.install(progress):
                print("\nADB installed successfully!")
            else:
                print("\nFailed to install ADB")
                return 1

        return 0

    # Command-line operations
    if args.scan or args.clean or args.list or args.catch or args.uninstall:
        return run_cli_mode(args)

    # Default: Launch TUI
    from src.tui import SuperToolTUI
    app = SuperToolTUI()
    app.run()
    return 0


def run_cli_mode(args):
    """Run in command-line mode (non-interactive)."""
    from rich.console import Console
    from rich.table import Table

    from src.adb_manager import ADBManager
    from src.scanner import AppScanner
    from src.installer import ensure_adb_installed
    from src.database import get_database

    console = Console()

    # Initialize ADB
    try:
        adb_path = ensure_adb_installed()
    except RuntimeError as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1

    adb = ADBManager(adb_path)
    adb.start_server()

    # Get devices
    devices = adb.get_devices()
    connected = [d for d in devices if d.state.value == "device"]

    if not connected:
        console.print("[red]No connected devices found![/red]")
        console.print("Please connect a device with USB debugging enabled.")
        return 1

    # Select device
    if args.device:
        device = next((d for d in connected if d.serial == args.device), None)
        if not device:
            console.print(f"[red]Device {args.device} not found![/red]")
            return 1
    else:
        device = connected[0]

    adb.set_current_device(device.serial)
    console.print(f"[green]Using device:[/green] {device.display_name} ({device.serial})")

    # Execute command
    if args.list:
        packages = adb.get_third_party_packages()
        console.print(f"\n[bold]Third-party packages ({len(packages)}):[/bold]")
        for pkg in sorted(packages):
            console.print(f"  {pkg}")
        return 0

    if args.catch:
        foreground = adb.get_foreground_package()
        if foreground:
            console.print(f"\n[bold]Foreground app:[/bold] {foreground}")

            db = get_database()
            info = db.lookup(foreground)
            if info:
                console.print(f"[red]KNOWN THREAT:[/red] {info.name}")
                console.print(f"Risk: {info.risk.value}")
                console.print(f"Category: {info.category.value}")
        else:
            console.print("[yellow]Could not identify foreground app[/yellow]")
        return 0

    if args.uninstall:
        console.print(f"Uninstalling {args.uninstall}...")
        success, msg = adb.uninstall_package(args.uninstall, user_id=0)
        if success:
            console.print(f"[green]Success![/green]")
        else:
            console.print(f"[red]Failed: {msg}[/red]")
        return 0 if success else 1

    if args.scan or args.clean:
        scanner = AppScanner(adb)

        console.print("\n[bold]Scanning device...[/bold]")
        risky_apps = scanner.quick_scan()

        if not risky_apps:
            console.print("[green]No threats found! Device appears clean.[/green]")
            return 0

        # Display results
        table = Table(title=f"Found {len(risky_apps)} Threats")
        table.add_column("Risk", style="bold")
        table.add_column("App")
        table.add_column("Package")

        for app in risky_apps:
            risk_style = "red" if app.risk_level.value == "critical" else "yellow"
            table.add_row(
                f"[{risk_style}]{app.risk_level.value.upper()}[/{risk_style}]",
                app.app_name,
                app.package_name
            )

        console.print(table)

        if args.clean:
            console.print("\n[bold]Removing threats...[/bold]")
            removed = 0
            for app in risky_apps:
                success, _ = adb.uninstall_package(app.package_name, user_id=0)
                if success:
                    console.print(f"[green]✓[/green] Removed: {app.package_name}")
                    removed += 1
                else:
                    console.print(f"[red]✗[/red] Failed: {app.package_name}")

            console.print(f"\n[bold]Removed {removed}/{len(risky_apps)} threats[/bold]")

        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
