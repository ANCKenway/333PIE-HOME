# ⚡ 333HOME - Référence Rapide (Pense-Bête)

> **Pour démarrer rapidement** - Condensé architecture + endpoints clés  
> **Version** : 3.0.0 | **Date** : 30 octobre 2025

---

## 🏗️ Architecture en 3 Couches

```
┌─────────────────────────────────────────────────────────┐
│                   WEB INTERFACE                         │
│            index.html (Alpine.js + TailwindCSS)         │
└─────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    FASTAPI APP                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ Devices  │  │ Network  │  │  Hub (Unified View)  │  │
│  │  Router  │  │  Router  │  │       Router         │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   DATA LAYER                            │
│  devices.json  |  network_registry.json  |  *.json     │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Endpoints Critiques (Les Plus Utilisés)

### 🔥 Top 10 Endpoints

| Endpoint | Méthode | Usage | Refresh |
|----------|---------|-------|---------|
| `/api/hub/devices` | `GET` | Vue unifiée tous devices | 5s auto |
| `/api/network/registry/` | `GET` | Registry complet (source vérité) | 5s auto |
| `/api/network/registry/refresh` | `POST` | Refresh ARP + VPN (<1s) | Manuel |
| `/api/devices/` | `GET` | Liste devices managés | - |
| `/api/devices/` | `POST` | Ajouter device | - |
| `/api/devices/{id}` | `PATCH` | Modifier device | - |
| `/api/devices/{id}` | `DELETE` | Supprimer device | - |
| `/api/devices/{id}/wake` | `POST` | Wake-on-LAN | - |
| `/api/network/registry/device/{mac}` | `GET` | Historique device (modal) | - |
| `/api/network/scan` | `POST` | Scan nmap complet (ON-DEMAND) | Manuel |

---

## 📂 Structure Fichiers Clés

```
333HOME/
├── app.py                           # Point d'entrée FastAPI
├── web/
│   ├── index.html                   # Interface principale (57K)
│   └── assets/                      # CSS/JS/images
├── src/
│   ├── core/
│   │   ├── config.py                # Settings globaux
│   │   ├── logging_config.py        # Configuration logs
│   │   └── unified/
│   │       ├── router.py            # Hub API (vue unifiée)
│   │       └── unified_service.py   # Logique enrichissement
│   ├── features/
│   │   ├── devices/
│   │   │   ├── router.py            # CRUD devices managés
│   │   │   ├── manager.py           # DeviceManager (devices.json)
│   │   │   └── schemas.py           # Pydantic models
│   │   └── network/
│   │       ├── router.py            # Router agrégateur network
│   │       ├── registry.py          # NetworkRegistry (source vérité)
│   │       ├── dhcp_router.py       # Tracking DHCP
│   │       └── routers/
│   │           ├── scan_router.py   # Scans nmap ON-DEMAND
│   │           ├── device_router.py # Devices réseau
│   │           ├── registry_router.py  # Registry endpoints
│   │           ├── latency_router.py   # Mesures latence
│   │           └── bandwidth_router.py # Monitoring bande passante
│   └── shared/                      # Utilitaires communs
└── data/
    ├── devices.json                 # Devices managés
    ├── network_registry.json        # Registry (source vérité)
    ├── dhcp_history.json            # Historique DHCP
    └── network_scan_history.json    # Historique scans
```

---

## 🔑 Concepts Clés

### 1️⃣ **Devices Managés** vs **Devices Réseau**

| Type | Source | API | Fichier | Gestion |
|------|--------|-----|---------|---------|
| **Managés** | Ajout manuel | `/api/devices` | `devices.json` | CRUD complet |
| **Réseau** | Scans auto | `/api/network/devices` | `network_registry.json` | Read-only |

### 2️⃣ **Network Registry** = Source Unique de Vérité

- **Fichier** : `data/network_registry.json`
- **Contenu** : TOUS les devices jamais détectés (online + offline)
- **Enrichissement** : Chaque scan AJOUTE au registry (jamais d'écrasement)
- **Historique** : IP changes, hostname changes, présence/absence

### 3️⃣ **Hub Unified View** = Enrichissement Croisé

Le Hub (`/api/hub/devices`) combine :
- Données devices managés (`devices.json`)
- Statut réseau temps réel (`network_registry.json`)
- Infos VPN (Tailscale)

**Exemple** : Device "333PIE" (managé) + registry → `{name, ip, mac, is_online, vpn_ip}`

### 4️⃣ **Refresh Registry** = Ultra-Rapide (<1s)

```bash
POST /api/network/registry/refresh
```

- ✅ ARP cache système (pas de ping)
- ✅ Tailscale status (API locale)
- ✅ Update `is_online`, `is_vpn_connected`, `last_seen`
- ❌ SANS scan nmap (pour ça : `POST /api/network/scan`)

### 5️⃣ **Flag `is_managed`** (Phase 6)

Flag dans registry indiquant si device est dans `devices.json` :
- ✅ `is_managed: true` → Device géré, enrichissement hostname possible
- ❌ `is_managed: false` → Device détecté par scan, pas géré

**Auto-marquage** :
- Lors création device : `POST /api/devices/` → auto-mark managed ✅
- Manuel : `POST /api/network/registry/device/{mac}/manage`

---

## 🚀 Commandes Rapides

### Démarrage

```bash
# Démarrer l'app
./start.sh

# Ou manuellement
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Tests rapides

```bash
# Health check
curl http://localhost:8000/health

# Liste devices managés
curl http://localhost:8000/api/devices/ | jq

# Vue unifiée hub
curl http://localhost:8000/api/hub/devices | jq

# Registry complet
curl http://localhost:8000/api/network/registry/ | jq

# Refresh registry (rapide)
curl -X POST http://localhost:8000/api/network/registry/refresh

# Scan complet nmap
curl -X POST http://localhost:8000/api/network/scan
```

### Logs

```bash
# Logs temps réel
tail -f /tmp/333home.log

# Logs avec filtres
tail -f /tmp/333home.log | grep -E "ERROR|WARNING|✅|❌"
```

---

## 🔧 Cycles Automatiques

### Interface Web (`index.html`)

```javascript
setInterval(async () => {
    await fetchDevices();           // GET /api/hub/devices
    await refreshRegistryStatus();  // POST /api/network/registry/refresh
}, 5000);  // Toutes les 5 secondes
```

**Résultat** :
- Mise à jour temps réel `last_seen`
- Statut online/offline immédiat
- Badge VPN dynamique
- Détection connexion/déconnexion

### Backend (`app.py`)

⚠️ **Monitoring auto DÉSACTIVÉ** :
```python
# ⚠️ MONITORING DÉSACTIVÉ : Scans ON-DEMAND uniquement via API
# Raison : Éviter perturbations réseau et détection antivirus
```

**Scans manuels uniquement** :
- Via API : `POST /api/network/scan`
- Ou interface web : Bouton "🔄 Rafraîchir"

---

## 🎨 Interface Web - Composants Clés

### Modal Historique (`viewHistory()`)

```javascript
// Ligne 746-778 index.html
async function viewHistory(device) {
    const response = await fetch(`/api/network/registry/device/${device.mac}`);
    // Affiche : IP history, hostname history, stats détections
}
```

### Modal Édition (`editDevice()`)

```javascript
// Ligne 783-825 index.html
function editDevice(device) {
    showEditModal = true;
    editingDevice = {...device};  // Clone pour édition
}
```

### Auto-Refresh Registry

```javascript
// Ligne 703-714 index.html
async function refreshRegistryStatus() {
    await fetch('/api/network/registry/refresh', { method: 'POST' });
    // Refresh ultra-rapide (<1s) sans reload page
}
```

---

## 🐛 Debug Rapide

### Badge VPN manquant ?

1. **Vérifier registry** :
   ```bash
   curl -s http://localhost:8000/api/network/registry/ | \
       jq '.devices[] | select(.mac == "XX:XX:XX:XX:XX:XX") | {current_hostname, is_vpn_connected, is_managed}'
   ```

2. **Problème** : `is_managed: false` ?
   ```bash
   # Marquer comme géré
   curl -X POST http://localhost:8000/api/network/registry/device/XX:XX:XX:XX:XX:XX/manage
   ```

3. **Refresh** :
   ```bash
   curl -X POST http://localhost:8000/api/network/registry/refresh
   ```

### Device pas détecté ?

```bash
# Vérifier ARP cache
arp -a | grep 192.168.1.XXX

# Vérifier Tailscale
tailscale status | grep <hostname>

# Scan complet nmap
curl -X POST http://localhost:8000/api/network/scan
```

### Logs vides ?

```bash
# Vérifier niveau logs
grep "logging_config" /tmp/333home.log

# Changer niveau (config.py)
DEBUG = True  # Activer logs debug
```

---

## 📊 Métriques Système

### Performance

| Opération | Temps | Type |
|-----------|-------|------|
| Registry refresh | <1s | ARP + Tailscale |
| Scan nmap complet | 5-15s | Full scan |
| Hub unified view | <100ms | Enrichissement |
| Device CRUD | <50ms | JSON r/w |

### Fichiers

| Fichier | Taille typique | Fréquence maj |
|---------|----------------|---------------|
| `devices.json` | 1-5 KB | Manuel (CRUD) |
| `network_registry.json` | 10-50 KB | Toutes les 5s |
| `network_scan_history.json` | 50-200 KB | ON-DEMAND |
| `dhcp_history.json` | 5-20 KB | Lors scans |

---

## 🎯 Phases Développement (Historique)

| Phase | Date | Objectif | Résultat |
|-------|------|----------|----------|
| **Phase 1** | 28 Oct | Audit RULES.md | ✅ 250L code mort supprimées |
| **Phase 2** | 28 Oct | Fix bugs page Appareils | ✅ DELETE/WOL avec ID |
| **Phase 3** | 28 Oct | Modal Historique | ✅ IP/hostname history |
| **Phase 4** | 28 Oct | Temps réel last_seen | ✅ Cycle 5s auto-refresh |
| **Phase 5** | 30 Oct | Bouton Modifier | ✅ Modal édition CRUD |
| **Phase 6** | 30 Oct | Fix badge VPN | ✅ Enrichissement hostname + auto-mark managed |
| **Audit Final** | 30 Oct | Conformité RULES.md | ✅ Score 10/10 |

---

## 📚 Documentation Complète

Pour aller plus loin :

| Document | Contenu |
|----------|---------|
| `API_INVENTORY.md` | Inventaire exhaustif 35 routes API |
| `ARCHITECTURE.md` | Architecture globale système |
| `HUB_ARCHITECTURE.md` | Vue unifiée + enrichissement |
| `NETWORK_ARCHITECTURE.md` | Scans, registry, monitoring |
| `API_DOCUMENTATION.md` | Schémas Pydantic + exemples |
| `AUDIT_CODE_COMPLET.md` | Rapport audit Phase 1 |
| `RULES.md` | Règles d'or développement |

---

## ✅ Checklist Avant Production

- [x] Aucune route dupliquée
- [x] Aucun fichier `.backup`, `.old`, `.v2`
- [x] Logs configurés (`/tmp/333home.log`)
- [x] Monitoring auto désactivé (ON-DEMAND uniquement)
- [x] Auto-refresh 5s fonctionnel
- [x] Badge VPN opérationnel
- [x] Tests API validés (CRUD + WOL + Refresh)
- [x] Documentation à jour
- [x] Conformité RULES.md : **10/10** ✅

---

**🎉 Système prêt pour production !**
