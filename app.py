"""
🏠 333HOME - Application FastAPI principale
Serveur moderne pour la gestion de parc informatique avec scanner réseau avancé
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import asyncio
import time
import json
import httpx
import os
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
TAILSCALE_CONFIG_FILE = CONFIG_DIR / "tailscale_config.json"

DATA_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

# Fonctions utilitaires Tailscale
def load_tailscale_config():
    """Charger la configuration Tailscale depuis le fichier"""
    try:
        if TAILSCALE_CONFIG_FILE.exists():
            with open(TAILSCALE_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config
        return {"api_key": None, "tailnet": None, "last_updated": None}
    except Exception as e:
        print(f"Erreur chargement config Tailscale: {e}")
        return {"api_key": None, "tailnet": None, "last_updated": None}

def save_tailscale_config(api_key: str, tailnet: str):
    """Sauvegarder la configuration Tailscale dans le fichier"""
    try:
        config = {
            "api_key": api_key,
            "tailnet": tailnet,
            "last_updated": time.time()
        }
        with open(TAILSCALE_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Erreur sauvegarde config Tailscale: {e}")
        return False

def get_tailscale_credentials():
    """Récupérer les identifiants Tailscale (priorité: fichier > env)"""
    config = load_tailscale_config()
    
    api_key = config.get('api_key') or os.getenv('TAILSCALE_API_KEY')
    tailnet = config.get('tailnet') or os.getenv('TAILSCALE_TAILNET')
    
    return api_key, tailnet

# Modules selon architecture RULES.md
from modules.devices import DeviceManager, DeviceMonitor
from modules.network.scan_storage import get_scan_storage
from modules.network.network_history import get_network_history

# Instance globale du gestionnaire de devices
device_manager = DeviceManager(DATA_DIR)
device_monitor = DeviceMonitor()
scan_storage = get_scan_storage(DATA_DIR)
network_history = get_network_history(DATA_DIR)

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration de l'app
app = FastAPI(
    title="333HOME",
    description="Système de domotique et gestion de parc informatique",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chemins
BASE_DIR = Path(__file__).parent
WEB_DIR = BASE_DIR / "web"
STATIC_DIR = WEB_DIR / "static"

# Scanner réseau selon architecture modulaire
from modules.network import NetworkScanner
network_scanner = NetworkScanner()

# ===== API ENDPOINTS DE BASE =====

@app.get("/api/status")
async def get_status():
    """Status de l'application avec format attendu par le JS"""
    import psutil
    
    return {
        "success": True,
        "data": {
            "app_name": "333HOME v2.0.0",
            "version": "2.0.0",
            "status": "running",
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "scanner_available": True
        },
        "message": "Serveur opérationnel avec scanner réseau avancé"
    }

# ===== VPN TAILSCALE =====

@app.get("/api/tailscale/config")
async def get_tailscale_config():
    """Get current Tailscale configuration"""
    try:
        api_key, tailnet = get_tailscale_credentials()
        
        return {
            "success": True,
            "config": {
                "api_key_configured": bool(api_key),
                "tailnet": tailnet or "Non configuré",
                "api_key_partial": api_key[-8:] if api_key else None
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def auto_add_vpn_ips_from_tailscale(devices):
    """Auto-ajouter l'IP VPN Tailscale si correspondance nom trouvée"""
    try:
        config_file = os.path.join(os.path.dirname(__file__), 'config', 'tailscale_config.json')
        if not os.path.exists(config_file):
            return
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        if not config.get('api_key'):
            return
        
        # Récupérer appareils Tailscale
        tailscale_devices = await fetch_tailscale_devices_internal(config['api_key'], config['tailnet'])
        if not tailscale_devices:
            return
        
        devices_updated = 0
        
        # Pour chaque appareil local, chercher correspondance Tailscale
        for device in devices:
            # Skip si VPN déjà configuré manuellement
            if device.get('is_vpn') and device.get('ip_secondary'):
                continue
            
            device_name = device.get('name', '').lower()
            device_hostname = device.get('hostname', '').lower()
            
            # Chercher correspondance par nom/hostname
            for ts_device in tailscale_devices:
                ts_hostname = ts_device.get('hostname', '').lower()
                ts_name = ts_device.get('name', '').lower()
                
                # Correspondance exacte ou similaire
                if ((ts_hostname and device_hostname and ts_hostname == device_hostname) or
                    (ts_name and device_name and ts_name == device_name) or
                    (ts_hostname and device_name and ts_hostname in device_name)):
                    
                    # Auto-ajouter IP VPN Tailscale
                    vpn_ip = ts_device.get('addresses', [None])[0]
                    if vpn_ip:
                        device['is_vpn'] = True
                        device['ip_secondary'] = vpn_ip
                        devices_updated += 1
                        logger.info(f"✅ Auto-ajout IP VPN {vpn_ip} pour {device.get('name')} via Tailscale")
                    break
        
        # Sauvegarder si modifications
        if devices_updated > 0:
            # DeviceManager.save_devices() attend la structure complète {"devices": [...]}
            device_manager.save_devices({"devices": devices})
            logger.info(f"🔄 {devices_updated} appareils mis à jour avec IP VPN Tailscale")
            
    except Exception as e:
        logger.warning(f"Auto-ajout IP VPN Tailscale échoué (non critique): {e}")


async def fetch_tailscale_devices_internal(api_key: str, tailnet: str):
    """Fonction interne pour récupérer les appareils Tailscale"""
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {api_key}"}
            response = await client.get(f"https://api.tailscale.com/api/v2/tailnet/{tailnet}/devices", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('devices', [])
            else:
                logger.error(f"Erreur API Tailscale: {response.status_code}")
                return []
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des appareils Tailscale: {e}")
        return []


@app.get("/api/tailscale/devices")
async def get_tailscale_devices():
    """Get Tailscale devices"""
    try:
        api_key, tailnet = get_tailscale_credentials()
        
        if not api_key:
            return {
                "success": False, 
                "error": "Clé API Tailscale non configurée",
                "error_type": "missing_api_key",
                "help_url": "https://login.tailscale.com/admin/settings/keys"
            }
        
        if not tailnet:
            return {"success": False, "error": "Tailnet non configuré"}
        
        # Call Tailscale API
        headers = {"Authorization": f"Bearer {api_key}"}
        url = f"https://api.tailscale.com/api/v2/tailnet/{tailnet}/devices"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "devices": data.get("devices", [])}
            elif response.status_code == 401:
                return {
                    "success": False, 
                    "error": "Clé API expirée ou invalide",
                    "error_type": "expired_api_key",
                    "help_text": "Les clés API Tailscale expirent après 90 jours maximum. Veuillez générer une nouvelle clé.",
                    "help_url": "https://login.tailscale.com/admin/settings/keys"
                }
            elif response.status_code == 403:
                return {
                    "success": False, 
                    "error": "Accès non autorisé - vérifiez vos permissions",
                    "error_type": "permission_denied",
                    "help_url": "https://login.tailscale.com/admin/settings/keys"
                }
            elif response.status_code == 404:
                return {
                    "success": False, 
                    "error": "Tailnet introuvable (erreur 404)",
                    "error_type": "tailnet_not_found",
                    "help_text": f"Tailnet '{tailnet}' introuvable. Vérifiez le format et l'ID dans l'admin Tailscale.",
                    "help_url": "https://login.tailscale.com/admin/settings/general",
                    "debug_info": {
                        "used_tailnet": tailnet,
                        "api_url": url
                    }
                }
            else:
                return {"success": False, "error": f"Erreur API Tailscale: {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/tailscale/config")
async def update_tailscale_config(config_data: dict):
    """Update Tailscale configuration"""
    try:
        api_key = config_data.get('api_key', '').strip()
        tailnet = config_data.get('tailnet', '').strip()
        
        if not api_key:
            return {"success": False, "error": "Clé API requise"}
        
        if not tailnet:
            return {"success": False, "error": "Tailnet requis"}
        
        # Test the API key before saving
        headers = {"Authorization": f"Bearer {api_key}"}
        url = f"https://api.tailscale.com/api/v2/tailnet/{tailnet}/devices"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 401:
                return {
                    "success": False, 
                    "error": "Clé API invalide ou expirée",
                    "help_text": "Vérifiez que la clé API est correcte et qu'elle n'a pas expiré (max 90 jours).",
                    "help_url": "https://login.tailscale.com/admin/settings/keys"
                }
            elif response.status_code == 403:
                return {
                    "success": False, 
                    "error": "Permissions insuffisantes",
                    "help_text": "La clé API doit avoir les permissions 'Devices: Read'.",
                    "help_url": "https://login.tailscale.com/admin/settings/keys"
                }
            elif response.status_code == 404:
                return {
                    "success": False, 
                    "error": "Tailnet introuvable (erreur 404)",
                    "help_text": "Vérifiez le nom de votre Tailnet. Il doit être au format 'tail<hash>.ts.net' (visible dans l'admin Tailscale) ou votre email si vous utilisez un compte personnel.",
                    "help_url": "https://login.tailscale.com/admin/settings/general"
                }
            elif response.status_code != 200:
                return {"success": False, "error": f"Erreur de test API: {response.status_code}"}
        
        # Store configuration persistante
        if save_tailscale_config(api_key, tailnet):
            return {
                "success": True, 
                "message": "Configuration Tailscale mise à jour avec succès",
                "config": {
                    "tailnet": tailnet,
                    "api_key_partial": api_key[-8:]
                }
            }
        else:
            return {"success": False, "error": "Erreur lors de la sauvegarde de la configuration"}
    except Exception as e:
        return {"success": False, "error": f"Erreur lors de la mise à jour: {str(e)}"}

@app.get("/api/tailscale/debug/{tailnet_test}")
async def debug_tailscale_api(tailnet_test: str):
    """Debug endpoint to test different tailnet formats"""
    try:
        api_key, _ = get_tailscale_credentials()
        
        if not api_key:
            return {"error": "No API key configured"}
        
        # Test different URL formats
        test_urls = [
            f"https://api.tailscale.com/api/v2/tailnet/{tailnet_test}/devices",
            f"https://api.tailscale.com/api/v2/tailnet/{tailnet_test}.ts.net/devices",
            f"https://api.tailscale.com/api/v2/tailnet/tail{tailnet_test}.ts.net/devices"
        ]
        
        headers = {"Authorization": f"Bearer {api_key}"}
        results = []
        
        async with httpx.AsyncClient() as client:
            for url in test_urls:
                try:
                    response = await client.get(url, headers=headers)
                    results.append({
                        "url": url,
                        "status_code": response.status_code,
                        "success": response.status_code == 200,
                        "response_size": len(response.content) if response.status_code == 200 else 0
                    })
                except Exception as e:
                    results.append({
                        "url": url,
                        "error": str(e)
                    })
        
        return {
            "tailnet_input": tailnet_test,
            "test_results": results,
            "api_key_configured": bool(api_key),
            "api_key_partial": api_key[-8:] if api_key else None
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/tailscale/raw-devices")
async def get_raw_tailscale_devices():
    """Debug: Get raw Tailscale devices data to see the exact structure"""
    try:
        api_key, tailnet = get_tailscale_credentials()
        
        if not api_key or not tailnet:
            return {"error": "Configuration manquante"}
        
        headers = {"Authorization": f"Bearer {api_key}"}
        url = f"https://api.tailscale.com/api/v2/tailnet/{tailnet}/devices"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "raw_data": data,
                    "devices_count": len(data.get("devices", [])),
                    "sample_device": data.get("devices", [])[0] if data.get("devices") else None
                }
            else:
                return {"error": f"Status: {response.status_code}", "response": response.text}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/info")
async def get_info():
    """Informations détaillées du système"""
    import psutil
    import platform
    from datetime import datetime
    
    return {
        "success": True,
        "data": {
            "system": {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "architecture": platform.machine(),
                "hostname": platform.node(),
                "python_version": platform.python_version()
            },
            "resources": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            },
            "timestamp": datetime.now().isoformat(),
            "app_name": "333HOME v2.0.0",
            "app_version": "2.0.0"
        }
    }

@app.get("/api/devices")
async def get_devices():
    """Appareils avec monitoring local + auto-ajout IP VPN Tailscale"""
    try:
        # ÉTAPE 1 : Charger les appareils configurés
        devices = device_manager.load_devices()
        
        # ÉTAPE 2 : Auto-ajout IP VPN Tailscale si correspondance nom trouvée
        await auto_add_vpn_ips_from_tailscale(devices)
        
        # ÉTAPE 3 : Monitoring local + VPN (logique originale inchangée)
        enriched_devices = await device_monitor.get_devices_with_status(devices)
        
        # ÉTAPE 4 : Formatage final + transformation VPN pour le frontend
        for device in enriched_devices:
            # Formatage temps
            if device.get('last_checked'):
                last_check_ago = int(time.time() - device['last_checked'])
                if last_check_ago < 60:
                    device["last_seen"] = f"Il y a {last_check_ago}s"
                elif last_check_ago < 3600:
                    device["last_seen"] = f"Il y a {last_check_ago//60}min"
                else:
                    device["last_seen"] = f"Il y a {last_check_ago//3600}h"
            else:
                device["last_seen"] = "Jamais vérifié"
            
            # Transformation VPN : vpn_status (monitor) -> vpn (frontend)
            if device.get('vpn_status', {}).get('enabled'):
                device['vpn'] = {
                    'connected': True,
                    'online': device.get('vpn_status', {}).get('status') == 'online',
                    'tailscale_ip': device.get('vpn_status', {}).get('ip'),
                    'method': 'local_ping'
                }
        
        return {"devices": enriched_devices}
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des appareils: {e}")
        return {"error": str(e), "devices": []}

@app.get("/api/devices/refresh")
async def refresh_devices():
    """Forcer la vérification de tous les appareils (bypass cache)"""
    try:
        # Vider le cache du monitor
        device_monitor.clear_cache()
        
        # Charger les appareils
        devices = device_manager.load_devices()
        
        # Monitoring forcé sans cache
        enriched_devices = await device_monitor.get_devices_with_status(devices)
        
        # Ajouter informations de monitoring + transformation VPN (même logique que /api/devices)
        for device in enriched_devices:
            # Formatage temps
            if device.get('last_checked'):
                last_check_ago = int(time.time() - device['last_checked'])
                if last_check_ago < 60:
                    device["last_seen"] = f"Il y a {last_check_ago}s"
                elif last_check_ago < 3600:
                    device["last_seen"] = f"Il y a {last_check_ago//60}min"
                else:
                    device["last_seen"] = f"Il y a {last_check_ago//3600}h"
            else:
                device["last_seen"] = "Jamais vérifié"
            
            # Transformation VPN : vpn_status (monitor) -> vpn (frontend) - MÊME LOGIQUE QUE /api/devices
            if device.get('vpn_status', {}).get('enabled'):
                device['vpn'] = {
                    'connected': True,
                    'online': device.get('vpn_status', {}).get('status') == 'online',
                    'tailscale_ip': device.get('vpn_status', {}).get('ip'),
                    'method': 'local_ping'
                }
        
        logger.info(f"Monitoring forcé de {len(devices)} appareils")
        return {"success": True, "devices": enriched_devices}
    except Exception as e:
        logger.error(f"Erreur lors du rafraîchissement des appareils: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.post("/api/devices")
async def add_device(device_data: dict):
    """Ajouter un nouvel appareil"""
    try:
        success = device_manager.add_device(device_data)
        if success:
            return {"success": True, "message": "Appareil ajouté"}
        else:
            return {"success": False, "message": "Appareil déjà existant"}
    except Exception as e:
        logger.error(f"Erreur ajout appareil: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.put("/api/devices/{device_id}")
async def update_device(device_id: str, updates: dict):
    """Mettre à jour un appareil"""
    try:
        success = device_manager.update_device(device_id, updates)
        if success:
            return {"success": True, "message": "Appareil mis à jour"}
        else:
            raise HTTPException(status_code=404, detail="Appareil non trouvé")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur mise à jour appareil: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.delete("/api/devices/{device_id}")
async def delete_device(device_id: str):
    """Supprimer un appareil"""
    try:
        success = device_manager.remove_device(device_id)
        if success:
            return {"success": True, "message": "Appareil supprimé"}
        else:
            raise HTTPException(status_code=404, detail="Appareil non trouvé")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suppression appareil: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/monitoring/stats")
async def get_monitoring_stats():
    """Statistiques du monitoring en temps réel"""
    try:
        stats = device_monitor.get_monitoring_stats()
        device_stats = device_manager.get_stats()
        
        return {
            "success": True, 
            "monitoring": stats,
            "devices": device_stats
        }
    except Exception as e:
        logging.error(f"Erreur monitoring stats: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.post("/api/wake/{mac}")
async def wake_on_lan(mac: str):
    """Envoyer un paquet Wake-on-LAN"""
    try:
        import struct
        import socket
        
        # Nettoyer l'adresse MAC
        mac = mac.replace(':', '').replace('-', '').upper()
        
        if len(mac) != 12:
            raise HTTPException(status_code=400, detail="Adresse MAC invalide")
        
        # Créer le paquet magic
        mac_bytes = bytes.fromhex(mac)
        magic_packet = b'\xff' * 6 + mac_bytes * 16
        
        # Envoyer via broadcast UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, ('255.255.255.255', 9))
        sock.close()
        
        logger.info(f"Wake-on-LAN envoyé pour MAC {mac}")
        return {"success": True, "message": f"Wake-on-LAN envoyé pour {mac}"}
        
    except Exception as e:
        logger.error(f"Erreur Wake-on-LAN: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur Wake-on-LAN: {str(e)}")

@app.post("/api/monitoring/clear-cache")
async def clear_monitoring_cache():
    """Vider le cache de monitoring"""
    try:
        device_monitor.clear_cache()
        return {"success": True, "message": "Cache vidé"}
    except Exception as e:
        logging.error(f"Erreur clear cache: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

# ===== ENDPOINTS SCANNER RÉSEAU =====

@app.get("/api/network/scan")
async def professional_network_scan():
    """🔥 SCANNER RÉSEAU PROFESSIONNEL COMPLET"""
    try:
        logger.info("🚀 Lancement scan professionnel")
        start_time = time.time()
        
        result = network_scanner.professional_network_scan()
        
        # Calculer la durée du scan
        scan_duration = time.time() - start_time
        
        # Sauvegarder le scan (ancien système)
        if result and 'devices' in result:
            success = scan_storage.save_scan_result(result['devices'], scan_duration)
            logger.info(f"Scan sauvegardé (legacy): {success}")
            
            # Nouveau système d'historique unifié
            try:
                changes = network_history.update_scan_results(result['devices'], scan_duration)
                logger.info(f"Historique unifié mis à jour: {changes}")
            except Exception as history_error:
                logger.error(f"Erreur historique spécifique: {history_error}")
                import traceback
                logger.error(f"Traceback historique: {traceback.format_exc()}")
        
        return {"success": True, "scan_results": result}
    except Exception as e:
        logger.error(f"Erreur scan professionnel: {e}")
        import traceback
        logger.error(f"Traceback complet: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/quick-scan")
async def quick_network_scan():
    """Scanner rapide du réseau local"""
    try:
        # Scan rapide de la plage réseau
        result = network_scanner.scan_network_range()
        return {"success": True, "devices": result}
    except Exception as e:
        logger.error(f"Erreur scan rapide: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/detailed-scan")
async def detailed_network_scan(target: str = None):
    """Scanner détaillé avec ports et services"""
    try:
        if target:
            result = network_scanner.scan_host_detailed(target)
        else:
            result = network_scanner.scan_network_detailed()
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Erreur scan détaillé: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/discovery")
async def network_discovery():
    """Découverte réseau avec identification"""
    try:
        from modules.network.device_identifier import DeviceIdentifier
        identifier = DeviceIdentifier()
        
        # Scan de base
        devices = network_scanner.scan_network_range()
        
        # Enrichissement avec identification
        enriched_devices = []
        for device in devices:
            if device.get('mac'):
                device_info = await identifier.identify_device(device['mac'])
                device.update(device_info)
            enriched_devices.append(device)
        
        return {"success": True, "devices": enriched_devices}
    except Exception as e:
        logger.error(f"Erreur discovery: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

# ===== ENDPOINTS HISTORIQUE SCANS =====

@app.get("/api/network/last-scan")
async def get_last_scan():
    """Récupérer le dernier scan effectué"""
    try:
        last_scan = scan_storage.get_last_scan()
        return {"success": True, "last_scan": last_scan}
    except Exception as e:
        logger.error(f"Erreur last scan: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/scan-history")
async def get_scan_history(limit: int = 10):
    """Récupérer l'historique des scans"""
    try:
        history = scan_storage.get_scan_history(limit)
        return {"success": True, "history": history}
    except Exception as e:
        logger.error(f"Erreur history: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/disconnected-devices")
async def get_disconnected_devices(limit: int = 20):
    """Récupérer les appareils récemment déconnectés"""
    try:
        disconnected = scan_storage.get_disconnected_devices(limit)
        return {"success": True, "disconnected_devices": disconnected}
    except Exception as e:
        logger.error(f"Erreur disconnected: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/scan-stats")
async def get_scan_stats():
    """Récupérer les statistiques des scans (NOUVEAU: historique unifié)"""
    try:
        # Nouvelles stats depuis l'historique unifié
        stats = network_history.get_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Erreur scan stats: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

# ===== NOUVEAUX ENDPOINTS HISTORIQUE UNIFIÉ =====

@app.get("/api/network/devices-history")
async def get_devices_with_history():
    """Récupérer tous les appareils avec leur historique enrichi"""
    try:
        history_data = network_history.get_history()
        return {"success": True, "history": history_data}
    except Exception as e:
        logger.error(f"Erreur devices history: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/device-history/{mac}")
async def get_device_history(mac: str):
    """Récupérer l'historique détaillé d'un appareil spécifique via MAC"""
    try:
        device_data = network_history.get_device_by_mac(mac)
        if device_data:
            return {"success": True, "device": device_data}
        else:
            raise HTTPException(status_code=404, detail="Appareil non trouvé")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur device history: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/recent-events")
async def get_recent_network_events(limit: int = 20):
    """Récupérer les événements réseau récents (connexions, déconnexions, changements)"""
    try:
        events = network_history.get_recent_events(limit)
        return {"success": True, "events": events}
    except Exception as e:
        logger.error(f"Erreur recent events: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/scan-stats-legacy")
async def get_scan_stats_legacy():
    """Récupérer les statistiques des scans (ancien système)"""
    try:
        stats = scan_storage.get_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Erreur scan stats legacy: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")
    """Récupérer les statistiques des scans"""
    try:
        stats = scan_storage.get_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Erreur scan stats: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/stats")
async def network_stats():
    """Statistiques du scanner réseau"""
    try:
        stats = {
            "last_scan": network_scanner.last_scan_time,
            "total_scanned": len(network_scanner.scan_results),
            "scan_timeout": network_scanner.scan_timeout,
            "active_threads": network_scanner.max_threads
        }
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Erreur stats réseau: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

# ===== SERVEUR DE FICHIERS STATIQUES =====

# Vérifier et créer les répertoires si nécessaire
if not WEB_DIR.exists():
    WEB_DIR.mkdir(parents=True, exist_ok=True)
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Monter les fichiers statiques
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
async def read_root():
    """Page d'accueil"""
    index_file = WEB_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        raise HTTPException(status_code=404, detail="Page d'accueil non trouvée")

@app.get("/{filename}")
async def serve_web_files(filename: str):
    """Servir les fichiers web (templates, etc.)"""
    file_path = WEB_DIR / filename
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    else:
        raise HTTPException(status_code=404, detail="Fichier non trouvé")

# ===== GESTION DES ERREURS =====

from fastapi.responses import JSONResponse

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "Endpoint non trouvé",
            "detail": f"L'endpoint {request.url.path} n'existe pas"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Erreur interne: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Erreur interne du serveur",
            "detail": str(exc)
        }
    )

# ===== GESTION AVANCÉE TAILSCALE =====

@app.post("/api/tailscale/device/{device_id}/rename")
async def rename_tailscale_device(device_id: str, data: dict):
    """Renommer un appareil Tailscale"""
    try:
        api_key, tailnet = get_tailscale_credentials()
        new_name = data.get('name', '').strip()
        
        if not api_key or not tailnet:
            return {"success": False, "error": "Configuration manquante"}
        
        if not new_name:
            return {"success": False, "error": "Nom requis"}
        
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        url = f"https://api.tailscale.com/api/v2/device/{device_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json={"hostname": new_name})
            
            if response.status_code in [200, 204]:
                return {"success": True, "message": f"Appareil renommé en '{new_name}'"}
            else:
                return {"success": False, "error": f"Erreur API: {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/tailscale/device/{device_id}/authorize")
async def authorize_tailscale_device(device_id: str):
    """Autoriser un appareil Tailscale"""
    try:
        api_key, tailnet = get_tailscale_credentials()
        
        if not api_key or not tailnet:
            return {"success": False, "error": "Configuration manquante"}
        
        headers = {"Authorization": f"Bearer {api_key}"}
        url = f"https://api.tailscale.com/api/v2/device/{device_id}/authorized"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json={"authorized": True})
            
            if response.status_code in [200, 204]:
                return {"success": True, "message": "Appareil autorisé"}
            else:
                return {"success": False, "error": f"Erreur API: {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.delete("/api/tailscale/device/{device_id}")
async def delete_tailscale_device(device_id: str):
    """Supprimer un appareil Tailscale du réseau"""
    try:
        api_key, tailnet = get_tailscale_credentials()
        
        if not api_key or not tailnet:
            return {"success": False, "error": "Configuration manquante"}
        
        headers = {"Authorization": f"Bearer {api_key}"}
        url = f"https://api.tailscale.com/api/v2/device/{device_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers)
            
            if response.status_code in [200, 204]:
                return {"success": True, "message": "Appareil supprimé du réseau"}
            else:
                return {"success": False, "error": f"Erreur API: {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/tailscale/routes")
async def get_tailscale_routes():
    """Obtenir les routes subnet à partir des appareils"""
    try:
        api_key, tailnet = get_tailscale_credentials()
        
        if not api_key or not tailnet:
            return {"success": False, "error": "Configuration manquante"}
        
        headers = {"Authorization": f"Bearer {api_key}"}
        url = f"https://api.tailscale.com/api/v2/tailnet/{tailnet}/devices"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                devices = data.get("devices", [])
                
                # Extraire les routes des appareils
                routes = []
                for device in devices:
                    if device.get("advertiseRoutes"):
                        for route in device["advertiseRoutes"]:
                            routes.append({
                                "destination": route,
                                "advertiser": device.get("hostname", device.get("name", "Inconnu")),
                                "device_id": device.get("id"),
                                "enabled": route in device.get("enabledRoutes", [])
                            })
                
                return {"success": True, "routes": routes}
            else:
                return {"success": False, "error": f"Erreur API: {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/tailscale/acl")
async def get_tailscale_acl():
    """Obtenir les règles ACL (Access Control List)"""
    try:
        api_key, tailnet = get_tailscale_credentials()
        
        if not api_key or not tailnet:
            return {"success": False, "error": "Configuration manquante"}
        
        headers = {"Authorization": f"Bearer {api_key}"}
        url = f"https://api.tailscale.com/api/v2/tailnet/{tailnet}/acl"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return {"success": True, "acl": data}
                except json.JSONDecodeError:
                    # Réponse vide ou mal formée
                    return {"success": True, "acl": None}
            elif response.status_code == 403:
                return {"success": False, "error": "Permissions insuffisantes pour accéder aux ACL"}
            elif response.status_code == 404:
                return {"success": False, "error": "ACL non trouvées pour ce Tailnet"}
            else:
                return {"success": False, "error": f"Erreur API: {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== SYNCHRONISATION INTELLIGENTE VPN-LOCAL =====

def is_tailscale_device_online(device):
    """Détermine si un appareil Tailscale est en ligne (logique robuste)"""
    # Tentative de détection du statut selon différents formats API
    if device.get('online'):
        return True
    if device.get('connected'):
        return True
    if device.get('status') in ['online', 'active']:
        return True
    
    # Vérifier si récemment actif (fenêtre élargie à 30 minutes)
    last_seen = device.get('lastSeen')
    if last_seen:
        try:
            from datetime import datetime, timezone
            # Parse format ISO avec gestion timezone robuste
            if 'T' in last_seen:
                # Nettoyer la date
                cleaned_date = last_seen
                if cleaned_date.endswith('Z'):
                    cleaned_date = cleaned_date.replace('Z', '+00:00')
                elif '+' not in cleaned_date and 'Z' not in cleaned_date and 'T' in cleaned_date:
                    cleaned_date = cleaned_date + '+00:00'
                
                last_seen_dt = datetime.fromisoformat(cleaned_date)
                # Convertir en UTC si nécessaire
                if last_seen_dt.tzinfo is None:
                    last_seen_dt = last_seen_dt.replace(tzinfo=timezone.utc)
                
                now = datetime.now(timezone.utc)
                diff_minutes = (now - last_seen_dt).total_seconds() / 60
                
                # Considéré online si vu dans les 30 dernières minutes (au lieu de 5)
                is_online = diff_minutes < 30
                logger.info(f"Tailscale device {device.get('hostname', 'unknown')}: lastSeen={last_seen}, diff={diff_minutes:.1f}min, online={is_online}")
                return is_online
        except Exception as e:
            logger.error(f"Erreur parsing lastSeen {last_seen}: {e}")
            # En cas d'erreur de parsing, considérer comme online par défaut si on a une lastSeen récente
            return True
    
    # Si pas de lastSeen, vérifier si l'appareil a des adresses (signe qu'il est configuré)
    if device.get('addresses'):
        logger.info(f"Tailscale device {device.get('hostname', 'unknown')}: no lastSeen but has addresses, considering online")
        return True
    
    return False

@app.get("/api/sync/vpn-devices")
async def sync_vpn_with_local_devices():
    """Synchronisation intelligente entre appareils Tailscale et réseau local"""
    try:
        # Récupérer les appareils Tailscale
        api_key, tailnet = get_tailscale_credentials()
        if not api_key or not tailnet:
            return {"success": False, "error": "Configuration Tailscale manquante"}
        
        headers = {"Authorization": f"Bearer {api_key}"}
        url = f"https://api.tailscale.com/api/v2/tailnet/{tailnet}/devices"
        
        tailscale_devices = []
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                tailscale_devices = data.get("devices", [])

        # Récupérer les appareils locaux
        # DeviceManager expose load_devices(), pas get_all_devices()
        local_devices = device_manager.load_devices()

        # Logique de correspondance intelligente
        matches = []
        enhanced_devices = []
        
        for local_device in local_devices:
            enhanced_device = local_device.copy()
            vpn_match = None
            
            # Stratégies de correspondance
            for vpn_device in tailscale_devices:
                vpn_hostname = vpn_device.get('hostname', '').lower()
                vpn_name = vpn_device.get('name', '').lower()
                local_hostname = local_device.get('hostname', '').lower()
                local_name = local_device.get('name', '').lower()
                
                # 1. Correspondance exacte hostname
                if vpn_hostname and vpn_hostname == local_hostname:
                    vpn_match = vpn_device
                    break
                
                # 2. Correspondance exacte nom
                if vpn_name and vpn_name == local_name:
                    vpn_match = vpn_device
                    break
                
                # 3. Correspondance partielle (contient)
                if vpn_hostname and local_hostname and vpn_hostname in local_hostname:
                    vpn_match = vpn_device
                    break
                
                # 4. Correspondance par OS + similarité nom
                if (vpn_device.get('os', '').lower() == local_device.get('os', '').lower() and
                    vpn_hostname and local_hostname and 
                    any(word in vpn_hostname for word in local_hostname.split('-'))):
                    vpn_match = vpn_device
                    break
            
            # Enrichir l'appareil local avec les infos VPN
            if vpn_match:
                # Détecter si l'appareil est en ligne (même logique que dans l'interface)
                is_online = is_tailscale_device_online(vpn_match)
                
                enhanced_device['vpn'] = {
                    'connected': True,
                    'tailscale_ip': vpn_match.get('addresses', [None])[0],
                    'tailscale_id': vpn_match.get('id'),
                    'last_seen': vpn_match.get('lastSeen'),
                    'online': is_online,
                    'exit_node': vpn_match.get('advertisesExitNode', False),
                    'authorized': vpn_match.get('authorized', True)
                }
                matches.append({
                    'local': local_device,
                    'vpn': vpn_match,
                    'match_reason': 'hostname_match'
                })
            else:
                enhanced_device['vpn'] = {'connected': False}
            
            enhanced_devices.append(enhanced_device)
        
        # Appareils VPN non matchés (VPN only)
        matched_vpn_ids = [match['vpn']['id'] for match in matches]
        vpn_only_devices = [
            vpn for vpn in tailscale_devices 
            if vpn.get('id') not in matched_vpn_ids
        ]
        
        return {
            "success": True,
            "enhanced_devices": enhanced_devices,
            "matches_found": len(matches),
            "vpn_only_devices": vpn_only_devices,
            "total_local": len(local_devices),
            "total_vpn": len(tailscale_devices),
            "sync_timestamp": time.time()
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/sync/enable-auto-vpn")
async def enable_auto_vpn_sync():
    """Activer la synchronisation automatique VPN pour tous les appareils"""
    try:
        sync_result = await sync_vpn_with_local_devices()
        
        if not sync_result.get("success"):
            return sync_result
        
        # Mettre à jour les appareils avec les infos VPN
        enhanced_devices = sync_result.get("enhanced_devices", [])
        updated_count = 0
        
        for device in enhanced_devices:
            if device.get('vpn', {}).get('connected'):
                # Mettre à jour l'appareil dans le manager
                device_ip = device.get('ip')
                if device_ip:
                    # DeviceManager expose get_device_by_id(ip_or_mac)
                    existing_device = device_manager.get_device_by_id(device_ip)
                    if existing_device:
                        # Merge VPN info into existing device
                        updates = existing_device.copy()
                        updates.update(device)
                        device_manager.update_device(device_ip, updates)
                        updated_count += 1
        
        return {
            "success": True,
            "message": f"Synchronisation VPN activée - {updated_count} appareils enrichis",
            "updated_devices": updated_count,
            "matches": sync_result.get("matches_found", 0)
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== ÉVÉNEMENTS DE L'APPLICATION =====

@app.on_event("startup")
async def startup_event():
    """Actions au démarrage"""
    logger.info("🚀 Démarrage de 333HOME v2.0.0")
    logger.info(f"📁 Répertoire: {BASE_DIR}")
    logger.info(f"🌐 Interface web: {WEB_DIR}")
    logger.info("✅ Scanner réseau avancé disponible")

@app.on_event("shutdown")
async def shutdown_event():
    """Actions à l'arrêt"""
    logger.info("🛑 Arrêt de 333HOME")

# ===== FONCTION DE DÉMARRAGE =====

def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Démarrer le serveur FastAPI"""
    logger.info(f"🌐 Serveur: http://{host}:{port}")
    logger.info("📖 Documentation API: http://localhost:8000/api/docs")
    logger.info("🔗 Interface: http://localhost:8000")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    start_server(reload=True)