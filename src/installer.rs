//! ADB Platform Tools installer - auto-downloads from Google

use anyhow::{anyhow, Result};
use std::fs::{self, File};
use std::io::{Read, Write};
use std::path::{Path, PathBuf};

/// Download URLs for platform tools
const PLATFORM_TOOLS_WINDOWS: &str = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip";
const PLATFORM_TOOLS_LINUX: &str = "https://dl.google.com/android/repository/platform-tools-latest-linux.zip";
const PLATFORM_TOOLS_MACOS: &str = "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip";

/// Get the data directory for the application
pub fn get_data_dir() -> PathBuf {
    dirs::data_local_dir()
        .unwrap_or_else(|| PathBuf::from("."))
        .join("android-supertool")
}

/// Get the path where ADB should be installed
pub fn get_adb_dir() -> PathBuf {
    get_data_dir().join("platform-tools")
}

/// Get the path to the ADB executable
pub fn get_adb_path() -> PathBuf {
    let adb_dir = get_adb_dir();
    if cfg!(windows) {
        adb_dir.join("adb.exe")
    } else {
        adb_dir.join("adb")
    }
}

/// Check if ADB is already installed
pub fn is_adb_installed() -> bool {
    get_adb_path().exists()
}

/// Check if ADB is available in system PATH
pub fn is_adb_in_path() -> Option<PathBuf> {
    which::which("adb").ok()
}

/// Get the best available ADB path
pub fn get_best_adb_path() -> Option<PathBuf> {
    // First check our local installation
    if is_adb_installed() {
        return Some(get_adb_path());
    }

    // Then check system PATH
    is_adb_in_path()
}

/// Installer for ADB Platform Tools
pub struct Installer {
    progress_callback: Option<Box<dyn Fn(f32, &str) + Send>>,
}

impl Installer {
    pub fn new() -> Self {
        Self {
            progress_callback: None,
        }
    }

    /// Set a callback for progress updates
    pub fn with_progress<F>(mut self, callback: F) -> Self
    where
        F: Fn(f32, &str) + Send + 'static,
    {
        self.progress_callback = Some(Box::new(callback));
        self
    }

    fn report_progress(&self, progress: f32, message: &str) {
        if let Some(ref callback) = self.progress_callback {
            callback(progress, message);
        }
    }

    /// Download and install ADB Platform Tools
    pub fn install(&self) -> Result<PathBuf> {
        // Create data directory
        let data_dir = get_data_dir();
        fs::create_dir_all(&data_dir)?;

        self.report_progress(0.0, "Starting download...");

        // Get download URL for current OS
        let url = if cfg!(target_os = "windows") {
            PLATFORM_TOOLS_WINDOWS
        } else if cfg!(target_os = "macos") {
            PLATFORM_TOOLS_MACOS
        } else {
            PLATFORM_TOOLS_LINUX
        };

        // Download the zip file
        let zip_path = data_dir.join("platform-tools.zip");
        self.download_file(url, &zip_path)?;

        self.report_progress(0.7, "Extracting...");

        // Extract the zip
        self.extract_zip(&zip_path, &data_dir)?;

        // Clean up zip file
        let _ = fs::remove_file(&zip_path);

        // Make ADB executable on Unix
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let adb_path = get_adb_path();
            if adb_path.exists() {
                let mut perms = fs::metadata(&adb_path)?.permissions();
                perms.set_mode(0o755);
                fs::set_permissions(&adb_path, perms)?;
            }

            // Also make fastboot executable
            let fastboot_path = get_adb_dir().join("fastboot");
            if fastboot_path.exists() {
                let mut perms = fs::metadata(&fastboot_path)?.permissions();
                perms.set_mode(0o755);
                fs::set_permissions(&fastboot_path, perms)?;
            }
        }

        self.report_progress(1.0, "Installation complete!");

        let adb_path = get_adb_path();
        if adb_path.exists() {
            Ok(adb_path)
        } else {
            Err(anyhow!("ADB installation failed - executable not found"))
        }
    }

    /// Download a file with progress reporting
    fn download_file(&self, url: &str, dest: &Path) -> Result<()> {
        self.report_progress(0.1, "Connecting to Google servers...");

        let response = reqwest::blocking::get(url)?;

        if !response.status().is_success() {
            return Err(anyhow!("Download failed: HTTP {}", response.status()));
        }

        let total_size = response.content_length().unwrap_or(0);
        let mut downloaded: u64 = 0;

        let mut file = File::create(dest)?;
        let mut reader = response;

        let mut buffer = [0u8; 8192];
        loop {
            let bytes_read = reader.read(&mut buffer)?;
            if bytes_read == 0 {
                break;
            }

            file.write_all(&buffer[..bytes_read])?;
            downloaded += bytes_read as u64;

            if total_size > 0 {
                let progress = 0.1 + (downloaded as f32 / total_size as f32) * 0.6;
                let mb_downloaded = downloaded as f32 / 1_048_576.0;
                let mb_total = total_size as f32 / 1_048_576.0;
                self.report_progress(
                    progress,
                    &format!("Downloading... {:.1}/{:.1} MB", mb_downloaded, mb_total),
                );
            }
        }

        Ok(())
    }

    /// Extract a zip file
    fn extract_zip(&self, zip_path: &Path, dest_dir: &Path) -> Result<()> {
        let file = File::open(zip_path)?;
        let mut archive = zip::ZipArchive::new(file)?;

        let total_files = archive.len();

        for i in 0..archive.len() {
            let mut file = archive.by_index(i)?;
            let outpath = match file.enclosed_name() {
                Some(path) => dest_dir.join(path),
                None => continue,
            };

            if file.name().ends_with('/') {
                fs::create_dir_all(&outpath)?;
            } else {
                if let Some(parent) = outpath.parent() {
                    if !parent.exists() {
                        fs::create_dir_all(parent)?;
                    }
                }
                let mut outfile = File::create(&outpath)?;
                std::io::copy(&mut file, &mut outfile)?;
            }

            let progress = 0.7 + (i as f32 / total_files as f32) * 0.25;
            self.report_progress(progress, &format!("Extracting files... {}/{}", i + 1, total_files));
        }

        Ok(())
    }
}

impl Default for Installer {
    fn default() -> Self {
        Self::new()
    }
}
