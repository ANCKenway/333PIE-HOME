"""
Service de gestion des appareils réseau
Fonctionnalités : Wake-on-LAN, gestion des PC, sauvegarde config
"""

import subprocess
import json
import os
from typing import List, Dict, Optional
from datetime import datetime

class DeviceManager:
    """Gestionnaire des appareils domestiques"""
    
    def __init__(self):
        self.config_file = "config/devices.json"
        self.computers = self._load_computers()
    
    def _load_computers(self) -> List[Dict]:
        """Charge les ordinateurs depuis le fichier de config"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('computers', [])
        except Exception as e:
            print(f"Erreur chargement config: {e}")
        
        # Fallback: PC par défaut
        return [
            {
                "name": "PC-Bureau",
                "ip": "192.168.1.174", 
                "mac": "34-5A-60-7F-12-C1",
                "type": "desktop"
            }
        ]
    
    def _save_computers(self):
        """Sauvegarde les ordinateurs dans le fichier de config"""
        try:
            # Créer le dossier config s'il n'existe pas
            os.makedirs('config', exist_ok=True)
            
            # Charger la config existante ou créer une nouvelle
            config_data = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            
            # Mettre à jour la section computers
            config_data['computers'] = self.computers
            
            # Sauvegarder
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur sauvegarde config: {e}")
    
    def get_computers(self) -> List[Dict]:
        """Récupère la liste des ordinateurs"""
        return self.computers.copy()
    
    def wake_on_lan(self, mac: str) -> Dict:
        """Envoie un paquet Wake-on-LAN (implémentation native Python)"""
        try:
            import socket
            import struct
            
            # Nettoyer l'adresse MAC et la convertir
            mac_clean = mac.replace(':', '').replace('-', '').upper()
            
            # Vérifier que l'adresse MAC est valide
            if len(mac_clean) != 12:
                return {"success": False, "error": "Format MAC invalide"}
            
            try:
                # Convertir MAC en bytes
                mac_bytes = bytes.fromhex(mac_clean)
            except ValueError:
                return {"success": False, "error": "Format MAC invalide"}
            
            # Créer le paquet Magic Packet
            # 6 bytes de 0xFF suivis de 16 répétitions de l'adresse MAC
            magic_packet = b'\xFF' * 6 + mac_bytes * 16
            
            # Envoyer le paquet en broadcast
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            # Envoyer sur plusieurs ports pour maximiser les chances
            broadcast_ports = [7, 9, 40000]  # Ports standards WOL
            
            for port in broadcast_ports:
                sock.sendto(magic_packet, ('255.255.255.255', port))
            
            sock.close()
            
            return {
                "success": True, 
                "message": f"Wake-on-LAN envoyé à {mac} (Magic Packet sur ports 7, 9, 40000)"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Erreur WOL: {str(e)}"}
    
    def add_computer(self, name: str, ip: str, mac: str, device_type: str = "unknown") -> Dict:
        """Ajoute un nouvel ordinateur à la liste"""
        try:
            # Vérifier si l'appareil n'existe pas déjà
            existing = next((c for c in self.computers if c['ip'] == ip or c['mac'] == mac), None)
            if existing:
                return {"success": False, "error": "Appareil déjà existant"}
            
            # Ajouter le nouvel appareil
            new_computer = {
                "name": name,
                "ip": ip,
                "mac": mac.replace(':', '-'),  # Normaliser le format MAC
                "type": device_type,
                "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.computers.append(new_computer)
            self._save_computers()
            
            return {"success": True, "message": f"Appareil {name} ajouté avec succès"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def remove_computer(self, identifier: str) -> Dict:
        """Supprime un ordinateur (par IP ou MAC)"""
        try:
            original_count = len(self.computers)
            self.computers = [c for c in self.computers 
                            if c['ip'] != identifier and c['mac'] != identifier]
            
            if len(self.computers) < original_count:
                self._save_computers()
                return {"success": True, "message": "Appareil supprimé"}
            else:
                return {"success": False, "error": "Appareil non trouvé"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def ping_device(self, ip: str) -> bool:
        """Vérifie si un appareil répond au ping"""
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "2", ip], 
                capture_output=True, 
                timeout=3
            )
            return result.returncode == 0
        except:
            return False