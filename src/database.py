"""
Comprehensive Malware, Adware, and Bloatware Database
Contains patterns, known packages, and risk classifications
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set, Optional
import re


class RiskLevel(Enum):
    """Risk classification levels."""
    CRITICAL = "critical"    # Confirmed malware, spyware, ransomware
    HIGH = "high"            # Aggressive adware, data stealers, trojans
    MEDIUM = "medium"        # Bloatware, intrusive ads, trackers
    LOW = "low"              # Mild bloatware, unnecessary pre-installed apps
    SAFE = "safe"            # Known safe apps
    UNKNOWN = "unknown"      # Not in database


class AppCategory(Enum):
    """Categories of problematic apps."""
    MALWARE = "malware"
    SPYWARE = "spyware"
    ADWARE = "adware"
    BLOATWARE = "bloatware"
    FAKE_CLEANER = "fake_cleaner"
    FAKE_ANTIVIRUS = "fake_antivirus"
    FAKE_BATTERY = "fake_battery"
    FAKE_BOOSTER = "fake_booster"
    POPUP_ADS = "popup_ads"
    BROWSER_HIJACKER = "browser_hijacker"
    DATA_HARVESTER = "data_harvester"
    CRYPTO_MINER = "crypto_miner"
    SUBSCRIPTION_SCAM = "subscription_scam"
    TRACKING = "tracking"
    CARRIER_BLOAT = "carrier_bloat"
    OEM_BLOAT = "oem_bloat"
    SYSTEM_REPLACER = "system_replacer"
    LOAN_SHARK = "loan_shark"
    GAMBLING = "gambling"
    UNKNOWN = "unknown"


@dataclass
class AppInfo:
    """Information about a known problematic app."""
    package: str
    name: str
    risk: RiskLevel
    category: AppCategory
    description: str
    removal_safe: bool = True


# ============================================================================
# CRITICAL RISK - Confirmed Malware, Spyware, Dangerous Apps
# ============================================================================
CRITICAL_PACKAGES: Dict[str, AppInfo] = {
    # Banking Trojans / Financial Malware
    "com.tencent.fakemm": AppInfo(
        "com.tencent.fakemm", "Fake WeChat Trojan", RiskLevel.CRITICAL,
        AppCategory.MALWARE, "Banking trojan disguised as WeChat", True
    ),
    "com.android.vending.billing": AppInfo(
        "com.android.vending.billing", "Fake Billing Malware", RiskLevel.CRITICAL,
        AppCategory.MALWARE, "Fake Play billing malware", True
    ),

    # Spyware / Stalkerware
    "com.mspy": AppInfo(
        "com.mspy", "mSpy Stalkerware", RiskLevel.CRITICAL,
        AppCategory.SPYWARE, "Commercial stalkerware app", True
    ),
    "com.flexispy": AppInfo(
        "com.flexispy", "FlexiSpy Stalkerware", RiskLevel.CRITICAL,
        AppCategory.SPYWARE, "Commercial stalkerware app", True
    ),
    "com.spyzie": AppInfo(
        "com.spyzie", "Spyzie Stalkerware", RiskLevel.CRITICAL,
        AppCategory.SPYWARE, "Stalkerware/spy app", True
    ),
    "com.cocospy": AppInfo(
        "com.cocospy", "Cocospy Stalkerware", RiskLevel.CRITICAL,
        AppCategory.SPYWARE, "Stalkerware/spy app", True
    ),
    "org.torproject.android.malware": AppInfo(
        "org.torproject.android.malware", "Fake Tor Browser", RiskLevel.CRITICAL,
        AppCategory.MALWARE, "Malware disguised as Tor", True
    ),
}

# ============================================================================
# HIGH RISK - Aggressive Adware, Data Stealers, Fake Apps
# ============================================================================
HIGH_RISK_PACKAGES: Dict[str, AppInfo] = {
    # Fake PDF Apps
    "com.technoware.pdf": AppInfo(
        "com.technoware.pdf", "Fake PDF Reader", RiskLevel.HIGH,
        AppCategory.ADWARE, "Aggressive fullscreen ads PDF reader", True
    ),
    "com.smartpdf.reader": AppInfo(
        "com.smartpdf.reader", "Smart PDF Reader", RiskLevel.HIGH,
        AppCategory.ADWARE, "Known adware PDF app", True
    ),
    "com.pdf.all.reader": AppInfo(
        "com.pdf.all.reader", "PDF All Reader", RiskLevel.HIGH,
        AppCategory.ADWARE, "Aggressive popup ads", True
    ),
    "com.document.pdf.reader": AppInfo(
        "com.document.pdf.reader", "Document PDF Reader", RiskLevel.HIGH,
        AppCategory.POPUP_ADS, "Fullscreen popup ad malware", True
    ),

    # Fake Cleaners / Optimizers (Very Common Scam Category)
    "com.cleanmaster.mguard": AppInfo(
        "com.cleanmaster.mguard", "Clean Master", RiskLevel.HIGH,
        AppCategory.FAKE_CLEANER, "Fake cleaner with aggressive ads", True
    ),
    "com.cleanmaster.sdk": AppInfo(
        "com.cleanmaster.sdk", "Clean Master SDK", RiskLevel.HIGH,
        AppCategory.ADWARE, "Adware SDK component", True
    ),
    "com.super.cleaner": AppInfo(
        "com.super.cleaner", "Super Cleaner", RiskLevel.HIGH,
        AppCategory.FAKE_CLEANER, "Fake cleaner app", True
    ),
    "com.supercleaner.optimizer": AppInfo(
        "com.supercleaner.optimizer", "Super Cleaner Optimizer", RiskLevel.HIGH,
        AppCategory.FAKE_CLEANER, "Fake optimizer scam", True
    ),
    "com.speed.booster.cleaner": AppInfo(
        "com.speed.booster.cleaner", "Speed Booster Cleaner", RiskLevel.HIGH,
        AppCategory.FAKE_CLEANER, "Fake booster with ads", True
    ),
    "com.phone.cleaner.booster": AppInfo(
        "com.phone.cleaner.booster", "Phone Cleaner Booster", RiskLevel.HIGH,
        AppCategory.FAKE_CLEANER, "Adware fake cleaner", True
    ),
    "com.junk.cleaner.phone": AppInfo(
        "com.junk.cleaner.phone", "Junk Cleaner", RiskLevel.HIGH,
        AppCategory.FAKE_CLEANER, "Fake junk cleaner", True
    ),
    "com.clean.master.pro": AppInfo(
        "com.clean.master.pro", "Clean Master Pro", RiskLevel.HIGH,
        AppCategory.FAKE_CLEANER, "Fake cleaner impostor", True
    ),
    "com.turbo.cleaner": AppInfo(
        "com.turbo.cleaner", "Turbo Cleaner", RiskLevel.HIGH,
        AppCategory.FAKE_CLEANER, "Adware cleaner app", True
    ),
    "com.rocket.cleaner": AppInfo(
        "com.rocket.cleaner", "Rocket Cleaner", RiskLevel.HIGH,
        AppCategory.FAKE_CLEANER, "Fake cleaner with popups", True
    ),
    "com.virus.cleaner.antivirus": AppInfo(
        "com.virus.cleaner.antivirus", "Virus Cleaner Antivirus", RiskLevel.HIGH,
        AppCategory.FAKE_ANTIVIRUS, "Fake antivirus scam", True
    ),
    "com.antivirus.security.free": AppInfo(
        "com.antivirus.security.free", "Free Antivirus Security", RiskLevel.HIGH,
        AppCategory.FAKE_ANTIVIRUS, "Fake antivirus", True
    ),

    # Fake Battery Apps
    "com.battery.saver.fast": AppInfo(
        "com.battery.saver.fast", "Fast Battery Saver", RiskLevel.HIGH,
        AppCategory.FAKE_BATTERY, "Fake battery saver with ads", True
    ),
    "com.du.battery.saver": AppInfo(
        "com.du.battery.saver", "DU Battery Saver", RiskLevel.HIGH,
        AppCategory.FAKE_BATTERY, "Known adware app", True
    ),
    "com.battery.doctor": AppInfo(
        "com.battery.doctor", "Battery Doctor", RiskLevel.HIGH,
        AppCategory.FAKE_BATTERY, "Fake battery optimizer", True
    ),
    "com.super.battery": AppInfo(
        "com.super.battery", "Super Battery", RiskLevel.HIGH,
        AppCategory.FAKE_BATTERY, "Fake battery saver", True
    ),

    # Water/Habit Tracker Adware (The one from user's experience)
    "wht.water.habit.tracker": AppInfo(
        "wht.water.habit.tracker", "Water Habit Tracker", RiskLevel.HIGH,
        AppCategory.POPUP_ADS, "Fullscreen takeover ad malware", True
    ),
    "com.water.drink.reminder": AppInfo(
        "com.water.drink.reminder", "Water Drink Reminder", RiskLevel.HIGH,
        AppCategory.POPUP_ADS, "Known popup ad app", True
    ),

    # Fake Flashlight Apps
    "com.flashlight.bright": AppInfo(
        "com.flashlight.bright", "Bright Flashlight", RiskLevel.HIGH,
        AppCategory.ADWARE, "Adware flashlight app", True
    ),
    "com.super.flashlight": AppInfo(
        "com.super.flashlight", "Super Flashlight", RiskLevel.HIGH,
        AppCategory.DATA_HARVESTER, "Data harvesting flashlight", True
    ),
    "com.flashlight.led.torch": AppInfo(
        "com.flashlight.led.torch", "LED Flashlight Torch", RiskLevel.HIGH,
        AppCategory.ADWARE, "Excessive permissions flashlight", True
    ),

    # Fake VPN Apps
    "com.free.vpn.master": AppInfo(
        "com.free.vpn.master", "Free VPN Master", RiskLevel.HIGH,
        AppCategory.DATA_HARVESTER, "Data harvesting fake VPN", True
    ),
    "com.supervpn.free": AppInfo(
        "com.supervpn.free", "SuperVPN Free", RiskLevel.HIGH,
        AppCategory.DATA_HARVESTER, "Known malicious VPN", True
    ),
    "com.fast.vpn.free": AppInfo(
        "com.fast.vpn.free", "Fast Free VPN", RiskLevel.HIGH,
        AppCategory.DATA_HARVESTER, "Malicious VPN app", True
    ),

    # Fake App Lockers
    "com.applock.photo": AppInfo(
        "com.applock.photo", "AppLock Photo", RiskLevel.HIGH,
        AppCategory.ADWARE, "Adware app locker", True
    ),
    "com.domobile.applock": AppInfo(
        "com.domobile.applock", "AppLock DoMobile", RiskLevel.HIGH,
        AppCategory.ADWARE, "Known adware app", True
    ),

    # Loan Shark / Predatory Lending Apps (Common in developing markets)
    "com.branch.borrower": AppInfo(
        "com.branch.borrower", "Branch Loan", RiskLevel.HIGH,
        AppCategory.LOAN_SHARK, "Predatory lending app", True
    ),
    "com.opay.loan": AppInfo(
        "com.opay.loan", "OPay Loan", RiskLevel.HIGH,
        AppCategory.LOAN_SHARK, "High-interest predatory loan", True
    ),
    "com.quick.cash.loan": AppInfo(
        "com.quick.cash.loan", "Quick Cash Loan", RiskLevel.HIGH,
        AppCategory.LOAN_SHARK, "Predatory loan app", True
    ),

    # Known Adware SDKs / Frameworks
    "com.startapp": AppInfo(
        "com.startapp", "StartApp SDK", RiskLevel.HIGH,
        AppCategory.ADWARE, "Aggressive ad SDK", True
    ),
    "com.ironsource.aura": AppInfo(
        "com.ironsource.aura", "Aura by IronSource", RiskLevel.HIGH,
        AppCategory.BLOATWARE, "Pre-installed bloatware", True
    ),

    # Browser Hijackers
    "com.uc.browser.turbo": AppInfo(
        "com.uc.browser.turbo", "UC Browser Turbo", RiskLevel.HIGH,
        AppCategory.BROWSER_HIJACKER, "Sends data to China", True
    ),
}

# ============================================================================
# MEDIUM RISK - Bloatware, Trackers, Intrusive Apps
# ============================================================================
MEDIUM_RISK_PACKAGES: Dict[str, AppInfo] = {
    # Facebook Bloatware
    "com.facebook.appmanager": AppInfo(
        "com.facebook.appmanager", "Facebook App Manager", RiskLevel.MEDIUM,
        AppCategory.BLOATWARE, "Facebook pre-installed manager", True
    ),
    "com.facebook.system": AppInfo(
        "com.facebook.system", "Facebook System", RiskLevel.MEDIUM,
        AppCategory.BLOATWARE, "Facebook system service", True
    ),
    "com.facebook.services": AppInfo(
        "com.facebook.services", "Facebook Services", RiskLevel.MEDIUM,
        AppCategory.TRACKING, "Facebook tracking service", True
    ),
    "com.facebook.katana": AppInfo(
        "com.facebook.katana", "Facebook", RiskLevel.MEDIUM,
        AppCategory.BLOATWARE, "Pre-installed Facebook", True
    ),
    "com.instagram.android": AppInfo(
        "com.instagram.android", "Instagram", RiskLevel.MEDIUM,
        AppCategory.BLOATWARE, "Pre-installed Instagram", True
    ),

    # Samsung Bloatware
    "com.samsung.android.bixby.agent": AppInfo(
        "com.samsung.android.bixby.agent", "Bixby Voice", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Samsung Bixby assistant", True
    ),
    "com.samsung.android.bixby.service": AppInfo(
        "com.samsung.android.bixby.service", "Bixby Service", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Bixby background service", True
    ),
    "com.samsung.android.visionintelligence": AppInfo(
        "com.samsung.android.visionintelligence", "Bixby Vision", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Bixby Vision feature", True
    ),
    "com.samsung.android.game.gamehome": AppInfo(
        "com.samsung.android.game.gamehome", "Game Launcher", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Samsung Game Launcher", True
    ),
    "com.samsung.android.game.gametools": AppInfo(
        "com.samsung.android.game.gametools", "Game Tools", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Samsung Game Tools", True
    ),
    "com.samsung.android.arzone": AppInfo(
        "com.samsung.android.arzone", "AR Zone", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Samsung AR Zone", True
    ),
    "com.samsung.android.aremoji": AppInfo(
        "com.samsung.android.aremoji", "AR Emoji", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Samsung AR Emoji", True
    ),
    "com.samsung.sree": AppInfo(
        "com.samsung.sree", "Samsung SREE", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Samsung service", True
    ),

    # Xiaomi/MIUI Bloatware
    "com.miui.analytics": AppInfo(
        "com.miui.analytics", "MIUI Analytics", RiskLevel.MEDIUM,
        AppCategory.TRACKING, "Xiaomi tracking service", True
    ),
    "com.xiaomi.mipicks": AppInfo(
        "com.xiaomi.mipicks", "Mi Picks", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Xiaomi app store ads", True
    ),
    "com.miui.msa.global": AppInfo(
        "com.miui.msa.global", "MSA", RiskLevel.MEDIUM,
        AppCategory.ADWARE, "MIUI System Ads", True
    ),
    "com.miui.cloudbackup": AppInfo(
        "com.miui.cloudbackup", "Mi Cloud Backup", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Mi Cloud service", True
    ),
    "com.miui.cloudservice": AppInfo(
        "com.miui.cloudservice", "Mi Cloud Service", RiskLevel.MEDIUM,
        AppCategory.TRACKING, "Xiaomi cloud with telemetry", True
    ),
    "com.miui.videoplayer": AppInfo(
        "com.miui.videoplayer", "Mi Video", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Built-in video player", True
    ),
    "com.miui.player": AppInfo(
        "com.miui.player", "Mi Music", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Built-in music player", True
    ),
    "com.mi.android.globalminusscreen": AppInfo(
        "com.mi.android.globalminusscreen", "App Vault", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Xiaomi App Vault", True
    ),
    "com.xiaomi.glgm": AppInfo(
        "com.xiaomi.glgm", "Games", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Xiaomi Games app", True
    ),
    "com.miui.bugreport": AppInfo(
        "com.miui.bugreport", "Bug Report", RiskLevel.MEDIUM,
        AppCategory.TRACKING, "MIUI bug reporting", True
    ),
    "com.xiaomi.payment": AppInfo(
        "com.xiaomi.payment", "Mi Pay", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Mi Pay service", True
    ),

    # Huawei Bloatware
    "com.huawei.hiview": AppInfo(
        "com.huawei.hiview", "HiView", RiskLevel.MEDIUM,
        AppCategory.TRACKING, "Huawei analytics", True
    ),
    "com.huawei.himovie.overseas": AppInfo(
        "com.huawei.himovie.overseas", "Huawei Video", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Huawei Video app", True
    ),
    "com.huawei.appmarket": AppInfo(
        "com.huawei.appmarket", "AppGallery", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Huawei app store", True
    ),

    # Oppo/Realme Bloatware
    "com.oppo.market": AppInfo(
        "com.oppo.market", "Oppo App Market", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Oppo app store", True
    ),
    "com.heytap.browser": AppInfo(
        "com.heytap.browser", "Oppo Browser", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "Oppo built-in browser", True
    ),
    "com.coloros.gamespace": AppInfo(
        "com.coloros.gamespace", "Game Space", RiskLevel.MEDIUM,
        AppCategory.OEM_BLOAT, "ColorOS Game Space", True
    ),

    # Common Pre-installed Bloatware
    "com.opera.mini.native": AppInfo(
        "com.opera.mini.native", "Opera Mini", RiskLevel.MEDIUM,
        AppCategory.BLOATWARE, "Pre-installed browser", True
    ),
    "com.opera.browser": AppInfo(
        "com.opera.browser", "Opera Browser", RiskLevel.MEDIUM,
        AppCategory.BLOATWARE, "Pre-installed browser", True
    ),
    "flipboard.app": AppInfo(
        "flipboard.app", "Flipboard", RiskLevel.MEDIUM,
        AppCategory.BLOATWARE, "Pre-installed news app", True
    ),
    "com.linkedin.android": AppInfo(
        "com.linkedin.android", "LinkedIn", RiskLevel.MEDIUM,
        AppCategory.BLOATWARE, "Pre-installed LinkedIn", True
    ),
    "com.booking": AppInfo(
        "com.booking", "Booking.com", RiskLevel.MEDIUM,
        AppCategory.BLOATWARE, "Pre-installed booking app", True
    ),
    "com.tripadvisor.tripadvisor": AppInfo(
        "com.tripadvisor.tripadvisor", "TripAdvisor", RiskLevel.MEDIUM,
        AppCategory.BLOATWARE, "Pre-installed travel app", True
    ),

    # Game/Entertainment Bloatware
    "com.king.candycrushsaga": AppInfo(
        "com.king.candycrushsaga", "Candy Crush Saga", RiskLevel.MEDIUM,
        AppCategory.BLOATWARE, "Pre-installed game", True
    ),
    "com.zynga.words": AppInfo(
        "com.zynga.words", "Words With Friends", RiskLevel.MEDIUM,
        AppCategory.BLOATWARE, "Pre-installed game", True
    ),

    # Carrier Bloatware
    "com.vzw.hss.myverizon": AppInfo(
        "com.vzw.hss.myverizon", "My Verizon", RiskLevel.MEDIUM,
        AppCategory.CARRIER_BLOAT, "Verizon bloatware", True
    ),
    "com.att.myWireless": AppInfo(
        "com.att.myWireless", "myAT&T", RiskLevel.MEDIUM,
        AppCategory.CARRIER_BLOAT, "AT&T bloatware", True
    ),
    "com.sprint.ce.updater": AppInfo(
        "com.sprint.ce.updater", "Sprint Updater", RiskLevel.MEDIUM,
        AppCategory.CARRIER_BLOAT, "Sprint bloatware", True
    ),
    "com.tmobile.pr.mytmobile": AppInfo(
        "com.tmobile.pr.mytmobile", "T-Mobile", RiskLevel.MEDIUM,
        AppCategory.CARRIER_BLOAT, "T-Mobile app", True
    ),
}

# ============================================================================
# LOW RISK - Mild Bloatware, Optional Apps
# ============================================================================
LOW_RISK_PACKAGES: Dict[str, AppInfo] = {
    # Microsoft Apps (Usually Pre-installed)
    "com.microsoft.office.outlook": AppInfo(
        "com.microsoft.office.outlook", "Outlook", RiskLevel.LOW,
        AppCategory.BLOATWARE, "Pre-installed email app", True
    ),
    "com.microsoft.office.word": AppInfo(
        "com.microsoft.office.word", "Word", RiskLevel.LOW,
        AppCategory.BLOATWARE, "Pre-installed office app", True
    ),
    "com.microsoft.office.excel": AppInfo(
        "com.microsoft.office.excel", "Excel", RiskLevel.LOW,
        AppCategory.BLOATWARE, "Pre-installed office app", True
    ),
    "com.microsoft.office.powerpoint": AppInfo(
        "com.microsoft.office.powerpoint", "PowerPoint", RiskLevel.LOW,
        AppCategory.BLOATWARE, "Pre-installed office app", True
    ),
    "com.microsoft.skydrive": AppInfo(
        "com.microsoft.skydrive", "OneDrive", RiskLevel.LOW,
        AppCategory.BLOATWARE, "Pre-installed cloud storage", True
    ),

    # Google Bloatware (Optional Apps)
    "com.google.android.apps.tachyon": AppInfo(
        "com.google.android.apps.tachyon", "Google Duo/Meet", RiskLevel.LOW,
        AppCategory.BLOATWARE, "Google video calling", True
    ),
    "com.google.android.apps.magazines": AppInfo(
        "com.google.android.apps.magazines", "Google News", RiskLevel.LOW,
        AppCategory.BLOATWARE, "Google News app", True
    ),
    "com.google.android.videos": AppInfo(
        "com.google.android.videos", "Google Play Movies", RiskLevel.LOW,
        AppCategory.BLOATWARE, "Google Movies app", True
    ),
    "com.google.android.music": AppInfo(
        "com.google.android.music", "Google Play Music", RiskLevel.LOW,
        AppCategory.BLOATWARE, "Deprecated music app", True
    ),
    "com.google.android.apps.books": AppInfo(
        "com.google.android.apps.books", "Google Play Books", RiskLevel.LOW,
        AppCategory.BLOATWARE, "Google Books app", True
    ),
    "com.google.android.apps.googleassistant": AppInfo(
        "com.google.android.apps.googleassistant", "Google Assistant", RiskLevel.LOW,
        AppCategory.OEM_BLOAT, "Google Assistant standalone", True
    ),

    # Demo/Sample Apps
    "com.android.samples": AppInfo(
        "com.android.samples", "Sample Apps", RiskLevel.LOW,
        AppCategory.BLOATWARE, "Android sample apps", True
    ),
}

# ============================================================================
# PATTERN MATCHING - Detect risky apps by name patterns
# ============================================================================

# Patterns that indicate HIGH RISK
HIGH_RISK_PATTERNS = [
    # Fake Cleaners/Boosters
    r".*clean(er|master|up).*",
    r".*boost(er)?.*speed.*",
    r".*speed.*boost(er)?.*",
    r".*ram.*clean.*",
    r".*junk.*clean.*",
    r".*cache.*clean.*",
    r".*phone.*clean.*",
    r".*optimizer.*",
    r".*turbo.*clean.*",
    r".*super.*clean.*",

    # Fake Antivirus
    r".*antivirus.*free.*",
    r".*virus.*clean.*",
    r".*security.*scan.*",
    r".*malware.*scan.*",

    # Fake Battery
    r".*battery.*saver.*",
    r".*battery.*doctor.*",
    r".*battery.*boost.*",
    r".*power.*saver.*",
    r".*super.*battery.*",

    # Suspicious VPN patterns
    r".*free.*vpn.*",
    r".*vpn.*free.*",
    r".*vpn.*master.*",
    r".*super.*vpn.*",
    r".*turbo.*vpn.*",

    # Popup ad apps
    r".*popup.*",
    r".*lockscreen.*reward.*",
    r".*screen.*locker.*ad.*",

    # Loan shark apps
    r".*quick.*cash.*",
    r".*instant.*loan.*",
    r".*fast.*loan.*",
    r".*easy.*loan.*",

    # Crypto miners
    r".*crypto.*mine.*",
    r".*bitcoin.*mine.*",
    r".*coin.*mine.*",
]

# Patterns that indicate MEDIUM RISK
MEDIUM_RISK_PATTERNS = [
    # Ad-supported replacements
    r".*caller.*id.*",
    r".*dialer.*pro.*",
    r".*sms.*replacement.*",
    r".*launcher.*pro.*",
    r".*keyboard.*free.*",

    # Tracking/Analytics
    r".*analytics.*",
    r".*telemetry.*",
    r".*tracking.*",

    # OEM services
    r"com\.(samsung|xiaomi|huawei|oppo|vivo|realme)\..*",
    r"com\.miui\..*",
    r"com\.coloros\..*",
    r"com\.heytap\..*",
]

# Patterns for SAFE system apps (should not be removed)
SAFE_PATTERNS = [
    r"com\.android\.(systemui|settings|launcher|phone|contacts|messaging|calendar|providers\..*)",
    r"com\.google\.android\.(gms|gsf|play\.services|webview)",
    r"com\.android\.vending",  # Play Store
    r"com\.android\.inputmethod\..*",
    r"com\.android\.server\..*",
    r"android",
]

# Package prefixes that indicate system/safe apps
SAFE_PREFIXES = [
    "com.android.providers.",
    "com.android.server.",
    "com.android.internal.",
    "com.qualcomm.",
    "com.mediatek.",
    "android.",
]

# ============================================================================
# SUSPICIOUS PERMISSION COMBINATIONS
# ============================================================================
DANGEROUS_PERMISSION_COMBOS = {
    "data_harvester": [
        "android.permission.READ_CONTACTS",
        "android.permission.READ_CALL_LOG",
        "android.permission.READ_SMS",
        "android.permission.INTERNET",
    ],
    "spyware": [
        "android.permission.RECORD_AUDIO",
        "android.permission.CAMERA",
        "android.permission.ACCESS_FINE_LOCATION",
        "android.permission.INTERNET",
    ],
    "adware": [
        "android.permission.SYSTEM_ALERT_WINDOW",
        "android.permission.INTERNET",
        "android.permission.RECEIVE_BOOT_COMPLETED",
    ],
    "stalkerware": [
        "android.permission.ACCESS_FINE_LOCATION",
        "android.permission.READ_CONTACTS",
        "android.permission.READ_SMS",
        "android.permission.READ_CALL_LOG",
        "android.permission.RECORD_AUDIO",
    ],
}

# Permissions that are suspicious for simple apps
OVER_PRIVILEGED_PERMISSIONS = [
    "android.permission.SYSTEM_ALERT_WINDOW",  # Draw over other apps
    "android.permission.WRITE_SETTINGS",
    "android.permission.READ_PHONE_STATE",
    "android.permission.READ_CONTACTS",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.RECORD_AUDIO",
    "android.permission.CAMERA",
    "android.permission.READ_SMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.READ_CALL_LOG",
    "android.permission.PROCESS_OUTGOING_CALLS",
    "android.permission.REQUEST_INSTALL_PACKAGES",
    "android.permission.BIND_ACCESSIBILITY_SERVICE",
    "android.permission.BIND_DEVICE_ADMIN",
]


class AppDatabase:
    """Database handler for app risk lookups."""

    def __init__(self):
        """Initialize the database with all known packages."""
        self.packages: Dict[str, AppInfo] = {}
        self._load_packages()

        # Compile regex patterns
        self.high_risk_patterns = [re.compile(p, re.IGNORECASE) for p in HIGH_RISK_PATTERNS]
        self.medium_risk_patterns = [re.compile(p, re.IGNORECASE) for p in MEDIUM_RISK_PATTERNS]
        self.safe_patterns = [re.compile(p, re.IGNORECASE) for p in SAFE_PATTERNS]

    def _load_packages(self):
        """Load all packages into the main dictionary."""
        self.packages.update(CRITICAL_PACKAGES)
        self.packages.update(HIGH_RISK_PACKAGES)
        self.packages.update(MEDIUM_RISK_PACKAGES)
        self.packages.update(LOW_RISK_PACKAGES)

    def lookup(self, package_name: str) -> Optional[AppInfo]:
        """
        Look up a package in the database.

        Args:
            package_name: The package name to look up

        Returns:
            AppInfo if found, None otherwise
        """
        return self.packages.get(package_name)

    def is_safe_system_app(self, package_name: str) -> bool:
        """Check if package is a safe system app that shouldn't be removed."""
        # Check safe prefixes
        for prefix in SAFE_PREFIXES:
            if package_name.startswith(prefix):
                return True

        # Check safe patterns
        for pattern in self.safe_patterns:
            if pattern.match(package_name):
                return True

        return False

    def analyze_by_pattern(self, package_name: str) -> RiskLevel:
        """
        Analyze a package by name patterns.

        Args:
            package_name: The package name to analyze

        Returns:
            Risk level based on pattern matching
        """
        # Check if safe first
        if self.is_safe_system_app(package_name):
            return RiskLevel.SAFE

        # Check high risk patterns
        for pattern in self.high_risk_patterns:
            if pattern.search(package_name):
                return RiskLevel.HIGH

        # Check medium risk patterns
        for pattern in self.medium_risk_patterns:
            if pattern.search(package_name):
                return RiskLevel.MEDIUM

        return RiskLevel.UNKNOWN

    def get_risk_level(self, package_name: str) -> RiskLevel:
        """
        Get the risk level of a package.

        Args:
            package_name: The package name to check

        Returns:
            Risk level (CRITICAL, HIGH, MEDIUM, LOW, SAFE, or UNKNOWN)
        """
        # Check known packages first
        info = self.lookup(package_name)
        if info:
            return info.risk

        # Check if it's a safe system app
        if self.is_safe_system_app(package_name):
            return RiskLevel.SAFE

        # Analyze by patterns
        return self.analyze_by_pattern(package_name)

    def get_all_by_risk(self, risk_level: RiskLevel) -> List[AppInfo]:
        """Get all known apps of a specific risk level."""
        return [info for info in self.packages.values() if info.risk == risk_level]

    def search(self, query: str) -> List[AppInfo]:
        """Search for apps by name or package."""
        query_lower = query.lower()
        results = []
        for info in self.packages.values():
            if query_lower in info.package.lower() or query_lower in info.name.lower():
                results.append(info)
        return results


# Singleton instance
_db_instance: Optional[AppDatabase] = None


def get_database() -> AppDatabase:
    """Get the singleton database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = AppDatabase()
    return _db_instance
