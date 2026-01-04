"""
App Scanner and AI Analyzer Module
Scans devices for malware, adware, and bloatware with AI-powered analysis
"""

import os
import re
import json
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Tuple
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

from .database import (
    AppDatabase, get_database, RiskLevel, AppCategory,
    DANGEROUS_PERMISSION_COMBOS, OVER_PRIVILEGED_PERMISSIONS
)
from .adb_manager import ADBManager, PackageInfo


class ScanStatus(Enum):
    """Scan status states."""
    PENDING = "pending"
    SCANNING = "scanning"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AppRiskAssessment:
    """Risk assessment result for an app."""
    package_name: str
    app_name: str
    risk_level: RiskLevel
    category: AppCategory
    risk_score: int  # 0-100
    reasons: List[str]
    is_system: bool
    is_removable: bool
    recommendation: str
    permissions_concern: List[str] = field(default_factory=list)
    matched_patterns: List[str] = field(default_factory=list)
    ai_analysis: str = ""

    @property
    def risk_color(self) -> str:
        """Get color code for the risk level."""
        colors = {
            RiskLevel.CRITICAL: "red",
            RiskLevel.HIGH: "bright_red",
            RiskLevel.MEDIUM: "yellow",
            RiskLevel.LOW: "cyan",
            RiskLevel.SAFE: "green",
            RiskLevel.UNKNOWN: "white",
        }
        return colors.get(self.risk_level, "white")


@dataclass
class ScanResult:
    """Complete scan result for a device."""
    device_serial: str
    device_name: str
    scan_time: float
    total_apps: int
    status: ScanStatus
    critical_apps: List[AppRiskAssessment] = field(default_factory=list)
    high_risk_apps: List[AppRiskAssessment] = field(default_factory=list)
    medium_risk_apps: List[AppRiskAssessment] = field(default_factory=list)
    low_risk_apps: List[AppRiskAssessment] = field(default_factory=list)
    safe_apps: List[AppRiskAssessment] = field(default_factory=list)
    unknown_apps: List[AppRiskAssessment] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def threat_count(self) -> int:
        """Get total number of threats (critical + high + medium)."""
        return len(self.critical_apps) + len(self.high_risk_apps) + len(self.medium_risk_apps)

    @property
    def removable_threats(self) -> List[AppRiskAssessment]:
        """Get all removable threat apps."""
        threats = []
        for app in self.critical_apps + self.high_risk_apps + self.medium_risk_apps:
            if app.is_removable:
                threats.append(app)
        return threats

    def get_summary(self) -> Dict[str, int]:
        """Get a summary of risk levels."""
        return {
            "critical": len(self.critical_apps),
            "high": len(self.high_risk_apps),
            "medium": len(self.medium_risk_apps),
            "low": len(self.low_risk_apps),
            "safe": len(self.safe_apps),
            "unknown": len(self.unknown_apps),
            "total": self.total_apps,
        }


class AppScanner:
    """Scans Android devices for risky apps."""

    # Mapping of common app name keywords to categories
    KEYWORD_RISK_MAP = {
        # High risk keywords
        "cleaner": (RiskLevel.HIGH, AppCategory.FAKE_CLEANER),
        "booster": (RiskLevel.HIGH, AppCategory.FAKE_BOOSTER),
        "optimizer": (RiskLevel.HIGH, AppCategory.FAKE_CLEANER),
        "antivirus": (RiskLevel.HIGH, AppCategory.FAKE_ANTIVIRUS),
        "virus scan": (RiskLevel.HIGH, AppCategory.FAKE_ANTIVIRUS),
        "battery saver": (RiskLevel.HIGH, AppCategory.FAKE_BATTERY),
        "ram clean": (RiskLevel.HIGH, AppCategory.FAKE_CLEANER),
        "junk clean": (RiskLevel.HIGH, AppCategory.FAKE_CLEANER),
        "phone clean": (RiskLevel.HIGH, AppCategory.FAKE_CLEANER),
        "speed boost": (RiskLevel.HIGH, AppCategory.FAKE_BOOSTER),
        "super clean": (RiskLevel.HIGH, AppCategory.FAKE_CLEANER),
        "turbo clean": (RiskLevel.HIGH, AppCategory.FAKE_CLEANER),
        "free vpn": (RiskLevel.HIGH, AppCategory.DATA_HARVESTER),
        "vpn free": (RiskLevel.HIGH, AppCategory.DATA_HARVESTER),
        "quick loan": (RiskLevel.HIGH, AppCategory.LOAN_SHARK),
        "instant cash": (RiskLevel.HIGH, AppCategory.LOAN_SHARK),
        "easy loan": (RiskLevel.HIGH, AppCategory.LOAN_SHARK),
    }

    def __init__(self, adb_manager: ADBManager, database: Optional[AppDatabase] = None):
        """
        Initialize the scanner.

        Args:
            adb_manager: ADB manager instance
            database: App database (uses singleton if None)
        """
        self.adb = adb_manager
        self.db = database or get_database()
        self._ai_client = None

    def _init_ai_client(self):
        """Initialize the AI client for advanced analysis."""
        try:
            import anthropic
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if api_key:
                self._ai_client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            pass

    def scan_device(
        self,
        include_system: bool = False,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
        use_ai: bool = False
    ) -> ScanResult:
        """
        Scan the connected device for risky apps.

        Args:
            include_system: Include system apps in scan
            progress_callback: Callback(status, current, total) for progress
            use_ai: Use AI for advanced analysis (requires ANTHROPIC_API_KEY)

        Returns:
            ScanResult with categorized apps
        """
        start_time = time.time()

        # Get device info
        devices = self.adb.get_devices()
        current_device = self.adb.get_current_device()

        device_info = None
        for d in devices:
            if d.serial == current_device:
                device_info = d
                break

        if not device_info:
            return ScanResult(
                device_serial=current_device or "unknown",
                device_name="Unknown Device",
                scan_time=0,
                total_apps=0,
                status=ScanStatus.ERROR,
                errors=["No device connected"]
            )

        result = ScanResult(
            device_serial=device_info.serial,
            device_name=device_info.display_name,
            scan_time=0,
            total_apps=0,
            status=ScanStatus.SCANNING
        )

        # Get package list
        if progress_callback:
            progress_callback("Getting package list...", 0, 0)

        if include_system:
            packages = self.adb.get_packages(include_system=True)
        else:
            packages = self.adb.get_third_party_packages()

        result.total_apps = len(packages)

        if progress_callback:
            progress_callback(f"Scanning {len(packages)} apps...", 0, len(packages))

        # Initialize AI if requested
        if use_ai:
            self._init_ai_client()

        # Scan each package
        for i, package in enumerate(packages):
            try:
                assessment = self._assess_package(package, use_ai=use_ai)

                # Categorize by risk level
                if assessment.risk_level == RiskLevel.CRITICAL:
                    result.critical_apps.append(assessment)
                elif assessment.risk_level == RiskLevel.HIGH:
                    result.high_risk_apps.append(assessment)
                elif assessment.risk_level == RiskLevel.MEDIUM:
                    result.medium_risk_apps.append(assessment)
                elif assessment.risk_level == RiskLevel.LOW:
                    result.low_risk_apps.append(assessment)
                elif assessment.risk_level == RiskLevel.SAFE:
                    result.safe_apps.append(assessment)
                else:
                    result.unknown_apps.append(assessment)

            except Exception as e:
                result.errors.append(f"Error scanning {package}: {str(e)}")

            if progress_callback:
                progress_callback(f"Scanning: {package[:40]}...", i + 1, len(packages))

        # Sort by risk score
        result.critical_apps.sort(key=lambda x: x.risk_score, reverse=True)
        result.high_risk_apps.sort(key=lambda x: x.risk_score, reverse=True)
        result.medium_risk_apps.sort(key=lambda x: x.risk_score, reverse=True)

        result.scan_time = time.time() - start_time
        result.status = ScanStatus.COMPLETED

        return result

    def _assess_package(self, package_name: str, use_ai: bool = False) -> AppRiskAssessment:
        """
        Assess the risk of a single package.

        Args:
            package_name: The package name to assess
            use_ai: Use AI for analysis

        Returns:
            AppRiskAssessment object
        """
        reasons = []
        risk_score = 0
        matched_patterns = []
        permissions_concern = []
        category = AppCategory.UNKNOWN
        app_name = package_name.split('.')[-1].replace('_', ' ').title()

        # Check database first
        db_info = self.db.lookup(package_name)
        if db_info:
            return AppRiskAssessment(
                package_name=package_name,
                app_name=db_info.name,
                risk_level=db_info.risk,
                category=db_info.category,
                risk_score=self._risk_to_score(db_info.risk),
                reasons=[db_info.description],
                is_system=False,
                is_removable=db_info.removal_safe,
                recommendation=self._get_recommendation(db_info.risk, db_info.category)
            )

        # Check if safe system app
        if self.db.is_safe_system_app(package_name):
            return AppRiskAssessment(
                package_name=package_name,
                app_name=app_name,
                risk_level=RiskLevel.SAFE,
                category=AppCategory.UNKNOWN,
                risk_score=0,
                reasons=["System app - safe to keep"],
                is_system=True,
                is_removable=False,
                recommendation="Keep - Required system app"
            )

        # Get package details for deeper analysis
        pkg_info = self.adb.get_package_info(package_name)

        if pkg_info:
            app_name = package_name.split('.')[-1].replace('_', ' ').title()

            # Check if it's a system app
            is_system = pkg_info.is_system

            # Analyze permissions
            permission_risk, perm_reasons = self._analyze_permissions(
                pkg_info.permissions,
                package_name
            )
            risk_score += permission_risk
            reasons.extend(perm_reasons)
            permissions_concern = [p for p in pkg_info.permissions if p in OVER_PRIVILEGED_PERMISSIONS]

        else:
            is_system = False

        # Pattern-based analysis
        pattern_risk = self.db.analyze_by_pattern(package_name)
        if pattern_risk != RiskLevel.UNKNOWN:
            if pattern_risk == RiskLevel.HIGH:
                risk_score += 60
                reasons.append("Package name matches known risky patterns")
                matched_patterns.append(package_name)
            elif pattern_risk == RiskLevel.MEDIUM:
                risk_score += 30
                reasons.append("Package name matches suspicious patterns")

        # Keyword analysis
        keyword_risk, keyword_cat = self._analyze_keywords(package_name)
        if keyword_risk != RiskLevel.UNKNOWN:
            if keyword_risk == RiskLevel.HIGH:
                risk_score += 50
                category = keyword_cat
                reasons.append(f"App name contains high-risk keywords ({keyword_cat.value})")

        # Installer analysis
        if pkg_info and pkg_info.installer:
            installer_risk = self._analyze_installer(pkg_info.installer)
            if installer_risk > 0:
                risk_score += installer_risk
                reasons.append(f"Installed from untrusted source: {pkg_info.installer}")

        # Determine final risk level
        risk_level = self._score_to_risk(risk_score)

        # AI analysis if enabled and risk is uncertain
        ai_analysis = ""
        if use_ai and self._ai_client and risk_level == RiskLevel.UNKNOWN:
            ai_analysis = self._ai_analyze(package_name, pkg_info)
            if ai_analysis:
                reasons.append(f"AI Analysis: {ai_analysis[:100]}...")

        # Generate recommendation
        recommendation = self._get_recommendation(risk_level, category)

        return AppRiskAssessment(
            package_name=package_name,
            app_name=app_name,
            risk_level=risk_level,
            category=category,
            risk_score=min(risk_score, 100),
            reasons=reasons if reasons else ["No known issues detected"],
            is_system=is_system,
            is_removable=not is_system or risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH],
            recommendation=recommendation,
            permissions_concern=permissions_concern,
            matched_patterns=matched_patterns,
            ai_analysis=ai_analysis
        )

    def _analyze_permissions(
        self,
        permissions: List[str],
        package_name: str
    ) -> Tuple[int, List[str]]:
        """Analyze permissions for risk indicators."""
        risk_score = 0
        reasons = []

        # Check for dangerous permission combos
        for combo_name, combo_perms in DANGEROUS_PERMISSION_COMBOS.items():
            matched = sum(1 for p in combo_perms if p in permissions)
            if matched >= len(combo_perms) - 1:  # Allow one missing
                risk_score += 40
                reasons.append(f"Has {combo_name} permission pattern")

        # Check for over-privileged permissions
        dangerous_count = sum(1 for p in permissions if p in OVER_PRIVILEGED_PERMISSIONS)
        if dangerous_count >= 5:
            risk_score += 30
            reasons.append(f"Excessive dangerous permissions ({dangerous_count})")
        elif dangerous_count >= 3:
            risk_score += 15
            reasons.append(f"Multiple dangerous permissions ({dangerous_count})")

        # Check for specific suspicious permissions
        if "android.permission.SYSTEM_ALERT_WINDOW" in permissions:
            # This is the popup ad permission
            risk_score += 25
            reasons.append("Can draw over other apps (popup ads)")

        if "android.permission.BIND_DEVICE_ADMIN" in permissions:
            risk_score += 35
            reasons.append("Requests device admin (hard to remove)")

        if "android.permission.BIND_ACCESSIBILITY_SERVICE" in permissions:
            risk_score += 30
            reasons.append("Requests accessibility service (can read screen)")

        return risk_score, reasons

    def _analyze_keywords(self, package_name: str) -> Tuple[RiskLevel, AppCategory]:
        """Analyze package name for risky keywords."""
        package_lower = package_name.lower()

        for keyword, (risk, category) in self.KEYWORD_RISK_MAP.items():
            if keyword.replace(' ', '') in package_lower or keyword.replace(' ', '.') in package_lower:
                return risk, category

        return RiskLevel.UNKNOWN, AppCategory.UNKNOWN

    def _analyze_installer(self, installer: str) -> int:
        """Analyze the installer package for trust level."""
        trusted_installers = [
            "com.android.vending",  # Play Store
            "com.google.android.packageinstaller",
            "com.samsung.android.packageinstaller",
            "com.miui.packageinstaller",
            "com.amazon.venezia",  # Amazon App Store
        ]

        if installer in trusted_installers:
            return 0

        # Unknown installer
        if installer and installer not in trusted_installers:
            return 15  # Slight risk for sideloaded apps

        return 0

    def _ai_analyze(self, package_name: str, pkg_info: Optional[PackageInfo]) -> str:
        """Use AI to analyze an unknown package."""
        if not self._ai_client:
            return ""

        try:
            prompt = f"""Analyze this Android app package for potential security risks:

Package: {package_name}
Permissions: {', '.join(pkg_info.permissions[:10]) if pkg_info else 'Unknown'}
Install Location: {pkg_info.install_location.value if pkg_info else 'Unknown'}

Based on the package name and permissions, assess if this app is likely:
1. Legitimate and safe
2. Potentially unwanted (PUP/bloatware)
3. Adware or aggressive advertising
4. Potentially malicious

Respond in 1-2 sentences with your assessment and confidence level."""

            response = self._ai_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except Exception:
            return ""

    def _risk_to_score(self, risk: RiskLevel) -> int:
        """Convert risk level to numeric score."""
        scores = {
            RiskLevel.CRITICAL: 95,
            RiskLevel.HIGH: 75,
            RiskLevel.MEDIUM: 50,
            RiskLevel.LOW: 25,
            RiskLevel.SAFE: 5,
            RiskLevel.UNKNOWN: 0,
        }
        return scores.get(risk, 0)

    def _score_to_risk(self, score: int) -> RiskLevel:
        """Convert numeric score to risk level."""
        if score >= 80:
            return RiskLevel.CRITICAL
        elif score >= 55:
            return RiskLevel.HIGH
        elif score >= 35:
            return RiskLevel.MEDIUM
        elif score >= 15:
            return RiskLevel.LOW
        elif score > 0:
            return RiskLevel.SAFE
        return RiskLevel.UNKNOWN

    def _get_recommendation(self, risk: RiskLevel, category: AppCategory) -> str:
        """Get action recommendation based on risk and category."""
        recommendations = {
            RiskLevel.CRITICAL: "REMOVE IMMEDIATELY - Confirmed malware/spyware",
            RiskLevel.HIGH: "REMOVE - Aggressive adware or data harvester",
            RiskLevel.MEDIUM: "Consider removing - Bloatware or intrusive app",
            RiskLevel.LOW: "Optional removal - Mild bloatware",
            RiskLevel.SAFE: "Keep - Safe app",
            RiskLevel.UNKNOWN: "Manual review recommended",
        }

        base_rec = recommendations.get(risk, "Unknown")

        # Add category-specific advice
        category_advice = {
            AppCategory.FAKE_CLEANER: " (Fake cleaner - does nothing useful)",
            AppCategory.FAKE_ANTIVIRUS: " (Fake antivirus - provides no protection)",
            AppCategory.POPUP_ADS: " (Source of popup ads)",
            AppCategory.LOAN_SHARK: " (Predatory lending app)",
            AppCategory.SPYWARE: " (Monitors your activity)",
        }

        return base_rec + category_advice.get(category, "")

    def quick_scan(self) -> List[AppRiskAssessment]:
        """
        Quick scan that only checks third-party apps against the database.
        Much faster than full scan.

        Returns:
            List of risky apps found
        """
        risky_apps = []
        packages = self.adb.get_third_party_packages()

        for package in packages:
            # Quick database lookup only
            db_info = self.db.lookup(package)
            if db_info and db_info.risk in [RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM]:
                risky_apps.append(AppRiskAssessment(
                    package_name=package,
                    app_name=db_info.name,
                    risk_level=db_info.risk,
                    category=db_info.category,
                    risk_score=self._risk_to_score(db_info.risk),
                    reasons=[db_info.description],
                    is_system=False,
                    is_removable=True,
                    recommendation=self._get_recommendation(db_info.risk, db_info.category)
                ))

        return risky_apps

    def find_popup_source(self) -> Optional[str]:
        """
        Try to identify the source of popup ads by checking foreground app.
        Should be called when a popup appears.

        Returns:
            Package name if identified, None otherwise
        """
        foreground = self.adb.get_foreground_package()
        if foreground:
            assessment = self._assess_package(foreground)
            if assessment.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                return foreground
        return foreground  # Return anyway so user can investigate
