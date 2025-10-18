"""
🔥 API Routes Network - Scanner ULTRA BLINDÉ avec identification maximale 🔥
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List
import logging
import time

from .advanced_scanner import ultra_scanner

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/scan/live")
async def scan_network_live():
    """
    � Lance un scan réseau ULTRA BLINDÉ en temps réel
    Découvre TOUS les appareils avec identification maximale
    Utilise Nmap, Scapy, bannering, OS detection, etc.
    """
    try:
        logger.info("� Démarrage scan réseau ULTRA BLINDÉ")
        result = await ultra_scanner.scan_live_ultra()
        
        if result["success"]:
            logger.info(f"✅ Scan ultra terminé: {result['stats']['total_devices']} appareils")
            return {
                "status": "success",
                "message": result["message"],
                "data": result
            }
        else:
            logger.error(f"❌ Erreur scan ultra: {result.get('error', 'Erreur inconnue')}")
            raise HTTPException(status_code=500, detail=result.get("error", "Erreur de scan"))
            
    except Exception as e:
        logger.error(f"❌ Erreur API scan ultra: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur du scanner ultra: {str(e)}")

@router.get("/scan/quick")
async def scan_network_quick():
    """
    ⚡ Scan rapide du réseau local avec techniques allégées
    """
    try:
        # Scan limité au réseau principal avec techniques réduites
        result = await ultra_scanner.scan_network_ultra_blindé(target_networks=["192.168.1.0/24"])
        
        devices_data = [device.__dict__ for device in result]
        
        return {
            "status": "success", 
            "message": f"⚡ Scan rapide terminé - {len(devices_data)} appareils",
            "devices": devices_data,
            "stats": {
                "total": len(devices_data),
                "online": len([d for d in devices_data if d.get("status") == "online"]),
                "with_mac": len([d for d in devices_data if d.get("mac")]),
                "identified": len([d for d in devices_data if d.get("device_type") != "unknown"])
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur scan rapide: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur scan rapide: {str(e)}")

@router.get("/devices")
async def get_network_devices():
    """
    📱 Récupère la liste ultra détaillée des appareils réseau
    """
    try:
        result = await ultra_scanner.scan_live_ultra()
        
        if result["success"]:
            return {
                "status": "success",
                "devices": result["devices"],
                "stats": result["stats"],
                "message": f"📱 {len(result['devices'])} appareils ultra analysés"
            }
        else:
            raise HTTPException(status_code=500, detail="Erreur récupération appareils")
            
    except Exception as e:
        logger.error(f"❌ Erreur récupération appareils: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/discover")
def discover_devices():
    """
    🔍 Découverte des appareils (compatibilité frontend)
    """
    try:
        # Scan direct avec la méthode synchrone
        devices = ultra_scanner.scan_network_ultra_blindé_sync()
        devices_data = []
        
        for device in devices:
            if hasattr(device, '__dict__'):
                device_dict = device.__dict__.copy()
            else:
                device_dict = device
            
            # Assurer la compatibilité frontend
            if 'status' not in device_dict:
                device_dict['status'] = 'online' if device_dict.get('ip') else 'unknown'
            
            devices_data.append(device_dict)
        
        logger.info(f"✅ Découverte terminée: {len(devices_data)} appareils")
        
        # Format compatible avec le frontend
        return {
            "devices": devices_data,
            "stats": {
                "total": len(devices_data),
                "online": len([d for d in devices_data if d.get("status") == "online"]),
                "with_mac": len([d for d in devices_data if d.get("mac")]),
                "identified": len([d for d in devices_data if d.get("device_type") != "unknown"])
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur découverte: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scan")
@router.post("/scan")
def scan_network():
    """
    🔍 Scan réseau (compatibilité frontend)  
    """
    try:
        # Scan direct avec la méthode synchrone
        devices = ultra_scanner.scan_network_ultra_blindé_sync()
        devices_data = []
        
        for device in devices:
            if hasattr(device, '__dict__'):
                device_dict = device.__dict__.copy()
            else:
                device_dict = device
            
            # Assurer la compatibilité frontend
            if 'status' not in device_dict:
                device_dict['status'] = 'online' if device_dict.get('ip') else 'unknown'
            
            devices_data.append(device_dict)
        
        logger.info(f"✅ Scan terminé: {len(devices_data)} appareils")
        
        return {
            "success": True,
            "devices": devices_data,
            "stats": {
                "total_devices": len(devices_data),
                "online": len([d for d in devices_data if d.get("status") == "online"]),
                "with_mac": len([d for d in devices_data if d.get("mac")]),
                "identified": len([d for d in devices_data if d.get("device_type") != "unknown"])
            },
            "timestamp": time.time(),
            "message": f"🔍 Scan terminé: {len(devices_data)} appareils"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        return {"success": False, "error": str(e)}

@router.get("/scan/result")
async def get_scan_result():
    """
    📊 Résultat du dernier scan (compatibilité frontend)
    """
    try:
        # Utilise le cache du scanner s'il existe, sinon lance un scan
        result = await ultra_scanner.scan_live_ultra()
        
        if result["success"]:
            return {
                "success": True,
                "data": {
                    "devices": result["devices"], 
                    "stats": result["stats"],
                    "timestamp": result.get("timestamp", "unknown")
                }
            }
        else:
            return {"success": False, "error": "Pas de résultat de scan disponible"}
            
    except Exception as e:
        logger.error(f"❌ Erreur résultat scan: {e}")
        return {"success": False, "error": str(e)}

@router.get("/stats")
async def get_network_stats():
    """
    📊 Statistiques réseau ultra détaillées en temps réel
    """
    try:
        result = await ultra_scanner.scan_live_ultra()
        
        if result["success"]:
            enhanced_stats = result["stats"]
            enhanced_stats.update({
                "scan_quality": "ultra_blindé",
                "identification_rate": (enhanced_stats.get("identified_vendor", 0) / max(enhanced_stats.get("total_devices", 1), 1)) * 100,
                "mac_discovery_rate": (enhanced_stats.get("with_mac", 0) / max(enhanced_stats.get("total_devices", 1), 1)) * 100
            })
            
            return {
                "status": "success",
                "stats": enhanced_stats,
                "last_scan": result.get("scan_time", 0),
                "message": "📊 Statistiques ultra détaillées mises à jour"
            }
        else:
            return {
                "status": "error",
                "stats": {"total_devices": 0, "online_devices": 0},
                "error": result.get("error", "Scan failed")
            }
            
    except Exception as e:
        logger.error(f"❌ Erreur stats réseau: {e}")
        return {
            "status": "error", 
            "stats": {"total_devices": 0, "online_devices": 0},
            "error": str(e)
        }

@router.get("/device/{ip}")
async def get_device_details(ip: str):
    """
    🔍 Détails ultra complets d'un appareil spécifique
    """
    try:
        result = await ultra_scanner.scan_live_ultra()
        
        if result["success"]:
            # Recherche de l'appareil par IP
            device = next((d for d in result["devices"] if d["ip"] == ip), None)
            
            if device:
                # Enrichissement des données pour l'affichage
                device["identification_confidence"] = f"{device.get('confidence_score', 0):.1f}%"
                device["scan_techniques"] = ", ".join(device.get('scan_techniques_used', []))
                
                return {
                    "status": "success",
                    "device": device,
                    "message": f"🔍 Appareil {ip} analysé en ultra détail"
                }
            else:
                raise HTTPException(status_code=404, detail=f"Appareil {ip} non trouvé")
        else:
            raise HTTPException(status_code=500, detail="Erreur scan réseau")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur détails appareil {ip}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scan/advanced/{network}")
async def scan_specific_network(network: str):
    """
    🎯 Scan ultra blindé d'un réseau spécifique
    """
    try:
        logger.info(f"🎯 Scan ultra blindé du réseau: {network}")
        
        # Validation basique du format réseau
        if not ("/" in network and any(c.isdigit() for c in network)):
            raise HTTPException(status_code=400, detail="Format réseau invalide (ex: 192.168.1.0/24)")
        
        result = await ultra_scanner.scan_network_ultra_blindé(target_networks=[network])
        devices_data = [device.__dict__ for device in result]
        
        return {
            "status": "success",
            "message": f"🎯 Scan ultra du réseau {network} terminé",
            "network": network,
            "devices": devices_data,
            "stats": {
                "total": len(devices_data),
                "online": len([d for d in devices_data if d.get("status") == "online"]),
                "identified": len([d for d in devices_data if d.get("device_type") != "unknown"]),
                "avg_confidence": sum(d.get("confidence_score", 0) for d in devices_data) / len(devices_data) if devices_data else 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur scan réseau {network}: {e}")
        raise HTTPException(status_code=500, detail=str(e))