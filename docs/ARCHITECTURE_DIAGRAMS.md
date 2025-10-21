# 🏗️ Architecture Diagrams - HUB v6.0

## 📊 Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────────┐
│                         🏠 333HOME HUB v6.0                         │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      FRONTEND (SPA)                          │  │
│  │                                                              │  │
│  │  hub.html (Entry point)                                     │  │
│  │       ↓                                                      │  │
│  │  app-hub.js (Orchestrator)                                  │  │
│  │       ↓                                                      │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │  Router (Hash-based) ← → Module Loader              │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  │       ↓                                                      │  │
│  │  ┌────────────────────────────────────────────────┐         │  │
│  │  │  Modules (Lazy loaded)                        │         │  │
│  │  │  ├─ 📊 Dashboard                              │         │  │
│  │  │  ├─ 📱 Devices    ✅ COMPLET                  │         │  │
│  │  │  ├─ 🌐 Network    ✅ COMPLET                  │         │  │
│  │  │  ├─ 🔒 Tailscale  ⚠️  PLACEHOLDER             │         │  │
│  │  │  └─ ⚙️  System     ⚠️  PLACEHOLDER             │         │  │
│  │  └────────────────────────────────────────────────┘         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                             ↕ HTTP/JSON                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    BACKEND (FastAPI)                         │  │
│  │                                                              │  │
│  │  app.py (Main app)                                          │  │
│  │       ↓                                                      │  │
│  │  ┌────────────────────────────────────────────────┐         │  │
│  │  │  Features (Backend modules)                   │         │  │
│  │  │  ├─ devices/   ✅ 9 endpoints                 │         │  │
│  │  │  ├─ network/   ✅ 13 endpoints                │         │  │
│  │  │  ├─ tailscale/ ❌ À CRÉER                     │         │  │
│  │  │  └─ system/    ❌ À CRÉER                     │         │  │
│  │  └────────────────────────────────────────────────┘         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                             ↕                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      DATA STORAGE                            │  │
│  │                                                              │  │
│  │  data/                                                       │  │
│  │  ├─ devices.json          (Devices DB)                      │  │
│  │  ├─ scan_history.json     (Network scans)                   │  │
│  │  └─ network_history.json  (Network stats)                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Navigation Flow

### User Journey

```
┌──────────────────────────────────────────────────────────────────┐
│  1. USER OPENS http://localhost:8000/hub                        │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│  2. BROWSER loads hub.html                                       │
│     - HTML structure                                             │
│     - CSS (modern.css + inline styles)                           │
│     - <script type="module" src="app-hub.js">                    │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│  3. APP-HUB.JS initializes                                       │
│     - Import router, moduleLoader                                │
│     - HubApp.init()                                              │
│       ├─ registerRoutes() - 5 routes                             │
│       ├─ setupNavigation() - nav-item listeners                  │
│       ├─ setupMobileMenu() - hamburger menu                      │
│       └─ router.handleRouteChange() - load initial route         │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│  4. ROUTER reads hash                                            │
│     - window.location.hash = '' → default: 'dashboard'           │
│     - Find route config for 'dashboard'                          │
│     - Call route.init()                                          │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│  5. MODULE LOADER loads dashboard-module.js                      │
│     - Dynamic import: import('/static/js/modules/...')           │
│     - Cache module for future use                                │
│     - Return module exports                                      │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│  6. DASHBOARD MODULE initializes                                 │
│     - new DashboardModule()                                      │
│     - instance.init()                                            │
│       ├─ loadData() - fetch stats from backend                   │
│       └─ render() - display in #page-dashboard                   │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│  7. USER SEES Dashboard page                                     │
│     - System stats                                               │
│     - Devices summary                                            │
│     - Network summary                                            │
│     - Quick actions                                              │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│  8. USER CLICKS "📱 Devices" in sidebar                          │
│     - nav-item[data-route="devices"].click                       │
│     - router.navigate('devices')                                 │
│     - window.location.hash = '#/devices'                         │
│     - hashchange event                                           │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│  9. ROUTER handles route change                                  │
│     - Call currentRoute.destroy() (dashboard.destroy())          │
│     - Hide #page-dashboard                                       │
│     - Load 'devices' route                                       │
│     - Call route.init()                                          │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│  10. DEVICES MODULE loads                                        │
│      - Module already cached? Use it : Load it                   │
│      - new DevicesModule()                                       │
│      - instance.init()                                           │
│        ├─ loadDevices() - GET /api/devices/                      │
│        └─ render() - display devices grid                        │
└──────────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│  11. USER SEES Devices page                                      │
│      - List of devices                                           │
│      - Add/Edit/Delete buttons                                   │
│      - Wake-on-LAN & Ping actions                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Module Loading Sequence

```
┌─────────────────────────────────────────────────────────────┐
│  ROUTE REGISTRATION (app-hub.js - registerRoutes())        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  router.register('dashboard', {                            │
│      title: 'Dashboard',                                   │
│      init: async () => {                                   │
│          ┌────────────────────────────────────────────┐    │
│          │ MODULE LOADER                              │    │
│          │  const module = await moduleLoader.load(  │    │
│          │      'dashboard',                          │    │
│          │      '/static/js/modules/dashboard-...'   │    │
│          │  )                                         │    │
│          └────────────────────────────────────────────┘    │
│                         ↓                                   │
│          ┌────────────────────────────────────────────┐    │
│          │ DYNAMIC IMPORT                             │    │
│          │  import('/static/js/modules/...')          │    │
│          │  → Returns module exports                  │    │
│          └────────────────────────────────────────────┘    │
│                         ↓                                   │
│          ┌────────────────────────────────────────────┐    │
│          │ INSTANTIATE                                │    │
│          │  const instance = new module.DashboardModule() │
│          │  await instance.init()                     │    │
│          │  this.modules.set('dashboard', instance)   │    │
│          └────────────────────────────────────────────┘    │
│      },                                                     │
│      destroy: () => {                                      │
│          const instance = this.modules.get('dashboard');   │
│          if (instance) instance.destroy();                 │
│          this.modules.delete('dashboard');                 │
│      }                                                      │
│  })                                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Module Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    MODULE LIFECYCLE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐                                          │
│  │   INITIAL    │  User navigates to route                 │
│  │   (not loaded)│                                          │
│  └──────┬───────┘                                          │
│         │                                                   │
│         ↓ moduleLoader.load()                              │
│  ┌──────────────┐                                          │
│  │   LOADING    │  Dynamic import in progress              │
│  │              │                                          │
│  └──────┬───────┘                                          │
│         │                                                   │
│         ↓ import successful                                │
│  ┌──────────────┐                                          │
│  │   LOADED     │  Module exports available                │
│  │              │  (cached in moduleLoader.modules)        │
│  └──────┬───────┘                                          │
│         │                                                   │
│         ↓ new Module()                                     │
│  ┌──────────────┐                                          │
│  │ INSTANTIATED │  Instance created                        │
│  │              │                                          │
│  └──────┬───────┘                                          │
│         │                                                   │
│         ↓ instance.init()                                  │
│  ┌──────────────┐                                          │
│  │  INITIALIZED │  ✅ ACTIVE                               │
│  │              │  - Data loaded                           │
│  │              │  - Rendered                              │
│  │              │  - Event listeners attached              │
│  │              │  - Auto-refresh started                  │
│  └──────┬───────┘                                          │
│         │                                                   │
│         │ User navigates away                              │
│         ↓ instance.destroy()                               │
│  ┌──────────────┐                                          │
│  │  DESTROYED   │  - clearInterval()                       │
│  │              │  - removeEventListeners()                │
│  │              │  - Cleanup                               │
│  └──────┬───────┘                                          │
│         │                                                   │
│         ↓ delete from hubApp.modules                       │
│  ┌──────────────┐                                          │
│  │   CACHED     │  Module code still in moduleLoader       │
│  │   (in memory)│  Ready for fast reload                   │
│  └──────────────┘                                          │
│         │                                                   │
│         └─────────► Can be re-instantiated quickly         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔌 API Communication

### Frontend → Backend

```
┌─────────────────────────────────────────────────────────────┐
│                   DEVICES MODULE FLOW                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────┐        │
│  │  USER ACTION                                   │        │
│  │  - Click "⚡ Wake" button                      │        │
│  └────────┬───────────────────────────────────────┘        │
│           ↓                                                 │
│  ┌────────────────────────────────────────────────┐        │
│  │  DEVICES MODULE                                │        │
│  │  async wakeDevice(id) {                        │        │
│  │      await fetch(`/api/devices/${id}/wake`, { │        │
│  │          method: 'POST'                        │        │
│  │      })                                        │        │
│  │  }                                             │        │
│  └────────┬───────────────────────────────────────┘        │
│           ↓ HTTP POST                                       │
│  ┌────────────────────────────────────────────────┐        │
│  │  FASTAPI BACKEND                               │        │
│  │  @router.post("/devices/{id}/wake")           │        │
│  │  async def wake_device(id: int)                │        │
│  └────────┬───────────────────────────────────────┘        │
│           ↓                                                 │
│  ┌────────────────────────────────────────────────┐        │
│  │  DEVICES ROUTER                                │        │
│  │  - Load device from storage                    │        │
│  │  - Send WOL magic packet                       │        │
│  │  - Return result                               │        │
│  └────────┬───────────────────────────────────────┘        │
│           ↓ HTTP 200 OK + JSON                             │
│  ┌────────────────────────────────────────────────┐        │
│  │  RESPONSE                                      │        │
│  │  { "success": true, "message": "WOL sent" }   │        │
│  └────────┬───────────────────────────────────────┘        │
│           ↓                                                 │
│  ┌────────────────────────────────────────────────┐        │
│  │  DEVICES MODULE                                │        │
│  │  showNotification('⚡ Wake-on-LAN envoyé')     │        │
│  └────────────────────────────────────────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Component Hierarchy

```
hub.html
├── .app-container
│   ├── .sidebar
│   │   ├── .sidebar-header
│   │   │   └── "🏠 333HOME"
│   │   ├── .sidebar-nav
│   │   │   ├── .nav-item[data-route="dashboard"] 📊
│   │   │   ├── .nav-item[data-route="devices"]   📱
│   │   │   ├── .nav-item[data-route="network"]   🌐
│   │   │   ├── .nav-item[data-route="tailscale"] 🔒
│   │   │   └── .nav-item[data-route="system"]    ⚙️
│   │   └── .sidebar-footer
│   │       └── "Version 6.0.0"
│   │
│   └── .main-content
│       ├── .content-header
│       │   ├── .menu-toggle (☰) [mobile only]
│       │   └── #page-title
│       └── .content-body
│           ├── #page-dashboard.page.active  ← DashboardModule
│           ├── #page-devices.page           ← DevicesModule
│           ├── #page-network.page           ← NetworkModule
│           ├── #page-tailscale.page         ← TailscaleModule
│           └── #page-system.page            ← SystemModule
│
└── .mobile-overlay [mobile only]
```

---

## 🗺️ Routes Map

```
┌─────────────────────────────────────────────────────────────┐
│                        ROUTES                               │
├────────────┬────────────────────┬──────────────────────────┤
│   Route    │      Module        │        Backend           │
├────────────┼────────────────────┼──────────────────────────┤
│            │                    │                          │
│ #/dashboard│ dashboard-module.js│ ⚠️ TODO: /api/system/stats│
│            │ ✅ Vue d'ensemble   │                          │
│            │                    │                          │
├────────────┼────────────────────┼──────────────────────────┤
│            │                    │                          │
│ #/devices  │ devices-module.js  │ ✅ /api/devices/*        │
│            │ ✅ CRUD complet     │    - GET /              │
│            │ ✅ Wake-on-LAN      │    - POST /             │
│            │ ✅ Ping             │    - PATCH /{id}        │
│            │                    │    - DELETE /{id}       │
│            │                    │    - POST /{id}/wake    │
│            │                    │    - POST /{id}/ping    │
│            │                    │                          │
├────────────┼────────────────────┼──────────────────────────┤
│            │                    │                          │
│ #/network  │ network-module.js  │ ✅ /api/network/*        │
│            │ (→ network-dashboard)│   - POST /scan         │
│            │ ✅ Network scan     │    - GET /devices       │
│            │ ✅ Bandwidth        │    - GET /stats         │
│            │ ✅ Latency          │    - GET /history       │
│            │                    │    - POST /bandwidth/*  │
│            │                    │    - POST /latency/*    │
│            │                    │                          │
├────────────┼────────────────────┼──────────────────────────┤
│            │                    │                          │
│ #/tailscale│ tailscale-module.js│ ❌ TODO: /api/tailscale/*│
│            │ ⚠️ Placeholder      │    - GET /status        │
│            │                    │    - GET /devices       │
│            │                    │    - POST /configure    │
│            │                    │                          │
├────────────┼────────────────────┼──────────────────────────┤
│            │                    │                          │
│ #/system   │ system-module.js   │ ❌ TODO: /api/system/*   │
│            │ ⚠️ Placeholder      │    - GET /stats         │
│            │                    │    - GET /temperature   │
│            │                    │    - GET /services      │
│            │                    │                          │
└────────────┴────────────────────┴──────────────────────────┘
```

---

## 📱 Mobile Menu Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    MOBILE MENU                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CLOSED STATE (default)                                     │
│  ┌──────────────────────────────────────────┐              │
│  │ ☰ Menu  │  Content (full width)          │              │
│  └──────────────────────────────────────────┘              │
│                                                             │
│         ↓ User clicks ☰                                     │
│                                                             │
│  OPENING ANIMATION                                          │
│  ┌──────────────────────────────────────────┐              │
│  │ [Sidebar sliding in from left]           │              │
│  │ [Overlay fading in]                      │              │
│  └──────────────────────────────────────────┘              │
│                                                             │
│         ↓ 0.3s transition                                   │
│                                                             │
│  OPEN STATE                                                 │
│  ┌────────────┬─────────────────────────────┐              │
│  │ Sidebar    │ Content (dimmed)            │              │
│  │ (250px)    │                             │              │
│  │            │  [Opaque overlay]           │              │
│  │ 📊 Dash    │                             │              │
│  │ 📱 Dev     │  User can:                  │              │
│  │ 🌐 Net     │  - Click nav item → Navigate│              │
│  │ 🔒 VPN     │  - Click overlay → Close    │              │
│  │ ⚙️ Sys     │                             │              │
│  └────────────┴─────────────────────────────┘              │
│                                                             │
│         ↓ User clicks nav-item or overlay                   │
│                                                             │
│  CLOSING ANIMATION                                          │
│  ┌──────────────────────────────────────────┐              │
│  │ [Sidebar sliding out to left]            │              │
│  │ [Overlay fading out]                     │              │
│  └──────────────────────────────────────────┘              │
│                                                             │
│         ↓ 0.3s transition                                   │
│                                                             │
│  BACK TO CLOSED STATE                                       │
│  ┌──────────────────────────────────────────┐              │
│  │ ☰ Menu  │  New page content              │              │
│  └──────────────────────────────────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 State Management

```
┌─────────────────────────────────────────────────────────────┐
│                 STATE MANAGEMENT                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  GLOBAL STATE (HubApp)                                      │
│  ┌────────────────────────────────────────┐                │
│  │  hubApp: {                             │                │
│  │      modules: Map<string, Module>      │                │
│  │      router: Router                    │                │
│  │      moduleLoader: ModuleLoader        │                │
│  │      initialized: boolean              │                │
│  │  }                                     │                │
│  └────────────────────────────────────────┘                │
│                                                             │
│  ROUTER STATE                                               │
│  ┌────────────────────────────────────────┐                │
│  │  router: {                             │                │
│  │      routes: Map<string, RouteConfig>  │                │
│  │      currentRoute: Route               │                │
│  │      defaultRoute: 'dashboard'         │                │
│  │  }                                     │                │
│  └────────────────────────────────────────┘                │
│                                                             │
│  MODULE LOADER STATE                                        │
│  ┌────────────────────────────────────────┐                │
│  │  moduleLoader: {                       │                │
│  │      modules: Map<string, Module>      │                │
│  │      loading: Map<string, Promise>     │                │
│  │  }                                     │                │
│  └────────────────────────────────────────┘                │
│                                                             │
│  MODULE-SPECIFIC STATE (ex: Devices)                        │
│  ┌────────────────────────────────────────┐                │
│  │  devicesModule: {                      │                │
│  │      devices: Device[]                 │                │
│  │      refreshInterval: number           │                │
│  │  }                                     │                │
│  └────────────────────────────────────────┘                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

**Version** : 6.0.0  
**Date** : 21 octobre 2025  
**Type** : Architecture Diagrams
