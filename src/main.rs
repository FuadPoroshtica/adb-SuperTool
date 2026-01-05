//! Android SuperTool - Mobile Shop Edition
//!
//! A complete tool for managing Android devices:
//! - Scan for malware, adware, and bloatware
//! - Samsung device debloating for entry-level phones
//! - Recovery and firmware management

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod adb;
mod app;
mod database;
mod debloater;
mod installer;
mod recovery;
mod scanner;

use app::SuperToolApp;
use clap::Parser;
use eframe::egui;

/// Android SuperTool - Device management for mobile shops
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Run in headless mode (CLI only)
    #[arg(short = 'H', long)]
    headless: bool,

    /// Device serial number to use
    #[arg(short, long)]
    device: Option<String>,
}

fn main() -> eframe::Result<()> {
    // Initialize logging
    tracing_subscriber::fmt::init();

    let args = Args::parse();

    if args.headless {
        // Headless mode - future CLI implementation
        println!("Android SuperTool v1.0.0");
        println!("Headless mode not yet implemented. Please run in GUI mode.");
        return Ok(());
    }

    // GUI mode
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([1024.0, 700.0])
            .with_min_inner_size([800.0, 500.0])
            .with_title("Android SuperTool")
            .with_icon(load_icon()),
        ..Default::default()
    };

    eframe::run_native(
        "Android SuperTool",
        options,
        Box::new(|cc| Ok(Box::new(SuperToolApp::new(cc)))),
    )
}

/// Load the application icon
fn load_icon() -> egui::IconData {
    // Simple 32x32 icon - a wrench emoji representation
    let size = 32;
    let mut rgba = vec![0u8; size * size * 4];

    // Create a simple gradient icon (blue-purple)
    for y in 0..size {
        for x in 0..size {
            let idx = (y * size + x) * 4;
            let fx = x as f32 / size as f32;
            let fy = y as f32 / size as f32;

            // Distance from center
            let dx = fx - 0.5;
            let dy = fy - 0.5;
            let dist = (dx * dx + dy * dy).sqrt();

            if dist < 0.45 {
                // Inside the circle
                rgba[idx] = (100.0 + fx * 100.0) as u8;     // R
                rgba[idx + 1] = (50.0 + fy * 50.0) as u8;   // G
                rgba[idx + 2] = (200.0 + fx * 55.0) as u8;  // B
                rgba[idx + 3] = 255;                         // A
            } else {
                // Transparent outside
                rgba[idx + 3] = 0;
            }
        }
    }

    egui::IconData {
        rgba,
        width: size as u32,
        height: size as u32,
    }
}
