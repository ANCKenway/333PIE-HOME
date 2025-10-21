"""
🏠 333HOME - Multi-Source Network Scanner

Scanner universel combinant plusieurs sources pour enrichissement maximal.
Agnostique du routeur - fonctionne sur tout réseau.

Sources:
- nmap: Scan réseau complet (IP, ports, OS detection)
- ARP: MAC/IP mapping (rapide, fiable)
- mDNS: Service discovery (hostname .local)
- NetBIOS: Windows name resolution

Architecture: Parallèle + Fusion intelligente via DeviceIntelligenceEngine

Références:
- docs/NETWORK_PRO_ARCHITECTURE.md
- TODO_NETWORK_PRO.md Phase 2
"""

import asyncio
import subprocess
import json
import re
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as ET
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.core.device_intelligence import DeviceData, DeviceIntelligenceEngine
from src.core.models.unified_device import UnifiedDevice, DeviceStatus

# Logger
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


class MultiSourceScanner:
    """
    Scanner multi-sources pour découverte réseau complète
    
    Combine nmap + ARP + mDNS + NetBIOS pour enrichissement maximal.
    Utilise DeviceIntelligenceEngine pour fusion intelligente.
    """
    
    def __init__(self, subnet: str = "192.168.1.0/24"):
        self.subnet = subnet
        self.engine = DeviceIntelligenceEngine()
        self.logger = logger
        
        # Configuration sources
        self.enabled_sources = {
            'nmap': True,
            'arp': True,
            'mdns': True,
            'netbios': True,
            'tailscale': True  # VPN devices
        }
        
        # Cache des derniers scans
        self.last_scan_results: Dict[str, List[DeviceData]] = {}
        self.last_unified_devices: Dict[str, UnifiedDevice] = {}
    
    async def scan_all(self) -> List[UnifiedDevice]:
        """
        Lance tous les scans avec throttling pour éviter surcharge réseau
        
        🔧 Optimisé: Scans séquentiels avec délais pour ne pas perturber le LAN
        
        Returns:
            Liste des UnifiedDevice enrichis
        """
        self.logger.info(f"🔍 Starting multi-source scan on {self.subnet} (throttled mode)")
        start_time = datetime.now()
        
        # 🔧 SCANS SÉQUENTIELS avec throttling (au lieu de parallèle)
        # Raison: Éviter pics de trafic réseau et détection antivirus
        results = []
        
        if self.enabled_sources['tailscale']:
            self.logger.info("⏳ Tailscale scan (1/5)...")
            results.append(await self.scan_tailscale())
            await asyncio.sleep(1)
        
        if self.enabled_sources['arp']:
            self.logger.info("⏳ ARP scan (2/5)...")
            results.append(await self.scan_arp())
            await asyncio.sleep(2)  # Throttle 2s entre sources
        
        if self.enabled_sources['mdns']:
            self.logger.info("⏳ mDNS scan (3/5)...")
            results.append(await self.scan_mdns())
            await asyncio.sleep(2)
        
        if self.enabled_sources['netbios']:
            self.logger.info("⏳ NetBIOS scan (4/5)...")
            results.append(await self.scan_netbios())
            await asyncio.sleep(2)
        
        if self.enabled_sources['nmap']:
            self.logger.info("⏳ nmap scan (5/5 - slowest)...")
            results.append(await self.scan_nmap())
        
        # Traiter résultats (comme avant)
        results = [r for r in results if not isinstance(r, Exception)]
        
        # Filtrer les erreurs
        all_device_data: List[DeviceData] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Scan failed: {result}")
                continue
            if result:
                all_device_data.extend(result)
        
        # Grouper par MAC
        devices_by_mac: Dict[str, List[DeviceData]] = {}
        for data in all_device_data:
            mac = data.mac.upper()
            if mac not in devices_by_mac:
                devices_by_mac[mac] = []
            devices_by_mac[mac].append(data)
        
        # Fusionner avec DeviceIntelligenceEngine
        unified_devices: List[UnifiedDevice] = []
        for mac, sources in devices_by_mac.items():
            # Merger les données
            merged_dict = self.engine.merge_device_data(sources)
            
            # Calculer confidence
            confidence = self.engine.calculate_confidence(merged_dict, sources)
            merged_dict['confidence_score'] = confidence
            
            # Détecter changements si device existant
            if mac in self.last_unified_devices:
                old_device = self.last_unified_devices[mac]
                changes = self.engine.detect_changes(
                    old_device.to_dict(),
                    merged_dict
                )
                if changes:
                    self.logger.info(f"📊 {len(changes)} changes detected for {mac[:17]}")
                    for change in changes:
                        self.logger.info(f"   • {change.change_type.value}: {change.old_value} → {change.new_value}")
            
            # Créer UnifiedDevice
            try:
                unified = self._create_unified_device(merged_dict, sources)
                unified_devices.append(unified)
            except Exception as e:
                self.logger.error(f"Failed to create UnifiedDevice for {mac}: {e}")
        
        # Détecter conflits
        conflicts = self.engine.detect_conflicts([d.to_dict() for d in unified_devices])
        if conflicts:
            self.logger.warning(f"⚠️  {len(conflicts)} network conflicts detected!")
            for conflict in conflicts:
                self.logger.warning(f"   {conflict.conflict_type.value}: {conflict.description}")
        
        # Sauvegarder cache
        self.last_unified_devices = {d.mac: d for d in unified_devices}
        
        duration = (datetime.now() - start_time).total_seconds()
        self.logger.info(f"✅ Scan complete: {len(unified_devices)} devices in {duration:.2f}s")
        
        return unified_devices
    
    async def scan_nmap(self) -> List[DeviceData]:
        """
        Scan nmap: IP, ports, OS detection, latency
        
        Command: nmap -sn -T2 (polite timing)
        🔧 Optimisé pour ne pas perturber le réseau
        """
        self.logger.info("📡 nmap: Starting (polite mode)...")
        devices = []
        
        try:
            # -T2 = Polite timing (moins agressif que défaut -T3)
            # -sn = ping scan, -PR = ARP ping ACTIVÉ (plus rapide!)
            # --max-rate=50 = Limite à 50 paquets/sec max
            # --host-timeout=2s = Timeout de 2s par host
            cmd = f"nmap -sn -T2 -PR --max-rate=50 --host-timeout=2s -oX - {self.subnet}"
            
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Timeout global de 60 secondes max pour tout le scan
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60.0)
            except asyncio.TimeoutError:
                proc.kill()
                self.logger.warning("nmap: Timeout after 60s")
                return devices
            
            if proc.returncode != 0:
                self.logger.error(f"nmap failed: {stderr.decode()}")
                return devices
            
            # Parse XML output
            root = ET.fromstring(stdout.decode())
            
            for host in root.findall('.//host'):
                # Status
                status = host.find('status')
                if status is None or status.get('state') != 'up':
                    continue
                
                # IP
                address_ip = host.find("./address[@addrtype='ipv4']")
                if address_ip is None:
                    continue
                ip = address_ip.get('addr')
                
                # MAC
                address_mac = host.find("./address[@addrtype='mac']")
                if address_mac is None:
                    continue
                mac = address_mac.get('addr')
                vendor = address_mac.get('vendor')
                
                # Hostname
                hostname = None
                hostnames = host.find('hostnames')
                if hostnames is not None:
                    hostname_elem = hostnames.find('hostname')
                    if hostname_elem is not None:
                        hostname = hostname_elem.get('name')
                
                # Latency
                times = host.find('times')
                latency = None
                if times is not None:
                    rtt = times.get('rttvar')
                    if rtt:
                        latency = float(rtt) / 1000  # Convert to ms
                
                device = DeviceData(
                    mac=mac,
                    ip=ip,
                    hostname=hostname,
                    vendor=vendor,
                    source='nmap',
                    is_online=True,
                    response_time_ms=latency,
                    timestamp=datetime.now(),
                    scan_type='ping'
                )
                devices.append(device)
            
            self.logger.info(f"📡 nmap: Found {len(devices)} devices")
            
        except Exception as e:
            self.logger.error(f"nmap scan error: {e}")
        
        return devices
    
    async def scan_arp(self) -> List[DeviceData]:
        """
        Scan ARP cache: MAC/IP mapping rapide et fiable
        
        Command: ip neigh show
        """
        self.logger.info("📡 ARP: Starting...")
        devices = []
        
        try:
            proc = await asyncio.create_subprocess_shell(
                "ip neigh show",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                self.logger.error(f"ARP scan failed: {stderr.decode()}")
                return devices
            
            # Parse output
            # Format: IP dev INTERFACE lladdr MAC REACHABLE/STALE/DELAY
            for line in stdout.decode().split('\n'):
                if not line.strip():
                    continue
                
                parts = line.split()
                if len(parts) < 5:
                    continue
                
                ip = parts[0]
                
                # Find MAC (after lladdr)
                try:
                    lladdr_idx = parts.index('lladdr')
                    mac = parts[lladdr_idx + 1]
                except (ValueError, IndexError):
                    continue
                
                # Check if reachable
                is_online = 'REACHABLE' in line or 'DELAY' in line
                
                device = DeviceData(
                    mac=mac,
                    ip=ip,
                    source='arp',
                    is_online=is_online,
                    timestamp=datetime.now(),
                    scan_type='arp_cache'
                )
                devices.append(device)
            
            self.logger.info(f"📡 ARP: Found {len(devices)} devices")
            
        except Exception as e:
            self.logger.error(f"ARP scan error: {e}")
        
        return devices
    
    async def scan_mdns(self) -> List[DeviceData]:
        """
        Scan mDNS: Service discovery pour hostnames .local
        
        Uses avahi-browse if available
        """
        self.logger.info("📡 mDNS: Starting...")
        devices = []
        
        try:
            # Check if avahi-browse is available
            check = await asyncio.create_subprocess_shell(
                "which avahi-browse",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await check.communicate()
            
            if check.returncode != 0:
                self.logger.warning("mDNS: avahi-browse not found, skipping")
                return devices
            
            # Scan for all services
            proc = await asyncio.create_subprocess_shell(
                "avahi-browse -a -t -r -p",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5.0)
            except asyncio.TimeoutError:
                proc.kill()
                self.logger.warning("mDNS: Timeout after 5s")
                return devices
            
            # Parse output
            # Format: =;interface;protocol;name;type;domain;hostname;address;port;txt
            seen_macs = set()
            for line in stdout.decode().split('\n'):
                if not line.startswith('='):
                    continue
                
                parts = line.split(';')
                if len(parts) < 8:
                    continue
                
                hostname = parts[6] if len(parts) > 6 else None
                ip = parts[7] if len(parts) > 7 else None
                
                if not hostname or not ip:
                    continue
                
                # Get MAC from ARP (mDNS doesn't provide MAC)
                # This is a limitation - we need to correlate with ARP
                # For now, skip if we can't get MAC
                mac = await self._get_mac_for_ip(ip)
                if not mac or mac in seen_macs:
                    continue
                
                seen_macs.add(mac)
                
                device = DeviceData(
                    mac=mac,
                    ip=ip,
                    hostname=hostname,
                    source='mdns',
                    is_online=True,
                    timestamp=datetime.now(),
                    scan_type='service_discovery'
                )
                devices.append(device)
            
            self.logger.info(f"📡 mDNS: Found {len(devices)} devices")
            
        except Exception as e:
            self.logger.error(f"mDNS scan error: {e}")
        
        return devices
    
    async def scan_netbios(self) -> List[DeviceData]:
        """
        Scan NetBIOS: Windows name resolution
        
        Uses nbtscan if available
        """
        self.logger.info("📡 NetBIOS: Starting...")
        devices = []
        
        try:
            # Check if nbtscan is available
            check = await asyncio.create_subprocess_shell(
                "which nbtscan",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await check.communicate()
            
            if check.returncode != 0:
                self.logger.warning("NetBIOS: nbtscan not found, skipping")
                return devices
            
            # Scan subnet
            proc = await asyncio.create_subprocess_shell(
                f"nbtscan -r {self.subnet}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            # Parse output
            # Format: IP    NetBIOS_Name    Server    User    MAC
            for line in stdout.decode().split('\n'):
                if not line.strip() or line.startswith('Doing'):
                    continue
                
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                ip = parts[0]
                hostname = parts[1]
                
                # Try to extract MAC from end of line
                mac_match = re.search(r'([0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2})', line)
                if not mac_match:
                    # Fallback: get MAC from ARP
                    mac = await self._get_mac_for_ip(ip)
                    if not mac:
                        continue
                else:
                    mac = mac_match.group(1)
                
                device = DeviceData(
                    mac=mac,
                    ip=ip,
                    hostname=hostname,
                    source='netbios',
                    is_online=True,
                    timestamp=datetime.now(),
                    scan_type='netbios_scan'
                )
                devices.append(device)
            
            self.logger.info(f"📡 NetBIOS: Found {len(devices)} devices")
            
        except Exception as e:
            self.logger.error(f"NetBIOS scan error: {e}")
        
        return devices
    
    async def scan_tailscale(self) -> List[DeviceData]:
        """
        Scan Tailscale VPN: récupère les devices connectés au réseau VPN
        
        Uses tailscale status --json
        """
        self.logger.info("📡 Tailscale: Starting...")
        devices = []
        
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
                return devices
            
            # Get tailscale status JSON
            proc = await asyncio.create_subprocess_shell(
                "tailscale status --json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                self.logger.warning(f"Tailscale: Not running or not connected")
                return devices
            
            # Parse JSON
            import json
            data = json.loads(stdout.decode())
            
            # Iterate over peers
            for peer_id, peer_data in data.get('Peer', {}).items():
                hostname = peer_data.get('HostName', 'Unknown')
                tailscale_ips = peer_data.get('TailscaleIPs', [])
                
                if not tailscale_ips:
                    continue
                
                tailscale_ip = tailscale_ips[0]  # Première IP Tailscale
                
                # Essayer de récupérer la MAC depuis l'ARP cache
                # Note: Les IPs Tailscale (100.x.x.x) n'auront généralement pas de MAC
                # mais on peut chercher le hostname dans l'ARP local
                mac = await self._find_mac_by_hostname(hostname)
                
                if not mac:
                    # Utiliser l'IP Tailscale comme identifiant unique si pas de MAC
                    mac = f"VPN:{tailscale_ip.replace('.', ':')}"
                
                device = DeviceData(
                    mac=mac,
                    ip=tailscale_ip,
                    hostname=hostname,
                    source='tailscale',
                    is_online=True,  # Si dans tailscale status = online
                    timestamp=datetime.now(),
                    scan_type='tailscale_vpn',
                    vendor='Tailscale VPN'
                )
                devices.append(device)
            
            self.logger.info(f"📡 Tailscale: Found {len(devices)} VPN devices")
            
        except Exception as e:
            self.logger.error(f"Tailscale scan error: {e}")
        
        return devices
    
    async def _find_mac_by_hostname(self, hostname: str) -> Optional[str]:
        """Helper: Chercher MAC d'un device via son hostname dans ARP"""
        try:
            # Essayer de résoudre le hostname en IP locale
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
                    # Chercher MAC pour cette IP locale
                    return await self._get_mac_for_ip(local_ip)
        except:
            pass
        return None
    
    async def _get_mac_for_ip(self, ip: str) -> Optional[str]:
        """Helper: Get MAC from ARP cache for given IP"""
        try:
            proc = await asyncio.create_subprocess_shell(
                f"ip neigh show {ip}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            
            # Parse: IP dev INTERFACE lladdr MAC
            output = stdout.decode()
            match = re.search(r'lladdr\s+([0-9a-fA-F:]+)', output)
            if match:
                return match.group(1)
        except:
            pass
        return None
    
    def _create_unified_device(
        self,
        merged_dict: Dict[str, Any],
        sources: List[DeviceData]
    ) -> UnifiedDevice:
        """
        Créer UnifiedDevice depuis données fusionnées
        """
        mac = merged_dict['mac']
        
        # Créer ou mettre à jour
        if mac in self.last_unified_devices:
            device = self.last_unified_devices[mac]
            
            # Update fields
            if merged_dict.get('ip') and merged_dict['ip'] != device.current_ip:
                device.add_ip_change(
                    merged_dict['ip'],
                    merged_dict.get('sources', ['unknown'])[0],
                    reason='scan_detected'
                )
            
            if merged_dict.get('hostname') and merged_dict['hostname'] != device.hostname:
                device.add_hostname_change(
                    merged_dict['hostname'],
                    merged_dict.get('sources', ['unknown'])[0]
                )
            
            device.last_seen = datetime.now()
            device.increment_detection()
            
            if merged_dict.get('is_online'):
                if not device.is_online:
                    device.start_online_period()
            else:
                if device.is_online:
                    device.mark_offline()
            
        else:
            # Nouveau device
            status = DeviceStatus.ONLINE if merged_dict.get('is_online', True) else DeviceStatus.OFFLINE
            
            device = UnifiedDevice(
                mac=mac,
                id=f"dev_{mac.replace(':', '').lower()}",
                name=merged_dict.get('hostname', 'Unknown'),
                hostname=merged_dict.get('hostname'),
                vendor=merged_dict.get('vendor'),
                current_ip=merged_dict.get('ip'),
                subnet=self.subnet,
                status=status,
                last_seen=datetime.now(),
                first_seen=datetime.now(),
                sources=merged_dict.get('sources', []),
                confidence_score=merged_dict.get('confidence_score', 0.0),
                data_quality=merged_dict.get('data_quality', 'medium')
            )
            
            if merged_dict.get('is_online'):
                device.start_online_period()
        
        # Update stats
        device.sources = merged_dict.get('sources', [])
        device.confidence_score = merged_dict.get('confidence_score', 0.0)
        device.data_quality = merged_dict.get('data_quality', 'medium')
        device.last_updated = datetime.now()
        
        if merged_dict.get('response_time_ms'):
            # Update average latency (simple moving average)
            if device.average_latency_ms > 0:
                device.average_latency_ms = (device.average_latency_ms + merged_dict['response_time_ms']) / 2
            else:
                device.average_latency_ms = merged_dict['response_time_ms']
        
        return device
    
    def get_statistics(self) -> Dict[str, Any]:
        """Statistiques du dernier scan"""
        if not self.last_unified_devices:
            return {
                'total_devices': 0,
                'online_devices': 0,
                'offline_devices': 0,
                'sources_used': [],
                'avg_confidence': 0.0
            }
        
        devices = list(self.last_unified_devices.values())
        online = sum(1 for d in devices if d.is_online)
        
        # Sources utilisées
        all_sources = set()
        for d in devices:
            all_sources.update(d.sources)
        
        # Confidence moyenne
        avg_conf = sum(d.confidence_score for d in devices) / len(devices)
        
        return {
            'total_devices': len(devices),
            'online_devices': online,
            'offline_devices': len(devices) - online,
            'sources_used': list(all_sources),
            'avg_confidence': round(avg_conf, 2),
            'last_scan': datetime.now().isoformat()
        }


# === CLI pour tests ===

async def main():
    """Test CLI"""
    import sys
    
    subnet = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.0/24"
    
    print(f"\n🏠 333HOME - Multi-Source Scanner Test")
    print(f"Subnet: {subnet}\n")
    
    scanner = MultiSourceScanner(subnet)
    devices = await scanner.scan_all()
    
    print(f"\n📊 Results:")
    print(f"   Total devices: {len(devices)}")
    print(f"\n{'MAC':<20} {'IP':<15} {'Hostname':<25} {'Vendor':<20} {'Sources'}")
    print("=" * 110)
    
    for device in sorted(devices, key=lambda d: d.current_ip or ''):
        sources_str = ','.join(device.sources)
        print(f"{device.mac:<20} {device.current_ip or 'N/A':<15} {device.hostname or 'Unknown':<25} {device.vendor or 'N/A':<20} {sources_str}")
    
    stats = scanner.get_statistics()
    print(f"\n📈 Statistics:")
    print(f"   Online: {stats['online_devices']}/{stats['total_devices']}")
    print(f"   Sources: {', '.join(stats['sources_used'])}")
    print(f"   Avg confidence: {stats['avg_confidence']:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
