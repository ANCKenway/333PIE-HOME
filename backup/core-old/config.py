"""
🏠 333HOME - Configuration Centralisée
Gestion de parc informatique domestique
"""

import os
from pathlib import Path

# ===== INFORMATIONS APPLICATION =====
APP_NAME = "333HOME"
APP_VERSION = "4.0.0"
APP_DESCRIPTION = "Gestion de parc informatique domestique"

# ===== CHEMINS =====
BASE_DIR = Path(__file__).parent.parent
CORE_DIR = BASE_DIR / "core"
MODULES_DIR = BASE_DIR / "modules"
WEB_DIR = BASE_DIR / "web"
DATA_DIR = BASE_DIR / "data"
SCRIPTS_DIR = BASE_DIR / "scripts"

# ===== SERVEUR =====
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"

# ===== DONNÉES =====
DEVICES_FILE = DATA_DIR / "devices.json"
SCAN_HISTORY_FILE = DATA_DIR / "scan_history.json"
SYSTEM_LOGS_FILE = DATA_DIR / "system_logs.json"

# ===== RÉSEAU =====
DEFAULT_NETWORK = "192.168.1.0"
SCAN_TIMEOUT = 1
MAX_SCAN_WORKERS = 30
VENDOR_API_URL = "https://api.macvendors.com"

# ===== MONITORING =====
SYSTEM_UPDATE_INTERVAL = 5  # secondes
TEMPERATURE_WARNING = 70    # °C
MEMORY_WARNING = 85        # %
DISK_WARNING = 90          # %

# Création des dossiers nécessaires
for directory in [DATA_DIR, WEB_DIR / "assets"]:
    directory.mkdir(exist_ok=True)

print(f"✅ {APP_NAME} v{APP_VERSION} - Configuration chargée")
print(f"📁 Base: {BASE_DIR}")
print(f"🌐 Serveur: {SERVER_HOST}:{SERVER_PORT}")
print(f"🔧 Debug: {DEBUG_MODE}")