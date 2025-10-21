# 📋 AUDIT COMPLET API BACKEND - 333HOME

## ✅ APIs DISPONIBLES (Toutes fonctionnelles)

### 🏠 HUB API (`/api/hub/*`)
| Endpoint | Méthode | Description | Utilisé |
|----------|---------|-------------|---------|
| `/api/hub/devices` | GET | Liste TOUS devices unifiés (devices.json + network + tailscale) | ✅ OUI |
| `/api/hub/devices/{id}` | GET | Device par ID | ❌ PAS ENCORE |
| `/api/hub/devices/mac/{mac}` | GET | Device par MAC | ❌ PAS ENCORE |
| `/api/hub/stats` | GET | Stats globales (total/online/offline/managed) | ✅ OUI |
| `/api/hub/scan` | POST | Lance scan réseau unifié | ✅ OUI |
| `/api/hub/health` | GET | Health check | ✅ OUI |

### 🌐 NETWORK API (`/api/scan/*`)
| Endpoint | Méthode | Description | Utilisé |
|----------|---------|-------------|---------|
| `/api/scan/interfaces` | GET | Liste interfaces réseau | ❌ NON |
| `/api/scan/` | GET/POST | Scanner réseau (nmap/arp) | ✅ OUI |
| `/api/scan/quick` | GET | Scan rapide ARP | ❌ NON |
| `/api/scan/{scan_id}/status` | GET | Statut scan en cours | ❌ NON |
| `/api/scan/devices` | GET | Devices découverts | ❌ NON |
| `/api/scan/device/{ip}` | GET | Info device par IP | ❌ NON |
| `/api/scan/device/mac/{mac}` | GET | Info device par MAC | ❌ NON |
| `/api/scan/vendor/{mac}` | GET | Fabricant par MAC | ❌ NON |
| `/api/scan/export` | GET | Exporter résultats scan (JSON/CSV) | ❌ NON |
| `/api/scan/cache` | DELETE | Vider cache | ❌ NON |
| `/api/scan/cache/stats` | GET | Stats cache | ❌ NON |
| `/api/scan/device/add` | POST | Ajouter device manuellement | ❌ NON |
| `/api/scan/statistics` | GET | Statistiques réseau détaillées | ❌ NON |

### 📱 DEVICES API (`/api/devices/*`)
| Endpoint | Méthode | Description | Utilisé |
|----------|---------|-------------|---------|
| `/api/devices` | GET | Liste devices gérés | ✅ OUI (via hub) |
| `/api/devices` | POST | Ajouter device | ✅ OUI |
| `/api/devices/{ip}` | DELETE | Supprimer device | ✅ OUI |
| `/api/devices/{ip}` | PUT | Modifier device | ❌ NON |
| `/api/devices/wake/{ip}` | POST | Wake-on-LAN | ❌ NON |

### 🔄 NETWORK V2 API (`/api/network/v2/*`)
| Endpoint | Méthode | Description | Utilisé |
|----------|---------|-------------|---------|
| `/api/network/v2/devices` | GET | Tous devices (avec filtres) | ❌ NON |
| `/api/network/v2/devices/{mac}` | GET | Device détaillé | ❌ NON |
| `/api/network/v2/devices/{mac}/history` | GET | Historique device | ❌ NON |
| `/api/network/v2/stats` | GET | Stats réseau | ❌ NON |
| `/api/network/v2/scan` | POST | Force scan | ❌ NON |
| `/api/network/v2/conflicts` | GET | Conflits IP/MAC | ❌ NON |
| `/api/network/v2/monitoring/stats` | GET | Stats monitoring temps réel | ❌ NON |

## 🎯 FONCTIONNALITÉS À INTÉGRER

### 1. Dashboard Status (ENRICHIR)
- ✅ Stats de base (total/online/offline/managed)
- ❌ **Ajouter**: Graphiques temps réel via `/api/network/v2/monitoring/stats`
- ❌ **Ajouter**: Liste conflits via `/api/network/v2/conflicts`
- ❌ **Ajouter**: Stats cache via `/api/scan/cache/stats`

### 2. Devices Management (COMPLÉTER)
- ✅ Liste devices
- ✅ Ajouter/Supprimer
- ❌ **Ajouter**: Édition device (PUT /api/devices/{ip})
- ❌ **Ajouter**: Wake-on-LAN (POST /api/devices/wake/{ip})
- ❌ **Ajouter**: Historique device (GET /api/network/v2/devices/{mac}/history)
- ❌ **Ajouter**: Détails fabricant (GET /api/scan/vendor/{mac})

### 3. Network Scan (ENRICHIR)
- ✅ Lancer scan basique
- ❌ **Ajouter**: Interfaces réseau (GET /api/scan/interfaces)
- ❌ **Ajouter**: Scan rapide ARP (GET /api/scan/quick)
- ❌ **Ajouter**: Suivi scan en temps réel (GET /api/scan/{scan_id}/status)
- ❌ **Ajouter**: Export résultats (GET /api/scan/export)
- ❌ **Ajouter**: Statistiques réseau (GET /api/scan/statistics)

### 4. VPN Tailscale (CRÉER)
- ❌ **Créer**: Toute la page VPN
- ❌ **Intégrer**: Sync Tailscale (si API existe)

### 5. Test API (CRÉER)
- ❌ **Créer**: Interface test endpoints
- ❌ **Ajouter**: Test tous endpoints avec résultats
- ❌ **Ajouter**: Export logs/résultats

## 🚀 PLAN D'ACTION

### Phase 1: Dashboard Pro ⭐
- [ ] Graphiques temps réel (Chart.js via CDN)
- [ ] Widget conflits réseau
- [ ] Widget stats cache
- [ ] Auto-refresh toutes les 10s

### Phase 2: Devices Complet
- [ ] Édition device (modal)
- [ ] Wake-on-LAN
- [ ] Historique device (modal/drawer)
- [ ] Info fabricant
- [ ] Filtres avancés (online/offline/managed)

### Phase 3: Network Scanner Pro
- [ ] Choix interface réseau
- [ ] Scan rapide vs complet
- [ ] Barre progression scan
- [ ] Export JSON/CSV
- [ ] Stats détaillées

### Phase 4: VPN & Test
- [ ] Page VPN complète
- [ ] Page Test API interactive
- [ ] Documentation API intégrée

## 📊 PRIORISATION
1. **CRITIQUE** : Dashboard + Device History + Wake-on-LAN
2. **IMPORTANT** : Network Scanner enrichi + Export
3. **NICE TO HAVE** : VPN + Test API
