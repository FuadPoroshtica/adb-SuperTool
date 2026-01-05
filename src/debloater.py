"""
Samsung Device Debloater Module
Aggressive debloating for Samsung entry-level devices (A05, A06, A07, A16, A17, etc.)
Makes Android minimal and lightweight

Based on community research from:
- https://github.com/khlam/debloat-samsung-android
- https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation
- https://github.com/Achno/debloat-samsung-ADB-shizuku
- https://github.com/invinciblevenom/debloat_samsung_android
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Set, Tuple, Optional


class DebloatLevel(Enum):
    """Debloat intensity levels."""
    LIGHT = "light"       # Remove obvious bloatware, keep Samsung features
    MEDIUM = "medium"     # Remove most bloatware, keep essential Samsung apps
    AGGRESSIVE = "aggressive"  # Maximum removal for ultra-minimal experience
    CUSTOM = "custom"     # User selects categories


class PackageCategory(Enum):
    """Categories of packages for selective removal."""
    SAMSUNG_BLOAT = "samsung_bloat"
    SAMSUNG_BIXBY = "samsung_bixby"
    SAMSUNG_AR_EMOJI = "samsung_ar_emoji"
    SAMSUNG_GAMES = "samsung_games"
    SAMSUNG_THEMES = "samsung_themes"
    SAMSUNG_KNOX = "samsung_knox"
    SAMSUNG_DEX = "samsung_dex"
    SAMSUNG_HEALTH = "samsung_health"
    SAMSUNG_PAY = "samsung_pay"
    SAMSUNG_PASS = "samsung_pass"
    SAMSUNG_CLOUD = "samsung_cloud"
    SAMSUNG_KIDS = "samsung_kids"
    SAMSUNG_EDGE = "samsung_edge"
    SAMSUNG_SHARING = "samsung_sharing"
    MICROSOFT = "microsoft"
    FACEBOOK = "facebook"
    GOOGLE_BLOAT = "google_bloat"
    CARRIER = "carrier"
    AMAZON = "amazon"
    NETFLIX = "netflix"
    LINKEDIN = "linkedin"
    OTHER_BLOAT = "other_bloat"


@dataclass
class DebloatPackage:
    """Package information for debloating."""
    package: str
    name: str
    category: PackageCategory
    description: str
    safe_to_remove: bool = True
    breaks_feature: str = ""  # What feature breaks if removed


# ============================================================================
# SAMSUNG ENTRY-LEVEL DEVICE DETECTION
# ============================================================================
SAMSUNG_ENTRY_LEVEL_MODELS = [
    # A0x Series (Ultra Budget)
    "SM-A055", "SM-A056",  # A05, A05s
    "SM-A065", "SM-A066",  # A06
    "SM-A075", "SM-A076",  # A07

    # A1x Series (Budget)
    "SM-A165", "SM-A166",  # A16
    "SM-A175", "SM-A176",  # A17
    "SM-A145", "SM-A146",  # A14
    "SM-A135", "SM-A136",  # A13
    "SM-A125", "SM-A127",  # A12

    # A2x Series (Lower Mid-range)
    "SM-A245", "SM-A246",  # A24
    "SM-A235", "SM-A236",  # A23
    "SM-A225", "SM-A226",  # A22

    # M Series (Budget)
    "SM-M055",  # M05
    "SM-M145", "SM-M146",  # M14
    "SM-M155", "SM-M156",  # M15

    # F Series (Budget - some regions)
    "SM-F055", "SM-F145",
]


# ============================================================================
# PACKAGE LISTS BY CATEGORY
# ============================================================================

# Samsung Bixby - AI Assistant (Not useful on entry-level, wastes RAM)
SAMSUNG_BIXBY_PACKAGES = [
    DebloatPackage("com.samsung.android.bixby.agent", "Bixby Voice",
                   PackageCategory.SAMSUNG_BIXBY, "Bixby voice assistant"),
    DebloatPackage("com.samsung.android.bixby.service", "Bixby Service",
                   PackageCategory.SAMSUNG_BIXBY, "Bixby background service"),
    DebloatPackage("com.samsung.android.bixby.wakeup", "Bixby Wakeup",
                   PackageCategory.SAMSUNG_BIXBY, "Bixby wake word detection"),
    DebloatPackage("com.samsung.android.visionintelligence", "Bixby Vision",
                   PackageCategory.SAMSUNG_BIXBY, "Bixby camera AI features"),
    DebloatPackage("com.samsung.android.bixby.agent.dummy", "Bixby Dummy",
                   PackageCategory.SAMSUNG_BIXBY, "Bixby placeholder"),
    DebloatPackage("com.samsung.android.bixbyvision.framework", "Bixby Vision Framework",
                   PackageCategory.SAMSUNG_BIXBY, "Bixby Vision core"),
    DebloatPackage("com.samsung.android.app.routines", "Bixby Routines",
                   PackageCategory.SAMSUNG_BIXBY, "Automation routines"),
    DebloatPackage("com.samsung.android.app.spage", "Samsung Free/Bixby Home",
                   PackageCategory.SAMSUNG_BIXBY, "Left home screen page"),
    DebloatPackage("com.samsung.android.voc", "Bixby Dictation",
                   PackageCategory.SAMSUNG_BIXBY, "Voice typing for Bixby"),
]

# Samsung AR/Emoji - Heavy and useless on entry-level
SAMSUNG_AR_EMOJI_PACKAGES = [
    DebloatPackage("com.samsung.android.aremoji", "AR Emoji",
                   PackageCategory.SAMSUNG_AR_EMOJI, "AR Emoji creation"),
    DebloatPackage("com.samsung.android.arzone", "AR Zone",
                   PackageCategory.SAMSUNG_AR_EMOJI, "AR features hub"),
    DebloatPackage("com.samsung.android.livestickers", "Live Stickers",
                   PackageCategory.SAMSUNG_AR_EMOJI, "Animated stickers"),
    DebloatPackage("com.samsung.android.app.dressroom", "AR Emoji Editor",
                   PackageCategory.SAMSUNG_AR_EMOJI, "AR Emoji customization"),
    DebloatPackage("com.sec.android.mimage.avatarstickers", "Avatar Stickers",
                   PackageCategory.SAMSUNG_AR_EMOJI, "AR avatar stickers"),
    DebloatPackage("com.samsung.android.aremojieditor", "AR Emoji Editor",
                   PackageCategory.SAMSUNG_AR_EMOJI, "Edit AR Emojis"),
    DebloatPackage("com.samsung.android.emojiupdater", "Emoji Updater",
                   PackageCategory.SAMSUNG_AR_EMOJI, "Updates emoji"),
    DebloatPackage("com.sec.android.mimage.avatar.stickers", "Avatar Stickers",
                   PackageCategory.SAMSUNG_AR_EMOJI, "More avatar stickers"),
]

# Samsung Games - Gaming hub (useless on weak GPUs)
SAMSUNG_GAMES_PACKAGES = [
    DebloatPackage("com.samsung.android.game.gamehome", "Game Launcher",
                   PackageCategory.SAMSUNG_GAMES, "Samsung Game Launcher"),
    DebloatPackage("com.samsung.android.game.gametools", "Game Tools",
                   PackageCategory.SAMSUNG_GAMES, "In-game tools overlay"),
    DebloatPackage("com.samsung.android.game.gos", "Game Optimizing Service",
                   PackageCategory.SAMSUNG_GAMES, "Game performance limiter"),
    DebloatPackage("com.samsung.android.gamedriver", "Game Driver",
                   PackageCategory.SAMSUNG_GAMES, "Custom GPU drivers"),
    DebloatPackage("com.enhance.gameservice", "Game Service",
                   PackageCategory.SAMSUNG_GAMES, "Gaming enhancement"),
    DebloatPackage("com.samsung.android.game.gamebooster", "Game Booster",
                   PackageCategory.SAMSUNG_GAMES, "Game performance boost"),
]

# Samsung Themes - Wastes storage and battery
SAMSUNG_THEMES_PACKAGES = [
    DebloatPackage("com.samsung.android.themestore", "Galaxy Themes",
                   PackageCategory.SAMSUNG_THEMES, "Theme store"),
    DebloatPackage("com.samsung.android.themecenter", "Theme Center",
                   PackageCategory.SAMSUNG_THEMES, "Theme management"),
    DebloatPackage("com.samsung.android.app.dofviewer", "Wallpaper Service",
                   PackageCategory.SAMSUNG_THEMES, "Dynamic wallpapers"),
    DebloatPackage("com.samsung.android.dynamiclock", "Dynamic Lock Screen",
                   PackageCategory.SAMSUNG_THEMES, "Lock screen customization"),
    DebloatPackage("com.samsung.android.wallpaper.res", "Wallpaper Resources",
                   PackageCategory.SAMSUNG_THEMES, "Default wallpapers"),
]

# Samsung Knox - Enterprise security (not needed for consumers)
SAMSUNG_KNOX_PACKAGES = [
    DebloatPackage("com.samsung.android.knox.containercore", "Knox Container",
                   PackageCategory.SAMSUNG_KNOX, "Knox work profile"),
    DebloatPackage("com.sec.enterprise.knox.cloudmdm.smdms", "Knox MDM",
                   PackageCategory.SAMSUNG_KNOX, "Mobile device management"),
    DebloatPackage("com.samsung.android.knox.analytics.uploader", "Knox Analytics",
                   PackageCategory.SAMSUNG_KNOX, "Knox usage analytics"),
    DebloatPackage("com.samsung.knox.securefolder", "Secure Folder",
                   PackageCategory.SAMSUNG_KNOX, "Encrypted folder", True, "Secure Folder feature"),
    DebloatPackage("com.samsung.android.knox.containeragent", "Knox Agent",
                   PackageCategory.SAMSUNG_KNOX, "Knox background agent"),
    DebloatPackage("com.samsung.android.kgclient", "Knox Guard",
                   PackageCategory.SAMSUNG_KNOX, "Knox Guard client"),
    DebloatPackage("com.samsung.android.knox.pushmanager", "Knox Push",
                   PackageCategory.SAMSUNG_KNOX, "Knox push notifications"),
    DebloatPackage("com.samsung.android.knox.kpecore", "Knox Platform",
                   PackageCategory.SAMSUNG_KNOX, "Knox platform core"),
    DebloatPackage("com.samsung.android.knox.attestation", "Knox Attestation",
                   PackageCategory.SAMSUNG_KNOX, "Security attestation"),
]

# Samsung DeX - Desktop mode (not available on entry-level)
SAMSUNG_DEX_PACKAGES = [
    DebloatPackage("com.samsung.android.mdx", "Samsung DeX",
                   PackageCategory.SAMSUNG_DEX, "Desktop experience"),
    DebloatPackage("com.samsung.android.mdx.kit", "DeX Kit",
                   PackageCategory.SAMSUNG_DEX, "DeX components"),
    DebloatPackage("com.samsung.android.mdx.quickboard", "DeX Keyboard",
                   PackageCategory.SAMSUNG_DEX, "DeX on-screen keyboard"),
    DebloatPackage("com.sec.android.desktopmode.uiservice", "DeX UI",
                   PackageCategory.SAMSUNG_DEX, "DeX user interface"),
    DebloatPackage("com.samsung.desktopsystemui", "DeX System UI",
                   PackageCategory.SAMSUNG_DEX, "DeX system interface"),
]

# Samsung Health - Fitness tracking
SAMSUNG_HEALTH_PACKAGES = [
    DebloatPackage("com.samsung.android.forest", "Digital Wellbeing (Samsung)",
                   PackageCategory.SAMSUNG_HEALTH, "Screen time tracking"),
    DebloatPackage("com.sec.android.app.shealth", "Samsung Health",
                   PackageCategory.SAMSUNG_HEALTH, "Health tracking app", True, "Samsung Health"),
    DebloatPackage("com.samsung.android.service.health", "Health Service",
                   PackageCategory.SAMSUNG_HEALTH, "Health background service"),
    DebloatPackage("com.samsung.android.healthplatform", "Health Platform",
                   PackageCategory.SAMSUNG_HEALTH, "Health data platform"),
]

# Samsung Pay/Wallet
SAMSUNG_PAY_PACKAGES = [
    DebloatPackage("com.samsung.android.spay", "Samsung Pay",
                   PackageCategory.SAMSUNG_PAY, "Mobile payments", True, "Samsung Pay"),
    DebloatPackage("com.samsung.android.spayfw", "Samsung Pay Framework",
                   PackageCategory.SAMSUNG_PAY, "Payment framework"),
    DebloatPackage("com.samsung.android.samsungpay.gear", "Samsung Pay Gear",
                   PackageCategory.SAMSUNG_PAY, "Watch payments"),
    DebloatPackage("com.samsung.android.authfw", "Samsung Auth Framework",
                   PackageCategory.SAMSUNG_PAY, "Authentication"),
    DebloatPackage("com.samsung.android.spaymini", "Samsung Pay Mini",
                   PackageCategory.SAMSUNG_PAY, "Lite payment app"),
]

# Samsung Pass - Password manager
SAMSUNG_PASS_PACKAGES = [
    DebloatPackage("com.samsung.android.samsungpass", "Samsung Pass",
                   PackageCategory.SAMSUNG_PASS, "Password manager", True, "Samsung Pass"),
    DebloatPackage("com.samsung.android.samsungpassautofill", "Samsung Pass Autofill",
                   PackageCategory.SAMSUNG_PASS, "Autofill service"),
    DebloatPackage("com.samsung.android.autofill", "Samsung Autofill",
                   PackageCategory.SAMSUNG_PASS, "Form autofill"),
]

# Samsung Cloud
SAMSUNG_CLOUD_PACKAGES = [
    DebloatPackage("com.samsung.android.scloud", "Samsung Cloud",
                   PackageCategory.SAMSUNG_CLOUD, "Cloud backup", True, "Samsung Cloud backup"),
    DebloatPackage("com.samsung.android.scloud.quota", "Cloud Quota",
                   PackageCategory.SAMSUNG_CLOUD, "Cloud storage management"),
    DebloatPackage("com.samsung.android.rubin.app", "Samsung Customization",
                   PackageCategory.SAMSUNG_CLOUD, "Personalization service"),
    DebloatPackage("com.samsung.android.mobileservice", "Samsung Mobile Services",
                   PackageCategory.SAMSUNG_CLOUD, "Samsung account services"),
]

# Samsung Kids Mode
SAMSUNG_KIDS_PACKAGES = [
    DebloatPackage("com.samsung.android.kidsinstaller", "Kids Installer",
                   PackageCategory.SAMSUNG_KIDS, "Kids mode setup"),
    DebloatPackage("com.samsung.android.app.kidshome", "Samsung Kids",
                   PackageCategory.SAMSUNG_KIDS, "Kids mode launcher"),
    DebloatPackage("com.samsung.android.kidsdrawingapp", "Kids Drawing",
                   PackageCategory.SAMSUNG_KIDS, "Drawing app for kids"),
]

# Samsung Edge Panels
SAMSUNG_EDGE_PACKAGES = [
    DebloatPackage("com.samsung.android.app.appsedge", "Apps Edge",
                   PackageCategory.SAMSUNG_EDGE, "App shortcuts panel"),
    DebloatPackage("com.samsung.android.app.taskedge", "Task Edge",
                   PackageCategory.SAMSUNG_EDGE, "Task shortcuts"),
    DebloatPackage("com.samsung.android.app.clipboardedge", "Clipboard Edge",
                   PackageCategory.SAMSUNG_EDGE, "Clipboard panel"),
    DebloatPackage("com.samsung.android.app.cocktailbarservice", "Edge Panels",
                   PackageCategory.SAMSUNG_EDGE, "Edge panel service"),
    DebloatPackage("com.samsung.android.service.peoplestripe", "People Edge",
                   PackageCategory.SAMSUNG_EDGE, "Contact shortcuts"),
    DebloatPackage("com.samsung.android.app.smartcapture", "Smart Capture",
                   PackageCategory.SAMSUNG_EDGE, "Screenshot edge panel"),
]

# Samsung Sharing Features
SAMSUNG_SHARING_PACKAGES = [
    DebloatPackage("com.samsung.android.app.sharelive", "Share Live",
                   PackageCategory.SAMSUNG_SHARING, "Live screen sharing"),
    DebloatPackage("com.samsung.android.app.simplesharing", "Simple Sharing",
                   PackageCategory.SAMSUNG_SHARING, "Quick Share lite"),
    DebloatPackage("com.samsung.android.privateshare", "Private Share",
                   PackageCategory.SAMSUNG_SHARING, "Secure file sharing"),
    DebloatPackage("com.samsung.android.aware.service", "Aware Service",
                   PackageCategory.SAMSUNG_SHARING, "Nearby device awareness"),
    DebloatPackage("com.samsung.android.allshare.service.mediashare", "Media Share",
                   PackageCategory.SAMSUNG_SHARING, "DLNA media sharing"),
    DebloatPackage("com.samsung.android.smartmirroring", "Smart View",
                   PackageCategory.SAMSUNG_SHARING, "Screen mirroring", True, "Screen mirroring"),
    DebloatPackage("com.sec.android.easyMover.Agent", "Smart Switch Agent",
                   PackageCategory.SAMSUNG_SHARING, "Smart Switch helper"),
    DebloatPackage("com.sec.android.easyMover", "Smart Switch",
                   PackageCategory.SAMSUNG_SHARING, "Data transfer app"),
    DebloatPackage("com.samsung.android.app.galaxyfinder", "Finder",
                   PackageCategory.SAMSUNG_SHARING, "Samsung search"),
]

# Samsung General Bloatware
SAMSUNG_GENERAL_BLOAT = [
    DebloatPackage("com.samsung.android.app.tips", "Samsung Tips",
                   PackageCategory.SAMSUNG_BLOAT, "Usage tips"),
    DebloatPackage("com.samsung.android.app.reminder", "Reminder",
                   PackageCategory.SAMSUNG_BLOAT, "Samsung Reminder app"),
    DebloatPackage("com.samsung.android.calendar", "Samsung Calendar",
                   PackageCategory.SAMSUNG_BLOAT, "Calendar app", True, "Samsung Calendar"),
    DebloatPackage("com.samsung.android.app.notes", "Samsung Notes",
                   PackageCategory.SAMSUNG_BLOAT, "Notes app", True, "Samsung Notes"),
    DebloatPackage("com.sec.android.app.voicenote", "Voice Recorder",
                   PackageCategory.SAMSUNG_BLOAT, "Voice recording"),
    DebloatPackage("com.sec.android.daemonapp", "Weather Daemon",
                   PackageCategory.SAMSUNG_BLOAT, "Weather widget service"),
    DebloatPackage("com.samsung.android.weather", "Samsung Weather",
                   PackageCategory.SAMSUNG_BLOAT, "Weather app"),
    DebloatPackage("com.samsung.android.app.social", "What's New",
                   PackageCategory.SAMSUNG_BLOAT, "Samsung promotions"),
    DebloatPackage("com.samsung.android.oneconnect", "SmartThings",
                   PackageCategory.SAMSUNG_BLOAT, "IoT control", True, "SmartThings"),
    DebloatPackage("com.samsung.android.visionarapps", "Vision AR Apps",
                   PackageCategory.SAMSUNG_BLOAT, "AR applications"),
    DebloatPackage("com.sec.android.widgetapp.easymodecontactswidget", "Easy Mode Widget",
                   PackageCategory.SAMSUNG_BLOAT, "Easy mode contacts"),
    DebloatPackage("com.sec.android.widgetapp.samsungapps", "Galaxy Store Widget",
                   PackageCategory.SAMSUNG_BLOAT, "App store widget"),
    DebloatPackage("com.samsung.android.da.daagent", "Device Care Agent",
                   PackageCategory.SAMSUNG_BLOAT, "Device optimization agent"),
    DebloatPackage("com.samsung.android.fmm", "Find My Mobile",
                   PackageCategory.SAMSUNG_BLOAT, "Device finder", True, "Find My Mobile"),
    DebloatPackage("com.sec.android.app.quicktool", "Quick Tools",
                   PackageCategory.SAMSUNG_BLOAT, "Quick utilities"),
    DebloatPackage("com.samsung.android.video", "Samsung Video",
                   PackageCategory.SAMSUNG_BLOAT, "Video player"),
    DebloatPackage("com.sec.android.app.music", "Samsung Music",
                   PackageCategory.SAMSUNG_BLOAT, "Music player"),
    DebloatPackage("com.samsung.android.email.provider", "Email Provider",
                   PackageCategory.SAMSUNG_BLOAT, "Samsung Email"),
    DebloatPackage("com.samsung.android.app.sbrowseredge", "Browser Edge",
                   PackageCategory.SAMSUNG_BLOAT, "Samsung Internet edge panel"),
    DebloatPackage("com.sec.android.app.billing", "Samsung Billing",
                   PackageCategory.SAMSUNG_BLOAT, "In-app purchases"),
    DebloatPackage("com.samsung.android.app.watchmanager", "Galaxy Wearable",
                   PackageCategory.SAMSUNG_BLOAT, "Watch app"),
    DebloatPackage("com.samsung.android.app.camera.sticker.facearavatar.preload", "Camera Stickers",
                   PackageCategory.SAMSUNG_BLOAT, "Camera AR stickers"),
    DebloatPackage("com.samsung.storyservice", "Story Service",
                   PackageCategory.SAMSUNG_BLOAT, "Story feature"),
    DebloatPackage("com.samsung.android.accessibility.talkback", "Samsung TalkBack",
                   PackageCategory.SAMSUNG_BLOAT, "Samsung screen reader"),
    DebloatPackage("com.samsung.android.wellbeing", "Digital Wellbeing",
                   PackageCategory.SAMSUNG_BLOAT, "Screen time"),
    DebloatPackage("com.samsung.android.app.ledcover", "LED Cover",
                   PackageCategory.SAMSUNG_BLOAT, "LED case support"),
    DebloatPackage("com.samsung.android.app.routines", "Routines",
                   PackageCategory.SAMSUNG_BLOAT, "Automation"),
    DebloatPackage("com.samsung.android.beaconmanager", "Beacon Manager",
                   PackageCategory.SAMSUNG_BLOAT, "Bluetooth beacon"),
    DebloatPackage("com.samsung.android.app.omcagent", "OMC Agent",
                   PackageCategory.SAMSUNG_BLOAT, "Configuration agent"),
    DebloatPackage("com.samsung.android.ipsgeofence", "Geofence",
                   PackageCategory.SAMSUNG_BLOAT, "Location geofencing"),
    DebloatPackage("com.samsung.android.location", "Samsung Location SDK",
                   PackageCategory.SAMSUNG_BLOAT, "Location services"),
    DebloatPackage("com.samsung.android.mcfds", "MCF DS",
                   PackageCategory.SAMSUNG_BLOAT, "Configuration service"),
    DebloatPackage("com.samsung.android.dqagent", "DQA",
                   PackageCategory.SAMSUNG_BLOAT, "Device quality agent"),
    DebloatPackage("com.samsung.android.sdm.config", "SDM Config",
                   PackageCategory.SAMSUNG_BLOAT, "Samsung config"),
    DebloatPackage("com.samsung.android.mcfserver", "MCF Server",
                   PackageCategory.SAMSUNG_BLOAT, "Config server"),
    DebloatPackage("com.samsung.android.provider.filterprovider", "Filter Provider",
                   PackageCategory.SAMSUNG_BLOAT, "Photo filters"),
]

# Microsoft Pre-installed Apps
MICROSOFT_PACKAGES = [
    DebloatPackage("com.microsoft.appmanager", "Microsoft Apps",
                   PackageCategory.MICROSOFT, "Microsoft app manager"),
    DebloatPackage("com.microsoft.office.outlook", "Outlook",
                   PackageCategory.MICROSOFT, "Email client"),
    DebloatPackage("com.microsoft.office.word", "Word",
                   PackageCategory.MICROSOFT, "Document editor"),
    DebloatPackage("com.microsoft.office.excel", "Excel",
                   PackageCategory.MICROSOFT, "Spreadsheet"),
    DebloatPackage("com.microsoft.office.powerpoint", "PowerPoint",
                   PackageCategory.MICROSOFT, "Presentations"),
    DebloatPackage("com.microsoft.office.officehub", "Office Hub",
                   PackageCategory.MICROSOFT, "Office apps hub"),
    DebloatPackage("com.microsoft.office.officehubrow", "Office",
                   PackageCategory.MICROSOFT, "Office mobile"),
    DebloatPackage("com.microsoft.skydrive", "OneDrive",
                   PackageCategory.MICROSOFT, "Cloud storage"),
    DebloatPackage("com.microsoft.office.onenote", "OneNote",
                   PackageCategory.MICROSOFT, "Note taking"),
    DebloatPackage("com.linkedin.android", "LinkedIn",
                   PackageCategory.MICROSOFT, "Professional network"),
    DebloatPackage("com.microsoft.todos", "Microsoft To Do",
                   PackageCategory.MICROSOFT, "Task manager"),
    DebloatPackage("com.microsoft.bing", "Bing",
                   PackageCategory.MICROSOFT, "Search app"),
]

# Facebook Pre-installed Apps
FACEBOOK_PACKAGES = [
    DebloatPackage("com.facebook.katana", "Facebook",
                   PackageCategory.FACEBOOK, "Social media"),
    DebloatPackage("com.facebook.appmanager", "Facebook App Manager",
                   PackageCategory.FACEBOOK, "FB app updater"),
    DebloatPackage("com.facebook.system", "Facebook System",
                   PackageCategory.FACEBOOK, "FB system services"),
    DebloatPackage("com.facebook.services", "Facebook Services",
                   PackageCategory.FACEBOOK, "FB background services"),
    DebloatPackage("com.instagram.android", "Instagram",
                   PackageCategory.FACEBOOK, "Photo sharing"),
    DebloatPackage("com.whatsapp", "WhatsApp",
                   PackageCategory.FACEBOOK, "Messaging", True, "WhatsApp"),
    DebloatPackage("com.facebook.orca", "Messenger",
                   PackageCategory.FACEBOOK, "FB Messenger"),
]

# Google Bloatware (non-essential)
GOOGLE_BLOAT_PACKAGES = [
    DebloatPackage("com.google.android.apps.tachyon", "Google Duo/Meet",
                   PackageCategory.GOOGLE_BLOAT, "Video calling"),
    DebloatPackage("com.google.android.apps.docs", "Google Docs",
                   PackageCategory.GOOGLE_BLOAT, "Document editor"),
    DebloatPackage("com.google.android.apps.docs.editors.sheets", "Google Sheets",
                   PackageCategory.GOOGLE_BLOAT, "Spreadsheet"),
    DebloatPackage("com.google.android.apps.docs.editors.slides", "Google Slides",
                   PackageCategory.GOOGLE_BLOAT, "Presentations"),
    DebloatPackage("com.google.android.videos", "Google TV",
                   PackageCategory.GOOGLE_BLOAT, "Movie rentals"),
    DebloatPackage("com.google.android.music", "Play Music",
                   PackageCategory.GOOGLE_BLOAT, "Deprecated music app"),
    DebloatPackage("com.google.android.apps.magazines", "Google News",
                   PackageCategory.GOOGLE_BLOAT, "News aggregator"),
    DebloatPackage("com.google.android.apps.books", "Play Books",
                   PackageCategory.GOOGLE_BLOAT, "E-book reader"),
    DebloatPackage("com.google.android.apps.podcasts", "Google Podcasts",
                   PackageCategory.GOOGLE_BLOAT, "Podcast app"),
    DebloatPackage("com.google.android.apps.googleassistant", "Google Assistant",
                   PackageCategory.GOOGLE_BLOAT, "Voice assistant", True, "Google Assistant"),
    DebloatPackage("com.google.ar.core", "AR Core",
                   PackageCategory.GOOGLE_BLOAT, "AR platform"),
    DebloatPackage("com.google.vr.vrcore", "VR Services",
                   PackageCategory.GOOGLE_BLOAT, "VR platform"),
    DebloatPackage("com.google.android.apps.wellbeing", "Digital Wellbeing",
                   PackageCategory.GOOGLE_BLOAT, "Screen time tracking"),
    DebloatPackage("com.google.android.feedback", "Feedback",
                   PackageCategory.GOOGLE_BLOAT, "Send feedback"),
    DebloatPackage("com.google.android.printservice.recommendation", "Print Service",
                   PackageCategory.GOOGLE_BLOAT, "Print recommendations"),
    DebloatPackage("com.android.chrome", "Chrome",
                   PackageCategory.GOOGLE_BLOAT, "Web browser", True, "Chrome browser"),
    DebloatPackage("com.google.android.youtube", "YouTube",
                   PackageCategory.GOOGLE_BLOAT, "Video app", True, "YouTube"),
    DebloatPackage("com.google.android.apps.youtube.music", "YouTube Music",
                   PackageCategory.GOOGLE_BLOAT, "Music streaming"),
]

# Amazon Pre-installed
AMAZON_PACKAGES = [
    DebloatPackage("com.amazon.fv", "Amazon FreeVee",
                   PackageCategory.AMAZON, "Free streaming"),
    DebloatPackage("com.amazon.kindle", "Kindle",
                   PackageCategory.AMAZON, "E-book reader"),
    DebloatPackage("com.amazon.mShop.android", "Amazon Shopping",
                   PackageCategory.AMAZON, "Shopping app"),
    DebloatPackage("com.amazon.mp3", "Amazon Music",
                   PackageCategory.AMAZON, "Music streaming"),
    DebloatPackage("com.amazon.venezia", "Amazon Appstore",
                   PackageCategory.AMAZON, "App store"),
    DebloatPackage("com.amazon.avod.thirdpartyclient", "Prime Video",
                   PackageCategory.AMAZON, "Video streaming"),
]

# Netflix
NETFLIX_PACKAGES = [
    DebloatPackage("com.netflix.mediaclient", "Netflix",
                   PackageCategory.NETFLIX, "Video streaming"),
    DebloatPackage("com.netflix.partner.activation", "Netflix Activation",
                   PackageCategory.NETFLIX, "Netflix partner"),
]

# Other Common Bloatware
OTHER_BLOAT_PACKAGES = [
    DebloatPackage("com.booking", "Booking.com",
                   PackageCategory.OTHER_BLOAT, "Hotel booking"),
    DebloatPackage("com.tripadvisor.tripadvisor", "TripAdvisor",
                   PackageCategory.OTHER_BLOAT, "Travel reviews"),
    DebloatPackage("flipboard.app", "Flipboard",
                   PackageCategory.OTHER_BLOAT, "News aggregator"),
    DebloatPackage("com.flipboard.boxer.samsung", "Flipboard Samsung",
                   PackageCategory.OTHER_BLOAT, "Flipboard integration"),
    DebloatPackage("com.imdb.mobile", "IMDb",
                   PackageCategory.OTHER_BLOAT, "Movie database"),
    DebloatPackage("com.yelp.android", "Yelp",
                   PackageCategory.OTHER_BLOAT, "Business reviews"),
    DebloatPackage("com.skype.raider", "Skype",
                   PackageCategory.OTHER_BLOAT, "Video calling"),
    DebloatPackage("com.audible.application", "Audible",
                   PackageCategory.OTHER_BLOAT, "Audiobooks"),
    DebloatPackage("cn.wps.moffice_eng", "WPS Office",
                   PackageCategory.OTHER_BLOAT, "Office suite"),
    DebloatPackage("com.spotify.music", "Spotify",
                   PackageCategory.OTHER_BLOAT, "Music streaming"),
    DebloatPackage("com.ticketmaster.mobile.android.na", "Ticketmaster",
                   PackageCategory.OTHER_BLOAT, "Event tickets"),
]


# ============================================================================
# DEBLOAT PRESETS
# ============================================================================

def get_light_debloat_packages() -> List[DebloatPackage]:
    """
    Light debloat - Remove obvious bloatware, keep Samsung features.
    Good for users who still want Samsung ecosystem.
    """
    packages = []
    packages.extend(MICROSOFT_PACKAGES)
    packages.extend(FACEBOOK_PACKAGES)
    packages.extend(AMAZON_PACKAGES)
    packages.extend(NETFLIX_PACKAGES)
    packages.extend(OTHER_BLOAT_PACKAGES)
    packages.extend(SAMSUNG_AR_EMOJI_PACKAGES)
    packages.extend(SAMSUNG_GAMES_PACKAGES)
    packages.extend(SAMSUNG_DEX_PACKAGES)  # Not available on entry-level anyway
    packages.extend(SAMSUNG_KIDS_PACKAGES)
    return packages


def get_medium_debloat_packages() -> List[DebloatPackage]:
    """
    Medium debloat - Remove most bloatware, keep essential Samsung apps.
    Good balance for most users.
    """
    packages = get_light_debloat_packages()
    packages.extend(SAMSUNG_BIXBY_PACKAGES)
    packages.extend(SAMSUNG_THEMES_PACKAGES)
    packages.extend(SAMSUNG_EDGE_PACKAGES)
    packages.extend(SAMSUNG_SHARING_PACKAGES)
    packages.extend(SAMSUNG_CLOUD_PACKAGES)
    packages.extend(SAMSUNG_PASS_PACKAGES)
    packages.extend(GOOGLE_BLOAT_PACKAGES)
    return packages


def get_aggressive_debloat_packages() -> List[DebloatPackage]:
    """
    Aggressive debloat - Maximum removal for ultra-minimal experience.
    For users who want near-stock Android.
    """
    packages = get_medium_debloat_packages()
    packages.extend(SAMSUNG_KNOX_PACKAGES)
    packages.extend(SAMSUNG_HEALTH_PACKAGES)
    packages.extend(SAMSUNG_PAY_PACKAGES)
    packages.extend(SAMSUNG_GENERAL_BLOAT)
    return packages


def get_packages_by_category(category: PackageCategory) -> List[DebloatPackage]:
    """Get all packages in a specific category."""
    category_map = {
        PackageCategory.SAMSUNG_BIXBY: SAMSUNG_BIXBY_PACKAGES,
        PackageCategory.SAMSUNG_AR_EMOJI: SAMSUNG_AR_EMOJI_PACKAGES,
        PackageCategory.SAMSUNG_GAMES: SAMSUNG_GAMES_PACKAGES,
        PackageCategory.SAMSUNG_THEMES: SAMSUNG_THEMES_PACKAGES,
        PackageCategory.SAMSUNG_KNOX: SAMSUNG_KNOX_PACKAGES,
        PackageCategory.SAMSUNG_DEX: SAMSUNG_DEX_PACKAGES,
        PackageCategory.SAMSUNG_HEALTH: SAMSUNG_HEALTH_PACKAGES,
        PackageCategory.SAMSUNG_PAY: SAMSUNG_PAY_PACKAGES,
        PackageCategory.SAMSUNG_PASS: SAMSUNG_PASS_PACKAGES,
        PackageCategory.SAMSUNG_CLOUD: SAMSUNG_CLOUD_PACKAGES,
        PackageCategory.SAMSUNG_KIDS: SAMSUNG_KIDS_PACKAGES,
        PackageCategory.SAMSUNG_EDGE: SAMSUNG_EDGE_PACKAGES,
        PackageCategory.SAMSUNG_SHARING: SAMSUNG_SHARING_PACKAGES,
        PackageCategory.SAMSUNG_BLOAT: SAMSUNG_GENERAL_BLOAT,
        PackageCategory.MICROSOFT: MICROSOFT_PACKAGES,
        PackageCategory.FACEBOOK: FACEBOOK_PACKAGES,
        PackageCategory.GOOGLE_BLOAT: GOOGLE_BLOAT_PACKAGES,
        PackageCategory.AMAZON: AMAZON_PACKAGES,
        PackageCategory.NETFLIX: NETFLIX_PACKAGES,
        PackageCategory.OTHER_BLOAT: OTHER_BLOAT_PACKAGES,
    }
    return category_map.get(category, [])


def get_all_debloat_packages() -> List[DebloatPackage]:
    """Get all debloat packages."""
    return get_aggressive_debloat_packages()


def is_entry_level_samsung(model: str) -> bool:
    """Check if a device model is an entry-level Samsung."""
    model_upper = model.upper()
    for prefix in SAMSUNG_ENTRY_LEVEL_MODELS:
        if prefix.upper() in model_upper:
            return True
    return False


def get_category_display_name(category: PackageCategory) -> str:
    """Get human-readable category name."""
    names = {
        PackageCategory.SAMSUNG_BLOAT: "Samsung Bloatware",
        PackageCategory.SAMSUNG_BIXBY: "Bixby & AI",
        PackageCategory.SAMSUNG_AR_EMOJI: "AR Emoji & Stickers",
        PackageCategory.SAMSUNG_GAMES: "Game Launcher & Tools",
        PackageCategory.SAMSUNG_THEMES: "Themes & Wallpapers",
        PackageCategory.SAMSUNG_KNOX: "Knox Security",
        PackageCategory.SAMSUNG_DEX: "Samsung DeX",
        PackageCategory.SAMSUNG_HEALTH: "Samsung Health",
        PackageCategory.SAMSUNG_PAY: "Samsung Pay",
        PackageCategory.SAMSUNG_PASS: "Samsung Pass",
        PackageCategory.SAMSUNG_CLOUD: "Samsung Cloud",
        PackageCategory.SAMSUNG_KIDS: "Kids Mode",
        PackageCategory.SAMSUNG_EDGE: "Edge Panels",
        PackageCategory.SAMSUNG_SHARING: "Sharing Features",
        PackageCategory.MICROSOFT: "Microsoft Apps",
        PackageCategory.FACEBOOK: "Facebook/Meta Apps",
        PackageCategory.GOOGLE_BLOAT: "Google Bloatware",
        PackageCategory.CARRIER: "Carrier Apps",
        PackageCategory.AMAZON: "Amazon Apps",
        PackageCategory.NETFLIX: "Netflix",
        PackageCategory.LINKEDIN: "LinkedIn",
        PackageCategory.OTHER_BLOAT: "Other Bloatware",
    }
    return names.get(category, category.value.replace("_", " ").title())
