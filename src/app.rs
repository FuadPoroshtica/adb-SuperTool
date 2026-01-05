//! Main application state and GUI

use crate::adb::{AdbManager, DeviceInfo};
use crate::debloater::{DebloatLevel, DebloatPackage, Debloater};
use crate::installer::{self, Installer};
use crate::recovery::{Manufacturer, RecoveryManager};
use crate::scanner::{AppScanner, ScanResult, ThreatSummary};
use eframe::egui;
use std::sync::{Arc, Mutex};
use std::thread;

/// Current view/tab in the application
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum View {
    Home,
    Scan,
    Debloat,
    Recovery,
    Settings,
}

/// Status of the ADB installation
#[derive(Debug, Clone)]
pub enum AdbStatus {
    Checking,
    NotInstalled,
    Installing(f32, String),
    Ready(String),
    Error(String),
}

/// Status of ongoing operations
#[derive(Debug, Clone)]
pub enum OperationStatus {
    Idle,
    Running(String),
    Success(String),
    Error(String),
}

/// Main application state
pub struct SuperToolApp {
    // Core components
    adb: Option<Arc<AdbManager>>,
    adb_status: Arc<Mutex<AdbStatus>>,

    // Current state
    current_view: View,
    devices: Vec<DeviceInfo>,
    selected_device: Option<usize>,
    operation_status: OperationStatus,

    // Scan state
    scan_results: Vec<ScanResult>,
    scan_summary: Option<ThreatSummary>,
    show_safe_apps: bool,
    scanning: Arc<Mutex<bool>>,

    // Debloat state
    debloat_level: DebloatLevel,
    debloat_packages: Vec<DebloatPackage>,
    is_entry_level: bool,

    // Recovery state
    manufacturer: Option<Manufacturer>,
    reset_confirmations: u8,

    // UI state
    status_message: String,
    show_confirmation_dialog: bool,
    confirmation_action: Option<Box<dyn FnOnce(&mut Self) + Send>>,
}

impl Default for SuperToolApp {
    fn default() -> Self {
        Self {
            adb: None,
            adb_status: Arc::new(Mutex::new(AdbStatus::Checking)),
            current_view: View::Home,
            devices: Vec::new(),
            selected_device: None,
            operation_status: OperationStatus::Idle,
            scan_results: Vec::new(),
            scan_summary: None,
            show_safe_apps: false,
            scanning: Arc::new(Mutex::new(false)),
            debloat_level: DebloatLevel::Medium,
            debloat_packages: Vec::new(),
            is_entry_level: false,
            manufacturer: None,
            reset_confirmations: 0,
            status_message: String::new(),
            show_confirmation_dialog: false,
            confirmation_action: None,
        }
    }
}

impl SuperToolApp {
    pub fn new(cc: &eframe::CreationContext<'_>) -> Self {
        // Configure fonts and style
        let mut style = (*cc.egui_ctx.style()).clone();
        style.spacing.item_spacing = egui::vec2(10.0, 8.0);
        style.spacing.button_padding = egui::vec2(12.0, 6.0);
        cc.egui_ctx.set_style(style);

        let mut app = Self::default();
        app.check_adb_installation();
        app
    }

    /// Check if ADB is installed and install if needed
    fn check_adb_installation(&mut self) {
        let status = Arc::clone(&self.adb_status);

        thread::spawn(move || {
            // Check if ADB already exists
            if let Some(adb_path) = installer::get_best_adb_path() {
                *status.lock().unwrap() = AdbStatus::Ready(adb_path.to_string_lossy().to_string());
                return;
            }

            // Need to install
            *status.lock().unwrap() = AdbStatus::NotInstalled;
        });
    }

    /// Start ADB installation
    fn start_adb_installation(&mut self) {
        let status = Arc::clone(&self.adb_status);

        thread::spawn(move || {
            *status.lock().unwrap() = AdbStatus::Installing(0.0, "Starting...".to_string());

            let status_clone = Arc::clone(&status);
            let installer = Installer::new().with_progress(move |progress, message| {
                *status_clone.lock().unwrap() =
                    AdbStatus::Installing(progress, message.to_string());
            });

            match installer.install() {
                Ok(path) => {
                    *status.lock().unwrap() = AdbStatus::Ready(path.to_string_lossy().to_string());
                }
                Err(e) => {
                    *status.lock().unwrap() = AdbStatus::Error(e.to_string());
                }
            }
        });
    }

    /// Initialize ADB manager after installation
    fn init_adb(&mut self) {
        if let AdbStatus::Ready(path) = &*self.adb_status.lock().unwrap() {
            let adb = Arc::new(AdbManager::new(path.into()));
            if let Err(e) = adb.start_server() {
                self.status_message = format!("Warning: Could not start ADB server: {}", e);
            }
            self.adb = Some(adb);
        }
    }

    /// Refresh the list of connected devices
    fn refresh_devices(&mut self) {
        if let Some(ref adb) = self.adb {
            match adb.get_devices() {
                Ok(devices) => {
                    self.devices = devices;
                    if self.selected_device.is_none() && !self.devices.is_empty() {
                        self.selected_device = Some(0);
                        if let Some(device) = self.devices.first() {
                            adb.set_device(&device.serial);
                        }
                    }
                }
                Err(e) => {
                    self.status_message = format!("Error getting devices: {}", e);
                }
            }
        }
    }

    /// Select a device
    fn select_device(&mut self, index: usize) {
        if index < self.devices.len() {
            self.selected_device = Some(index);
            if let Some(ref adb) = self.adb {
                adb.set_device(&self.devices[index].serial);
            }
            // Clear scan results when switching devices
            self.scan_results.clear();
            self.scan_summary = None;
        }
    }

    /// Start scanning the device
    fn start_scan(&mut self) {
        if let Some(ref adb) = self.adb {
            let adb_clone = Arc::clone(adb);
            let scanning = Arc::clone(&self.scanning);

            *scanning.lock().unwrap() = true;
            self.operation_status = OperationStatus::Running("Scanning device...".to_string());

            // We'll do a simple blocking scan for now
            let scanner = AppScanner::new(adb_clone);
            match scanner.scan_device() {
                Ok(results) => {
                    self.scan_summary = Some(AppScanner::get_threat_summary(&results));
                    self.scan_results = results;
                    self.operation_status = OperationStatus::Success("Scan complete!".to_string());
                }
                Err(e) => {
                    self.operation_status =
                        OperationStatus::Error(format!("Scan failed: {}", e));
                }
            }

            *scanning.lock().unwrap() = false;
        }
    }

    /// Remove selected threats
    fn remove_selected(&mut self) {
        if let Some(ref adb) = self.adb {
            let selected: Vec<_> = self
                .scan_results
                .iter()
                .filter(|r| r.is_selected)
                .map(|r| r.package.package_name.clone())
                .collect();

            if selected.is_empty() {
                self.status_message = "No apps selected".to_string();
                return;
            }

            let mut removed = 0;
            let mut failed = 0;

            for pkg in &selected {
                if adb.uninstall_package(pkg).unwrap_or(false) {
                    removed += 1;
                } else if adb.disable_package(pkg).unwrap_or(false) {
                    removed += 1;
                } else {
                    failed += 1;
                }
            }

            self.status_message = format!("Removed: {}, Failed: {}", removed, failed);

            // Remove from results
            self.scan_results.retain(|r| !r.is_selected);
            self.scan_summary = Some(AppScanner::get_threat_summary(&self.scan_results));
        }
    }

    /// Load debloat packages
    fn load_debloat_packages(&mut self) {
        if let Some(ref adb) = self.adb {
            let debloater = Debloater::new(Arc::clone(adb));
            self.is_entry_level = debloater.is_entry_level_samsung();

            let all_packages = Debloater::get_packages_for_level(self.debloat_level);
            match debloater.get_installed_packages(&all_packages) {
                Ok(packages) => self.debloat_packages = packages,
                Err(e) => self.status_message = format!("Error: {}", e),
            }
        }
    }

    /// Run debloat on selected packages
    fn run_debloat(&mut self) {
        if let Some(ref adb) = self.adb {
            let debloater = Debloater::new(Arc::clone(adb));
            let selected: Vec<_> = self
                .debloat_packages
                .iter()
                .filter(|p| p.is_selected)
                .map(|p| p.package.clone())
                .collect();

            if selected.is_empty() {
                self.status_message = "No packages selected".to_string();
                return;
            }

            let results = debloater.debloat_packages(&selected);
            let success = results.iter().filter(|(_, s)| *s).count();
            let failed = results.len() - success;

            self.status_message = format!("Removed: {}, Failed: {}", success, failed);

            // Remove successful ones from list
            let successful_pkgs: std::collections::HashSet<_> = results
                .iter()
                .filter(|(_, s)| *s)
                .map(|(p, _)| p.as_str())
                .collect();
            self.debloat_packages
                .retain(|p| !successful_pkgs.contains(p.package.as_str()));
        }
    }
}

impl eframe::App for SuperToolApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // Check ADB status and init if ready
        let should_init = matches!(&*self.adb_status.lock().unwrap(), AdbStatus::Ready(_))
            && self.adb.is_none();
        if should_init {
            self.init_adb();
            self.refresh_devices();
        }

        // Top panel with title and device selector
        egui::TopBottomPanel::top("top_panel").show(ctx, |ui| {
            ui.add_space(5.0);
            ui.horizontal(|ui| {
                ui.heading("🔧 Android SuperTool");
                ui.add_space(20.0);

                // Device selector
                if !self.devices.is_empty() {
                    ui.label("Device:");
                    let selected_name = self
                        .selected_device
                        .and_then(|i| self.devices.get(i))
                        .map(|d| format!("{} ({})", d.model, d.serial))
                        .unwrap_or_else(|| "Select...".to_string());

                    // Collect device info to avoid borrow issues
                    let device_labels: Vec<_> = self.devices.iter()
                        .map(|d| format!("{} {} - {} (Android {})",
                            d.manufacturer, d.model, d.serial, d.android_version))
                        .collect();
                    let current_selection = self.selected_device;
                    let mut new_selection = None;

                    egui::ComboBox::from_id_salt("device_selector")
                        .selected_text(&selected_name)
                        .show_ui(ui, |ui| {
                            for (i, label) in device_labels.iter().enumerate() {
                                if ui.selectable_label(current_selection == Some(i), label).clicked() {
                                    new_selection = Some(i);
                                }
                            }
                        });

                    if let Some(idx) = new_selection {
                        self.select_device(idx);
                    }
                }

                if ui.button("🔄 Refresh").clicked() {
                    self.refresh_devices();
                }
            });
            ui.add_space(5.0);
        });

        // Left panel with navigation
        egui::SidePanel::left("nav_panel")
            .resizable(false)
            .default_width(150.0)
            .show(ctx, |ui| {
                ui.add_space(10.0);
                ui.vertical(|ui| {
                    if ui
                        .selectable_label(self.current_view == View::Home, "🏠 Home")
                        .clicked()
                    {
                        self.current_view = View::Home;
                    }
                    if ui
                        .selectable_label(self.current_view == View::Scan, "🔍 Scan Device")
                        .clicked()
                    {
                        self.current_view = View::Scan;
                    }
                    if ui
                        .selectable_label(self.current_view == View::Debloat, "📱 Samsung Debloat")
                        .clicked()
                    {
                        self.current_view = View::Debloat;
                        self.load_debloat_packages();
                    }
                    if ui
                        .selectable_label(self.current_view == View::Recovery, "🔧 Recovery")
                        .clicked()
                    {
                        self.current_view = View::Recovery;
                        if let Some(ref adb) = self.adb {
                            let rm = RecoveryManager::new(Arc::clone(adb));
                            self.manufacturer = rm.get_manufacturer().ok();
                        }
                    }
                    ui.add_space(20.0);
                    if ui
                        .selectable_label(self.current_view == View::Settings, "⚙️ Settings")
                        .clicked()
                    {
                        self.current_view = View::Settings;
                    }
                });
            });

        // Status bar at bottom
        egui::TopBottomPanel::bottom("status_panel").show(ctx, |ui| {
            ui.horizontal(|ui| {
                // ADB status indicator - clone to avoid borrow issues
                let adb_status = self.adb_status.lock().unwrap().clone();
                let mut should_install = false;

                match &adb_status {
                    AdbStatus::Checking => {
                        ui.spinner();
                        ui.label("Checking ADB...");
                    }
                    AdbStatus::NotInstalled => {
                        ui.colored_label(egui::Color32::YELLOW, "⚠ ADB not installed");
                        if ui.button("Install").clicked() {
                            should_install = true;
                        }
                    }
                    AdbStatus::Installing(progress, msg) => {
                        ui.add(egui::ProgressBar::new(*progress).text(msg));
                    }
                    AdbStatus::Ready(_) => {
                        ui.colored_label(egui::Color32::GREEN, "✓ ADB Ready");
                    }
                    AdbStatus::Error(e) => {
                        ui.colored_label(egui::Color32::RED, format!("✗ Error: {}", e));
                    }
                }

                if should_install {
                    self.start_adb_installation();
                }

                ui.separator();

                // Device count
                ui.label(format!("{} device(s) connected", self.devices.len()));

                ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                    if !self.status_message.is_empty() {
                        ui.label(&self.status_message);
                    }
                });
            });
        });

        // Main content panel
        egui::CentralPanel::default().show(ctx, |ui| {
            match self.current_view {
                View::Home => self.render_home(ui),
                View::Scan => self.render_scan(ui),
                View::Debloat => self.render_debloat(ui),
                View::Recovery => self.render_recovery(ui),
                View::Settings => self.render_settings(ui),
            }
        });

        // Request repaint for animations
        if matches!(&*self.adb_status.lock().unwrap(), AdbStatus::Installing(_, _))
            || *self.scanning.lock().unwrap()
        {
            ctx.request_repaint();
        }
    }
}

// Render methods for each view
impl SuperToolApp {
    fn render_home(&mut self, ui: &mut egui::Ui) {
        ui.heading("Welcome to Android SuperTool");
        ui.add_space(10.0);
        ui.label("A complete solution for managing Android devices in your mobile shop.");
        ui.add_space(20.0);

        ui.horizontal(|ui| {
            ui.group(|ui| {
                ui.set_min_size(egui::vec2(200.0, 100.0));
                ui.vertical_centered(|ui| {
                    ui.heading("🔍");
                    ui.label("Scan Device");
                    ui.label("Find malware & bloatware");
                });
            });

            ui.group(|ui| {
                ui.set_min_size(egui::vec2(200.0, 100.0));
                ui.vertical_centered(|ui| {
                    ui.heading("📱");
                    ui.label("Samsung Debloat");
                    ui.label("Optimize entry-level phones");
                });
            });

            ui.group(|ui| {
                ui.set_min_size(egui::vec2(200.0, 100.0));
                ui.vertical_centered(|ui| {
                    ui.heading("🔧");
                    ui.label("Recovery");
                    ui.label("Reset & firmware tools");
                });
            });
        });

        ui.add_space(20.0);

        if self.devices.is_empty() {
            ui.colored_label(
                egui::Color32::YELLOW,
                "No devices connected. Connect a device with USB debugging enabled.",
            );
        } else if let Some(idx) = self.selected_device {
            if let Some(device) = self.devices.get(idx) {
                ui.group(|ui| {
                    ui.heading("Connected Device");
                    ui.horizontal(|ui| {
                        ui.label("Model:");
                        ui.strong(&device.model);
                    });
                    ui.horizontal(|ui| {
                        ui.label("Manufacturer:");
                        ui.strong(&device.manufacturer);
                    });
                    ui.horizontal(|ui| {
                        ui.label("Android:");
                        ui.strong(&device.android_version);
                    });
                    ui.horizontal(|ui| {
                        ui.label("Serial:");
                        ui.code(&device.serial);
                    });
                });
            }
        }
    }

    fn render_scan(&mut self, ui: &mut egui::Ui) {
        ui.heading("Device Scanner");
        ui.add_space(10.0);

        ui.horizontal(|ui| {
            if ui.button("🔍 Start Scan").clicked() && self.adb.is_some() {
                self.start_scan();
            }

            if !self.scan_results.is_empty() {
                if ui.button("🗑 Remove Selected").clicked() {
                    self.remove_selected();
                }

                ui.checkbox(&mut self.show_safe_apps, "Show safe apps");
            }
        });

        ui.add_space(10.0);

        // Summary
        if let Some(ref summary) = self.scan_summary {
            ui.horizontal(|ui| {
                ui.label(format!("Total: {}", summary.total));
                ui.colored_label(egui::Color32::from_rgb(255, 0, 100), format!("Critical: {}", summary.critical));
                ui.colored_label(egui::Color32::RED, format!("High: {}", summary.high));
                ui.colored_label(egui::Color32::YELLOW, format!("Medium: {}", summary.medium));
                ui.colored_label(egui::Color32::LIGHT_BLUE, format!("Low: {}", summary.low));
            });
        }

        ui.add_space(10.0);

        // Results table
        egui::ScrollArea::vertical().show(ui, |ui| {
            egui::Grid::new("scan_results")
                .num_columns(5)
                .striped(true)
                .min_col_width(100.0)
                .show(ui, |ui| {
                    ui.strong("");
                    ui.strong("Package");
                    ui.strong("Risk");
                    ui.strong("Category");
                    ui.strong("Description");
                    ui.end_row();

                    for result in self.scan_results.iter_mut() {
                        if !self.show_safe_apps && result.risk_level == crate::database::RiskLevel::Safe {
                            continue;
                        }

                        ui.checkbox(&mut result.is_selected, "");
                        ui.label(&result.package.package_name);
                        ui.colored_label(result.risk_color(), result.risk_level.as_str());
                        ui.label(&result.category);
                        ui.label(&result.description);
                        ui.end_row();
                    }
                });
        });
    }

    fn render_debloat(&mut self, ui: &mut egui::Ui) {
        ui.heading("Samsung Debloat");
        ui.add_space(10.0);

        if self.is_entry_level {
            ui.colored_label(
                egui::Color32::GREEN,
                "✓ Entry-level Samsung device detected!",
            );
        }

        ui.horizontal(|ui| {
            ui.label("Debloat Level:");
            egui::ComboBox::from_id_salt("debloat_level")
                .selected_text(format!("{:?}", self.debloat_level))
                .show_ui(ui, |ui| {
                    for level in [
                        DebloatLevel::Light,
                        DebloatLevel::Medium,
                        DebloatLevel::Aggressive,
                        DebloatLevel::Custom,
                    ] {
                        if ui
                            .selectable_label(self.debloat_level == level, format!("{:?}", level))
                            .clicked()
                        {
                            self.debloat_level = level;
                            self.load_debloat_packages();
                        }
                    }
                });

            if ui.button("🔄 Refresh").clicked() {
                self.load_debloat_packages();
            }

            if ui.button("☑ Select All").clicked() {
                for pkg in &mut self.debloat_packages {
                    pkg.is_selected = true;
                }
            }

            if ui.button("☐ Deselect All").clicked() {
                for pkg in &mut self.debloat_packages {
                    pkg.is_selected = false;
                }
            }

            if ui.button("🗑 Remove Selected").clicked() {
                self.run_debloat();
            }
        });

        ui.label(self.debloat_level.description());
        ui.add_space(10.0);

        egui::ScrollArea::vertical().show(ui, |ui| {
            let mut current_category = None;

            for pkg in &mut self.debloat_packages {
                if current_category != Some(pkg.category) {
                    current_category = Some(pkg.category);
                    ui.add_space(10.0);
                    ui.heading(pkg.category.name());
                }

                ui.horizontal(|ui| {
                    ui.checkbox(&mut pkg.is_selected, "");
                    ui.label(&pkg.name);
                    ui.weak(&pkg.package);
                    ui.label("-");
                    ui.label(&pkg.description);
                });
            }
        });
    }

    fn render_recovery(&mut self, ui: &mut egui::Ui) {
        ui.heading("Recovery & Firmware");
        ui.add_space(10.0);

        if let Some(manufacturer) = self.manufacturer {
            ui.label(format!("Detected manufacturer: {}", manufacturer.name()));
        }

        ui.add_space(10.0);
        ui.heading("Reboot Options");

        ui.horizontal(|ui| {
            if ui.button("🔄 Reboot").clicked() {
                if let Some(ref adb) = self.adb {
                    let rm = RecoveryManager::new(Arc::clone(adb));
                    if let Err(e) = rm.reboot() {
                        self.status_message = format!("Error: {}", e);
                    }
                }
            }

            if ui.button("🔧 Recovery Mode").clicked() {
                if let Some(ref adb) = self.adb {
                    let rm = RecoveryManager::new(Arc::clone(adb));
                    if let Err(e) = rm.reboot_recovery() {
                        self.status_message = format!("Error: {}", e);
                    }
                }
            }

            if ui.button("⬇ Download Mode").clicked() {
                if let Some(ref adb) = self.adb {
                    let rm = RecoveryManager::new(Arc::clone(adb));
                    if let Err(e) = rm.reboot_download() {
                        self.status_message = format!("Error: {}", e);
                    }
                }
            }

            if ui.button("⚡ Bootloader").clicked() {
                if let Some(ref adb) = self.adb {
                    let rm = RecoveryManager::new(Arc::clone(adb));
                    if let Err(e) = rm.reboot_bootloader() {
                        self.status_message = format!("Error: {}", e);
                    }
                }
            }
        });

        ui.add_space(20.0);
        ui.heading("Factory Reset");
        ui.colored_label(egui::Color32::RED, "⚠ WARNING: This will erase all data!");

        ui.horizontal(|ui| {
            ui.label(format!("Confirmations: {}/3", self.reset_confirmations));
            if self.reset_confirmations < 3 {
                if ui.button("Confirm Reset").clicked() {
                    self.reset_confirmations += 1;
                }
            } else {
                if ui.button("🗑 FACTORY RESET").clicked() {
                    if let Some(ref adb) = self.adb {
                        let rm = RecoveryManager::new(Arc::clone(adb));
                        if let Err(e) = rm.factory_reset() {
                            self.status_message = format!("Error: {}", e);
                        } else {
                            self.status_message = "Factory reset initiated".to_string();
                        }
                    }
                    self.reset_confirmations = 0;
                }
            }

            if self.reset_confirmations > 0 && ui.button("Cancel").clicked() {
                self.reset_confirmations = 0;
            }
        });

        ui.add_space(20.0);
        ui.heading("Firmware Sources");

        if let Some(manufacturer) = self.manufacturer {
            let sources = RecoveryManager::get_firmware_sources(manufacturer);
            for source in sources {
                ui.horizontal(|ui| {
                    ui.strong(&source.name);
                    ui.label("-");
                    ui.label(&source.description);
                    if ui.link("Open").clicked() {
                        let _ = open::that(&source.url);
                    }
                });
            }

            if let Some(tool) = RecoveryManager::get_flashing_tool(manufacturer) {
                ui.add_space(10.0);
                ui.heading("Flashing Tool");
                ui.strong(&tool.name);
                ui.label(&tool.description);
                if ui.link("Download").clicked() {
                    let _ = open::that(&tool.download_url);
                }
                ui.add_space(5.0);
                for instruction in &tool.instructions {
                    ui.label(instruction);
                }
            }
        }
    }

    fn render_settings(&mut self, ui: &mut egui::Ui) {
        ui.heading("Settings");
        ui.add_space(10.0);

        ui.group(|ui| {
            ui.heading("ADB");

            if let AdbStatus::Ready(path) = &*self.adb_status.lock().unwrap() {
                ui.horizontal(|ui| {
                    ui.label("ADB Path:");
                    ui.code(path);
                });
            }

            if ui.button("Restart ADB Server").clicked() {
                if let Some(ref adb) = self.adb {
                    if let Err(e) = adb.restart_server() {
                        self.status_message = format!("Error: {}", e);
                    } else {
                        self.status_message = "ADB server restarted".to_string();
                        self.refresh_devices();
                    }
                }
            }
        });

        ui.add_space(10.0);

        ui.group(|ui| {
            ui.heading("About");
            ui.label("Android SuperTool v1.0.0");
            ui.label("Mobile shop edition for device management");
            ui.add_space(5.0);
            ui.label("Features:");
            ui.label("• Scan for malware, adware, and bloatware");
            ui.label("• Samsung device debloating");
            ui.label("• Recovery and firmware tools");
        });
    }
}
