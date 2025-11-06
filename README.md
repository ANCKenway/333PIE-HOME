# 🏠 333HOME v3.0

**Système de domotique et gestion de parc informatique pour Raspberry Pi**

> 🚀 Application moderne avec FastAPI + Interface web responsive  
> 🔄 Redémarrage à distance sans SSH  
> 🤖 Agents de monitoring avec WebSocket

## 🎯 Fonctionnalités principales

- 📱 **Gestion d'appareils** : CRUD complet, Wake-on-LAN, monitoring ping
- 🌐 **Scanner réseau** : Découverte automatique, historique, détection vendors (60+)
- 📊 **Monitoring** : Bandwidth, latency, statistiques réseau
- 🤖 **Agents** : Système d'agents avec WebSocket pour contrôle à distance
- 🔒 **VPN Tailscale** : Intégration et monitoring VPN
- � **Contrôle à distance** : Page `/restart` pour redémarrage sans SSH
- ⚙️ **Service systemd** : Démarrage automatique au boot, redémarrage auto en cas de crash

## 📦 Architecture

```
333HOME/
├── app.py                      # Application FastAPI principale
├── requirements.txt            # Dépendances Python
├── conftest.py                 # Configuration pytest
│
├── start.sh                    # Démarrage serveur (legacy)
├── stop.sh                     # Arrêt serveur
├── install_systemd.sh          # Installation service systemd
├── test_restart.sh             # Test système de redémarrage
│
├── src/                        # Code source modulaire
│   ├── core/                   # Configuration, logging, unified API
│   │   ├── config.py          # Configuration centralisée (Pydantic)
│   │   ├── logging_config.py  # Logging structuré
│   │   └── unified/           # API unifiée devices+network
│   │
│   ├── shared/                 # Utilitaires partagés
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   └── utils.py
│   │
│   └── features/               # Modules fonctionnels
│       ├── agents/            # 🤖 Système d'agents avec WebSocket
│       ├── devices/           # 📱 Gestion appareils favoris
│       └── network/           # 🌐 Scanner et monitoring réseau
│           ├── registry.py    # Registry centralisé
│           ├── scanners/      # Différents scanners
│           └── routers/       # API endpoints
│
├── web/                        # Interface web
│   ├── index.html             # Interface principale
│   ├── restart.html           # Page de redémarrage d'urgence
│   └── assets/                # CSS, JS, images
│
├── static/agents/              # Packages agents téléchargeables
├── data/                       # Données runtime (gitignored)
├── tests/                      # Tests unitaires
├── scripts/                    # Scripts utilitaires
│
└── docs/                       # Documentation
    ├── QUICK_REFERENCE.md     # Référence rapide
    ├── ARCHITECTURE.md        # Architecture détaillée
    ├── API_DOCUMENTATION.md   # Documentation API
    ├── AGENTS_ARCHITECTURE.md # Architecture agents
    ├── NETWORK_ARCHITECTURE.md # Architecture réseau
    └── DEVELOPER_GUIDE.md     # Guide développeur
```

## ✅ État d'avancement

### 🎉 Complété (v6.0)

**Frontend HUB** :
- [x] **Architecture SPA** : Router hash-based + Module Loader
- [x] **Interface unifiée** : hub.html avec sidebar navigation
- [x] **Dashboard Module** : Vue d'ensemble (placeholder)
- [x] **Devices Module** : Gestion complète CRUD + Wake-on-LAN
- [x] **Network Module** : Adaptateur pour monitoring réseau
- [x] **Responsive Design** : Desktop + Mobile (menu hamburger)
- [x] **Documentation HUB** : Architecture, Quick Start, Diagrams

**Backend** :
- [x] **Core Architecture** : config, logging, lifecycle moderne
- [x] **Shared Utilities** : exceptions, utils, constants
- [x] **Feature Devices** : CRUD complet, monitoring, Wake-on-LAN (9 endpoints)
- [x] **Feature Network** : Scanner, bandwidth, latency (13 endpoints)
- [x] **Storage v3.0** : Format moderne avec migration automatique

### 🚧 En cours (Prochaines sessions)

**Frontend** :
- [ ] **Tailscale Module** : Interface VPN (placeholder créé)
- [ ] **System Module** : Monitoring système (placeholder créé)
- [ ] **Notifications Toast** : Système global de notifications
- [ ] **Real-time Updates** : WebSockets pour stats live

**Backend** :
- [ ] **Feature System** : Monitoring CPU/RAM/Disk/Temp
- [ ] **Feature Tailscale** : Intégration VPN
- [ ] **Dashboard Endpoint** : Agrégation stats globales
- [ ] **Tests Complets** : Suite de tests automatisés

## 🚀 Démarrage rapide

### Installation

```bash
# Cloner le projet
cd ~/333HOME

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python3 app.py
```

### Accès
- **🏠 HUB Unifié** : http://localhost:8000/hub ⭐ **RECOMMANDÉ**
- **API Documentation** : http://localhost:8000/api/docs
- **Interface legacy** : http://localhost:8000/
- **Health check** : http://localhost:8000/health

### Navigation HUB

```
http://localhost:8000/hub
├─ #/dashboard   📊 Vue d'ensemble
├─ #/devices     📱 Gestion devices (CRUD, Wake-on-LAN, Ping)
├─ #/network     🌐 Monitoring réseau (Scan, Bandwidth, Latency)
├─ #/tailscale   🔒 VPN Tailscale (à venir)
└─ #/system      ⚙️ Système (CPU, RAM, Disk - à venir)
```

## 🎯 Modules du HUB

### 📊 Dashboard - Vue d'ensemble
Tableau de bord centralisé affichant les stats de toutes les features.

**Fonctionnalités** :
- ⚠️ System stats (CPU, RAM, Disk, Uptime) - placeholder
- ⚠️ Devices summary (total, online, offline) - placeholder
- ⚠️ Network summary (devices, scans) - placeholder
- ⚠️ Tailscale status - placeholder
- ✅ Quick actions vers autres modules

**Status:** ⚠️ Frontend créé, backend TODO

### 📱 Devices - Appareils "Favoris"
Liste d'appareils **sélectionnés manuellement** pour un monitoring avancé et des actions spécifiques.

**Status:** ✅ **100% Fonctionnel** (Backend + Frontend HUB)

**Fonctionnalités** :
- ✅ Interface moderne dans HUB
- ✅ Liste devices avec grid responsive
- ✅ CRUD complet (Create, Read, Update, Delete)
- ✅ Modal pour add/edit
- ✅ Wake-on-LAN avec bouton ⚡
- ✅ Ping avec bouton 📡
- ✅ Auto-refresh (30s)
- ✅ Empty state
- ✅ 9 API endpoints testés

### 🌐 Network - Hub Monitoring Réseau
**Monitoring réseau complet** avec découverte automatique, historique, et timeline.

**Status:** ✅ **100% Fonctionnel** (Backend + Frontend HUB)

**Fonctionnalités** :
- ✅ Intégré dans HUB unifié
- ✅ Scanner réseau multi-méthodes (ICMP + mDNS + ARP)
- ✅ Détection avancée : 60+ vendors
- ✅ Bandwidth monitoring (widget)
- ✅ Latency monitoring (widget)
- ✅ Historique complet
- ✅ Timeline des événements
- ✅ 13 API endpoints testés

**Performance:** Scan 192.168.1.0/24 en ~7 secondes

**Documentation:** [NETWORK_ARCHITECTURE.md](docs/NETWORK_ARCHITECTURE.md)

### 🔒 Tailscale - VPN Management
**Gestion du VPN Tailscale** pour connexions sécurisées.

**Status:** ⚠️ Frontend placeholder créé, backend TODO

**Fonctionnalités à venir** :
- [ ] Status VPN (connecté/déconnecté)
- [ ] Liste des devices Tailscale
- [ ] Configuration API key
- [ ] Routes & ACL

**Backend à créer** : `src/features/tailscale/`

### ⚙️ System - Monitoring Système
**Surveillance système Raspberry Pi** en temps réel.

**Status:** ⚠️ Frontend placeholder créé, backend TODO

**Fonctionnalités à venir** :
- [ ] CPU usage (%)
- [ ] Memory usage (GB, %)
- [ ] Disk usage (GB, %)
- [ ] Température Raspberry Pi
- [ ] Uptime
- [ ] Services management

**Backend à créer** : `src/features/system/`

### Endpoints API

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/devices/` | Liste tous les appareils |
| GET | `/api/devices/summary` | Résumé du statut |
| GET | `/api/devices/{id}` | Récupère un appareil |
| POST | `/api/devices/` | Crée un appareil |
| PATCH | `/api/devices/{id}` | Met à jour un appareil |
| DELETE | `/api/devices/{id}` | Supprime un appareil |
| POST | `/api/devices/{id}/wake` | Wake-on-LAN |
| POST | `/api/devices/{id}/ping` | Ping un appareil |

Voir [docs/DEVICES_FEATURE.md](docs/DEVICES_FEATURE.md) pour la documentation complète.

## 🎨 Principes architecturaux

### 1. Feature-Based Architecture
Chaque feature est **autonome** et contient :
- Routes API (`router.py`)
- Logique métier (`manager.py`, `service.py`)
- Modèles de données (`schemas.py`)
- Stockage (`storage.py`)

### 2. Séparation des responsabilités
- **`src/core/`** : Infrastructure (config, logging, lifecycle)
- **`src/shared/`** : Code réutilisable entre features
- **`src/features/`** : Logique métier isolée

### 3. Type Safety
- Pydantic pour validation des données
- Type hints Python partout
- Modèles de données stricts

### 4. Logging structuré
- Logs avec couleurs pour lisibilité
- Contexte d'opération pour traçabilité
- Niveaux de log appropriés

### 5. Moderne et maintenable
- FastAPI moderne (lifespan vs deprecated on_event)
- Format de données versionnés
- Migration automatique
- Documentation inline et externe

## 📝 Format de données (v3.0)

### Exemple : devices.json

```json
{
  "version": "3.0",
  "updated_at": "2025-10-19T17:00:00Z",
  "devices": [
    {
      "id": "dev_rpi_d83add123456",
      "name": "Raspberry Pi 5",
      "ip": "192.168.1.150",
      "mac": "d8:3a:dd:12:34:56",
      "type": "serveur",
      "tags": ["production", "linux"],
      "metadata": {
        "os": "Raspberry Pi OS",
        "vendor": "Raspberry Pi Foundation"
      },
      "created_at": "2025-10-19T10:00:00Z",
      "updated_at": "2025-10-19T17:00:00Z"
    }
  ]
}
```

### Migration automatique
- ✅ Détection automatique de l'ancien format
- ✅ Backup créé avant migration
- ✅ Conversion vers v3.0 transparente
- ✅ Génération automatique des tags

## 🧪 Tests

```bash
# Tester la migration
python3 -c "from src.features.devices import DeviceManager; DeviceManager()"

# Tester l'API
curl http://localhost:8000/api/devices/ | jq .

# Tester le monitoring
curl http://localhost:8000/api/devices/summary | jq .
```

## 📚 Documentation

### HUB v6.0
- [HUB_ARCHITECTURE.md](docs/HUB_ARCHITECTURE.md) - Architecture HUB complète
- [QUICK_START_HUB.md](docs/QUICK_START_HUB.md) - Guide démarrage rapide HUB
- [FRONTEND_STRUCTURE_HUB.md](docs/FRONTEND_STRUCTURE_HUB.md) - Structure frontend
- [ARCHITECTURE_DIAGRAMS.md](docs/ARCHITECTURE_DIAGRAMS.md) - Diagrammes visuels
- [TODO_HUB_V6.md](TODO_HUB_V6.md) - Roadmap et prochaines étapes

### Features Backend
- [DEVICES_FEATURE.md](docs/DEVICES_FEATURE.md) - Feature devices complète
- [NETWORK_ARCHITECTURE.md](docs/NETWORK_ARCHITECTURE.md) - Architecture réseau
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Architecture générale backend
- [RULES.md](RULES.md) - Règles de développement

## 🔄 Prochaines étapes

Voir [TODO_HUB_V6.md](TODO_HUB_V6.md) pour la roadmap complète.

### Priorité 1 - Backend System (1-2 jours)
- [ ] Créer `src/features/system/`
- [ ] Endpoint `GET /api/system/stats` (CPU, RAM, Disk, Uptime)
- [ ] Température Raspberry Pi
- [ ] Mettre à jour `system-module.js` frontend

### Priorité 2 - Backend Tailscale (2-3 jours)
- [ ] Créer `src/features/tailscale/`
- [ ] Wrapper Tailscale CLI
- [ ] Endpoints `/status`, `/devices`, `/configure`
- [ ] Mettre à jour `tailscale-module.js` frontend

### Priorité 3 - Dashboard Endpoint (1 jour)
- [ ] Endpoint `GET /api/system/dashboard`
- [ ] Agréger stats de toutes features
- [ ] Mettre à jour `dashboard-module.js` frontend

### Priorité 4 - Améliorations UX (3-4 jours)
- [ ] Notifications Toast system
- [ ] Loading states
- [ ] Error boundaries
- [ ] Better forms & validations
- [ ] Real-time updates (WebSockets)

## 🤝 Contribution

Le projet suit des **règles strictes** définies dans [RULES.md](RULES.md) :
- Code propre et documenté
- Architecture modulaire
- Type hints obligatoires
- Tests pour chaque feature
- Documentation inline

## 📄 Licence

Projet personnel - Raspberry Pi 5

---

**Version** : 6.0.0  
**Dernière mise à jour** : 21 octobre 2025  
**Architecture** : HUB Unifié (SPA) + Feature-Based Backend
