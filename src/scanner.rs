//! App scanner that analyzes installed apps for threats

use crate::adb::{AdbManager, PackageInfo};
use crate::database::{RiskLevel, ThreatDatabase};
use eframe::egui;
use std::sync::Arc;

/// Result of scanning an app
#[derive(Debug, Clone)]
pub struct ScanResult {
    pub package: PackageInfo,
    pub risk_level: RiskLevel,
    pub category: String,
    pub description: String,
    pub is_selected: bool,
}

impl ScanResult {
    pub fn risk_color(&self) -> egui::Color32 {
        match self.risk_level {
            RiskLevel::Critical => egui::Color32::from_rgb(255, 0, 100),   // Magenta/Pink
            RiskLevel::High => egui::Color32::from_rgb(255, 50, 50),      // Red
            RiskLevel::Medium => egui::Color32::from_rgb(255, 180, 0),    // Orange/Yellow
            RiskLevel::Low => egui::Color32::from_rgb(100, 150, 255),     // Blue
            RiskLevel::Safe => egui::Color32::from_rgb(50, 200, 50),      // Green
        }
    }
}

/// Scanner for analyzing apps on a device
pub struct AppScanner {
    adb: Arc<AdbManager>,
    database: ThreatDatabase,
}

impl AppScanner {
    pub fn new(adb: Arc<AdbManager>) -> Self {
        Self {
            adb,
            database: ThreatDatabase::new(),
        }
    }

    /// Scan all third-party apps on the device
    pub fn scan_device(&self) -> anyhow::Result<Vec<ScanResult>> {
        let packages = self.adb.get_third_party_packages()?;
        let mut results = Vec::new();

        for pkg in packages {
            let (risk_level, description) = self.database.analyze(&pkg.package_name);
            let category = self.categorize(&pkg.package_name, risk_level);

            results.push(ScanResult {
                package: pkg,
                risk_level,
                category,
                description,
                is_selected: false,
            });
        }

        // Sort by risk level (highest first)
        results.sort_by(|a, b| b.risk_level.cmp(&a.risk_level));

        Ok(results)
    }

    /// Scan all apps including system apps
    pub fn scan_all(&self) -> anyhow::Result<Vec<ScanResult>> {
        let packages = self.adb.get_packages(true)?;
        let mut results = Vec::new();

        for pkg in packages {
            let (risk_level, description) = self.database.analyze(&pkg.package_name);
            let category = self.categorize(&pkg.package_name, risk_level);

            results.push(ScanResult {
                package: pkg,
                risk_level,
                category,
                description,
                is_selected: false,
            });
        }

        results.sort_by(|a, b| b.risk_level.cmp(&a.risk_level));

        Ok(results)
    }

    /// Categorize an app based on its package name and risk level
    fn categorize(&self, package: &str, risk: RiskLevel) -> String {
        match risk {
            RiskLevel::Critical => "Malware".to_string(),
            RiskLevel::High => "Adware/PUP".to_string(),
            RiskLevel::Medium => "Bloatware".to_string(),
            RiskLevel::Low => "Optional".to_string(),
            RiskLevel::Safe => {
                // Try to categorize safe apps
                if package.contains("google") {
                    "Google".to_string()
                } else if package.contains("samsung") || package.contains("sec.") {
                    "Samsung".to_string()
                } else if package.contains("miui") || package.contains("xiaomi") {
                    "Xiaomi".to_string()
                } else if package.contains("huawei") {
                    "Huawei".to_string()
                } else {
                    "User App".to_string()
                }
            }
        }
    }

    /// Quick scan - only detect high-risk and critical threats
    pub fn quick_scan(&self) -> anyhow::Result<Vec<ScanResult>> {
        let all_results = self.scan_device()?;
        Ok(all_results
            .into_iter()
            .filter(|r| r.risk_level >= RiskLevel::High)
            .collect())
    }

    /// Get count of threats by risk level
    pub fn get_threat_summary(results: &[ScanResult]) -> ThreatSummary {
        let mut summary = ThreatSummary::default();

        for result in results {
            match result.risk_level {
                RiskLevel::Critical => summary.critical += 1,
                RiskLevel::High => summary.high += 1,
                RiskLevel::Medium => summary.medium += 1,
                RiskLevel::Low => summary.low += 1,
                RiskLevel::Safe => summary.safe += 1,
            }
        }

        summary.total = results.len();
        summary
    }
}

/// Summary of scan results
#[derive(Debug, Default, Clone)]
pub struct ThreatSummary {
    pub total: usize,
    pub critical: usize,
    pub high: usize,
    pub medium: usize,
    pub low: usize,
    pub safe: usize,
}

impl ThreatSummary {
    pub fn threats(&self) -> usize {
        self.critical + self.high + self.medium
    }
}
