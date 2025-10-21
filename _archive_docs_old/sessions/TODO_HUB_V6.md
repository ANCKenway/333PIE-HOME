# 📋 TODO - HUB v6.0

## ✅ Terminé (Session actuelle)

### Frontend Architecture
- [x] Router hash-based (`core/router.js`)
- [x] Module Loader dynamique (`core/module-loader.js`)
- [x] Application HUB principale (`app-hub.js`)
- [x] Interface HUB (`hub.html`)
- [x] Design responsive (desktop + mobile)

### Modules Frontend
- [x] Dashboard Module (placeholder)
- [x] Devices Module (complet avec CRUD)
- [x] Network Module (adaptateur)
- [x] Tailscale Module (placeholder)
- [x] System Module (placeholder)

### Documentation
- [x] Architecture HUB (`docs/HUB_ARCHITECTURE.md`)
- [x] Quick Start Guide (`docs/QUICK_START_HUB.md`)
- [x] Frontend Structure (`docs/FRONTEND_STRUCTURE_HUB.md`)
- [x] Architecture Diagrams (`docs/ARCHITECTURE_DIAGRAMS.md`)
- [x] Session Recap (`SESSION_HUB_V6.md`)

---

## 🎯 Prochaines priorités

### Priorité 1 : Backend System ⚙️

**Objectif** : Monitoring système complet

#### Fichiers à créer

```
src/features/system/
├── __init__.py
├── router.py          # Endpoints FastAPI
├── schemas.py         # Models Pydantic
└── monitor.py         # Logic monitoring (psutil, etc.)
```

#### Endpoints requis

- [ ] `GET /api/system/stats`
  ```json
  {
    "cpu": { "percent": 45.2, "cores": 4 },
    "memory": { "used_gb": 3.2, "total_gb": 8.0, "percent": 40 },
    "disk": { "used_gb": 120, "total_gb": 256, "percent": 47 },
    "uptime": "2 days, 5 hours"
  }
  ```

- [ ] `GET /api/system/temperature`
  ```json
  {
    "cpu_temp": 52.5,
    "unit": "celsius"
  }
  ```

- [ ] `GET /api/system/services`
  ```json
  {
    "services": [
      { "name": "tailscale", "status": "running" },
      { "name": "ssh", "status": "running" }
    ]
  }
  ```

#### Implémentation

1. Installer dépendances :
   ```bash
   pip install psutil
   ```

2. Créer `src/features/system/monitor.py` :
   ```python
   import psutil
   import datetime
   
   def get_system_stats():
       return {
           "cpu": {
               "percent": psutil.cpu_percent(interval=1),
               "cores": psutil.cpu_count()
           },
           "memory": {
               "used_gb": round(psutil.virtual_memory().used / (1024**3), 1),
               "total_gb": round(psutil.virtual_memory().total / (1024**3), 1),
               "percent": psutil.virtual_memory().percent
           },
           "disk": {
               "used_gb": round(psutil.disk_usage('/').used / (1024**3), 1),
               "total_gb": round(psutil.disk_usage('/').total / (1024**3), 1),
               "percent": psutil.disk_usage('/').percent
           },
           "uptime": str(datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time()))
       }
   
   def get_cpu_temperature():
       # Raspberry Pi specific
       try:
           temp = psutil.sensors_temperatures()
           if 'cpu_thermal' in temp:
               return temp['cpu_thermal'][0].current
       except:
           pass
       return None
   ```

3. Créer router et monter dans `app.py`

4. Mettre à jour `system-module.js` pour afficher vraies données

**Temps estimé** : 2-3 heures

---

### Priorité 2 : Backend Tailscale 🔒

**Objectif** : Intégration VPN Tailscale

#### Fichiers à créer

```
src/features/tailscale/
├── __init__.py
├── router.py          # Endpoints FastAPI
├── schemas.py         # Models Pydantic
└── client.py          # Tailscale CLI wrapper
```

#### Endpoints requis

- [ ] `GET /api/tailscale/status`
  ```json
  {
    "connected": true,
    "ip": "100.64.1.5",
    "hostname": "raspberrypi",
    "online": true
  }
  ```

- [ ] `GET /api/tailscale/devices`
  ```json
  {
    "devices": [
      { "hostname": "laptop", "ip": "100.64.1.2", "online": true },
      { "hostname": "phone", "ip": "100.64.1.3", "online": false }
    ]
  }
  ```

- [ ] `POST /api/tailscale/configure`
  ```json
  {
    "api_key": "tskey-..."
  }
  ```

#### Implémentation

1. Wrapper Tailscale CLI :
   ```python
   import subprocess
   import json
   
   def get_tailscale_status():
       result = subprocess.run(
           ['tailscale', 'status', '--json'],
           capture_output=True,
           text=True
       )
       return json.loads(result.stdout) if result.returncode == 0 else None
   ```

2. Créer endpoints FastAPI

3. Mettre à jour `tailscale-module.js`

**Temps estimé** : 3-4 heures

---

### Priorité 3 : Dashboard Stats Endpoint 📊

**Objectif** : Endpoint pour agréger toutes les stats

#### Endpoint à créer

- [ ] `GET /api/system/dashboard`
  ```json
  {
    "devices": {
      "total": 12,
      "online": 8,
      "offline": 4
    },
    "network": {
      "devices_scanned": 15,
      "scans_count": 42,
      "last_scan": "2025-10-21T14:30:00Z"
    },
    "tailscale": {
      "connected": true,
      "devices": 5
    },
    "system": {
      "uptime": "2 days, 5 hours",
      "cpu": 45.2,
      "memory": 40,
      "disk": 47
    }
  }
  ```

#### Implémentation

1. Créer dans `src/features/system/router.py` :
   ```python
   @router.get("/dashboard")
   async def get_dashboard_stats():
       # Agréger depuis devices, network, tailscale, system
       pass
   ```

2. Mettre à jour `dashboard-module.js` pour fetch `/api/system/dashboard`

**Temps estimé** : 1-2 heures

---

### Priorité 4 : Améliorations UX 🎨

**Objectif** : Meilleure expérience utilisateur

#### Features à ajouter

- [ ] **Notifications Toast**
  - Créer `core/notifications.js`
  - Toast success/error/info
  - Auto-dismiss après 3s
  - Stack multiple toasts

- [ ] **Loading States**
  - Spinners pendant chargement
  - Skeleton loaders
  - Disable buttons pendant actions

- [ ] **Error Boundaries**
  - Catch errors dans modules
  - Afficher message user-friendly
  - Bouton "Retry"

- [ ] **Better Forms**
  - Validation temps réel
  - Messages d'erreur clairs
  - Auto-focus sur premier champ

- [ ] **Confirmations**
  - Modal confirmation au lieu de `confirm()`
  - Actions destructives (delete) confirmées

**Temps estimé** : 4-6 heures

---

### Priorité 5 : Real-time Updates 🔄

**Objectif** : Mises à jour en temps réel

#### Technologies

- [ ] **WebSockets** ou **Server-Sent Events (SSE)**

#### Features

- [ ] Live system stats (CPU/RAM/Disk)
- [ ] Live bandwidth graph
- [ ] Live latency monitoring
- [ ] Device online/offline events
- [ ] Scan progress updates

#### Implémentation

1. Backend FastAPI WebSocket :
   ```python
   from fastapi import WebSocket
   
   @app.websocket("/ws")
   async def websocket_endpoint(websocket: WebSocket):
       await websocket.accept()
       while True:
           stats = get_system_stats()
           await websocket.send_json(stats)
           await asyncio.sleep(5)
   ```

2. Frontend WebSocket client :
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws');
   ws.onmessage = (event) => {
       const stats = JSON.parse(event.data);
       updateUI(stats);
   };
   ```

**Temps estimé** : 6-8 heures

---

## 🔧 Améliorations techniques

### Code Quality

- [ ] ESLint configuration
- [ ] JSDoc comments
- [ ] Type annotations (JSDoc ou TypeScript)
- [ ] Unit tests (Jest)
- [ ] Integration tests

### Performance

- [ ] Lazy load images/assets
- [ ] Debounce auto-refresh
- [ ] Cache API responses
- [ ] Service Worker (PWA)
- [ ] Code splitting

### Security

- [ ] HTTPS
- [ ] Authentication (login/logout)
- [ ] API tokens
- [ ] CSRF protection
- [ ] Rate limiting

---

## 📱 Features futures

### PWA (Progressive Web App)

- [ ] Service Worker
- [ ] Offline mode
- [ ] Add to Home Screen
- [ ] Push notifications

### Settings Page

- [ ] User preferences
  - Dark/Light mode toggle
  - Auto-refresh interval
  - Notification preferences
- [ ] API configuration
  - Backend URL
  - Timeout settings
- [ ] Backup/Restore
  - Export devices.json
  - Import configuration

### Advanced Features

- [ ] **Plex Integration**
  - Plex server status
  - Currently playing
  - Start/Stop server

- [ ] **Docker Management**
  - List containers
  - Start/Stop containers
  - View logs

- [ ] **Home Assistant Integration**
  - Devices sync
  - Automations trigger

- [ ] **Network Mapping**
  - Visual network topology
  - Device relationships
  - Network diagram

---

## 🐛 Bugs connus

Aucun bug connu pour l'instant.

---

## 📚 Documentation à améliorer

- [ ] API Documentation (OpenAPI/Swagger)
- [ ] User Guide (screenshots)
- [ ] Developer Guide (contributing)
- [ ] Deployment Guide (systemd service)
- [ ] Troubleshooting Guide

---

## 🎓 Apprentissage continu

### Technologies à explorer

- [ ] TypeScript (pour type safety)
- [ ] Vue.js ou React (comparaison avec vanilla JS)
- [ ] Tailwind CSS (alternative à modern.css)
- [ ] Chart.js (pour graphiques)
- [ ] Socket.IO (alternative à WebSockets)

---

## 📅 Planning suggéré

### Semaine 1
- [ ] Backend System (Priorité 1)
- [ ] Backend Tailscale (Priorité 2)
- [ ] Dashboard Endpoint (Priorité 3)

### Semaine 2
- [ ] Notifications Toast (Priorité 4)
- [ ] Loading States (Priorité 4)
- [ ] Error Boundaries (Priorité 4)

### Semaine 3
- [ ] WebSockets (Priorité 5)
- [ ] Real-time graphs (Priorité 5)

### Semaine 4
- [ ] Settings Page
- [ ] PWA (Service Worker)
- [ ] Documentation

---

## 💡 Notes

### Points d'attention

1. **Toujours tester sur Raspberry Pi** avant de considérer terminé
2. **Respecter RULES.md** : architecture modulaire, code propre
3. **Documentation** : Mettre à jour docs après chaque feature
4. **Git commits** : Messages clairs et descriptifs
5. **Performance** : Tester avec plusieurs devices/scans

### Ressources utiles

- FastAPI docs : https://fastapi.tiangolo.com/
- Tailscale docs : https://tailscale.com/kb/
- psutil docs : https://psutil.readthedocs.io/
- MDN WebSockets : https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

---

**Version** : 6.0.0  
**Dernière mise à jour** : 21 octobre 2025  
**Status** : 🚧 En développement
