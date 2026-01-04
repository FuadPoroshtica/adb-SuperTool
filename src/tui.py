"""
Terminal User Interface for Android SuperTool
Beautiful, easy-to-use interface for mobile shop technicians
"""

import os
import sys
import time
from typing import List, Optional, Callable
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich.align import Align
    from rich.box import ROUNDED, DOUBLE, HEAVY
    from rich.style import Style
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .adb_manager import ADBManager, DeviceInfo, DeviceState
from .scanner import AppScanner, ScanResult, AppRiskAssessment, ScanStatus
from .database import RiskLevel, AppCategory, get_database
from .installer import ADBInstaller


class Colors:
    """Color scheme for the TUI."""
    CRITICAL = "bold red"
    HIGH = "red"
    MEDIUM = "yellow"
    LOW = "cyan"
    SAFE = "green"
    UNKNOWN = "dim white"
    HEADER = "bold blue"
    SUCCESS = "bold green"
    ERROR = "bold red"
    WARNING = "bold yellow"
    INFO = "bold cyan"
    ACCENT = "magenta"


class SuperToolTUI:
    """Main TUI application for Android SuperTool."""

    LOGO = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║     _   _   _ ___  ___  ___ ___ ___    _____  ___  _          ║
    ║    /_\ | \ | |   \| _ \/ _ \_ _|   \  |_   _|/ _ \| |         ║
    ║   / _ \|  \| | |) |   / (_) | || |) |   | | | (_) | |__       ║
    ║  /_/ \_\_|\__|___/|_|_\\___/___|___/    |_|  \___/|____|      ║
    ║                                                               ║
    ║           SUPER TOOL - Mobile Shop Edition v1.0               ║
    ║        Clean Phones Fast | Remove Viruses | Easy ADB          ║
    ╚═══════════════════════════════════════════════════════════════╝
    """

    MENU_OPTIONS = [
        ("1", "Scan Device", "Scan for malware, adware, and bloatware"),
        ("2", "Quick Clean", "One-click remove all detected threats"),
        ("3", "View Installed Apps", "List all apps with risk assessment"),
        ("4", "Catch Popup Ad", "Identify app causing popup ads"),
        ("5", "Device Info", "View device information"),
        ("6", "Manual Uninstall", "Manually remove specific apps"),
        ("7", "Disable System Apps", "Disable bloatware without removing"),
        ("8", "Revoke Permissions", "Remove dangerous permissions from apps"),
        ("9", "ADB Shell", "Run custom ADB commands"),
        ("0", "Settings", "Configure tool settings"),
        ("Q", "Quit", "Exit the application"),
    ]

    def __init__(self):
        """Initialize the TUI."""
        if not RICH_AVAILABLE:
            print("Error: 'rich' library is required. Install with: pip install rich")
            sys.exit(1)

        self.console = Console()
        self.adb: Optional[ADBManager] = None
        self.scanner: Optional[AppScanner] = None
        self.installer = ADBInstaller()
        self.current_device: Optional[DeviceInfo] = None
        self.last_scan: Optional[ScanResult] = None
        self.settings = {
            "include_system_apps": False,
            "use_ai_analysis": False,
            "auto_backup": False,
            "confirm_removals": True,
        }

    def run(self):
        """Main entry point - run the TUI application."""
        try:
            self._show_splash()
            self._ensure_adb_installed()
            self._initialize_adb()
            self._main_loop()
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Interrupted by user[/yellow]")
        finally:
            self.console.print("\n[green]Thank you for using Android SuperTool![/green]")

    def _show_splash(self):
        """Show the splash screen."""
        self.console.clear()
        self.console.print(Panel(
            Align.center(Text(self.LOGO, style="bold cyan")),
            border_style="cyan",
            box=DOUBLE
        ))
        self.console.print()

    def _ensure_adb_installed(self):
        """Ensure ADB tools are installed."""
        if self.installer.is_installed() or self.installer.is_system_adb_available():
            version = self.installer.get_version()
            self.console.print(f"[green]✓[/green] ADB ready (version {version})")
            return

        self.console.print("[yellow]ADB not found. Downloading Android Platform Tools...[/yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("Downloading...", total=100)

            def update_progress(status: str, downloaded: int, total: int):
                if total > 0:
                    pct = (downloaded / total) * 100
                    progress.update(task, completed=pct, description=status)

            success = self.installer.install(update_progress)

        if success:
            self.console.print("[green]✓[/green] ADB installed successfully!")
        else:
            self.console.print("[red]✗[/red] Failed to install ADB")
            sys.exit(1)

    def _initialize_adb(self):
        """Initialize ADB manager and connect to device."""
        self.adb = ADBManager(self.installer.get_adb_command())
        self.adb.start_server()
        self.scanner = AppScanner(self.adb)

        # Try to connect to a device
        self._select_device()

    def _select_device(self) -> bool:
        """Select a device to work with."""
        self.console.print("\n[bold]Searching for devices...[/bold]")

        devices = self.adb.get_devices()

        if not devices:
            self.console.print(Panel(
                "[yellow]No devices found![/yellow]\n\n"
                "Please:\n"
                "1. Connect an Android device via USB\n"
                "2. Enable USB Debugging in Developer Options\n"
                "3. Accept the USB debugging prompt on the device\n\n"
                "Press Enter to retry...",
                title="No Devices",
                border_style="yellow"
            ))
            input()
            return self._select_device()

        # Filter connected devices
        connected = [d for d in devices if d.state == DeviceState.DEVICE]
        unauthorized = [d for d in devices if d.state == DeviceState.UNAUTHORIZED]

        if unauthorized:
            self.console.print(
                f"[yellow]! {len(unauthorized)} device(s) need authorization. "
                "Check device screen for USB debugging prompt.[/yellow]"
            )

        if not connected:
            self.console.print("[red]No authorized devices found.[/red]")
            if Confirm.ask("Retry?"):
                return self._select_device()
            return False

        if len(connected) == 1:
            self.current_device = connected[0]
            self.adb.set_current_device(connected[0].serial)
            self.console.print(
                f"[green]✓[/green] Connected to: [bold]{connected[0].display_name}[/bold] "
                f"({connected[0].serial})"
            )
            return True

        # Multiple devices - let user choose
        self.console.print("\n[bold]Multiple devices found:[/bold]")
        table = Table(box=ROUNDED)
        table.add_column("#", style="cyan")
        table.add_column("Device", style="white")
        table.add_column("Serial", style="dim")
        table.add_column("Android", style="green")

        for i, device in enumerate(connected, 1):
            table.add_row(
                str(i),
                device.display_name,
                device.serial,
                device.android_version
            )

        self.console.print(table)

        choice = Prompt.ask(
            "Select device",
            choices=[str(i) for i in range(1, len(connected) + 1)],
            default="1"
        )

        idx = int(choice) - 1
        self.current_device = connected[idx]
        self.adb.set_current_device(connected[idx].serial)
        self.console.print(f"[green]✓[/green] Selected: [bold]{connected[idx].display_name}[/bold]")
        return True

    def _main_loop(self):
        """Main menu loop."""
        while True:
            self._show_main_menu()
            choice = Prompt.ask(
                "\n[bold cyan]Enter choice[/bold cyan]",
                choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "q", "Q"],
                default="1"
            ).upper()

            if choice == "Q":
                break
            elif choice == "1":
                self._scan_device()
            elif choice == "2":
                self._quick_clean()
            elif choice == "3":
                self._view_apps()
            elif choice == "4":
                self._catch_popup()
            elif choice == "5":
                self._show_device_info()
            elif choice == "6":
                self._manual_uninstall()
            elif choice == "7":
                self._disable_system_apps()
            elif choice == "8":
                self._revoke_permissions()
            elif choice == "9":
                self._adb_shell()
            elif choice == "0":
                self._settings_menu()

    def _show_main_menu(self):
        """Display the main menu."""
        self.console.clear()

        # Header with device info
        device_info = f"[bold]{self.current_device.display_name}[/bold]" if self.current_device else "[red]No device[/red]"

        header = Table.grid(padding=1)
        header.add_column(justify="left")
        header.add_column(justify="right")
        header.add_row(
            "[bold cyan]ANDROID SUPERTOOL[/bold cyan]",
            f"Device: {device_info}"
        )

        self.console.print(Panel(header, box=ROUNDED, border_style="cyan"))

        # Last scan summary if available
        if self.last_scan:
            summary = self.last_scan.get_summary()
            scan_panel = Table.grid(padding=1)
            scan_panel.add_row(
                f"[red]Critical: {summary['critical']}[/red]",
                f"[yellow]High: {summary['high']}[/yellow]",
                f"[cyan]Medium: {summary['medium']}[/cyan]",
                f"[green]Safe: {summary['safe']}[/green]"
            )
            self.console.print(Panel(
                scan_panel,
                title="Last Scan Results",
                border_style="yellow" if summary['critical'] + summary['high'] > 0 else "green"
            ))

        # Menu options
        menu_table = Table(box=ROUNDED, show_header=False, padding=(0, 2))
        menu_table.add_column("Key", style="bold cyan", width=4)
        menu_table.add_column("Option", style="bold white", width=25)
        menu_table.add_column("Description", style="dim")

        for key, option, desc in self.MENU_OPTIONS:
            menu_table.add_row(f"[{key}]", option, desc)

        self.console.print(menu_table)

    def _scan_device(self):
        """Perform a full device scan."""
        self.console.clear()
        self.console.print(Panel("[bold]DEVICE SCAN[/bold]", border_style="cyan"))

        if not self.current_device:
            self.console.print("[red]No device connected![/red]")
            input("Press Enter to continue...")
            return

        include_system = Confirm.ask(
            "Include system apps in scan?",
            default=self.settings["include_system_apps"]
        )

        self.console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("Initializing scan...", total=100)

            def update_progress(status: str, current: int, total: int):
                if total > 0:
                    pct = (current / total) * 100
                    progress.update(task, completed=pct, description=status)

            self.last_scan = self.scanner.scan_device(
                include_system=include_system,
                progress_callback=update_progress,
                use_ai=self.settings["use_ai_analysis"]
            )

        self._display_scan_results(self.last_scan)

    def _display_scan_results(self, result: ScanResult):
        """Display scan results in a nice format."""
        self.console.print()

        summary = result.get_summary()

        # Summary panel
        summary_table = Table.grid(padding=2)
        summary_table.add_column(justify="center")
        summary_table.add_column(justify="center")
        summary_table.add_column(justify="center")
        summary_table.add_column(justify="center")
        summary_table.add_column(justify="center")

        summary_table.add_row(
            f"[bold red]CRITICAL\n{summary['critical']}[/bold red]",
            f"[red]HIGH\n{summary['high']}[/red]",
            f"[yellow]MEDIUM\n{summary['medium']}[/yellow]",
            f"[cyan]LOW\n{summary['low']}[/cyan]",
            f"[green]SAFE\n{summary['safe']}[/green]"
        )

        self.console.print(Panel(
            summary_table,
            title=f"Scan Complete - {result.total_apps} apps scanned in {result.scan_time:.1f}s",
            border_style="cyan"
        ))

        # Display threats
        if result.critical_apps or result.high_risk_apps:
            self.console.print("\n[bold red]THREATS FOUND:[/bold red]\n")

            threats_table = Table(box=ROUNDED)
            threats_table.add_column("Risk", style="bold", width=10)
            threats_table.add_column("App Name", width=25)
            threats_table.add_column("Package", width=35)
            threats_table.add_column("Reason", width=40)

            for app in result.critical_apps:
                threats_table.add_row(
                    "[bold red]CRITICAL[/bold red]",
                    app.app_name[:24],
                    app.package_name[:34],
                    app.reasons[0][:39] if app.reasons else ""
                )

            for app in result.high_risk_apps:
                threats_table.add_row(
                    "[red]HIGH[/red]",
                    app.app_name[:24],
                    app.package_name[:34],
                    app.reasons[0][:39] if app.reasons else ""
                )

            self.console.print(threats_table)

            self.console.print(
                f"\n[yellow]Found {len(result.removable_threats)} removable threats.[/yellow]"
            )

            if Confirm.ask("\nRemove all threats now?"):
                self._remove_threats(result.removable_threats)
        else:
            self.console.print("\n[bold green]No critical threats found![/bold green]")

        if result.medium_risk_apps:
            self.console.print(
                f"\n[yellow]Found {len(result.medium_risk_apps)} medium-risk apps (bloatware).[/yellow]"
            )
            if Confirm.ask("View medium-risk apps?"):
                self._display_app_list(result.medium_risk_apps, "Medium Risk Apps")

        input("\nPress Enter to continue...")

    def _display_app_list(self, apps: List[AppRiskAssessment], title: str):
        """Display a list of apps in a table."""
        table = Table(title=title, box=ROUNDED)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Risk", width=10)
        table.add_column("App Name", width=20)
        table.add_column("Package", width=35)
        table.add_column("Category", width=15)

        for i, app in enumerate(apps, 1):
            risk_style = {
                RiskLevel.CRITICAL: "bold red",
                RiskLevel.HIGH: "red",
                RiskLevel.MEDIUM: "yellow",
                RiskLevel.LOW: "cyan",
                RiskLevel.SAFE: "green",
            }.get(app.risk_level, "white")

            table.add_row(
                str(i),
                f"[{risk_style}]{app.risk_level.value.upper()}[/{risk_style}]",
                app.app_name[:19],
                app.package_name[:34],
                app.category.value[:14]
            )

        self.console.print(table)

    def _remove_threats(self, threats: List[AppRiskAssessment]):
        """Remove detected threat apps."""
        self.console.print("\n[bold]Removing threats...[/bold]\n")

        removed = 0
        failed = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("Removing...", total=len(threats))

            for app in threats:
                progress.update(task, description=f"Removing {app.app_name}...")

                # Try uninstall for user 0 first (most common)
                success, message = self.adb.uninstall_package(app.package_name, user_id=0)

                if not success:
                    # Try without user ID
                    success, message = self.adb.uninstall_package(app.package_name)

                if not success:
                    # Try disable as fallback
                    success, message = self.adb.disable_package(app.package_name)

                if success:
                    removed += 1
                    self.console.print(f"  [green]✓[/green] {app.package_name}")
                else:
                    failed += 1
                    self.console.print(f"  [red]✗[/red] {app.package_name}: {message}")

                progress.advance(task)

        self.console.print(f"\n[green]Removed: {removed}[/green] | [red]Failed: {failed}[/red]")

    def _quick_clean(self):
        """Quick clean - scan and remove all threats in one go."""
        self.console.clear()
        self.console.print(Panel("[bold]QUICK CLEAN[/bold]", border_style="green"))

        if not self.current_device:
            self.console.print("[red]No device connected![/red]")
            input("Press Enter to continue...")
            return

        self.console.print("Performing quick scan...")

        # Quick scan using database only
        risky_apps = self.scanner.quick_scan()

        if not risky_apps:
            self.console.print("\n[bold green]No known threats found![/bold green]")
            self.console.print("Device appears clean. Run full scan for deeper analysis.")
            input("\nPress Enter to continue...")
            return

        self.console.print(f"\n[yellow]Found {len(risky_apps)} threats:[/yellow]\n")

        for app in risky_apps:
            risk_style = "red" if app.risk_level == RiskLevel.CRITICAL else "yellow"
            self.console.print(
                f"  [{risk_style}]●[/{risk_style}] {app.app_name} ({app.package_name})"
            )

        self.console.print()

        if Confirm.ask("[bold]Remove all threats now?[/bold]", default=True):
            self._remove_threats(risky_apps)

        input("\nPress Enter to continue...")

    def _view_apps(self):
        """View all installed apps with risk assessment."""
        self.console.clear()
        self.console.print(Panel("[bold]INSTALLED APPS[/bold]", border_style="cyan"))

        if not self.current_device:
            self.console.print("[red]No device connected![/red]")
            input("Press Enter to continue...")
            return

        app_type = Prompt.ask(
            "View which apps?",
            choices=["1", "2", "3"],
            default="1"
        )

        self.console.print("\nLoading apps...")

        if app_type == "1":
            packages = self.adb.get_third_party_packages()
            title = "Third-Party Apps"
        elif app_type == "2":
            packages = self.adb.get_system_packages()
            title = "System Apps"
        else:
            packages = self.adb.get_packages(include_system=True)
            title = "All Apps"

        # Assess each app
        apps = []
        db = get_database()

        for pkg in packages:
            risk = db.get_risk_level(pkg)
            info = db.lookup(pkg)

            apps.append(AppRiskAssessment(
                package_name=pkg,
                app_name=info.name if info else pkg.split('.')[-1].title(),
                risk_level=risk,
                category=info.category if info else AppCategory.UNKNOWN,
                risk_score=0,
                reasons=[info.description] if info else [],
                is_system="system" in app_type.lower(),
                is_removable=True,
                recommendation=""
            ))

        # Sort by risk
        apps.sort(key=lambda x: {
            RiskLevel.CRITICAL: 0,
            RiskLevel.HIGH: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.LOW: 3,
            RiskLevel.UNKNOWN: 4,
            RiskLevel.SAFE: 5,
        }.get(x.risk_level, 6))

        self._display_app_list(apps[:50], f"{title} ({len(apps)} total, showing first 50)")

        input("\nPress Enter to continue...")

    def _catch_popup(self):
        """Identify the app causing popup ads."""
        self.console.clear()
        self.console.print(Panel(
            "[bold]CATCH POPUP AD SOURCE[/bold]\n\n"
            "This tool identifies which app is causing popup ads.\n\n"
            "[yellow]Instructions:[/yellow]\n"
            "1. Wait for a popup ad to appear on the device\n"
            "2. With the popup visible, press Enter here\n"
            "3. The tool will identify the source app\n",
            border_style="yellow"
        ))

        input("Press Enter when popup ad is visible...")

        self.console.print("\n[cyan]Identifying popup source...[/cyan]")

        foreground = self.adb.get_foreground_package()

        if foreground:
            self.console.print(f"\n[bold]Foreground app: [yellow]{foreground}[/yellow][/bold]")

            # Check if it's a known threat
            db = get_database()
            info = db.lookup(foreground)

            if info:
                self.console.print(f"[red]KNOWN THREAT: {info.name}[/red]")
                self.console.print(f"Category: {info.category.value}")
                self.console.print(f"Risk: {info.risk.value}")

                if Confirm.ask("\nRemove this app now?"):
                    success, msg = self.adb.uninstall_package(foreground, user_id=0)
                    if success:
                        self.console.print("[green]✓ App removed![/green]")
                    else:
                        self.console.print(f"[red]✗ Failed: {msg}[/red]")
            else:
                self.console.print("[yellow]App not in threat database.[/yellow]")
                self.console.print("This may still be the source of popups.")

                if Confirm.ask("\nBlock overlay permission for this app?"):
                    success, msg = self.adb.revoke_overlay_permission(foreground)
                    if success:
                        self.console.print("[green]✓ Overlay permission blocked![/green]")
                    else:
                        self.console.print(f"[yellow]Note: {msg}[/yellow]")

                if Confirm.ask("Remove this app?"):
                    success, msg = self.adb.uninstall_package(foreground, user_id=0)
                    if success:
                        self.console.print("[green]✓ App removed![/green]")
                    else:
                        self.console.print(f"[red]✗ Failed: {msg}[/red]")
        else:
            self.console.print("[yellow]Could not identify foreground app.[/yellow]")
            self.console.print("Try again when the popup is fully visible.")

        input("\nPress Enter to continue...")

    def _show_device_info(self):
        """Show detailed device information."""
        self.console.clear()

        if not self.current_device:
            self.console.print("[red]No device connected![/red]")
            input("Press Enter to continue...")
            return

        device = self.current_device

        info_table = Table(box=ROUNDED, show_header=False)
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="white")

        info_table.add_row("Manufacturer", device.manufacturer)
        info_table.add_row("Model", device.model)
        info_table.add_row("Android Version", device.android_version)
        info_table.add_row("SDK Version", str(device.sdk_version))
        info_table.add_row("Serial", device.serial)
        info_table.add_row("State", device.state.value)

        # Get additional info
        battery = self.adb.get_battery_info()
        if battery:
            level = battery.get("level", "Unknown")
            info_table.add_row("Battery Level", f"{level}%")

        storage = self.adb.get_storage_info()
        if storage:
            info_table.add_row(
                "Storage",
                f"{storage.get('used', '?')} / {storage.get('total', '?')} ({storage.get('use_percent', '?')} used)"
            )

        # Package counts
        third_party = len(self.adb.get_third_party_packages())
        info_table.add_row("Third-Party Apps", str(third_party))

        self.console.print(Panel(info_table, title="Device Information", border_style="cyan"))

        input("\nPress Enter to continue...")

    def _manual_uninstall(self):
        """Manually uninstall a specific package."""
        self.console.clear()
        self.console.print(Panel("[bold]MANUAL UNINSTALL[/bold]", border_style="red"))

        package = Prompt.ask("Enter package name to uninstall (or 'list' to search)")

        if package.lower() == 'list':
            search = Prompt.ask("Search for package containing")
            packages = self.adb.get_packages(include_system=True)
            matches = [p for p in packages if search.lower() in p.lower()]

            if matches:
                self.console.print(f"\nFound {len(matches)} matches:")
                for p in matches[:20]:
                    self.console.print(f"  {p}")
                if len(matches) > 20:
                    self.console.print(f"  ... and {len(matches) - 20} more")

                package = Prompt.ask("\nEnter package name to uninstall")
            else:
                self.console.print("[yellow]No matches found.[/yellow]")
                input("\nPress Enter to continue...")
                return

        if not package:
            return

        self.console.print(f"\n[yellow]Attempting to uninstall: {package}[/yellow]")

        if self.settings["confirm_removals"]:
            if not Confirm.ask("Confirm uninstall?"):
                return

        # Try multiple methods
        success, msg = self.adb.uninstall_package(package, user_id=0)

        if not success:
            self.console.print(f"[yellow]First attempt failed: {msg}[/yellow]")
            self.console.print("Trying without user ID...")
            success, msg = self.adb.uninstall_package(package)

        if not success:
            self.console.print(f"[yellow]Second attempt failed: {msg}[/yellow]")
            if Confirm.ask("Try disabling instead?"):
                success, msg = self.adb.disable_package(package)

        if success:
            self.console.print(f"[green]✓ Success: {msg}[/green]")
        else:
            self.console.print(f"[red]✗ Failed: {msg}[/red]")

        input("\nPress Enter to continue...")

    def _disable_system_apps(self):
        """Disable system bloatware."""
        self.console.clear()
        self.console.print(Panel("[bold]DISABLE SYSTEM APPS[/bold]", border_style="yellow"))

        self.console.print("Common bloatware that can be safely disabled:\n")

        db = get_database()
        bloatware = []

        # Get system packages and check which are bloatware
        system_packages = self.adb.get_system_packages()

        for pkg in system_packages:
            info = db.lookup(pkg)
            if info and info.risk in [RiskLevel.MEDIUM, RiskLevel.LOW]:
                bloatware.append(info)

        if not bloatware:
            self.console.print("[green]No known bloatware found in system apps![/green]")
            input("\nPress Enter to continue...")
            return

        table = Table(box=ROUNDED)
        table.add_column("#", width=4)
        table.add_column("App Name", width=25)
        table.add_column("Package", width=40)

        for i, app in enumerate(bloatware[:20], 1):
            table.add_row(str(i), app.name, app.package)

        self.console.print(table)

        choice = Prompt.ask(
            "\nEnter number to disable, 'all' for all, or 'back' to cancel",
            default="back"
        )

        if choice.lower() == 'back':
            return

        if choice.lower() == 'all':
            to_disable = [app.package for app in bloatware]
        else:
            try:
                idx = int(choice) - 1
                to_disable = [bloatware[idx].package]
            except (ValueError, IndexError):
                self.console.print("[red]Invalid choice[/red]")
                input("\nPress Enter to continue...")
                return

        for pkg in to_disable:
            success, msg = self.adb.disable_package(pkg)
            if success:
                self.console.print(f"[green]✓[/green] Disabled: {pkg}")
            else:
                self.console.print(f"[red]✗[/red] Failed: {pkg} - {msg}")

        input("\nPress Enter to continue...")

    def _revoke_permissions(self):
        """Revoke dangerous permissions from apps."""
        self.console.clear()
        self.console.print(Panel("[bold]REVOKE PERMISSIONS[/bold]", border_style="yellow"))

        package = Prompt.ask("Enter package name")

        if not package:
            return

        # Get package info
        info = self.adb.get_package_info(package)

        if not info:
            self.console.print("[red]Package not found![/red]")
            input("\nPress Enter to continue...")
            return

        if not info.permissions:
            self.console.print("[yellow]No permissions found for this package.[/yellow]")
            input("\nPress Enter to continue...")
            return

        dangerous = [p for p in info.permissions if 'permission' in p.lower()]

        self.console.print(f"\nPermissions for [bold]{package}[/bold]:\n")

        table = Table(box=ROUNDED)
        table.add_column("#", width=4)
        table.add_column("Permission", width=50)

        for i, perm in enumerate(dangerous[:20], 1):
            short_perm = perm.replace("android.permission.", "")
            table.add_row(str(i), short_perm)

        self.console.print(table)

        self.console.print("\n[bold]Quick actions:[/bold]")
        self.console.print("  [cyan]O[/cyan] - Block overlay/popup permission")
        self.console.print("  [cyan]#[/cyan] - Revoke specific permission by number")
        self.console.print("  [cyan]B[/cyan] - Back")

        choice = Prompt.ask("\nChoice", default="B").upper()

        if choice == 'O':
            success, msg = self.adb.revoke_overlay_permission(package)
            self.console.print(f"[green]✓[/green] {msg}" if success else f"[red]✗[/red] {msg}")
        elif choice == 'B':
            return
        else:
            try:
                idx = int(choice) - 1
                perm = dangerous[idx]
                success, msg = self.adb.revoke_permission(package, perm)
                self.console.print(f"[green]✓[/green] {msg}" if success else f"[red]✗[/red] {msg}")
            except (ValueError, IndexError):
                self.console.print("[red]Invalid choice[/red]")

        input("\nPress Enter to continue...")

    def _adb_shell(self):
        """Run custom ADB shell commands."""
        self.console.clear()
        self.console.print(Panel(
            "[bold]ADB SHELL[/bold]\n\n"
            "Run custom ADB commands. Type 'exit' to return to menu.\n"
            "[yellow]Be careful with system commands![/yellow]",
            border_style="cyan"
        ))

        while True:
            cmd = Prompt.ask("\n[cyan]adb shell>[/cyan]")

            if cmd.lower() in ['exit', 'quit', 'q']:
                break

            if not cmd:
                continue

            ret, stdout, stderr = self.adb.shell(cmd)

            if stdout:
                self.console.print(stdout)
            if stderr:
                self.console.print(f"[red]{stderr}[/red]")
            if ret != 0:
                self.console.print(f"[yellow]Exit code: {ret}[/yellow]")

    def _settings_menu(self):
        """Settings menu."""
        while True:
            self.console.clear()
            self.console.print(Panel("[bold]SETTINGS[/bold]", border_style="cyan"))

            table = Table(box=ROUNDED, show_header=False)
            table.add_column("Key", width=4)
            table.add_column("Setting", width=30)
            table.add_column("Value", width=20)

            settings_list = [
                ("1", "Include system apps in scans", self.settings["include_system_apps"]),
                ("2", "Use AI analysis", self.settings["use_ai_analysis"]),
                ("3", "Confirm before removals", self.settings["confirm_removals"]),
                ("4", "Switch device", "..."),
                ("5", "Restart ADB server", "..."),
            ]

            for key, name, value in settings_list:
                if isinstance(value, bool):
                    value_str = "[green]ON[/green]" if value else "[red]OFF[/red]"
                else:
                    value_str = str(value)
                table.add_row(f"[{key}]", name, value_str)

            self.console.print(table)
            self.console.print("\n[B] Back to main menu")

            choice = Prompt.ask("\nChoice", default="B").upper()

            if choice == 'B':
                break
            elif choice == '1':
                self.settings["include_system_apps"] = not self.settings["include_system_apps"]
            elif choice == '2':
                self.settings["use_ai_analysis"] = not self.settings["use_ai_analysis"]
                if self.settings["use_ai_analysis"]:
                    if not os.environ.get("ANTHROPIC_API_KEY"):
                        self.console.print("[yellow]Note: Set ANTHROPIC_API_KEY for AI analysis[/yellow]")
                        input("Press Enter...")
            elif choice == '3':
                self.settings["confirm_removals"] = not self.settings["confirm_removals"]
            elif choice == '4':
                self._select_device()
            elif choice == '5':
                self.console.print("Restarting ADB server...")
                self.adb.restart_server()
                time.sleep(2)
                self._select_device()


def main():
    """Main entry point."""
    app = SuperToolTUI()
    app.run()


if __name__ == "__main__":
    main()
