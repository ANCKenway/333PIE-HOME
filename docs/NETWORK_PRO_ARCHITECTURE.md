# 🏗️ Architecture Professionnelle - Network Supervision System

## 📅 Date : 21 Octobre 2025

## 🎯 Objectif : Système Type IPScanner Professionnel

### Vision

Créer un système de supervision réseau **de niveau professionnel** comparable à :
- Advanced IP Scanner
- Angry IP Scanner
- Nmap GUI Professional
- PRTG Network Monitor (version simplifiée)

**Différence clé avec l'existant** : Ne pas se contenter d'un "ping = point vert", mais avoir une **supervision intelligente** avec tracking MAC, historique complet, détection de changements, et intégration routeur.

---

## 🏛️ Architecture Globale

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND - Interface Pro                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │   Network    │  │   Devices    │  │  Monitoring  │  │   Alerts    │ │
│  │   Explorer   │  │   Manager    │  │  Dashboard   │  │   Center    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘ │
│                                                                           │
│  - Vue liste + détails           - Graphes temps réel (Chart.js)        │
│  - Filtres avancés               - Timeline d'événements                 │
│  - Tri multi-colonnes            - Widgets de santé                      │
│  - Export CSV/PDF                - Alertes visuelles                     │
│                                                                           │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                     BACKEND - API Unifiée (FastAPI)                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  /api/unified/devices         → Device Manager (source unique)           │
│  /api/network/scan            → Scanner Multi-sources                    │
│  /api/network/monitoring      → Monitoring Continu                       │
│  /api/network/alerts          → Système d'Alertes                        │
│  /api/network/dhcp            → DHCP Tracking                            │
│  /api/freebox/*               → Intégration Freebox                      │
│  /api/reports/*               → Rapports & Export                        │
│                                                                           │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    CORE SERVICES - Logique Métier                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │             Device Intelligence Engine                           │   │
│  │  - Tracking MAC-based (l'IP peut changer)                       │   │
│  │  - Historique complet (qui, quand, combien de temps)            │   │
│  │  - Détection de changements (IP, hostname, vendor)              │   │
│  │  - Gestion conflits (même IP, même MAC sur IPs différentes)     │   │
│  │  - Score de confiance (fiabilité des données)                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │             Multi-Source Scanner                                 │   │
│  │  1. Nmap Scan       : Découverte active (ICMP + ports)          │   │
│  │  2. ARP Scan        : Découverte passive (cache ARP)            │   │
│  │  3. mDNS/Bonjour    : Hostname detection (Mac/Linux)            │   │
│  │  4. NetBIOS         : Hostname Windows (nmblookup)              │   │
│  │  5. Freebox API     : Baux DHCP réels du routeur                │   │
│  │  6. SNMP            : Devices intelligents (optionnel)          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │             Continuous Monitoring System                         │   │
│  │  - Background task (asyncio)                                    │   │
│  │  - Scan périodique (configurable: 1-30 min)                     │   │
│  │  - Détection temps réel (nouveaux devices, disparitions)        │   │
│  │  - Calcul disponibilité (uptime %)                              │   │
│  │  - Latence moyenne + jitter                                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │             Alert Management System                              │   │
│  │  Types:                                                          │   │
│  │   • NEW_DEVICE         : Nouveau device détecté                 │   │
│  │   • DEVICE_ONLINE      : Device revenu en ligne                 │   │
│  │   • DEVICE_OFFLINE     : Device disparu                         │   │
│  │   • IP_CHANGED         : Changement d'IP (DHCP)                 │   │
│  │   • MAC_CHANGED        : Possible MAC spoofing                  │   │
│  │   • IP_CONFLICT        : Même IP sur 2+ MACs                    │   │
│  │   • DHCP_EXHAUSTION    : Pool DHCP presque plein                │   │
│  │  Handlers:                                                       │   │
│  │   • Console logs (toujours)                                     │   │
│  │   • File logs (alerts.json)                                     │   │
│  │   • Webhooks (optionnel: Discord, Slack, IFTTT)                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    DATA LAYER - Stockage Intelligent                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  unified_devices.json         → Single source of truth                   │
│  network_history.json         → Historique complet des scans             │
│  dhcp_leases.json            → Baux DHCP (tracking IP)                   │
│  alerts_history.json         → Historique des alertes                    │
│  monitoring_stats.json       → Stats de monitoring continu               │
│  freebox_cache.json          → Cache données Freebox API                 │
│                                                                           │
│  Principes:                                                               │
│  - MAC address = clé primaire (unique, stable)                           │
│  - Versioning (migration automatique)                                    │
│  - Backup automatique avant modifications                                │
│  - Compression anciens scans (>30 jours)                                 │
│                                                                           │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                 EXTERNAL INTEGRATIONS - Sources Externes                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │             Freebox API Integration                              │   │
│  │                                                                  │   │
│  │  Endpoints utilisés:                                             │   │
│  │   • /api/v8/login/           : Authentification                 │   │
│  │   • /api/v8/dhcp/dynamic_lease/ : Baux DHCP actifs              │   │
│  │   • /api/v8/lan/browser/     : Devices connectés                │   │
│  │   • /api/v8/connection/      : Stats connexion WAN              │   │
│  │                                                                  │   │
│  │  Bénéfices:                                                      │   │
│  │   ✅ Baux DHCP réels (IP + durée + renouvellement)              │   │
│  │   ✅ Hostnames réels (depuis le routeur)                        │   │
│  │   ✅ Devices Wi-Fi vs Ethernet                                  │   │
│  │   ✅ Signal Wi-Fi + bande passante utilisée                     │   │
│  │   ✅ Source de vérité pour conflits IP                          │   │
│  │                                                                  │   │
│  │  Sécurité:                                                       │   │
│  │   - App token stocké en sécurisé (pas en clair)                 │   │
│  │   - Refresh token automatique                                   │   │
│  │   - Rate limiting (1 req/sec max)                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │             Vendor Database (MAC OUI)                            │   │
│  │  - Base locale macvendors.json (90k+ vendors)                   │   │
│  │  - Fallback API macvendors.com                                  │   │
│  │  - Cache 30 jours                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Modèle de Données Unifié

### UnifiedDevice (version pro)

```python
class UnifiedDevice:
    # Identifiants (MAC = clé primaire)
    mac: str                    # Unique, stable
    id: str                     # dev_{mac_clean}
    
    # Identité
    name: str                   # Nom custom ou hostname
    hostname: str | None        # Hostname réseau
    vendor: str                 # Constructeur (OUI)
    device_type: str            # Type détecté
    
    # Réseau actuel
    current_ip: str             # IP actuelle
    subnet: str                 # Sous-réseau (192.168.1.0/24)
    interface_type: str         # ethernet | wifi | vpn
    
    # Statut
    status: DeviceStatus        # online | offline | unknown
    online: bool                # Raccourci
    last_seen: datetime         # Dernière détection
    first_seen: datetime        # Première détection
    
    # Historique
    ip_history: List[IPChange]  # Changements d'IP
    hostname_history: List[HostnameChange]
    uptime_periods: List[OnlinePeriod]
    
    # Statistiques
    total_scans_detected: int   # Nombre de scans où présent
    uptime_percentage: float    # % de disponibilité
    average_latency_ms: float   # Latence moyenne
    total_uptime_seconds: int   # Temps total en ligne
    
    # Capacités détectées
    open_ports: List[int]       # Ports ouverts
    services: List[Service]     # Services détectés
    os_detected: str | None     # OS si détecté
    os_confidence: float        # Confiance détection OS
    
    # Sources de données
    sources: List[str]          # [nmap, arp, freebox, mdns]
    confidence_score: float     # Score de fiabilité (0-1)
    data_quality: str           # high | medium | low
    
    # Gestion
    is_managed: bool            # Dans devices.json ?
    is_monitored: bool          # Monitoring actif ?
    is_whitelisted: bool        # Device autorisé
    tags: List[str]             # Tags custom
    notes: str                  # Notes utilisateur
    
    # Alertes
    has_active_alerts: bool     # Alertes en cours
    alert_count: int            # Nombre d'alertes total
    last_alert: datetime | None # Dernière alerte
    
    # Freebox specific (si disponible)
    freebox_data: FreeboxDevice | None
        - dhcp_lease: DHCPLease     # Bail DHCP
        - wifi_signal: int          # Signal Wi-Fi (dBm)
        - bandwidth_used: int       # Bande passante
        - connection_type: str      # Type connexion
        - last_activity: datetime   # Dernière activité
```

### IPChange (Historique IP)

```python
class IPChange:
    old_ip: str | None          # Ancienne IP
    new_ip: str                 # Nouvelle IP
    changed_at: datetime        # Date du changement
    detected_by: str            # Source (scan, freebox, dhcp)
    reason: str | None          # Raison si connue (dhcp_renew, etc.)
    dhcp_lease_time: int | None # Durée du bail (secondes)
```

### OnlinePeriod (Disponibilité)

```python
class OnlinePeriod:
    online_from: datetime       # Début période en ligne
    online_until: datetime | None # Fin (None = encore en ligne)
    duration_seconds: int       # Durée
    uptime_percentage: float    # % du temps total
    scan_detections: int        # Nombre de scans détectés
```

### NetworkAlert (Alertes)

```python
class NetworkAlert:
    id: str                     # Unique ID
    type: AlertType             # Type d'alerte
    severity: Severity          # critical | warning | info
    device_mac: str             # Device concerné
    title: str                  # Titre court
    message: str                # Message détaillé
    created_at: datetime        # Date création
    resolved_at: datetime | None # Date résolution
    is_resolved: bool           # Résolu ?
    metadata: Dict              # Données supplémentaires
```

---

## 🔧 Implémentation : Plan d'Action

### Phase 1 : Core Intelligence Engine (2-3h)

**Fichiers à créer** :

1. **`src/core/device_intelligence.py`** (400 lignes)
   ```python
   class DeviceIntelligenceEngine:
       """Moteur d'intelligence pour tracking devices"""
       
       def merge_device_data(self, sources: List[DeviceData]) -> UnifiedDevice:
           """Fusionne données de multiples sources"""
           
       def detect_changes(self, old: UnifiedDevice, new: DeviceData) -> List[Change]:
           """Détecte les changements significatifs"""
           
       def calculate_confidence(self, device: UnifiedDevice) -> float:
           """Calcule score de confiance des données"""
           
       def detect_conflicts(self, devices: List[UnifiedDevice]) -> List[Conflict]:
           """Détecte conflits (IP, MAC spoofing, etc.)"""
           
       def calculate_uptime(self, device: UnifiedDevice) -> UptimeStats:
           """Calcule statistiques de disponibilité"""
   ```

2. **`src/features/network/multi_source_scanner.py`** (500 lignes)
   ```python
   class MultiSourceScanner:
       """Scanner combinant multiples sources"""
       
       async def scan_all_sources(self) -> List[DeviceData]:
           """Scan toutes les sources en parallèle"""
           # 1. Nmap scan
           # 2. ARP scan
           # 3. mDNS/NetBIOS
           # 4. Freebox API
           # 5. SNMP (si activé)
           
       async def enrich_device_data(self, device: DeviceData) -> DeviceData:
           """Enrichit les données device"""
           # Vendor lookup
           # Port scan
           # Service detection
           # OS detection
   ```

3. **`src/features/freebox/api.py`** (600 lignes)
   ```python
   class FreeboxAPI:
       """Client API Freebox OS"""
       
       async def authenticate(self) -> str:
           """Authentification avec app token"""
           
       async def get_dhcp_leases(self) -> List[DHCPLease]:
           """Récupère baux DHCP actifs"""
           
       async def get_lan_devices(self) -> List[FreeboxDevice]:
           """Liste devices LAN connectés"""
           
       async def get_connection_stats(self) -> ConnectionStats:
           """Stats connexion WAN"""
   ```

4. **`src/features/network/monitoring_service.py`** (400 lignes)
   ```python
   class NetworkMonitoringService:
       """Service de monitoring continu"""
       
       async def start_monitoring(self, interval_minutes: int = 5):
           """Démarre monitoring en background"""
           
       async def scan_cycle(self):
           """Un cycle de scan complet"""
           
       def detect_changes(self, previous: List, current: List) -> List[Change]:
           """Détecte changements entre 2 scans"""
           
       async def trigger_alerts(self, changes: List[Change]):
           """Déclenche alertes pour changements"""
   ```

5. **`src/features/network/alert_manager.py`** (300 lignes)
   ```python
   class NetworkAlertManager:
       """Gestionnaire d'alertes réseau"""
       
       def create_alert(self, type: AlertType, device: UnifiedDevice, **kwargs):
           """Crée une alerte"""
           
       def get_active_alerts(self) -> List[NetworkAlert]:
           """Alertes actives"""
           
       async def notify(self, alert: NetworkAlert):
           """Envoie notifications (console, file, webhook)"""
           
       def resolve_alert(self, alert_id: str):
           """Marque une alerte comme résolue"""
   ```

### Phase 2 : API Endpoints (1-2h)

**Nouveaux endpoints** :

```python
# Router unifié
GET    /api/unified/devices                 # Liste complète unifiée
GET    /api/unified/devices/{mac}           # Détails device
GET    /api/unified/devices/{mac}/history   # Historique complet
GET    /api/unified/stats                   # Stats globales

# Monitoring
GET    /api/network/monitoring/status       # Status monitoring
POST   /api/network/monitoring/start        # Démarrer
POST   /api/network/monitoring/stop         # Arrêter
GET    /api/network/monitoring/stats        # Stats temps réel

# Alertes
GET    /api/network/alerts                  # Liste alertes
GET    /api/network/alerts/{id}             # Détails
POST   /api/network/alerts/{id}/resolve     # Résoudre
DELETE /api/network/alerts/{id}             # Supprimer

# Freebox
GET    /api/freebox/status                  # Status connexion API
GET    /api/freebox/dhcp                    # Baux DHCP
GET    /api/freebox/devices                 # Devices Freebox
POST   /api/freebox/sync                    # Sync manuelle

# Rapports
GET    /api/reports/summary                 # Résumé global
GET    /api/reports/devices/{mac}/report    # Rapport device
GET    /api/reports/export                  # Export CSV/JSON
```

### Phase 3 : Interface Professionnelle (3-4h)

**Modules frontend à créer/refondre** :

1. **`network-pro-module.js`** - Vue réseau pro
   - Tableau DataTables (tri, filtre, pagination)
   - Vue détails expandable par ligne
   - Graphes de disponibilité (Chart.js)
   - Filtres avancés (status, type, subnet, etc.)
   - Export CSV/PDF

2. **`device-details-module.js`** - Page détails device
   - Informations complètes
   - Graphe d'uptime (30 jours)
   - Historique IP/hostname
   - Timeline d'événements
   - Alertes associées
   - Actions rapides (ping, wake, scan ports)

3. **`monitoring-dashboard-module.js`** - Dashboard supervision
   - Widgets temps réel
   - Graphe disponibilité réseau
   - Liste événements récents
   - Alertes actives
   - Stats réseau (devices online, nouveaux, disparus)

4. **`alerts-module.js`** - Centre d'alertes
   - Liste alertes avec filtres
   - Détails alerte
   - Résolution rapide
   - Historique alertes

**Design components** :

```css
/* Thème professionnel */
--primary: #2563eb;      /* Bleu moderne */
--success: #10b981;      /* Vert */
--warning: #f59e0b;      /* Orange */
--danger: #ef4444;       /* Rouge */
--background: #0f172a;   /* Fond sombre */
--surface: #1e293b;      /* Cartes */
--text: #f1f5f9;         /* Texte */

/* Tables professionnelles */
.pro-table {
    border-collapse: separate;
    border-spacing: 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.pro-table th {
    background: linear-gradient(180deg, #334155, #1e293b);
    padding: 12px 16px;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
}

.pro-table td {
    padding: 12px 16px;
    border-bottom: 1px solid #334155;
}

.pro-table tr:hover {
    background: rgba(37, 99, 235, 0.1);
    cursor: pointer;
}

/* Badges professionnels */
.badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.badge-online {
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

/* Graphes */
.chart-container {
    position: relative;
    height: 300px;
    padding: 16px;
    background: #1e293b;
    border-radius: 8px;
}
```

### Phase 4 : Tests & Documentation (1-2h)

1. **Tests unitaires**
   - `test_device_intelligence.py`
   - `test_multi_source_scanner.py`
   - `test_freebox_api.py`
   - `test_monitoring_service.py`

2. **Documentation**
   - `docs/NETWORK_PRO_ARCHITECTURE.md`
   - `docs/FREEBOX_INTEGRATION.md`
   - `docs/MONITORING_GUIDE.md`
   - `docs/API_ENDPOINTS.md`
   - Mettre à jour `RULES.md` compliance

---

## 📈 Résultat Final Attendu

### Avant (Actuel)
- ❌ Ping basique = point vert
- ❌ Pas de tracking DHCP
- ❌ Pas de détection changements
- ❌ Interface simpliste
- ❌ Scan manuel uniquement

### Après (Pro)
- ✅ **Tracking MAC intelligent** (IP peut changer)
- ✅ **Multi-sources** (nmap + ARP + Freebox + mDNS)
- ✅ **Historique complet** (qui, quand, combien de temps)
- ✅ **Détection intelligente** (nouveaux, changements, conflits)
- ✅ **Interface riche** (graphes, timeline, détails)
- ✅ **Monitoring continu** (background, automatique)
- ✅ **Alertes avancées** (7 types d'alertes)
- ✅ **Intégration Freebox** (baux DHCP réels)
- ✅ **Rapports professionnels** (export CSV/PDF)

---

## ⏱️ Estimation Temps Total

- **Phase 1** (Core Intelligence) : 2-3h
- **Phase 2** (API Endpoints) : 1-2h
- **Phase 3** (Interface Pro) : 3-4h
- **Phase 4** (Tests & Docs) : 1-2h

**Total : 7-11 heures de développement**

---

## 🚀 Démarrage Immédiat

**Je propose de commencer par** :

1. **Créer DeviceIntelligenceEngine** (cœur du système)
2. **Intégrer Freebox API** (source de vérité DHCP)
3. **Refondre interface Network** (vue professionnelle)

**Voulez-vous que je démarre maintenant avec la Phase 1 : Core Intelligence Engine ?**
