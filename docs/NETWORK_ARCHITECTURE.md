# 🌐 Feature Network - Architecture Complète

## Vision

**Network** est le **hub central de monitoring réseau** qui permet de :
- 🔍 Scanner le réseau et découvrir tous les appareils connectés
- 📊 Suivre l'historique des connexions et changements d'IP
- 📈 Visualiser une timeline des événements réseau
- 🔗 Promouvoir des appareils découverts vers la liste "Devices" pour monitoring avancé
- 🏷️ Identifier automatiquement les appareils (vendor, OS, type)

## Différence Network vs Devices

| Aspect | 🌐 Network | 📱 Devices |
|--------|-----------|-----------|
| **But** | Monitoring réseau complet | Appareils "favoris" avec fonctionnalités avancées |
| **Contenu** | Tous les appareils jamais vus sur le réseau | Sélection manuelle d'appareils importants |
| **Données** | Historique complet, timeline | Configuration, tags, métadonnées |
| **Actions** | Scanner, voir historique, promouvoir | Wake-on-LAN, ping, gérer |
| **Stockage** | `network_scan_history.json` | `devices.json` |
| **Temporaire** | ❌ Non, garde l'historique | ❌ Non, persistent |

### Workflow
```
1. 🔍 Scan réseau → Découverte de "192.168.1.100 - PC-GAMER (ASUS)"
2. 📊 Apparaît dans Network avec historique
3. 🔗 User clique "Ajouter aux appareils favoris"
4. 📱 Appareil créé dans Devices avec Wake-on-LAN, monitoring, etc.
```

## Architecture Feature Network

```
src/features/network/
├── __init__.py              # Exports publics
├── schemas.py               # Modèles Pydantic
│   ├── ScanResult           # Résultat d'un scan
│   ├── NetworkDevice        # Appareil découvert
│   ├── IPHistoryEntry       # Entrée historique IP
│   ├── NetworkEvent         # Événement réseau
│   └── NetworkTimeline      # Timeline pour frontend
│
├── scanner.py               # NetworkScanner
│   ├── scan_network()       # Scan ICMP + mDNS + ARP
│   ├── detect_os()          # Détection OS (TTL, ports)
│   ├── detect_vendor()      # Détection via MAC OUI
│   └── identify_device()    # Identification intelligente
│
├── history.py               # NetworkHistory
│   ├── track_device()       # Enregistrer apparition
│   ├── track_ip_change()    # Changement d'IP
│   ├── track_mac_change()   # Changement de MAC
│   ├── get_device_history() # Historique d'un appareil
│   └── get_timeline()       # Timeline des événements
│
├── storage.py               # NetworkStorage
│   ├── Format v3.0 network_scan_history.json
│   ├── save_scan_result()
│   ├── load_scan_history()
│   └── migrate_old_format()
│
├── detector.py              # DeviceDetector
│   ├── get_vendor_from_mac() # OUI lookup
│   ├── detect_device_type()  # PC, mobile, IoT, etc.
│   └── get_os_info()         # OS detection avancée
│
└── router.py                # Routes API
    ├── POST /api/network/scan
    ├── GET  /api/network/devices
    ├── GET  /api/network/history/{mac}
    ├── GET  /api/network/timeline
    ├── POST /api/network/devices/{id}/promote
    └── GET  /api/network/stats
```

## Format de données v3.0

### network_scan_history.json

```json
{
  "version": "3.0",
  "updated_at": "2025-10-19T18:00:00Z",
  "scans": [
    {
      "scan_id": "scan_20251019_180000",
      "timestamp": "2025-10-19T18:00:00Z",
      "duration_ms": 2500,
      "devices_found": 12,
      "scanner_type": "icmp+mdns+arp"
    }
  ],
  "devices": {
    "dev_network_107c6178728b": {
      "mac": "10:7c:61:78:72:8b",
      "current_ip": "192.168.1.100",
      "current_hostname": "PC-GAMER",
      "vendor": "ASUSTek COMPUTER INC.",
      "device_type": "pc",
      "os_detected": "Windows 11",
      "first_seen": "2025-10-01T10:00:00Z",
      "last_seen": "2025-10-19T18:00:00Z",
      "total_appearances": 450,
      "currently_online": true,
      "in_devices": false,
      "tags": ["windows", "gaming"],
      "ip_history": [
        {
          "ip": "192.168.1.100",
          "first_seen": "2025-10-15T10:00:00Z",
          "last_seen": "2025-10-19T18:00:00Z",
          "duration_days": 4
        },
        {
          "ip": "192.168.1.50",
          "first_seen": "2025-10-01T10:00:00Z",
          "last_seen": "2025-10-14T23:59:59Z",
          "duration_days": 14
        }
      ]
    }
  },
  "events": [
    {
      "event_id": "evt_xxx",
      "timestamp": "2025-10-19T17:30:00Z",
      "type": "ip_changed",
      "device_mac": "10:7c:61:78:72:8b",
      "device_name": "PC-GAMER",
      "details": {
        "old_ip": "192.168.1.50",
        "new_ip": "192.168.1.100"
      }
    },
    {
      "event_id": "evt_yyy",
      "timestamp": "2025-10-19T17:00:00Z",
      "type": "device_appeared",
      "device_mac": "aa:bb:cc:dd:ee:ff",
      "device_name": "iPhone-John",
      "details": {
        "ip": "192.168.1.200",
        "vendor": "Apple Inc."
      }
    },
    {
      "event_id": "evt_zzz",
      "timestamp": "2025-10-19T16:45:00Z",
      "type": "device_disappeared",
      "device_mac": "11:22:33:44:55:66",
      "device_name": "Imprimante-Bureau",
      "details": {
        "last_ip": "192.168.1.150",
        "offline_duration_minutes": 15
      }
    }
  ]
}
```

### Champs clés

**Device Network** :
- `mac` : Identifiant principal (unique)
- `current_ip` : IP actuelle
- `ip_history` : Array de toutes les IPs utilisées
- `in_devices` : Bool - est dans la liste Devices favoris ?
- `currently_online` : Statut actuel
- `total_appearances` : Nombre de fois vu

**Events** :
- Types : `device_appeared`, `device_disappeared`, `ip_changed`, `hostname_changed`, `mac_changed`
- Timeline chronologique des événements
- Détails spécifiques par type

## Endpoints API

### POST `/api/network/scan`
Lance un nouveau scan du réseau.

**Body (optionnel)** :
```json
{
  "scan_type": "full",  // full, quick, mdns_only
  "subnet": "192.168.1.0/24",
  "timeout_ms": 2000
}
```

**Response** :
```json
{
  "scan_id": "scan_20251019_180000",
  "status": "completed",
  "duration_ms": 2500,
  "devices_found": 12,
  "new_devices": 2,
  "devices": [...]
}
```

### GET `/api/network/devices`
Liste tous les appareils découverts sur le réseau.

**Query params** :
- `online_only` (bool) : Filtrer seulement les appareils online
- `not_in_devices` (bool) : Filtrer ceux non promus
- `sort_by` : `last_seen`, `first_seen`, `hostname`, `ip`

**Response** : `List[NetworkDevice]`

### GET `/api/network/history/{mac}`
Historique complet d'un appareil.

**Path params** :
- `mac` : Adresse MAC de l'appareil

**Response** :
```json
{
  "mac": "10:7c:61:78:72:8b",
  "device_name": "PC-GAMER",
  "first_seen": "2025-10-01T10:00:00Z",
  "last_seen": "2025-10-19T18:00:00Z",
  "total_appearances": 450,
  "ip_history": [...],
  "events": [...],
  "online_periods": [
    {
      "start": "2025-10-19T08:00:00Z",
      "end": "2025-10-19T18:00:00Z",
      "duration_hours": 10
    }
  ]
}
```

### GET `/api/network/timeline`
Timeline des événements réseau.

**Query params** :
- `limit` (int) : Nombre d'événements (default: 100)
- `since` (datetime) : Événements depuis cette date
- `event_types` (array) : Filtrer par types

**Response** : `NetworkTimeline`

### POST `/api/network/devices/{mac}/promote`
Promouvoir un appareil du réseau vers la liste Devices.

**Path params** :
- `mac` : Adresse MAC de l'appareil

**Body (optionnel)** :
```json
{
  "name": "Mon PC Gaming",
  "description": "PC principal",
  "tags": ["gaming", "windows"]
}
```

**Response** : `DeviceResponse` (appareil créé dans Devices)

### GET `/api/network/stats`
Statistiques réseau globales.

**Response** :
```json
{
  "total_devices_seen": 45,
  "currently_online": 12,
  "average_devices_online": 10.5,
  "new_devices_last_24h": 3,
  "ip_changes_last_24h": 5,
  "most_stable_device": {
    "mac": "...",
    "name": "Serveur",
    "uptime_percentage": 99.8
  },
  "most_active_device": {
    "mac": "...",
    "name": "iPhone",
    "connect_disconnect_count": 156
  }
}
```

## Cas d'usage

### 1. Monitoring quotidien
```
User → Network page
  → Voit 12 appareils online
  → Timeline montre: "iPhone-John s'est connecté il y a 5 min"
  → Clic sur iPhone-John → Historique : IP a changé 3 fois ce mois
```

### 2. Découverte nouvel appareil
```
User → Lance scan réseau
  → Nouvel appareil détecté: "192.168.1.201 - Unknown (Xiaomi)"
  → User clique "Ajouter aux appareils"
  → Renseigne nom: "Xiaomi Mi Box TV"
  → Appareil créé dans Devices avec Wake-on-LAN disponible
```

### 3. Troubleshooting réseau
```
User → Cherche pourquoi un PC est inaccessible
  → Network page → Cherche "PC-Bureau"
  → Historique montre: IP changée il y a 2h (192.168.1.50 → 192.168.1.100)
  → User met à jour la config avec nouvelle IP
```

### 4. Sécurité réseau
```
User → Timeline réseau
  → Voit: "Appareil inconnu connecté: 192.168.1.250 (Unknown vendor)"
  → Clic pour plus d'infos
  → Décide de bloquer ou autoriser
```

## Migration depuis ancien code

### Fichiers à extraire de `_backup/modules/network/`

| Fichier ancien | Fonctionnalité | Nouveau fichier |
|----------------|----------------|-----------------|
| `scanner.py` | Scan nmap | `scanner.py` (refactoré) |
| `mdns_scanner.py` | Scan mDNS | Intégré dans `scanner.py` |
| `mac_vendor.py` | Lookup vendor | `detector.py` |
| `device_identifier.py` | Identification | `detector.py` |
| `network_history.py` | Historique (FIXÉ) | `history.py` |
| `scan_storage.py` | Stockage | `storage.py` (format v3.0) |

### Améliorations prévues

1. **Scanner unifié** : ICMP + mDNS + ARP en un seul scan
2. **Format v3.0** : Structure propre avec versioning
3. **Timeline** : Visualisation chronologique des événements
4. **Statistiques** : Métriques réseau intelligentes
5. **Intégration Devices** : Promotion seamless
6. **Performance** : Scan parallèle optimisé

## Conformité RULES.md

✅ **Séparation des responsabilités** :
- Scanner → découverte réseau
- History → suivi temporel
- Storage → persistence
- Detector → identification
- Router → API

✅ **Modularité** : Chaque composant est autonome

✅ **Type safety** : Pydantic schemas partout

✅ **Documentation** : Inline + ce fichier

✅ **Évolutivité** : Format v3.0 extensible

## Prochaines étapes

1. ✅ Définir architecture (ce document)
2. 🔄 Créer `schemas.py` avec tous les modèles
3. 🔄 Implémenter `scanner.py`
4. 🔄 Implémenter `history.py`
5. 🔄 Implémenter `storage.py` avec migration
6. 🔄 Implémenter `detector.py`
7. 🔄 Créer `router.py` avec tous les endpoints
8. 🔄 Tester et valider
9. 🔄 Intégrer avec frontend

---

**Vision résumée** : Network = Hub central de monitoring réseau complet avec historique, timeline, et pont vers Devices pour les appareils favoris. 🌐
