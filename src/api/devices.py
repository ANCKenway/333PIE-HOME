"""
API endpoints pour les appareils domestiques
Version simplifiée et propre
"""

from fastapi import APIRouter, HTTPException
from ..services import DeviceManager, PiMonitor

router = APIRouter()

# Instances des services
device_manager = DeviceManager()
pi_monitor = PiMonitor()

@router.get("/computers")
async def get_computers():
    """Liste des ordinateurs configurés"""
    computers = device_manager.get_computers()
    
    # Vérifier le status en temps réel
    for computer in computers:
        computer["status"] = "online" if device_manager.ping_device(computer["ip"]) else "offline"
    
    return {"computers": computers}

@router.post("/computers")
async def add_computer(device: dict):
    """Ajoute un nouvel appareil"""
    result = device_manager.add_computer(
        name=device.get('name'),
        ip=device.get('ip'), 
        mac=device.get('mac'),
        device_type=device.get('type', 'unknown')
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.delete("/computers/{device_id}")
async def remove_computer(device_id: str):
    """Supprime un appareil"""
    result = device_manager.remove_computer(device_id)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.post("/wol/{mac}")
async def wake_on_lan(mac: str):
    """Wake-on-LAN pour démarrer un PC"""
    result = device_manager.wake_on_lan(mac)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.get("/pi/status")
async def get_pi_status():
    """Status du Raspberry Pi"""
    return pi_monitor.get_system_status()

@router.get("/pi/services")
async def get_pi_services():
    """Services du Raspberry Pi"""
    status = pi_monitor.get_system_status()
    services = status.get("services", [])
    
    return {
        "pi_info": {
            "hostname": "333PIE",
            "description": "Raspberry Pi - Système de domotique",
            "services_count": len(services),
            "online_count": len([s for s in services if s["status"] == "online"])
        },
        "services": services
    }

@router.get("/system")
async def get_system_info():
    """Informations système simplifiées"""
    return pi_monitor.get_system_status()

@router.post("/computers/add")
async def add_computer(computer_data: dict):
    """Ajoute un nouvel ordinateur aux favoris"""
    required_fields = ['name', 'ip', 'mac']
    
    if not all(field in computer_data for field in required_fields):
        raise HTTPException(status_code=400, detail="Champs requis: name, ip, mac")
    
    result = device_manager.add_computer(
        name=computer_data['name'],
        ip=computer_data['ip'], 
        mac=computer_data['mac'],
        device_type=computer_data.get('type', 'unknown')
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return result

@router.delete("/computers/{identifier}")
async def remove_computer(identifier: str):
    """Supprime un ordinateur (par IP ou MAC)"""
    result = device_manager.remove_computer(identifier)
    
    if not result['success']:
        raise HTTPException(status_code=404, detail=result['error'])
    
    return result