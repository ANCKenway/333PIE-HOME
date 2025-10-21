# 🗂️ Structure Frontend - HUB v6.0

## 📁 Arborescence complète

```
web/
├── hub.html                          ⭐ Point d'entrée HUB (NOUVEAU)
├── index.html                        🔄 Ancien système (legacy)
├── network.html                      🔄 Page Network dédiée (legacy)
│
├── static/
│   ├── css/
│   │   └── modern.css                🎨 Design system (réutilisé)
│   │
│   └── js/
│       ├── app-hub.js                ⭐ Application HUB principale (NOUVEAU)
│       ├── app.js                    🔄 Ancien app (legacy)
│       │
│       ├── core/                     🧱 Core modules
│       │   ├── router.js             ⭐ Hash-based routing (NOUVEAU)
│       │   ├── module-loader.js      ⭐ Dynamic imports (NOUVEAU)
│       │   ├── api-client.js         ✅ Client API (existant)
│       │   └── component.js          ✅ Base component (existant)
│       │
│       └── modules/                  📦 Feature modules
│           ├── dashboard-module.js   ⭐ Vue d'ensemble (NOUVEAU)
│           ├── devices-module.js     ⭐ Gestion devices (NOUVEAU)
│           ├── network-module.js     ⭐ Adaptateur Network (NOUVEAU)
│           ├── tailscale-module.js   ⭐ VPN placeholder (NOUVEAU)
│           ├── system-module.js      ⭐ System placeholder (NOUVEAU)
│           │
│           ├── network-dashboard.js  ✅ Network dashboard (existant)
│           ├── bandwidth-widget.js   ✅ Bandwidth monitoring (existant)
│           └── latency-widget.js     ✅ Latency monitoring (existant)
│
└── assets/
    └── ...                           🖼️ Images, icons, etc.
```

---

## 🎯 Mapping Features → Modules

### HUB Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      🏠 333HOME HUB                         │
│                                                             │
│  ┌──────────────┬────────────────────────────────────────┐  │
│  │   Sidebar    │         Content Area                   │  │
│  │              │                                        │  │
│  │  📊 Dashboard│  ┌──────────────────────────────────┐  │  │
│  │  │           │  │                                  │  │  │
│  │  ├─ 📱 Dev   │  │     Module actif                │  │  │
│  │  │           │  │     (chargé dynamiquement)      │  │  │
│  │  ├─ 🌐 Net   │  │                                  │  │  │
│  │  │           │  └──────────────────────────────────┘  │  │
│  │  ├─ 🔒 VPN   │                                        │  │
│  │  │           │                                        │  │
│  │  └─ ⚙️ Sys   │                                        │  │
│  │              │                                        │  │
│  └──────────────┴────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Routes → Modules → Pages

| Route | Module | Page Container | Status |
|-------|--------|----------------|--------|
| `#/dashboard` | `dashboard-module.js` | `#page-dashboard` | ✅ Créé |
| `#/devices` | `devices-module.js` | `#page-devices` | ✅ Complet |
| `#/network` | `network-module.js` | `#page-network` | ✅ Complet |
| `#/tailscale` | `tailscale-module.js` | `#page-tailscale` | ⚠️ Placeholder |
| `#/system` | `system-module.js` | `#page-system` | ⚠️ Placeholder |

---

## 🔄 Flux de chargement

### 1. Chargement initial

```
User ouvre http://localhost:8000/hub
          ↓
hub.html chargé (HTML + CSS)
          ↓
<script type="module" src="app-hub.js">
          ↓
app-hub.js import { router } from './core/router.js'
          ↓
HubApp.init()
```

### 2. Initialisation HubApp

```javascript
// app-hub.js
class HubApp {
    async init() {
        this.registerRoutes();    // Enregistrer les 5 routes
        this.setupNavigation();   // Listeners sur nav-items
        this.setupMobileMenu();   // Menu hamburger
        router.handleRouteChange(); // Charger route initiale
    }
}
```

### 3. Navigation utilisateur

```
User click sur "📱 Devices" dans sidebar
          ↓
nav-item[data-route="devices"] clicked
          ↓
router.navigate('devices')
          ↓
window.location.hash = '#/devices'
          ↓
hashchange event → router.handleRouteChange()
          ↓
route.destroy() de l'ancien module (ex: dashboard)
          ↓
moduleLoader.load('devices', '/static/js/modules/devices-module.js')
          ↓
import('/static/js/modules/devices-module.js')
          ↓
new DevicesModule()
          ↓
instance.init()
          ↓
loadData() → fetch('/api/devices/')
          ↓
render() → innerHTML dans #page-devices
          ↓
#page-devices.classList.add('active')
```

---

## 📦 Détail des modules

### Core Modules

#### 1. router.js
```javascript
export class Router {
    routes: Map<string, RouteConfig>
    
    register(path, config)      // Enregistrer route
    navigate(path)              // Naviguer
    handleRouteChange()         // Gérer changement
    getCurrentPath()            // Path actuel
}
```

**Utilisation** :
```javascript
router.register('devices', {
    title: 'Devices',
    init: async () => { /* load module */ },
    destroy: () => { /* cleanup */ }
});

router.navigate('devices'); // → #/devices
```

---

#### 2. module-loader.js
```javascript
export class ModuleLoader {
    modules: Map<string, Module>
    loading: Map<string, Promise>
    
    load(name, path)    // Charger module
    get(name)           // Récupérer module
    unload(name)        // Décharger module
}
```

**Utilisation** :
```javascript
const module = await moduleLoader.load(
    'devices',
    '/static/js/modules/devices-module.js'
);

const DevicesModule = module.DevicesModule;
const instance = new DevicesModule();
```

---

#### 3. api-client.js (existant)
```javascript
export class NetworkAPI {
    async scan(options)
    async getDevices()
    async getStats()
    // ... 13 methods
}

export const networkAPI = new NetworkAPI();
```

**Note** : Ajouter DevicesAPI, SystemAPI, TailscaleAPI

---

#### 4. component.js (existant)
```javascript
export class Component {
    constructor(elementId)
    setState(newState)
    render()
}
```

---

### Feature Modules

#### 1. dashboard-module.js

**Responsabilité** : Vue d'ensemble du système

```javascript
export class DashboardModule extends Component {
    state: {
        devices: { total, online, offline },
        network: { devices, scans },
        tailscale: { connected, devices },
        system: { uptime, cpu, memory }
    }
    
    async init()
    async loadData()
    render()
    destroy()
}
```

**TODO Backend** :
- `GET /api/system/stats` pour agréger les données

---

#### 2. devices-module.js

**Responsabilité** : Gestion CRUD des appareils

```javascript
export class DevicesModule extends Component {
    devices: Device[]
    
    async init()
    async loadDevices()
    render()
    
    // CRUD
    async saveDevice(form)
    async deleteDevice(id)
    
    // Actions
    async pingDevice(id)
    async wakeDevice(id)
    
    // UI
    showDeviceModal(device?)
    
    destroy()
}
```

**Backend** : ✅ 9 endpoints opérationnels

---

#### 3. network-module.js

**Responsabilité** : Adaptateur pour NetworkDashboard

```javascript
export class NetworkModule {
    dashboard: NetworkDashboard
    
    async init() {
        this.dashboard = new NetworkDashboard();
        this.dashboard.elementId = 'page-network';
        await this.dashboard.init();
    }
    
    destroy() {
        this.dashboard.destroy();
    }
}
```

**Note** : Délègue tout à `network-dashboard.js`

---

#### 4. network-dashboard.js (existant)

**Responsabilité** : Dashboard Network complet

```javascript
export class NetworkDashboard extends Component {
    state: {
        scanning: boolean,
        devices: Device[],
        stats: Stats,
        scanOptions: ScanOptions
    }
    
    widgets: {
        bandwidth: BandwidthWidget,
        latency: LatencyWidget
    }
    
    async init()
    async startScan()
    async loadData()
    render()
    destroy()
}
```

**Backend** : ✅ 13 endpoints opérationnels

---

#### 5. tailscale-module.js

**Responsabilité** : Gestion VPN Tailscale

```javascript
export class TailscaleModule extends Component {
    status: TailscaleStatus
    devices: TailscaleDevice[]
    
    async init()
    async loadData()
    render()          // ⚠️ Placeholder actuellement
    destroy()
}
```

**TODO Backend** :
- `GET /api/tailscale/status`
- `GET /api/tailscale/devices`

---

#### 6. system-module.js

**Responsabilité** : Monitoring système

```javascript
export class SystemModule extends Component {
    stats: SystemStats
    
    async init()
    async loadData()
    render()          // ⚠️ Placeholder actuellement
    destroy()
}
```

**TODO Backend** :
- `GET /api/system/stats`
- `GET /api/system/temperature`

---

## 🎨 Styles

### modern.css (réutilisé)

Variables CSS :
```css
:root {
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --text-primary: #f1f5f9;
    --primary-color: #3b82f6;
    --border-color: #334155;
}
```

Components :
- `.card` : Carte générique
- `.btn`, `.btn-primary`, `.btn-sm` : Boutons
- `.stat-row`, `.stat-value` : Stats
- `.modal` : Modals

### hub.html styles

Styles HUB-specific :
- `.app-container` : Layout flex
- `.sidebar` : Navigation
- `.nav-item` : Menu items
- `.main-content` : Content area
- `.page` : Page containers
- `.dashboard-grid` : Dashboard layout
- `.devices-grid` : Devices layout

---

## 📱 Responsive Design

### Desktop (> 768px)

```
┌─────────────────────────────────┐
│  Sidebar (250px)  │  Content    │
│  (fixe)           │  (flex: 1)  │
└─────────────────────────────────┘
```

### Mobile (≤ 768px)

```
┌─────────────────────────────────┐
│  ☰ Menu     │     Content       │
│  (overlay)  │     (full width)  │
└─────────────────────────────────┘

Sidebar glisse depuis la gauche
Overlay opaque derrière
```

---

## 🔌 Ajouter une nouvelle feature

### Exemple : Module "Plex"

**1. Créer le module**

```javascript
// web/static/js/modules/plex-module.js
import { Component } from '../core/component.js';

export class PlexModule extends Component {
    async init() {
        await this.loadData();
    }
    
    async loadData() {
        const status = await fetch('/api/plex/status').then(r => r.json());
        this.render(status);
    }
    
    render(status) {
        const container = document.getElementById('page-plex');
        container.innerHTML = `
            <h1>🎬 Plex</h1>
            <p>Status: ${status.running ? 'Running' : 'Stopped'}</p>
        `;
    }
    
    destroy() {
        console.log('Plex module destroyed');
    }
}

export default PlexModule;
```

**2. Ajouter route dans app-hub.js**

```javascript
// app-hub.js - dans registerRoutes()
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

**3. Ajouter page dans hub.html**

```html
<!-- Dans .content-body -->
<div id="page-plex" class="page"></div>
```

**4. Ajouter nav item dans hub.html**

```html
<!-- Dans .sidebar-nav -->
<a class="nav-item" data-route="plex">
    <span class="icon">🎬</span>
    <span>Plex</span>
</a>
```

**5. Créer backend**

```python
# src/features/plex/router.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/plex", tags=["plex"])

@router.get("/status")
async def get_plex_status():
    return {"running": True, "version": "1.0"}
```

```python
# app.py
from src.features.plex import router as plex_router
app.include_router(plex_router)
```

**C'est tout !** 🎉

---

## 🐛 Debugging

### Console Browser

```javascript
// Accéder à l'app
window.hubApp

// Voir modules chargés
window.hubApp.modules

// Naviguer
window.hubApp.router.navigate('devices')

// Voir routes
window.hubApp.router.getRoutes()

// Module loader
import { moduleLoader } from '/static/js/core/module-loader.js';
moduleLoader.modules
```

### Network Tab

Vérifier :
- Chargement des modules JS (200 OK)
- Appels API (/api/devices/, /api/network/devices, etc.)
- Erreurs CORS

### Elements Tab

Vérifier :
- `.page.active` sur la bonne page
- `.nav-item.active` sur le bon item
- Contenu rendu dans `#page-{name}`

---

## 📈 Performance

### Optimisations

✅ **Lazy loading** : Modules chargés à la demande  
✅ **Caching** : Modules chargés restent en cache  
✅ **Cleanup** : `destroy()` libère ressources  
✅ **Auto-refresh** : Intervals raisonnables (30s+)  

### Métriques

| Métrique | Valeur | Note |
|----------|--------|------|
| Initial load | ~50KB | hub.html + app-hub.js |
| Module load | ~10-30KB | Par module |
| API calls | ~1-5KB | JSON responses |
| Auto-refresh | 30s | Configurable par module |

---

**Version** : 6.0.0  
**Architecture** : HUB Unifié  
**Modules** : 5 (2 complets, 3 placeholders)  
**Status** : ✅ Opérationnel
