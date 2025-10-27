"""
🏠 333HOME - Tailscale VPN Scanner

Scanner pour devices connectés au réseau VPN Tailscale.
Récupère les hostnames et IPs VPN via 'tailscale status --json'.

⚠️ NE CRÉE PAS DE DEVICES - retourne un enrichissement pour corréler avec devices locaux
"""

import asyncio
import json
import logging
import re
from typing import Dict, Optional


logger = logging.getLogger(__name__)


class TailscaleScanner:
    """
    Scanner Tailscale VPN
    
    Récupère les devices connectés au réseau VPN avec leurs hostnames.
    Retourne un dictionnaire hostname→(vpn_ip, local_ip) pour enrichir
    les devices locaux existants (PAS de création de duplicatas).
    """
    
    def __init__(self, subnet: str = "192.168.1.0/24"):
        self.subnet = subnet
        self.logger = logger
    
    async def scan(self) -> Dict[str, Dict[str, str]]:
        """
        Scan Tailscale VPN: récupère les devices connectés
        
        Returns:
            Dict {hostname: {'vpn_ip': '100.x.x.x', 'local_ip': '192.168.x.x'}}
            Pour enrichir les devices locaux existants (pas créer de duplicatas)
        """
        self.logger.info("📡 Tailscale: Starting enrichment scan...")
        enrichment_map = {}
        
        try:
            # Check if tailscale is available
            check = await asyncio.create_subprocess_shell(
                "which tailscale",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await check.communicate()
            
            if check.returncode != 0:
                self.logger.warning("Tailscale: Not installed, skipping")
                return enrichment_map
            
            # Get tailscale status JSON
            proc = await asyncio.create_subprocess_shell(
                "tailscale status --json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                self.logger.warning(f"Tailscale: Not running or not connected")
                return enrichment_map
            
            # Parse JSON
            data = json.loads(stdout.decode())
            
            # 1. Ajouter Self (notre propre device)
            self_data = data.get('Self', {})
            if self_data:
                hostname = self_data.get('HostName', '').strip()
                tailscale_ips = self_data.get('TailscaleIPs', [])
                is_online = self_data.get('Online', False)
                
                if hostname and tailscale_ips:
                    vpn_ip = tailscale_ips[0]
                    hostname_short = hostname.split('.')[0].upper()
                    
                    enrichment_map[hostname_short] = {
                        'vpn_ip': vpn_ip,
                        'local_ip': '192.168.1.150',  # Notre IP locale (connue)
                        'full_hostname': hostname,
                        'is_online': is_online,
                        'is_self': True  # Marqueur pour nous-mêmes
                    }
                    self.logger.info(f"📡 Tailscale: Added Self ({hostname} - {vpn_ip})")
            
            # 2. Itérer sur les peers (autres devices)
            for peer_id, peer_data in data.get('Peer', {}).items():
                hostname = peer_data.get('HostName', '').strip()
                tailscale_ips = peer_data.get('TailscaleIPs', [])
                is_online = peer_data.get('Online', False)  # ⚠️ CRITIQUE: vérifier si VPN actif
                
                if not hostname or not tailscale_ips:
                    continue
                
                vpn_ip = tailscale_ips[0]  # Première IP Tailscale
                
                # Normaliser hostname (enlever domain si présent)
                hostname_short = hostname.split('.')[0].upper()
                
                # Essayer de résoudre vers une IP locale
                local_ip = await self._resolve_to_local_ip(hostname)
                
                enrichment_map[hostname_short] = {
                    'vpn_ip': vpn_ip,
                    'local_ip': local_ip,  # Peut être None
                    'full_hostname': hostname,
                    'is_online': is_online  # ✅ Status VPN (connecté/déconnecté)
                }
            
            online_count = sum(1 for v in enrichment_map.values() if v['is_online'])
            self.logger.info(f"📡 Tailscale: Found {len(enrichment_map)} VPN devices ({online_count} online, {len(enrichment_map)-online_count} offline)")
            
        except Exception as e:
            self.logger.error(f"Tailscale scan error: {e}")
        
        return enrichment_map
    
    async def _resolve_to_local_ip(self, hostname: str) -> Optional[str]:
        """
        Résoudre un hostname vers une IP locale (192.168.x.x)
        
        Utilise getent hosts pour tenter de résoudre le hostname
        vers une IP du réseau local.
        """
        try:
            proc = await asyncio.create_subprocess_shell(
                f"getent hosts {hostname}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            
            if proc.returncode == 0:
                output = stdout.decode().strip()
                # Format: IP hostname
                parts = output.split()
                if parts:
                    local_ip = parts[0]
                    # Vérifier que c'est bien une IP locale (192.168.x.x ou 10.x.x.x)
                    if local_ip.startswith(('192.168.', '10.', '172.')):
                        return local_ip
        except Exception as e:
            self.logger.debug(f"Could not resolve {hostname}: {e}")
        
        return None
