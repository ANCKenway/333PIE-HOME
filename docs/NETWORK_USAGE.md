# 🏠 333HOME - Network Monitoring Pro - Documentation

**Version**: 1.0  
**Date**: 21 octobre 2025  
**Status**: ✅ Production Ready

---

## 📋 Vue d'ensemble

Système de monitoring réseau professionnel multi-sources avec détection intelligente des changements.

### Architecture

```
MultiSourceScanner (nmap+ARP+mDNS+NetBIOS)
          ↓
DeviceIntelligenceEngine (fusion + confidence + conflicts)
          ↓
UnifiedDevice Model (historique complet)
          ↓
NetworkServiceUnified (persistence + API)
          ↓
NetworkMonitoringService (background + alertes)
          ↓
API REST (/api/network/v2/*)
```

---

## 🚀 Démarrage Rapide

### 1. Démarrer l'application

```bash
cd /home/pie333/333HOME
./start.sh
```

Le monitoring démarre automatiquement en background (scan toutes les 5min).

### 2. Vérifier le status

```bash
curl http://localhost:8000/api/network/v2/health
```

### 3. Scanner manuellement

```bash
curl -X POST http://localhost:8000/api/network/v2/scan
```

---

## 📡 API Endpoints

### Base URL: `/api/network/v2`

### `GET /devices`
Liste tous les devices découverts.

**Query params**:
- `online_only=true` - Seulement les devices online
- `sources=nmap,arp` - Filtre par sources

**Response**:
```json
{
  "success": true,
  "count": 10,
  "devices": [
    {
      "mac": "AA:BB:CC:DD:EE:FF",
      "current_ip": "192.168.1.100",
      "hostname": "my-device",
      "vendor": "Apple",
      "sources": ["nmap", "arp", "mdns"],
      "confidence_score": 0.85,
      "is_online": true,
      "uptime_percentage": 95.5,
      ...
    }
  ]
}
```

### `GET /devices/{mac}`
Détails complets d'un device.

**Example**:
```bash
curl http://localhost:8000/api/network/v2/devices/AA:BB:CC:DD:EE:FF
```

### `GET /devices/{mac}/history`
Historique complet (IP, hostname, uptime).

**Response**:
```json
{
  "success": true,
  "history": {
    "mac": "AA:BB:CC:DD:EE:FF",
    "ip_history": [
      {
        "old_ip": "192.168.1.100",
        "new_ip": "192.168.1.101",
        "changed_at": "2025-10-21T10:30:00",
        "detected_by": "nmap"
      }
    ],
    "hostname_history": [...],
    "uptime_periods": [...],
    "statistics": {
      "total_scans": 150,
      "uptime_percentage": 95.5,
      "average_latency_ms": 3.2
    }
  }
}
```

### `GET /stats`
Statistiques réseau globales.

**Response**:
```json
{
  "success": true,
  "statistics": {
    "total_devices": 10,
    "online_devices": 8,
    "offline_devices": 2,
    "avg_confidence": 0.78,
    "avg_uptime": 92.3,
    "last_scan": "2025-10-21T11:57:03.903496"
  }
}
```

### `POST /scan`
Force un scan réseau immédiat (en background).

```bash
curl -X POST http://localhost:8000/api/network/v2/scan
```

### `GET /conflicts`
Liste des conflits réseau détectés (IP duplicate, MAC spoofing).

**Response**:
```json
{
  "success": true,
  "count": 1,
  "conflicts": [
    {
      "type": "ip_duplicate",
      "severity": "critical",
      "description": "IP 192.168.1.100 used by 2 devices",
      "affected_devices": ["AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66"],
      "detected_at": "2025-10-21T11:57:00"
    }
  ]
}
```

### `GET /monitoring/stats`
Statistiques du service de monitoring.

**Response**:
```json
{
  "success": true,
  "is_running": true,
  "config": {
    "scan_interval_seconds": 300,
    "enabled": true,
    "detect_changes": true
  },
  "stats": {
    "total_scans": 15,
    "last_scan": "2025-10-21T11:57:03",
    "total_changes_detected": 12,
    "new_devices_detected": 10,
    "devices_offline_detected": 1,
    "ip_changes_detected": 1,
    "hostname_changes_detected": 0,
    "uptime_seconds": 3600
  }
}
```

### `GET /health`
Health check du service.

---

## 🔍 Sources de données

Le système combine 4 sources pour maximum de précision :

### 1. **nmap** (haute fiabilité - 0.9)
- Scan réseau complet
- Détection OS
- Ports ouverts
- Latence

**Commande**: `nmap -sn -PR --disable-arp-ping 192.168.1.0/24`

### 2. **ARP** (fiabilité moyenne - 0.8)
- Cache ARP local
- Mapping MAC/IP rapide
- Status (REACHABLE/STALE)

**Commande**: `ip neigh show`

### 3. **mDNS** (fiabilité moyenne - 0.7)
- Service discovery
- Hostnames `.local`
- Devices Apple/Linux

**Commande**: `avahi-browse -a -t -r -p` (si installé)

### 4. **NetBIOS** (fiabilité moyenne - 0.7)
- Windows name resolution
- Devices Windows

**Commande**: `nbtscan -r 192.168.1.0/24` (si installé)

---

## 📊 Modèle de données: UnifiedDevice

### Champs principaux

```python
UnifiedDevice:
    # Identifiants
    mac: str                        # MAC address (clé primaire)
    id: str                         # dev_aabbccddeeff
    name: str                       # Nom custom ou hostname
    hostname: str                   # Hostname réseau
    vendor: str                     # Constructeur (OUI)
    
    # Réseau
    current_ip: str
    subnet: str
    interface_type: InterfaceType   # ETHERNET/WIFI/VPN
    
    # Statut
    status: DeviceStatus            # ONLINE/OFFLINE/UNKNOWN
    last_seen: datetime
    first_seen: datetime
    
    # Historique
    ip_history: List[IPChange]
    hostname_history: List[HostnameChange]
    uptime_periods: List[OnlinePeriod]
    
    # Statistiques
    total_scans_detected: int
    uptime_percentage: float
    average_latency_ms: float
    
    # Capacités
    capabilities: DeviceCapabilities
        - open_ports: List[int]
        - services: List[str]
        - detected_os: str
    
    # Sources & Qualité
    sources: List[str]              # [nmap, arp, mdns]
    confidence_score: float         # 0.0-1.0
    data_quality: str               # high/medium/low
    
    # Gestion
    is_managed: bool
    is_monitored: bool
    tags: List[str]
```

### Historique IP

```python
IPChange:
    old_ip: str
    new_ip: str
    changed_at: datetime
    detected_by: str                # nmap/arp/etc
    reason: str                     # dhcp_renew/manual/etc
```

---

## 🎯 DeviceIntelligenceEngine

### Fonctionnalités

#### 1. **Fusion multi-sources**
```python
merged = engine.merge_device_data(sources: List[DeviceData])
# Combine nmap + ARP + mDNS + NetBIOS
# Priorité : freebox > nmap > arp > mdns
# Retourne : Dict unifié
```

#### 2. **Détection changements**
```python
changes = engine.detect_changes(previous: Dict, current: Dict)
# Détecte: IP_CHANGED, HOSTNAME_CHANGED, STATUS_CHANGED,
#          NEW_DEVICE, DEVICE_DISAPPEARED, CONFLICT
# Retourne : List[DeviceChange]
```

#### 3. **Calcul de confiance**
```python
confidence = engine.calculate_confidence(device: Dict, sources: List)
# Facteurs:
#   - Nombre de sources (max 0.3)
#   - Fiabilité sources (max 0.4)
#   - Fraîcheur données (max 0.2)
#   - Cohérence (max 0.1)
# Retourne: float (0.0-1.0)
```

#### 4. **Détection conflits**
```python
conflicts = engine.detect_conflicts(devices: List[Dict])
# Types:
#   - IP_DUPLICATE: Même IP sur plusieurs MACs
#   - MAC_SPOOFING: Incohérences vendor/type
# Retourne: List[NetworkConflict]
```

#### 5. **Calcul uptime**
```python
stats = engine.calculate_uptime(history: List[Dict])
# Statistiques:
#   - uptime_percentage
#   - online_time_seconds
#   - detection_rate
#   - average_latency_ms
# Retourne: UptimeStats
```

---

## 🔄 Monitoring en Background

### Configuration

Par défaut :
- **Intervalle**: 5 minutes (300s)
- **Détection changements**: Activée
- **Logs**: Activés

### Détection automatique

Le monitoring détecte :
- 🆕 **NEW_DEVICE** : Nouveau device sur le réseau
- 📴 **DEVICE_OFFLINE** : Device disparu
- ✅ **DEVICE_ONLINE** : Device réapparu
- 🔄 **IP_CHANGED** : Changement d'IP (DHCP)
- 🏷️ **HOSTNAME_CHANGED** : Changement de hostname

### Logs

```
INFO: 📡 Monitoring: Starting scan...
INFO: ✅ Scan complete (10 devices in 7.04s)
INFO: 📊 3 changes detected:
INFO:    🆕 NEW: AA:BB:CC:DD:EE:FF - 192.168.1.100 (iPhone)
INFO:    🔄 IP CHANGE: 11:22:33:44:55:66 - 192.168.1.50 → 192.168.1.51
INFO:    📴 OFFLINE: 99:88:77:66:55:44 - 192.168.1.200
```

---

## 💾 Persistance

### Fichier: `data/devices_unified.json`

Format:
```json
{
  "version": "1.0",
  "last_updated": "2025-10-21T11:57:03",
  "devices": {
    "AA:BB:CC:DD:EE:FF": {
      "mac": "AA:BB:CC:DD:EE:FF",
      "current_ip": "192.168.1.100",
      "hostname": "my-device",
      "vendor": "Apple",
      "sources": ["nmap", "arp", "mdns"],
      "confidence_score": 0.85,
      "ip_history": [...],
      "uptime_periods": [...],
      ...
    }
  }
}
```

### Backup automatique

À chaque sauvegarde, l'ancien fichier est renommé en `.backup`.

---

## 🛠️ Dépannage

### Le monitoring ne démarre pas

Vérifier les logs :
```bash
tail -f /tmp/333home.log
```

### Pas de devices détectés

1. Vérifier que nmap est installé : `which nmap`
2. Scanner avec sudo pour nmap complet : `sudo nmap -sn 192.168.1.0/24`
3. Vérifier le subnet configuré (default: 192.168.1.0/24)

### Confidence score faible

- Score < 0.5 : Source unique ou données anciennes
- Score 0.5-0.7 : Sources multiples mais anciennes ou conflits
- Score > 0.7 : Multi-sources, données fraîches, cohérentes ✅

### Conflits IP détectés

Conflit légitime si :
- DHCP pool mal configuré
- IP statiques en conflit
- Device avec 2 interfaces (rare)

---

## 📚 Fichiers principaux

```
src/
├── core/
│   ├── device_intelligence.py      # Engine intelligence
│   └── models/
│       └── unified_device.py       # Modèle UnifiedDevice
│
├── features/network/
│   ├── multi_source_scanner.py     # Scanner multi-sources
│   ├── service_unified.py          # Service principal
│   └── monitoring_service.py       # Monitoring background
│
└── api/
    └── unified_router.py            # API REST

data/
└── devices_unified.json             # Persistance
```

---

## 🔜 Améliorations futures

- [ ] Alert Manager (webhook, email, Telegram)
- [ ] Frontend DataTables pro
- [ ] Graphes Chart.js (uptime, latence)
- [ ] Export CSV/JSON
- [ ] Configuration UI (scan interval, sources, etc.)
- [ ] Gestion whitelist/blacklist
- [ ] Intégration Freebox API (optionnelle)
- [ ] Support IPv6

---

## 📖 Références

- **Architecture**: `docs/NETWORK_PRO_ARCHITECTURE.md`
- **TODO**: `TODO_NETWORK_PRO.md`
- **Status**: `SESSION_DEV_AUTO_STATUS.md`
- **RULES**: `RULES.md`

---

**Développé avec ❤️ pour 333HOME**  
*Professional network monitoring made simple*
