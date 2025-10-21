# 🏠 333HOME - HUB Architecture v6.0

## 📋 Vue d'ensemble

Le nouveau **HUB unifié** est une refonte complète du frontend pour créer une architecture vraiment modulaire et évolutive. Fini l'approche "page par feature", place à une **Single Page Application (SPA)** avec navigation centralisée.

## 🎯 Objectifs atteints

✅ **HUB centralisé** : Une seule interface (`hub.html`) pour toutes les features  
✅ **Navigation unifiée** : Sidebar + routing hash-based (`#/dashboard`, `#/devices`, etc.)  
✅ **Architecture modulaire** : Chaque feature = 1 module indépendant  
✅ **Lazy loading** : Les modules se chargent dynamiquement à la demande  
✅ **Mobile-first** : Responsive avec menu hamburger  
✅ **Évolutivité** : Ajouter une feature = créer un module + enregistrer une route  

## 🏗️ Architecture

### Structure des fichiers

```
web/
├── hub.html                    # ⭐ Point d'entrée principal
├── index.html                  # 🔄 Ancien (legacy)
├── network.html                # 🔄 Ancien (spécifique Network)
└── static/
    └── js/
        ├── app-hub.js          # 🎯 Application HUB principale
        ├── core/
        │   ├── router.js       # 🧭 Routing hash-based
        │   ├── module-loader.js # 📦 Chargement dynamique
        │   ├── api-client.js   # 🌐 Client API (existant)
        │   └── component.js    # 🧱 Classe de base (existant)
        └── modules/
            ├── dashboard-module.js  # 📊 Dashboard global
            ├── devices-module.js    # 📱 Gestion devices
            ├── network-module.js    # 🌐 Monitoring réseau
            ├── tailscale-module.js  # 🔒 VPN Tailscale
            └── system-module.js     # ⚙️ Système
```

### Flux de navigation

```
1. User ouvre /hub
   ↓
2. hub.html charge app-hub.js (type="module")
   ↓
3. HubApp.init()
   - Enregistre les routes (dashboard, devices, network, tailscale, system)
   - Setup navigation listeners
   - Setup mobile menu
   ↓
4. Router lit le hash (#/dashboard par défaut)
   ↓
5. Router charge le module dynamiquement
   - moduleLoader.load('dashboard', '/static/js/modules/dashboard-module.js')
   - Crée instance : new DashboardModule()
   - Appelle instance.init()
   ↓
6. Module affiche son contenu dans #page-dashboard
   ↓
7. User clique sur un nav-item (ex: Devices)
   ↓
8. Router.navigate('devices')
   - Change hash: window.location.hash = '#/devices'
   - Détruit l'ancien module (dashboard.destroy())
   - Charge le nouveau module (devices-module.js)
   - Affiche #page-devices
```

## 📦 Modules

### 1. Router (`core/router.js`)

**Responsabilité** : Gestion de la navigation hash-based

```javascript
// Enregistrer une route
router.register('dashboard', {
    title: 'Dashboard',
    icon: '📊',
    init: async () => { /* charger module */ },
    destroy: () => { /* nettoyer */ }
});

// Naviguer
router.navigate('dashboard'); // → #/dashboard

// Écoute automatique des changements de hash
window.addEventListener('hashchange', () => router.handleRouteChange());
```

**Features** :
- Hash-based routing (compatible avec StaticFiles FastAPI)
- Navigation history (back/forward browser)
- Dynamic module loading
- Automatic cleanup (destroy old module)

### 2. Module Loader (`core/module-loader.js`)

**Responsabilité** : Chargement dynamique des modules ES6

```javascript
// Charger un module
const module = await moduleLoader.load('dashboard', '/static/js/modules/dashboard-module.js');

// Le module est caché pour les prochains appels
const samModuleCached = await moduleLoader.load('dashboard', '...');

// Décharger
moduleLoader.unload('dashboard');
```

**Features** :
- ES6 dynamic imports
- Module caching
- Loading state management
- Error handling

### 3. Dashboard Module (`modules/dashboard-module.js`)

**Vue d'ensemble globale** : Stats de toutes les features

**Contenu** :
- System status (uptime, CPU, memory)
- Devices summary (total, online, offline)
- Network summary (devices détectés, scans)
- Tailscale status (connected, devices)
- Quick actions (buttons vers autres pages)

**TODO** :
- Créer endpoint `/api/system/stats` pour agréger les données
- Implémenter auto-refresh (30s)

### 4. Devices Module (`modules/devices-module.js`)

**Gestion complète des appareils**

**Features** :
- ✅ Liste des devices (grid responsive)
- ✅ CRUD complet (create, update, delete)
- ✅ Wake-on-LAN (bouton ⚡)
- ✅ Ping device (bouton 📡)
- ✅ Modal pour add/edit
- ✅ Empty state

**Endpoints utilisés** :
- `GET /api/devices/` - Liste
- `POST /api/devices/` - Créer
- `PATCH /api/devices/{id}` - Modifier
- `DELETE /api/devices/{id}` - Supprimer
- `POST /api/devices/{id}/wake` - Wake-on-LAN
- `POST /api/devices/{id}/ping` - Ping

### 5. Network Module (`modules/network-module.js`)

**Adaptateur** pour réutiliser le NetworkDashboard existant

**Contenu** (délégué à NetworkDashboard) :
- Network scan (ARP, port scanning)
- Devices détectés
- Bandwidth monitoring (widget)
- Latency monitoring (widget)
- Timeline

**Note** : Le NetworkDashboard existant (network-dashboard.js) est réutilisé tel quel, juste adapté pour s'intégrer dans `#page-network`.

### 6. Tailscale Module (`modules/tailscale-module.js`)

**Gestion VPN Tailscale** (placeholder pour l'instant)

**TODO** :
- Implémenter endpoints Tailscale dans backend
- Status connection
- Liste des devices Tailscale
- Configuration API key
- Routes & ACL

**Backend à créer** :
- `GET /api/tailscale/status`
- `GET /api/tailscale/devices`
- `POST /api/tailscale/configure`

### 7. System Module (`modules/system-module.js`)

**Monitoring système** (placeholder pour l'instant)

**TODO** :
- Implémenter endpoints système dans backend
- CPU usage (%)
- Memory usage (GB, %)
- Disk usage (GB, %)
- Uptime
- Température Raspberry Pi

**Backend à créer** :
- `GET /api/system/stats`
- `GET /api/system/services`

## 🎨 Design System

Réutilisation de `modern.css` existant + styles HUB-specific dans `hub.html`.

**Éléments clés** :
- `.sidebar` : Navigation latérale
- `.nav-item` : Élément de menu
- `.page` : Container de module (caché par défaut)
- `.page.active` : Page visible
- `.dashboard-grid` : Grid responsive pour cards
- `.card` : Carte générique
- `.stat-row` : Ligne de statistique
- `.devices-grid` : Grid pour devices

**Mobile** :
- Sidebar hidden par défaut
- Menu hamburger (☰)
- Overlay opaque
- `.sidebar.open` pour afficher

## 🔌 Ajouter une nouvelle feature

**Exemple : Ajouter un module "Plex"**

### Étape 1 : Créer le module

```javascript
// web/static/js/modules/plex-module.js
import { Component } from '../core/component.js';

export class PlexModule extends Component {
    constructor() {
        super();
    }

    async init() {
        console.log('🎬 Initializing Plex Module');
        await this.loadData();
    }

    async loadData() {
        // Charger données depuis API
        this.render();
    }

    render() {
        const container = document.getElementById('page-plex');
        container.innerHTML = `
            <div class="page-header">
                <h1>🎬 Plex Media Server</h1>
            </div>
            <!-- Contenu -->
        `;
    }

    destroy() {
        console.log('🎬 Plex Module destroyed');
    }
}

export default PlexModule;
```

### Étape 2 : Ajouter la route dans app-hub.js

```javascript
// Dans registerRoutes()
router.register('plex', {
    title: 'Plex',
    icon: '🎬',
    init: async () => {
        const module = await moduleLoader.load(
            'plex',
            '/static/js/modules/plex-module.js'
        );
        const instance = new module.PlexModule();
        await instance.init();
        this.modules.set('plex', instance);
    },
    destroy: () => {
        const instance = this.modules.get('plex');
        if (instance) instance.destroy();
        this.modules.delete('plex');
    }
});
```

### Étape 3 : Ajouter la page dans hub.html

```html
<!-- Dans .content-body -->
<div id="page-plex" class="page"></div>
```

### Étape 4 : Ajouter le lien navigation dans hub.html

```html
<!-- Dans .sidebar-nav -->
<a class="nav-item" data-route="plex">
    <span class="icon">🎬</span>
    <span>Plex</span>
</a>
```

**C'est tout !** La feature est intégrée au HUB 🎉

## 🚀 Utilisation

### Lancer l'application

```bash
cd /home/pie333/333HOME
./start.sh
```

### Accéder au HUB

```
http://localhost:8000/hub
```

### Navigation

- Click sur sidebar → Change de page
- URL hash change → Module dynamique chargé
- Browser back/forward → Fonctionne automatiquement
- Mobile → Menu hamburger

## 📊 État des modules

| Module | Status | Backend | Frontend |
|--------|--------|---------|----------|
| Dashboard | ✅ Créé | ⚠️ TODO endpoint | ✅ Placeholder |
| Devices | ✅ Fonctionnel | ✅ 9 endpoints | ✅ CRUD complet |
| Network | ✅ Fonctionnel | ✅ 13 endpoints | ✅ Complet |
| Tailscale | ⚠️ Placeholder | ❌ À créer | ⚠️ Placeholder |
| System | ⚠️ Placeholder | ❌ À créer | ⚠️ Placeholder |

## 🔄 Migration depuis ancien système

### index.html (legacy)

- **Approche** : Tout dans un seul fichier HTML, app.js avec modules managers
- **Navigation** : Tabs avec `display: none/block`
- **Modules** : DataManager, DeviceManager, NetworkManager, UIManager
- **Status** : ⚠️ Keep pour compatibilité, mais obsolète

### network.html (feature-specific)

- **Approche** : Page dédiée Network uniquement
- **Status** : ⚠️ Keep pour référence, mais obsolète

### hub.html (nouveau)

- **Approche** : SPA avec routing moderne
- **Navigation** : Hash-based avec lazy loading
- **Modules** : Feature modules indépendants
- **Status** : ✅ **RECOMMANDÉ**

## 📝 Prochaines étapes

### Priorité 1 : Backend Dashboard
- [ ] Créer `src/features/system/`
- [ ] Endpoint `GET /api/system/stats`
- [ ] Retourner CPU, RAM, Disk, Uptime
- [ ] Agréger stats devices + network

### Priorité 2 : Backend Tailscale
- [ ] Créer `src/features/tailscale/`
- [ ] Endpoint `GET /api/tailscale/status`
- [ ] Endpoint `GET /api/tailscale/devices`
- [ ] Intégration avec Tailscale CLI

### Priorité 3 : Améliorer modules existants
- [ ] Dashboard : Implémenter vrais stats
- [ ] Devices : Améliorer UX (notifications toast)
- [ ] Network : Intégrer bandwidth/latency widgets
- [ ] System : Graphiques temps réel

### Priorité 4 : Features avancées
- [ ] Notifications toast globales
- [ ] Dark/Light mode toggle
- [ ] Settings page
- [ ] User authentication
- [ ] Real-time updates (WebSockets)

## 🎓 Bonnes pratiques

### Module structure

```javascript
export class MyModule extends Component {
    constructor() {
        super();
        this.state = {};
        this.refreshInterval = null;
    }

    async init() {
        await this.loadData();
        this.startAutoRefresh();
    }

    async loadData() {
        // Charger depuis API
        this.render();
    }

    render() {
        const container = document.getElementById('page-mymodule');
        container.innerHTML = `...`;
    }

    destroy() {
        // Cleanup: clearInterval, removeEventListeners, etc.
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}
```

### Naming conventions

- **Modules** : `{name}-module.js` (ex: `devices-module.js`)
- **Pages** : `#page-{name}` (ex: `#page-devices`)
- **Routes** : `{name}` (ex: `devices`)
- **Classes** : `{Name}Module` (ex: `DevicesModule`)

### Performance

- **Lazy loading** : Ne charger que le module affiché
- **Caching** : Les modules chargés restent en cache
- **Cleanup** : Toujours implémenter `destroy()` pour nettoyer
- **Auto-refresh** : Utiliser intervals raisonnables (30s+)

---

**Version** : 6.0.0  
**Date** : 21 octobre 2025  
**Architecture** : HUB Unifié  
**Status** : ✅ Opérationnel (modules Dashboard, Devices, Network fonctionnels)
