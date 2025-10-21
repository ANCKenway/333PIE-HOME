# 🌐 333HOME - API Network Documentation

**Version**: 2.0 (Refactored)  
**Date**: 21 octobre 2025  
**Status**: ✅ Production Ready

---

## ⚠️ CHANGEMENTS IMPORTANTS

### Mode ON-DEMAND Uniquement

**Le monitoring automatique est désactivé** pour éviter :
- 🚫 Perturbation du réseau local (trafic constant)
- 🚫 Détection par antivirus/firewalls (comportement suspect)
- 🚫 Impact négatif sur performance LAN

**Scans déclenchés manuellement** via API POST uniquement.

### Architecture Modulaire

Router principal (`router.py`) **refactorisé de 656→39 lignes** :
- ✅ `routers/scan_router.py` (118L) - Scans ON-DEMAND
- ✅ `routers/device_router.py` (229L) - Devices & timeline
- ✅ `routers/latency_router.py` (110L) - Latence/qualité
- ✅ `routers/bandwidth_router.py` (218L) - Bande passante

### Optimisations Réseau

**Scans non-agressifs** :
- ✅ `nmap -T2` (timing polite au lieu de -T3 défaut)
- ✅ `--max-rate=50` (limite 50 paquets/sec)
- ✅ Throttling 2s entre sources (séquentiel)
- ✅ Order: ARP → mDNS → NetBIOS → nmap (moins impactant en premier)

---

## 📡 Deux APIs Complémentaires

### 1. API Legacy : `/api/network/*`

**Fonctionnalités complètes** (NetworkScanner classique) :

#### Scans
- `POST /api/network/scan` - Scanner réseau
- `GET /api/network/scan/status` - Statut scan en cours

#### Devices
- `GET /api/network/devices` - Liste devices
- `GET /api/network/devices/history/{mac}` - Historique device
- `GET /api/network/devices/timeline` - Timeline événements
- `POST /api/network/devices/{mac}/promote` - Promouvoir vers favoris
- `GET /api/network/devices/stats` - Statistiques globales

#### Monitoring Avancé
- `GET /api/network/latency/{ip}` - Stats latence device
- `POST /api/network/latency/measure` - Mesurer latence
- `GET /api/network/bandwidth/stats` - Stats bande passante
- `GET /api/network/bandwidth/top-talkers` - Top devices trafic
- `POST /api/network/bandwidth/register` - Enregistrer device
- `POST /api/network/bandwidth/sample` - Ajouter échantillon

#### DHCP
- `GET /api/network/dhcp/summary` - Résumé DHCP
- `GET /api/network/dhcp/device/{mac}` - Historique IP device
- `GET /api/network/dhcp/conflicts` - Conflits IP
- `GET /api/network/dhcp/pool/{subnet}` - Usage pool DHCP

---

### 2. API Unified : `/api/network/v2/*`

**Nouveau système** (MultiSourceScanner + DeviceIntelligence) :

#### Core
- `GET /api/network/v2/health` - Health check système
- `GET /api/network/v2/stats` - Statistiques réseau

#### Devices
- `GET /api/network/v2/devices` - Liste devices (multi-sources)
  - Query: `?online_only=true&sources=nmap,arp`
- `GET /api/network/v2/devices/{mac}` - Détails device
- `GET /api/network/v2/devices/{mac}/history` - Historique complet

#### Scans
- `POST /api/network/v2/scan` - Scanner multi-sources ON-DEMAND
  - Body: `{"subnet": "192.168.1.0/24"}`

#### Monitoring
- `GET /api/network/v2/monitoring/stats` - Stats monitoring
  - ⚠️ Retourne toujours `is_running: false` (mode ON-DEMAND)

#### Intelligence
- `GET /api/network/v2/conflicts` - Conflits IP/MAC détectés

---

## 🔧 Exemples d'Utilisation

### Scanner le réseau (ON-DEMAND)

```bash
# API Unified (recommandé - multi-sources)
curl -X POST http://localhost:8000/api/network/v2/scan \
  -H "Content-Type: application/json" \
  -d '{"subnet": "192.168.1.0/24"}'

# API Legacy
curl -X POST http://localhost:8000/api/network/scan \
  -H "Content-Type: application/json" \
  -d '{
    "subnet": "192.168.1.0/24",
    "scan_type": "ping",
    "timeout_ms": 2000
  }'
```

### Lister devices online

```bash
# API Unified
curl "http://localhost:8000/api/network/v2/devices?online_only=true"

# API Legacy
curl "http://localhost:8000/api/network/devices?online_only=true"
```

### Obtenir détails device

```bash
# API Unified (plus complet - sources multiples)
curl http://localhost:8000/api/network/v2/devices/AA:BB:CC:DD:EE:FF

# API Legacy
curl http://localhost:8000/api/network/devices/history/AA:BB:CC:DD:EE:FF
```

### Mesurer latence

```bash
curl -X POST "http://localhost:8000/api/network/latency/measure?ips=192.168.1.1&ips=192.168.1.100"
```

### Conflits réseau

```bash
curl http://localhost:8000/api/network/v2/conflicts
```

---

## 📊 Réponses API

### UnifiedDevice (API v2)

```json
{
  "mac": "AA:BB:CC:DD:EE:FF",
  "current_ip": "192.168.1.100",
  "hostname": "my-laptop",
  "vendor": "Apple Inc.",
  "device_type": "computer",
  "os_info": "macOS",
  "sources": ["nmap", "arp", "mdns"],
  "confidence_score": 0.85,
  "is_online": true,
  "status": "online",
  "first_seen": "2025-10-20T10:30:00",
  "last_seen": "2025-10-21T12:15:00",
  "ip_history": [
    {"ip": "192.168.1.100", "first_seen": "...", "last_seen": "..."}
  ],
  "hostname_history": ["my-laptop"],
  "online_periods": [
    {"start": "...", "end": "...", "duration_seconds": 3600}
  ],
  "total_uptime_seconds": 86400,
  "uptime_percentage": 95.5,
  "scan_count": 120,
  "metadata": {}
}
```

### NetworkDevice (API legacy)

```json
{
  "id": "net_abc123",
  "mac": "AA:BB:CC:DD:EE:FF",
  "current_ip": "192.168.1.100",
  "current_hostname": "my-laptop",
  "vendor": "Apple",
  "device_type": "computer",
  "open_ports": [22, 80, 443],
  "services": [
    {"port": 80, "protocol": "tcp", "service": "http"}
  ],
  "os_guess": "macOS",
  "currently_online": true,
  "first_seen": "2025-10-20T10:30:00",
  "last_seen": "2025-10-21T12:15:00",
  "in_devices": false
}
```

---

## 🛠️ Troubleshooting

### Aucun device trouvé

```bash
# Vérifier health
curl http://localhost:8000/api/network/v2/health

# Scanner manuellement
curl -X POST http://localhost:8000/api/network/v2/scan

# Vérifier logs
tail -f /tmp/333home.log | grep -E "scan|device|nmap"
```

### Scan trop lent

**C'est normal** - scans optimisés pour ne pas perturber réseau :
- nmap avec `-T2` (polite) = plus lent mais respectueux
- Throttling 2s entre sources = ~10s total pour 4 sources
- Ordre ARP→mDNS→NetBIOS→nmap (plus rapides d'abord)

### Conflits IP détectés

```bash
# Voir conflits
curl http://localhost:8000/api/network/v2/conflicts

# Analyser DHCP
curl http://localhost:8000/api/network/dhcp/conflicts
```

---

## 📦 Structure Fichiers

### Code Source
```
src/features/network/
├── router.py (39L)                    # Aggregator principal
├── routers/
│   ├── scan_router.py (118L)         # Scans ON-DEMAND
│   ├── device_router.py (229L)       # Devices & timeline
│   ├── latency_router.py (110L)      # Latence/qualité
│   └── bandwidth_router.py (218L)    # Bande passante
├── multi_source_scanner.py (623L)    # Scanner 4 sources
├── scanner.py (490L)                 # Scanner legacy
├── service_unified.py (216L)         # Service unifié
├── storage.py (398L)                 # Persistence
└── ...

src/api/
└── unified_router.py (230L)          # API v2

src/core/
├── device_intelligence.py (633L)     # Engine fusion
└── models/unified_device.py (437L)   # Modèle UnifiedDevice
```

### Données
```
data/
├── devices_unified.json              # Devices multi-sources
├── devices_unified.json.backup       # Auto-backup
├── network_scan_history.json         # Historique scans
├── network_history.json              # Événements réseau
├── dhcp_history.json                 # DHCP tracking
└── devices.json                      # Devices legacy
```

---

## 🔐 Sécurité & Performance

### Optimisations Réseau

1. **Scans non-agressifs** :
   - nmap `-T2` (polite timing)
   - `--max-rate=50` paquets/sec
   - Pas de scan de ports par défaut (sauf demandé)

2. **Throttling** :
   - 2 secondes entre chaque source
   - Scans séquentiels (pas parallèles)
   - Ordre optimisé: ARP (rapide) → nmap (lent)

3. **ON-DEMAND uniquement** :
   - Pas de background automatique
   - Pas de boucle infinie
   - Évite détection antivirus

### Permissions Requises

```bash
# nmap nécessite sudo pour ARP scan
sudo setcap cap_net_raw+ep $(which nmap)

# Vérifier
getcap $(which nmap)
# Devrait afficher: cap_net_raw=ep
```

---

## 📚 Références

- **Architecture**: `docs/NETWORK_PRO_ARCHITECTURE.md`
- **DeviceIntelligence**: `src/core/device_intelligence.py`
- **Session refactoring**: `SESSION_REFACTORING_FINAL.md`
- **RULES.md**: Conventions projet

---

**Dernière mise à jour**: 21 octobre 2025  
**Auteur**: 333HOME Team
