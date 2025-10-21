# 📋 TODO - Network Supervision Professionnelle

## 🎯 Objectif Global

Transformer le système actuel en **supervision réseau professionnelle** type IPScanner/Advanced IP Scanner avec :
- Tracking MAC intelligent
- Multi-sources (nmap + ARP + Freebox API)
- Monitoring continu automatique
- Interface riche avec graphes
- Système d'alertes avancé

**Référence** : `docs/NETWORK_PRO_ARCHITECTURE.md`

---

## 🔴 Phase 1 : Core Intelligence Engine (PRIORITÉ 1)

### 1.1 Device Intelligence Engine
- [ ] Créer `src/core/device_intelligence.py`
  - [ ] Classe `DeviceIntelligenceEngine`
  - [ ] Méthode `merge_device_data()` (fusion multi-sources)
  - [ ] Méthode `detect_changes()` (détection changements)
  - [ ] Méthode `calculate_confidence()` (score fiabilité)
  - [ ] Méthode `detect_conflicts()` (conflits IP/MAC)
  - [ ] Méthode `calculate_uptime()` (stats disponibilité)

**Estimation** : 2h  
**Dépendances** : Aucune  
**Tests** : `test_device_intelligence.py`

### 1.2 Multi-Source Scanner
- [ ] Créer `src/features/network/multi_source_scanner.py`
  - [ ] Classe `MultiSourceScanner`
  - [ ] `scan_all_sources()` (parallèle : nmap, ARP, mDNS, Freebox)
  - [ ] `scan_nmap()` (scan nmap amélioré)
  - [ ] `scan_arp()` (cache ARP local)
  - [ ] `scan_mdns()` (Bonjour/mDNS)
  - [ ] `scan_netbios()` (hostnames Windows)
  - [ ] `enrich_device_data()` (enrichissement)
  - [ ] Intégration avec `DeviceIntelligenceEngine`

**Estimation** : 2h  
**Dépendances** : 1.1  
**Tests** : `test_multi_source_scanner.py`

### 1.3 Unified Device Model
- [ ] Créer `src/core/models/unified_device.py`
  - [ ] Classe `UnifiedDevice` (modèle complet)
  - [ ] Classe `IPChange` (historique IP)
  - [ ] Classe `OnlinePeriod` (périodes en ligne)
  - [ ] Classe `DeviceCapabilities` (capacités détectées)
  - [ ] Méthodes de sérialisation/désérialisation

**Estimation** : 1h  
**Dépendances** : Aucune  
**Tests** : `test_unified_device.py`

---

## 🟠 Phase 2 : Freebox API Integration (PRIORITÉ 2)

### 2.1 Freebox API Client
- [ ] Créer `src/features/freebox/__init__.py`
- [ ] Créer `src/features/freebox/api.py`
  - [ ] Classe `FreeboxAPI`
  - [ ] `authenticate()` (flow OAuth avec app token)
  - [ ] `get_dhcp_leases()` (baux DHCP actifs)
  - [ ] `get_lan_devices()` (devices LAN)
  - [ ] `get_connection_stats()` (stats WAN)
  - [ ] `get_wifi_devices()` (devices Wi-Fi)
  - [ ] Gestion refresh token automatique
  - [ ] Rate limiting (1 req/sec)

**Estimation** : 3h  
**Dépendances** : Aucune  
**Tests** : `test_freebox_api.py`  
**Doc** : `docs/FREEBOX_INTEGRATION.md`

### 2.2 Freebox Data Models
- [ ] Créer `src/features/freebox/models.py`
  - [ ] Classe `DHCPLease` (bail DHCP)
  - [ ] Classe `FreeboxDevice` (device Freebox)
  - [ ] Classe `ConnectionStats` (stats connexion)
  - [ ] Classe `WifiDevice` (device Wi-Fi)

**Estimation** : 1h  
**Dépendances** : 2.1  
**Tests** : Inclus dans 2.1

### 2.3 Freebox Integration Service
- [ ] Créer `src/features/freebox/integration_service.py`
  - [ ] Classe `FreeboxIntegrationService`
  - [ ] `sync_dhcp_leases()` (sync baux DHCP)
  - [ ] `sync_lan_devices()` (sync devices LAN)
  - [ ] `merge_with_unified_devices()` (fusion avec UnifiedDevice)
  - [ ] Cache des données (5 min)

**Estimation** : 2h  
**Dépendances** : 2.1, 2.2, 1.3  
**Tests** : `test_freebox_integration.py`

---

## 🟡 Phase 3 : Monitoring Continu (PRIORITÉ 3)

### 3.1 Monitoring Service
- [ ] Créer `src/features/network/monitoring_service.py`
  - [ ] Classe `NetworkMonitoringService`
  - [ ] `start_monitoring()` (background task asyncio)
  - [ ] `stop_monitoring()` (arrêt propre)
  - [ ] `scan_cycle()` (cycle de scan complet)
  - [ ] `detect_changes()` (comparaison scans)
  - [ ] Configuration interval (1-30 min)
  - [ ] Statistiques monitoring (uptime, latence)

**Estimation** : 2h  
**Dépendances** : 1.1, 1.2  
**Tests** : `test_monitoring_service.py`

### 3.2 Alert Manager
- [ ] Créer `src/features/network/alert_manager.py`
  - [ ] Classe `NetworkAlertManager`
  - [ ] Types d'alertes (NEW_DEVICE, DEVICE_OFFLINE, IP_CHANGED, etc.)
  - [ ] `create_alert()` (création alerte)
  - [ ] `get_active_alerts()` (alertes actives)
  - [ ] `resolve_alert()` (résolution)
  - [ ] `notify()` (notifications : console, file, webhook)
  - [ ] Stockage `alerts_history.json`

**Estimation** : 2h  
**Dépendances** : 3.1  
**Tests** : `test_alert_manager.py`

### 3.3 Alert Models
- [ ] Créer `src/features/network/alert_models.py`
  - [ ] Enum `AlertType`
  - [ ] Enum `Severity`
  - [ ] Classe `NetworkAlert`
  - [ ] Classe `AlertNotification`

**Estimation** : 30min  
**Dépendances** : Aucune  
**Tests** : Inclus dans 3.2

---

## 🟢 Phase 4 : API Endpoints (PRIORITÉ 4)

### 4.1 Unified API Router
- [ ] Créer `src/features/unified/__init__.py`
- [ ] Créer `src/features/unified/router.py`
  - [ ] GET `/api/unified/devices` (liste complète)
  - [ ] GET `/api/unified/devices/{mac}` (détails device)
  - [ ] GET `/api/unified/devices/{mac}/history` (historique)
  - [ ] GET `/api/unified/stats` (stats globales)
  - [ ] Intégration avec `DeviceIntelligenceEngine`

**Estimation** : 1h  
**Dépendances** : 1.1, 1.3  
**Tests** : `test_unified_router.py`

### 4.2 Monitoring API Router
- [ ] Ajouter dans `src/features/network/router.py`
  - [ ] GET `/api/network/monitoring/status`
  - [ ] POST `/api/network/monitoring/start`
  - [ ] POST `/api/network/monitoring/stop`
  - [ ] GET `/api/network/monitoring/stats`

**Estimation** : 1h  
**Dépendances** : 3.1  
**Tests** : Inclus dans network router tests

### 4.3 Alerts API Router
- [ ] Créer `src/features/network/alerts_router.py`
  - [ ] GET `/api/network/alerts` (liste)
  - [ ] GET `/api/network/alerts/{id}` (détails)
  - [ ] POST `/api/network/alerts/{id}/resolve`
  - [ ] DELETE `/api/network/alerts/{id}`

**Estimation** : 1h  
**Dépendances** : 3.2  
**Tests** : `test_alerts_router.py`

### 4.4 Freebox API Router
- [ ] Créer `src/features/freebox/router.py`
  - [ ] GET `/api/freebox/status`
  - [ ] GET `/api/freebox/dhcp`
  - [ ] GET `/api/freebox/devices`
  - [ ] POST `/api/freebox/sync`
  - [ ] POST `/api/freebox/configure` (setup initial)

**Estimation** : 1h  
**Dépendances** : 2.1, 2.3  
**Tests** : `test_freebox_router.py`

### 4.5 Reports API Router
- [ ] Créer `src/features/reports/__init__.py`
- [ ] Créer `src/features/reports/router.py`
  - [ ] GET `/api/reports/summary`
  - [ ] GET `/api/reports/devices/{mac}/report`
  - [ ] GET `/api/reports/export` (CSV/JSON)
  - [ ] POST `/api/reports/generate` (rapport custom)

**Estimation** : 2h  
**Dépendances** : 4.1  
**Tests** : `test_reports_router.py`

---

## 🔵 Phase 5 : Interface Frontend Professionnelle (PRIORITÉ 5)

### 5.1 Network Pro Module
- [ ] Refondre `web/static/js/modules/network-module.js`
  - [ ] DataTables integration (tri, filtre, pagination)
  - [ ] Vue liste professionnelle
  - [ ] Filtres avancés (status, type, subnet)
  - [ ] Actions groupées (export, scan multiple)
  - [ ] Vue détails expandable
  - [ ] Graphes par device (Chart.js)

**Estimation** : 3h  
**Dépendances** : 4.1  
**Tests** : Tests manuels UI

### 5.2 Device Details Page
- [ ] Créer `web/static/js/modules/device-details-module.js`
  - [ ] Page dédiée par device (/device/{mac})
  - [ ] Informations complètes
  - [ ] Graphe d'uptime (30 jours)
  - [ ] Historique IP/hostname (timeline)
  - [ ] Timeline événements
  - [ ] Alertes associées
  - [ ] Actions rapides (ping, wake, scan ports)

**Estimation** : 2h  
**Dépendances** : 4.1  
**Tests** : Tests manuels UI

### 5.3 Monitoring Dashboard
- [ ] Créer `web/static/js/modules/monitoring-dashboard-module.js`
  - [ ] Widgets temps réel
  - [ ] Graphe disponibilité réseau
  - [ ] Liste événements récents
  - [ ] Alertes actives (avec compteur)
  - [ ] Stats réseau (devices online, nouveaux, disparus)
  - [ ] Auto-refresh (5 sec)

**Estimation** : 2h  
**Dépendances** : 4.2, 4.3  
**Tests** : Tests manuels UI

### 5.4 Alerts Center
- [ ] Créer `web/static/js/modules/alerts-module.js`
  - [ ] Liste alertes avec filtres
  - [ ] Détails alerte (modal)
  - [ ] Résolution rapide
  - [ ] Historique alertes
  - [ ] Notifications toast (temps réel)

**Estimation** : 2h  
**Dépendances** : 4.3  
**Tests** : Tests manuels UI

### 5.5 Freebox Settings Page
- [ ] Créer `web/static/js/modules/freebox-module.js`
  - [ ] Configuration API Freebox
  - [ ] Test connexion
  - [ ] Sync manuelle
  - [ ] Affichage baux DHCP
  - [ ] Stats connexion WAN

**Estimation** : 1h  
**Dépendances** : 4.4  
**Tests** : Tests manuels UI

### 5.6 Professional CSS Theme
- [ ] Créer `web/static/css/network-pro.css`
  - [ ] Thème sombre professionnel
  - [ ] Tables professionnelles
  - [ ] Badges/labels modernes
  - [ ] Animations subtiles
  - [ ] Responsive design

**Estimation** : 2h  
**Dépendances** : Aucune  
**Tests** : Tests visuels

---

## 📚 Phase 6 : Documentation & Tests (PRIORITÉ 6)

### 6.1 Documentation Architecture
- [x] `docs/NETWORK_PRO_ARCHITECTURE.md` (fait)
- [ ] `docs/FREEBOX_INTEGRATION.md`
  - [ ] Guide d'installation
  - [ ] Configuration app token
  - [ ] Endpoints utilisés
  - [ ] Troubleshooting

**Estimation** : 1h

### 6.2 Documentation API
- [ ] `docs/API_ENDPOINTS.md`
  - [ ] Liste complète des endpoints
  - [ ] Schémas request/response
  - [ ] Exemples curl
  - [ ] Codes d'erreur

**Estimation** : 1h

### 6.3 Guide Utilisateur
- [ ] `docs/USER_GUIDE.md`
  - [ ] Installation & setup
  - [ ] Configuration Freebox
  - [ ] Utilisation interface
  - [ ] Gestion alertes
  - [ ] FAQ

**Estimation** : 1h

### 6.4 Tests Unitaires
- [ ] Tests tous les modules créés
  - [ ] `test_device_intelligence.py`
  - [ ] `test_multi_source_scanner.py`
  - [ ] `test_freebox_api.py`
  - [ ] `test_monitoring_service.py`
  - [ ] `test_alert_manager.py`
  - [ ] Coverage >80%

**Estimation** : 3h

### 6.5 Mise à jour RULES.md Compliance
- [ ] Vérifier conformité RULES.md
- [ ] Mettre à jour documentation
- [ ] Vérifier structure fichiers
- [ ] Vérifier conventions nommage

**Estimation** : 30min

---

## ⚡ Actions Immédiates (Prochaine Session)

### Session 1 : Core Engine (2-3h)
1. Créer `DeviceIntelligenceEngine`
2. Créer `UnifiedDevice` model
3. Créer `MultiSourceScanner`
4. Tests de base

### Session 2 : Freebox Integration (3h)
1. Créer `FreeboxAPI` client
2. Tester authentification
3. Récupérer baux DHCP
4. Integration avec unified devices

### Session 3 : Monitoring (2h)
1. Créer `NetworkMonitoringService`
2. Background task asyncio
3. Détection changements
4. Créer `AlertManager`

### Session 4 : API (2h)
1. Unified router
2. Monitoring endpoints
3. Alerts endpoints
4. Freebox endpoints

### Session 5 : Frontend (4h)
1. Refonte Network module
2. Device details page
3. Monitoring dashboard
4. Alerts center

### Session 6 : Finition (2h)
1. Tests complets
2. Documentation
3. Polissage UI
4. RULES.md compliance

**Total estimé : 15-17 heures**

---

## 📊 Checklist Globale

- [ ] **Phase 1** : Core Intelligence Engine (5h)
- [ ] **Phase 2** : Freebox API Integration (6h)
- [ ] **Phase 3** : Monitoring Continu (4.5h)
- [ ] **Phase 4** : API Endpoints (6h)
- [ ] **Phase 5** : Interface Frontend Pro (12h)
- [ ] **Phase 6** : Documentation & Tests (6.5h)

**Total : ~40 heures de développement**

---

## 🎯 Critères de Succès

- [ ] Tracking MAC intelligent fonctionne
- [ ] Multi-sources (3+ sources actives)
- [ ] Freebox API intégrée et fonctionnelle
- [ ] Monitoring automatique en background
- [ ] Système d'alertes avec 5+ types
- [ ] Interface professionnelle (graphes, timeline)
- [ ] Documentation complète (architecture + API + user guide)
- [ ] Tests unitaires >80% coverage
- [ ] RULES.md compliant à 100%
- [ ] Performance : scan complet <10 secondes
- [ ] Utilisable en production

---

**Prêt à démarrer ? Commençons par la Phase 1 : Core Intelligence Engine** 🚀
