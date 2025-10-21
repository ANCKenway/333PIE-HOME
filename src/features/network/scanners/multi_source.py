"""
🏠 333HOME - Multi-Source Network Scanner

Scanner universel orchestrant plusieurs sources pour enrichissement maximal.
Architecture modulaire (RULES.MD compliant).

Sources:
- Tailscale: VPN devices avec hostnames
- ARP: MAC/IP mapping (rapide, fiable)
- mDNS: Service discovery (hostname .local)
- NetBIOS: Windows name resolution
- nmap: Scan réseau complet (IP, ports, OS detection)

Références:
- docs/NETWORK_PRO_ARCHITECTURE.md
- src/features/network/scanners/ (modules individuels)
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from src.core.device_intelligence import DeviceData, DeviceIntelligenceEngine
from src.core.models.unified_device import UnifiedDevice, DeviceStatus
from .arp_scanner import ARPScanner  # ✅ Import direct (même dossier)
from .nmap_scanner import NmapScanner
from .mdns_scanner import MDNSScanner
from .netbios_scanner import NetBIOSScanner
from .tailscale_scanner import TailscaleScanner

logger = logging.getLogger(__name__)


class MultiSourceScanner:
    """
    Scanner multi-sources pour découverte réseau complète
    
    Combine Tailscale + ARP + mDNS + NetBIOS + nmap.
    Utilise DeviceIntelligenceEngine pour fusion intelligente.
    """
    
    def __init__(self, subnet: str = "192.168.1.0/24"):
        self.subnet = subnet
        self.engine = DeviceIntelligenceEngine()
        self.logger = logger
        
        # Configuration sources
        self.enabled_sources = {
            'tailscale': True,
            'arp': True,
            'mdns': True,
            'netbios': True,
            'nmap': True,
        }
        
        # Scanners modulaires
        self.scanners = {
            'tailscale': TailscaleScanner(subnet),
            'arp': ARPScanner(subnet),
            'mdns': MDNSScanner(subnet),
            'netbios': NetBIOSScanner(subnet),
            'nmap': NmapScanner(subnet),
        }
        
        # Cache des derniers scans
        self.last_scan_results: Dict[str, List[DeviceData]] = {}
        self.last_unified_devices: Dict[str, UnifiedDevice] = {}
    
    async def scan_all(self) -> List[UnifiedDevice]:
        """
        Lance tous les scans avec throttling
        
        🔧 Scans séquentiels pour éviter surcharge réseau
        
        Returns:
            Liste des UnifiedDevice enrichis
        """
        self.logger.info(f"🔍 Starting multi-source scan on {self.subnet} (throttled mode)")
        start_time = datetime.now()
        
        # Scans séquentiels avec throttling
        results = []
        
        # 1. Tailscale (VPN) - enrichissement uniquement (traité après)
        tailscale_enrichment = {}
        if self.enabled_sources['tailscale']:
            self.logger.info("⏳ Tailscale enrichment scan (1/5)...")
            tailscale_enrichment = await self.scanners['tailscale'].scan()
            await asyncio.sleep(1)
        
        # 2. ARP (rapide)
        if self.enabled_sources['arp']:
            self.logger.info("⏳ ARP scan (2/5)...")
            results.append(await self.scanners['arp'].scan())
            await asyncio.sleep(2)
        
        # 3. mDNS
        if self.enabled_sources['mdns']:
            self.logger.info("⏳ mDNS scan (3/5)...")
            results.append(await self.scanners['mdns'].scan())
            await asyncio.sleep(2)
        
        # 4. NetBIOS (Windows)
        if self.enabled_sources['netbios']:
            self.logger.info("⏳ NetBIOS scan (4/5)...")
            results.append(await self.scanners['netbios'].scan())
            await asyncio.sleep(2)
        
        # 5. Nmap (le plus lent)
        if self.enabled_sources['nmap']:
            self.logger.info("⏳ nmap scan (5/5 - slowest)...")
            results.append(await self.scanners['nmap'].scan())
        
        # Fusionner les résultats (SAUF Tailscale)
        all_device_data: List[DeviceData] = []
        for result in results:
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
            
            # Créer UnifiedDevice
            try:
                unified = self._create_unified_device(merged_dict, sources)
                unified_devices.append(unified)
            except Exception as e:
                self.logger.error(f"Failed to create UnifiedDevice for {mac}: {e}")
        
        # Enrichir avec données Tailscale (VPN badge)
        if tailscale_enrichment:
            self._enrich_with_tailscale(unified_devices, tailscale_enrichment)
        
        # Sauvegarder pour prochaine itération
        self.last_unified_devices = {d.mac: d for d in unified_devices}
        
        # Stats
        duration = (datetime.now() - start_time).total_seconds()
        vpn_count = sum(1 for d in unified_devices if d.is_vpn_connected)
        self.logger.info(f"✅ Scan complete: {len(unified_devices)} devices ({vpn_count} on VPN) in {duration:.2f}s")
        
        return unified_devices
    
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
            
            # 🔧 Update status based on scan result
            if merged_dict.get('is_online'):
                device.status = DeviceStatus.ONLINE
                if not device.is_online:
                    device.start_online_period()
            else:
                device.status = DeviceStatus.OFFLINE
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
            # Update average latency
            if device.average_latency_ms > 0:
                device.average_latency_ms = (device.average_latency_ms + merged_dict['response_time_ms']) / 2
            else:
                device.average_latency_ms = merged_dict['response_time_ms']
        
        return device
    
    def _enrich_with_tailscale(
        self,
        devices: List[UnifiedDevice],
        tailscale_map: Dict[str, Dict[str, str]]
    ) -> None:
        """
        Enrichir les devices locaux avec info VPN Tailscale
        
        Matche par hostname (case-insensitive) et ajoute badge VPN.
        N'ajoute PAS de nouveaux devices (évite les duplicatas).
        
        Args:
            devices: Liste des UnifiedDevice à enrichir
            tailscale_map: {hostname_upper: {'vpn_ip': '100.x.x.x', 'local_ip': '192.168.x.x'}}
        """
        if not tailscale_map:
            return
        
        matched_count = 0
        
        for device in devices:
            # Normaliser le hostname du device
            device_hostname = (device.hostname or device.name or "").strip().upper()
            if not device_hostname:
                continue
            
            # Matcher avec Tailscale (hostname court)
            device_hostname_short = device_hostname.split('.')[0]
            
            if device_hostname_short in tailscale_map:
                vpn_info = tailscale_map[device_hostname_short]
                
                # Enrichir le device avec VPN info
                device.is_vpn_connected = True
                device.vpn_ip = vpn_info['vpn_ip']
                device.vpn_hostname = vpn_info.get('full_hostname', device_hostname)
                
                # Ajouter 'tailscale' aux sources
                if 'tailscale' not in device.sources:
                    device.sources.append('tailscale')
                
                matched_count += 1
                self.logger.debug(f"🔗 Matched VPN: {device_hostname_short} → {vpn_info['vpn_ip']}")
        
        self.logger.info(f"🔗 Tailscale: Enriched {matched_count}/{len(tailscale_map)} VPN devices")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Statistiques du dernier scan"""
        if not self.last_unified_devices:
            return {
                'total_devices': 0,
                'online_devices': 0,
                'sources_used': [],
            }
        
        devices = list(self.last_unified_devices.values())
        online = sum(1 for d in devices if d.is_online)
        sources_used = set()
        for d in devices:
            sources_used.update(d.sources)
        
        return {
            'total_devices': len(devices),
            'online_devices': online,
            'sources_used': sorted(list(sources_used)),
            'average_confidence': sum(d.confidence_score for d in devices) / len(devices),
        }
