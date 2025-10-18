"""
📱 Module Devices - Gestion des appareils de la maison
Système de stockage et gestion des appareils connus
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
import json
from pathlib import Path
import time
import asyncio
import socket
import ipaddress
from pythonping import ping as py_ping

router = APIRouter()

# Fichier de stockage des appareils
DEVICES_FILE = Path(__file__).parent.parent.parent / "config" / "devices.json"

class DeviceManager:
    """Gestionnaire des appareils connus"""
    
    def __init__(self):
        self.devices = self.load_devices()
    
    def load_devices(self) -> Dict[str, dict]:
        """Charger les appareils depuis le fichier"""
        try:
            if DEVICES_FILE.exists():
                with open(DEVICES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"❌ Erreur chargement appareils: {e}")
            return {}
    
    def save_devices(self):
        """Sauvegarder les appareils"""
        try:
            DEVICES_FILE.parent.mkdir(exist_ok=True)
            with open(DEVICES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.devices, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erreur sauvegarde appareils: {e}")
    
    async def get_mac_address(self, ip: str) -> Optional[str]:
        """Récupérer l'adresse MAC d'un IP"""
        try:
            # Ping d'abord pour remplir l'ARP
            try:
                result = py_ping(ip, count=1, timeout=2)
            except:
                pass
            
            # Lecture table ARP
            import subprocess
            try:
                result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines[1:]:  # Skip header
                        parts = line.split()
                        if len(parts) >= 3 and parts[0] == ip:
                            mac = parts[2]
                            if mac != '(incomplete)' and ':' in mac:
                                return mac.upper()
            except:
                pass
            
            return None
        except Exception:
            return None
    
    async def get_device_info(self, ip: str) -> dict:
        """Récupérer les infos complètes d'un appareil"""
        info = {
            "ip": ip,
            "mac": None,
            "hostname": None,
            "status": "offline",
            "response_time": None,
            "last_seen": None
        }
        
        try:
            # Test ping
            result = py_ping(ip, count=1, timeout=3)
            if result.success():
                info["status"] = "online"
                info["response_time"] = result.rtt_avg_ms
                info["last_seen"] = time.time()
        except:
            pass
        
        # MAC address
        mac = await self.get_mac_address(ip)
        if mac:
            info["mac"] = mac
        
        # Hostname
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            info["hostname"] = hostname
        except:
            pass
        
        return info

# Instance globale
device_manager = DeviceManager()

@router.get("/")
async def get_devices():
    """Liste tous les appareils connus"""
    try:
        devices_list = []
        
        for device_id, device_data in device_manager.devices.items():
            # Test du statut en temps réel
            current_info = await device_manager.get_device_info(device_data["ip"])
            
            # Fusion des données
            device = {
                "id": device_id,
                "name": device_data.get("name", ""),
                "ip": device_data["ip"],
                "mac": current_info.get("mac") or device_data.get("mac"),
                "hostname": current_info.get("hostname") or device_data.get("hostname"),
                "status": current_info["status"],
                "response_time": current_info["response_time"],
                "last_seen": current_info["last_seen"],
                "device_type": device_data.get("device_type", "unknown"),
                "notes": device_data.get("notes", ""),
                "added_date": device_data.get("added_date")
            }
            devices_list.append(device)
        
        return {
            "success": True,
            "data": {
                "devices": devices_list,
                "total": len(devices_list),
                "online": len([d for d in devices_list if d["status"] == "online"])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération appareils: {str(e)}")

@router.post("/add")
async def add_device(device_data: dict):
    """Ajouter un nouvel appareil"""
    try:
        # Validation des données requises
        if not device_data.get("ip"):
            raise HTTPException(status_code=400, detail="IP obligatoire")
        
        ip = device_data["ip"]
        name = device_data.get("name", "")
        
        # Validation IP
        try:
            ipaddress.ip_address(ip)
        except:
            raise HTTPException(status_code=400, detail="IP invalide")
        
        # Récupération des infos auto
        device_info = await device_manager.get_device_info(ip)
        
        # Génération ID unique
        device_id = f"device_{int(time.time())}"
        
        # Données du device
        new_device = {
            "ip": ip,
            "name": name,
            "mac": device_info.get("mac") or device_data.get("mac"),
            "hostname": device_info.get("hostname") or device_data.get("hostname"),
            "device_type": device_data.get("device_type", "unknown"),
            "notes": device_data.get("notes", ""),
            "added_date": time.time()
        }
        
        # Sauvegarde
        device_manager.devices[device_id] = new_device
        device_manager.save_devices()
        
        return {
            "success": True,
            "data": {
                "device_id": device_id,
                "device": new_device,
                "auto_discovered": device_info
            },
            "message": f"Appareil {name or ip} ajouté avec succès"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur ajout appareil: {str(e)}")

@router.post("/import-from-scan")
async def import_from_scan(scan_results: dict):
    """Importer des appareils depuis un scan réseau"""
    try:
        imported = []
        devices_to_import = scan_results.get("devices", [])
        
        for device_data in devices_to_import:
            ip = device_data.get("ip")
            if not ip:
                continue
            
            # Vérifier si déjà existe
            exists = any(d["ip"] == ip for d in device_manager.devices.values())
            if exists:
                continue
            
            # Génération ID unique
            device_id = f"imported_{int(time.time())}_{len(imported)}"
            
            # Données du device
            new_device = {
                "ip": ip,
                "name": device_data.get("hostname", f"Device-{ip.split('.')[-1]}"),
                "mac": device_data.get("mac"),
                "hostname": device_data.get("hostname"),
                "device_type": device_data.get("device_type", "unknown"),
                "notes": f"Importé du scan - {device_data.get('vendor', 'Vendeur inconnu')}",
                "added_date": time.time(),
                "imported_from_scan": True
            }
            
            device_manager.devices[device_id] = new_device
            imported.append(new_device)
        
        device_manager.save_devices()
        
        return {
            "success": True,
            "data": {"imported": imported, "count": len(imported)},
            "message": f"{len(imported)} appareils importés depuis le scan"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur import: {str(e)}")
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import sys
import os

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from .service import DeviceService
from shared.models import Computer, APIResponse

router = APIRouter()

def get_device_service() -> DeviceService:
    """Dependency injection pour le service des appareils"""
    return DeviceService()

@router.get("/", response_model=List[Computer])
async def list_devices(service: DeviceService = Depends(get_device_service)):
    """Liste tous les appareils configurés"""
    return await service.list_devices()

@router.get("/stats")
async def get_device_stats(service: DeviceService = Depends(get_device_service)):
    """Statistiques des appareils"""
    return service.get_statistics()

@router.get("/{device_id}", response_model=Computer)
async def get_device(
    device_id: str,
    service: DeviceService = Depends(get_device_service)
):
    """Récupère un appareil spécifique"""
    device = await service.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Appareil non trouvé")
    return device

@router.post("/", response_model=APIResponse)
async def add_device(
    device_data: dict,
    service: DeviceService = Depends(get_device_service)
):
    """Ajoute un nouvel appareil"""
    result = await service.add_device(device_data)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result

@router.delete("/{device_id}", response_model=APIResponse)
async def remove_device(
    device_id: str,
    service: DeviceService = Depends(get_device_service)
):
    """Supprime un appareil"""
    result = await service.remove_device(device_id)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)
    return result

@router.post("/wake/{mac_address}", response_model=APIResponse)
async def wake_device(
    mac_address: str,
    service: DeviceService = Depends(get_device_service)
):
    """Envoie un signal Wake-on-LAN à un appareil"""
    result = await service.wake_device(mac_address)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result