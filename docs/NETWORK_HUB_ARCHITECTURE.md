# 🌐 Network Hub Architecture - 333HOME

## Vue d'ensemble

Le **Network Hub** est un système de monitoring réseau en temps réel basé sur un **registry persistant** qui stocke l'historique complet de tous les devices jamais détectés.

## 🎯 Philosophie

- **"Réseau"** = Hub de monitoring global (tous les devices avec historique)
- **"Appareils"** = Gestion avancée (WOL, monitoring ciblé)
- **Scan = Enrichissement** (pas de liste temporaire)
- **Suivi DHCP** automatique (changements IP/hostname trackés)

## 📁 Architecture

### 1. **NetworkRegistry** (`src/features/network/registry.py`)

**Fichier central**: `data/network_registry.json`

Stocke **TOUS les devices jamais vus** avec:
- ✅ Historique IP complet (tracking DHCP)
- ✅ Historique hostname
- ✅ Vendor, OS, device type
- ✅ Timestamps (first_seen, last_seen, last_seen_online)
- ✅ Compteurs (total_detections, occurrences par IP)
- ✅ Statut temps réel (is_online, is_vpn_connected)

#### Modèle de données

```python
DeviceRegistryEntry:
    # Identification
    mac: str
    current_ip: str
    current_hostname: str
    
    # Enrichissement
    vendor: str
    os_detected: str
    device_type: str
    
    # Statut
    is_online: bool
    is_vpn_connected: bool
    vpn_ip: str
    
    # Historique
    ip_history: List[IPHistoryEntry]
    hostname_history: List[HostnameHistoryEntry]
    
    # Timestamps
    first_seen: str
    last_seen: str
    last_seen_online: str
    
    # Métriques
    total_detections: int
    
    # Management
    is_managed: bool
```

#### Exemple d'historique IP

```json
{
  "mac": "D8:3A:DD:12:34:56",
  "current_ip": "192.168.1.100",
  "ip_history": [
    {
      "ip": "192.168.1.50",
      "first_seen": "2025-10-01T10:00:00",
      "last_seen": "2025-10-15T18:30:00",
      "occurrences": 127
    },
    {
      "ip": "192.168.1.100",
      "first_seen": "2025-10-16T09:00:00",
      "last_seen": "2025-10-21T19:00:00",
      "occurrences": 45
    }
  ]
}
```

### 2. **Scan Multi-Sources** (`src/features/network/multi_source_scanner.py`)

5 scanners modulaires:
1. **ARPScanner** - Cache ARP local (ultra-rapide)
2. **NmapScanner** - Détection avancée (vendor, ports, services)
3. **MDNSScanner** - Devices Apple/Linux avec Avahi/Bonjour
4. **NetBIOSScanner** - Devices Windows (NetBIOS names)
5. **TailscaleScanner** - VPN status (online/offline flag)

**Flow du scan**:
```
1. Tailscale enrichment (VPN mapping)
2. ARP scan (devices online)
3. mDNS scan (hostnames Apple/Linux)
4. NetBIOS scan (hostnames Windows)
5. nmap scan (vendor, OS, services) - OPTIONNEL pour quick
↓
Fusion intelligente → UnifiedDevice
↓
🔥 ENRICHISSEMENT DU REGISTRY
↓
Détection changements (IP, hostname, status)
↓
Log des events importants
```

### 3. **API Endpoints** (`src/features/network/routers/scan_router.py`)

#### `/api/network/scan` (POST)
Lance un scan et **enrichit le registry**

**Body**:
```json
{
  "scan_type": "full",
  "subnet": "192.168.1.0/24"
}
```

**Response**:
```json
{
  "scan_id": "scan_abc123",
  "devices_found": 12,
  "new_devices": 2,
  "duration_ms": 18500,
  "registry_changes": {
    "new": 2,
    "updated": 10,
    "changes": [
      {
        "type": "ip_changed",
        "mac": "AA:BB:CC:DD:EE:FF",
        "old_ip": "192.168.1.50",
        "new_ip": "192.168.1.100",
        "timestamp": "2025-10-21T19:00:00"
      }
    ]
  }
}
```

#### `/api/network/scan/ping` (GET)
Ping ultra-rapide (ARP + Tailscale) pour refresh temps réel

**Response**:
```json
{
  "timestamp": "2025-10-21T19:00:00",
  "online_count": 8,
  "vpn_count": 3,
  "devices": [
    {
      "mac": "AA:BB:CC:DD:EE:FF",
      "ip": "192.168.1.100",
      "is_online": true,
      "is_vpn_connected": true,
      "vpn_ip": "100.93.236.71",
      "hostname": "TITO"
    }
  ]
}
```

#### `/api/network/scan/registry` (GET)
**Registry complet** avec historique

**Response**:
```json
{
  "timestamp": "2025-10-21T19:00:00",
  "statistics": {
    "total_devices": 25,
    "online": 8,
    "offline": 17,
    "vpn_connected": 3,
    "managed": 5,
    "dhcp_dynamic": 12
  },
  "devices": [...]
}
```

#### `/api/network/scan/registry/{mac}` (GET)
Historique détaillé d'un device

**Response**: DeviceRegistryEntry complet avec tous les historiques

### 4. **Interface Web** (`web/index.html`)

#### Onglet "Réseau" (Hub de monitoring)

**Affichage**:
- 📊 Stats temps réel (online/offline/VPN)
- 🔍 Bouton unique "Scanner le réseau" (enrichissement)
- 📋 Liste du registry avec:
  - Statut temps réel (✅/❌)
  - Badge VPN (🔒 vert si connecté, gris si déconnecté)
  - Vendor, OS, dernière détection
  - Historique IP/hostname au clic
  - Bouton "Gérer" pour ajouter aux Appareils

**Refresh automatique**:
- Toutes les 10s: `/api/network/scan/ping` (statuts temps réel)
- Au démarrage: Charge le registry complet
- Après scan: Reload du registry

**Filtres**:
- Online/Offline
- VPN connecté
- Devices gérés
- Recherche (hostname, IP, MAC, vendor)

#### Onglet "Appareils" (Gestion avancée)

**Fonctionnalités**:
- Wake-on-LAN
- Notes personnalisées
- Groupes/tags
- Monitoring ciblé (futur)

## 🔄 Flow de détection des changements

### Cas 1: Changement IP (DHCP)

```
Device MAC=AA:BB:CC:DD:EE:FF détecté avec nouvelle IP
↓
Registry: current_ip = "192.168.1.50"
Scan: current_ip = "192.168.1.100"
↓
Change détecté: ip_changed
↓
1. Log: "🔄 IP changée: AA:BB:CC:DD:EE:FF 192.168.1.50 → 192.168.1.100"
2. Ajout à ip_history:
   - Ancienne IP: last_seen = now, occurrences++
   - Nouvelle IP: entrée créée avec first_seen = now
3. Mise à jour current_ip
4. Event ajouté aux changes pour l'UI
```

### Cas 2: Nouveau device

```
Device MAC=FF:EE:DD:CC:BB:AA jamais vu
↓
Création DeviceRegistryEntry:
- first_seen = now
- last_seen = now
- ip_history = [current_ip]
- hostname_history = [current_hostname]
- total_detections = 1
↓
Log: "✨ Nouveau device: FF:EE:DD:CC:BB:AA (hostname ou IP)"
↓
Event: type=new_device envoyé à l'UI
↓
UI: Notification "Nouvel appareil détecté"
```

### Cas 3: Device offline

```
Device présent dans registry mais absent du scan
↓
is_online: true → false
last_seen = now (timestamp actuel)
↓
Event: device_offline
↓
UI: Badge ❌, "Dernière détection: il y a 5 min"
```

### Cas 4: VPN déconnecté

```
TailscaleScanner: Online=false pour TITO
↓
updateNetworkStatus() reçoit is_vpn_connected=false
↓
UI: Badge 🔒 vert → gris
Console: "🔒 TITO: VPN DISCONNECTED"
```

## 🚀 Workflow complet

### 1. Démarrage du serveur

```
1. Chargement du NetworkRegistry (data/network_registry.json)
2. Chargement du dernier scan (data/network_scan_history.json)
3. UI charge le registry au load
4. Démarrage du refresh 10s (ping pour statuts)
```

### 2. Utilisateur clique "Scanner le réseau"

```
1. POST /api/network/scan {"scan_type": "full"}
2. MultiSourceScanner.scan_all()
   - Tailscale: 4 devices (1 online, 3 offline)
   - ARP: 9 devices online
   - mDNS: 1 device
   - NetBIOS: 2 devices
   - nmap: 9 devices (vendor, OS, services)
3. Fusion → 9 UnifiedDevices
4. NetworkRegistry.update_from_scan()
   - 2 nouveaux
   - 7 mis à jour
   - 3 changements (1 IP, 1 hostname, 1 nouveau)
5. Log des changements importants
6. Sauvegarde du registry
7. Response à l'UI
8. UI reload du registry
9. Affichage des changements
```

### 3. Refresh temps réel (toutes les 10s)

```
1. GET /api/network/scan/ping
2. ARP cache check (instantané)
3. Tailscale status JSON (instantané)
4. Return: {devices: [...], online_count, vpn_count}
5. UI update statuts (✅/❌, 🔒 vert/gris)
6. Log changements dans console
```

## 📊 Métriques et stats

### Statistics disponibles

```json
{
  "total_devices": 25,
  "online": 8,
  "offline": 17,
  "vpn_connected": 3,
  "managed": 5,
  "dhcp_dynamic": 12,  // Devices avec IP history > 1
  "last_updated": "2025-10-21T19:00:00"
}
```

### Métriques par device

- `total_detections`: Nombre de fois détecté depuis first_seen
- `ip_history.occurrences`: Nombre de fois vu avec cette IP
- `last_seen_online`: Dernière fois vu connecté
- Durée moyenne entre détections
- Patterns de présence (jours/heures)

## 🔧 Configuration

### Scan settings

```python
# src/features/network/scanners/nmap_scanner.py
nmap_command = "sudo nmap -sn -T4 -PR --min-rate=100 --host-timeout=3s"
# -T4: Aggressive timing (4s scan pour /24)
# -sn: Ping scan only (pas de ports)
# -PR: ARP ping (local network)
```

### Refresh intervals

```javascript
// web/index.html
setInterval(() => {
    if(this.tab==='network' && this.scanResults.length>0){
        this.updateNetworkStatus(); // Ping temps réel
    }
}, 10000); // 10 secondes
```

## 🎯 Avantages de l'architecture

### ✅ Suivi persistant
- Historique complet jamais perdu
- Tracking DHCP automatique
- Timeline des changements

### ✅ Performance
- ARP cache ultra-rapide (<1s)
- Scan nmap optimisé (4s pour /24)
- Refresh temps réel sans surcharge

### ✅ Intelligence
- Fusion multi-sources (5 scanners)
- Vendor enrichment (60+ random MACs)
- OS inference (heuristics)
- VPN status (Tailscale Online flag)

### ✅ Flexibilité
- Registry indépendant des scans
- Devices gérés séparément
- Extensible (futurs scanners)

## 🐛 Debugging

### Logs importants

```
✅ Network Registry chargé: 25 devices
📡 Tailscale: Found 4 VPN devices (1 online, 3 offline)
📡 ARP: Found 9 devices
✅ Scan complete: 9 devices (2 on VPN) in 18.5s
🔄 IP changée: AA:BB:CC:DD:EE:FF 192.168.1.50 → 192.168.1.100
📊 Registry enrichi: 2 nouveaux, 7 mis à jour
```

### Fichiers à surveiller

- `data/network_registry.json` - Registry principal
- `data/network_scan_history.json` - Historique scans
- `data/system_logs.json` - Logs centralisés

## 🚧 TODO Futur

- [ ] Timeline UI des changements (graphique)
- [ ] Alerts (nouveau device, changement IP suspect)
- [ ] Export registry (CSV, JSON)
- [ ] Analytics (devices jamais vus depuis X jours)
- [ ] Groupes de devices (home, IoT, servers)
- [ ] Monitoring ciblé par device

---

**Version**: 2.0.0  
**Date**: 21 octobre 2025  
**Architecture**: Network Hub persistant avec registry central
