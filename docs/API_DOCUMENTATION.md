# 📚 Documentation API 333HOME

## 🎯 Objectif
Documentation complète de l'API REST 333HOME avec tous les endpoints, paramètres et exemples de réponses.

## 🌐 Base URL
```
http://localhost:8000
```

## 📊 Vue d'Ensemble des Endpoints

### 📱 Devices API (7 endpoints)
- **Gestion** : CRUD complet des appareils
- **Contrôle** : Wake-on-LAN, refresh statuts
- **Monitoring** : Statuts VPN temps réel

### 🌐 Network API (15 endpoints)
- **Scanning** : Découverte réseau automatique
- **Analyse** : Topologie, historique, statistiques
- **Tests** : Ping, connectivité, performance

### 🔒 Tailscale API (12 endpoints)
- **Configuration** : Setup VPN Tailscale
- **Monitoring** : Statuts appareils VPN
- **Debug** : Tests connexion, logs

### 📊 Monitoring API (7 endpoints)
- **Métriques** : Performance, santé système
- **Surveillance** : Activité, benchmarks
- **Maintenance** : Cache, nettoyage

### 🔧 System API (6 endpoints)
- **Administration** : Arrêt, redémarrage système
- **Information** : Statut, logs, Raspberry Pi
- **Tests** : Ping, connectivité

### 📁 Static API (3 endpoints)
- **Pages Web** : Interface principale, debug, test

### 🤖 Agents API (8 endpoints)
- **Gestion** : Liste, détails, logs agents connectés
- **Contrôle** : Restart, update automatique
- **Tasks** : Exécution plugins, résultats temps réel
- **Monitoring** : WebSocket, statuts, versions

---

## 📱 Devices API

### GET /api/devices/
**Description** : Liste complète des appareils avec statut VPN
```json
{
  "devices": [
    {
      "id": "device_001",
      "name": "PC-Salon",
      "ip": "192.168.1.100",
      "ip_secondary": "100.64.0.10",
      "mac": "aa:bb:cc:dd:ee:ff",
      "device_type": "computer",
      "is_favorite": true,
      "is_vpn": true,
      "wake_on_lan": true,
      "vpn_status": {
        "status": "online",
        "response_time": 45,
        "last_check": "2025-10-19T10:30:00"
      }
    }
  ],
  "total": 5,
  "vpn_count": 2
}
```

### GET /api/devices/{device_id}
**Description** : Détails d'un appareil spécifique
**Paramètres** :
- `device_id` (string) : Identifiant unique de l'appareil

**Réponse** :
```json
{
  "id": "device_001",
  "name": "PC-Salon",
  "ip": "192.168.1.100",
  "ip_secondary": "100.64.0.10",
  "mac": "aa:bb:cc:dd:ee:ff",
  "device_type": "computer",
  "is_favorite": true,
  "is_vpn": true,
  "wake_on_lan": true,
  "vpn_status": {
    "status": "online",
    "response_time": 45,
    "last_check": "2025-10-19T10:30:00"
  }
}
```

### PUT /api/devices/{device_id}
**Description** : Mise à jour d'un appareil
**Body** :
```json
{
  "name": "Nouveau nom",
  "ip_secondary": "100.64.0.15",
  "is_vpn": true,
  "is_favorite": false
}
```

### POST /api/devices/wake
**Description** : Wake-on-LAN pour démarrer un appareil
**Body** :
```json
{
  "device_id": "device_001"
}
```

### POST /api/devices/refresh
**Description** : Actualisation du statut de tous les appareils
**Réponse** :
```json
{
  "message": "Actualisation en cours",
  "device_count": 5,
  "timestamp": "refresh_initiated"
}
```

---

## 🌐 Network API

### GET /api/network/scan
**Description** : Dernier scan réseau stocké
```json
{
  "scan": {
    "timestamp": "2025-10-19T10:00:00",
    "target": "192.168.1.0/24",
    "devices": [
      {
        "ip": "192.168.1.100",
        "hostname": "PC-Salon",
        "mac": "aa:bb:cc:dd:ee:ff",
        "open_ports": [22, 80, 443],
        "is_known": true
      }
    ],
    "scan_duration": "15.30s"
  },
  "devices_found": 8
}
```

### POST /api/network/scan
**Description** : Lancer un nouveau scan réseau
**Body** :
```json
{
  "target": "192.168.1.0/24",
  "ports": [22, 80, 443, 8080],
  "fast": true
}
```

### GET /api/network/analyze
**Description** : Analyse approfondie du réseau
```json
{
  "scan_info": {
    "timestamp": "2025-10-19T10:00:00",
    "devices_found": 8
  },
  "device_analysis": {
    "known_devices": 5,
    "discovered_devices": 8,
    "known_online": 4,
    "unknown_devices": 3
  },
  "new_devices": [
    {
      "ip": "192.168.1.200",
      "hostname": "Unknown-Device",
      "mac": "ff:ee:dd:cc:bb:aa"
    }
  ]
}
```

### GET /api/network/topology
**Description** : Topologie et cartographie réseau
```json
{
  "subnets": {
    "192.168.1.0/24": [
      {
        "ip": "192.168.1.100",
        "hostname": "PC-Salon",
        "ports": [22, 80]
      }
    ]
  },
  "device_types": {
    "computer": 3,
    "mobile": 2,
    "server": 1
  }
}
```

---

## 🔒 Tailscale API

### GET /api/tailscale/config
**Description** : Configuration Tailscale (clé API masquée)
```json
{
  "config": {
    "tailnet": "mon-tailnet.ts.net",
    "api_key": "***"
  },
  "is_configured": true
}
```

### POST /api/tailscale/config
**Description** : Mise à jour configuration Tailscale
**Body** :
```json
{
  "tailnet": "mon-tailnet.ts.net",
  "api_key": "tskey-auth-xxxxx"
}
```

### GET /api/tailscale/devices
**Description** : Liste des appareils Tailscale
```json
{
  "devices": [
    {
      "id": "device_tailscale_001",
      "name": "PC-Remote",
      "addresses": ["100.64.0.10"],
      "online": true,
      "os": "linux",
      "lastSeen": "2025-10-19T10:25:00"
    }
  ],
  "stats": {
    "total": 3,
    "online": 2,
    "offline": 1
  }
}
```

### GET /api/tailscale/network-map
**Description** : Cartographie du réseau Tailscale
```json
{
  "network_map": {
    "nodes": [
      {
        "id": "device_001",
        "name": "PC-Remote",
        "addresses": ["100.64.0.10"],
        "online": true
      }
    ],
    "subnets": ["100.64.0.0/24"],
    "exit_nodes": ["PC-Gateway"],
    "relay_nodes": []
  },
  "summary": {
    "total_nodes": 3,
    "online_nodes": 2,
    "subnets_count": 1
  }
}
```

---

## 📊 Monitoring API

### GET /api/monitoring/stats
**Description** : Statistiques de monitoring globales
```json
{
  "devices": {
    "total": 5,
    "favorites": 2,
    "vpn_enabled": 3,
    "by_type": {
      "computer": 3,
      "mobile": 2
    }
  },
  "network": {
    "last_scan_devices": 8,
    "last_scan_time": "2025-10-19T10:00:00",
    "history_scans": 12
  },
  "tailscale": {
    "configured": true,
    "device_count": 3,
    "online_count": 2
  }
}
```

### GET /api/monitoring/health
**Description** : Vérification de santé du système
```json
{
  "overall": "healthy",
  "components": {
    "device_manager": {
      "status": "healthy",
      "info": "5 appareils chargés"
    },
    "scan_storage": {
      "status": "healthy",
      "info": "Dernier scan: 2025-10-19T10:00:00"
    },
    "tailscale_service": {
      "status": "healthy",
      "info": "Configuré"
    }
  }
}
```

### GET /api/monitoring/performance
**Description** : Métriques de performance
```json
{
  "system": {
    "cpu_percent": 25.3,
    "memory_percent": 45.2,
    "memory_available_gb": 2.1,
    "disk_percent": 62.8,
    "disk_free_gb": 24.5
  },
  "application": {
    "devices_loaded": 5,
    "last_scan_age_minutes": 15.3
  }
}
```

---

## 🔧 System API

### GET /api/system/status
**Description** : Statut global du système
```json
{
  "status": "online",
  "timestamp": "2025-10-19T10:30:00",
  "python_version": "3.9.2",
  "platform": "posix",
  "memory": {
    "total": 4294967296,
    "available": 2147483648,
    "percent": 50.0
  },
  "disk": {
    "total": 32000000000,
    "free": 12000000000,
    "percent": 62.5
  }
}
```

### GET /api/system/raspberry
**Description** : Informations spécifiques Raspberry Pi
```json
{
  "is_raspberry": true,
  "cpu_temp": "45.2°C",
  "gpu_version": "GPU firmware version",
  "model": "Raspberry Pi 5 Model B Rev 1.0"
}
```

### POST /api/system/shutdown
**Description** : Arrêt sécurisé du système
```json
{
  "status": "shutdown_initiated",
  "message": "Arrêt système en cours..."
}
```

---

## 📁 Static API

### GET /
**Description** : Page d'accueil principale
**Réponse** : Fichier HTML index.html

### GET /debug
**Description** : Page de debug
**Réponse** : Fichier HTML debug.html

### GET /test-api
**Description** : Page de test API
**Réponse** : Fichier HTML test-api.html

---

## 🚨 Codes d'Erreur

### Codes HTTP Standards
- **200** : Succès
- **400** : Requête invalide
- **404** : Ressource non trouvée
- **500** : Erreur serveur interne

### Exemples de Réponses d'Erreur
```json
{
  "detail": "Appareil non trouvé"
}
```

```json
{
  "detail": "Tailscale non configuré"
}
```

## 🔧 Headers Recommandés

### Requêtes
```
Content-Type: application/json
Accept: application/json
```

### Réponses
```
Content-Type: application/json
Access-Control-Allow-Origin: *
```

---

## 🤖 Agents API

### Vue d'Ensemble
API pour la gestion des agents 333HOME connectés via WebSocket. Permet le contrôle à distance, les mises à jour automatiques et l'exécution de tâches.

**Base Path** : `/api/agents`

### GET /api/agents
**Description** : Liste tous les agents connectés avec leurs métadonnées

**Réponse** :
```json
[
  {
    "agent_id": "TITO",
    "version": "1.0.37",
    "platform": "Windows-10-10.0.19045-SP0",
    "hostname": "TITO-PC",
    "python_version": "3.11.5",
    "plugins": ["self_update", "system_info", "system_restart", "logmein_rescue"],
    "connected_at": "2025-11-04T20:00:45.123456+00:00",
    "last_heartbeat": "2025-11-04T20:05:30.789012+00:00"
  }
]
```

**Codes d'état** :
- `200 OK` : Liste retournée avec succès
- `500 Internal Server Error` : Erreur serveur

**Exemple curl** :
```bash
curl http://localhost:8000/api/agents
```

---

### GET /api/agents/{agent_id}
**Description** : Détails complets d'un agent spécifique

**Paramètres** :
- `agent_id` (string, path) : Identifiant unique de l'agent

**Réponse** :
```json
{
  "agent_id": "TITO",
  "version": "1.0.37",
  "platform": "Windows-10-10.0.19045-SP0",
  "hostname": "TITO-PC",
  "python_version": "3.11.5",
  "plugins": ["self_update", "system_info", "system_restart", "logmein_rescue"],
  "connected_at": "2025-11-04T20:00:45.123456+00:00",
  "last_heartbeat": "2025-11-04T20:05:30.789012+00:00",
  "metadata": {
    "install_path": "C:\\Program Files\\333HOME Agent",
    "config_path": "C:\\Program Files\\333HOME Agent\\config.json",
    "startup_type": "tray"
  }
}
```

**Codes d'état** :
- `200 OK` : Agent trouvé
- `404 Not Found` : Agent non connecté
- `500 Internal Server Error` : Erreur serveur

**Exemple curl** :
```bash
curl http://localhost:8000/api/agents/TITO
```

---

### POST /api/agents/{agent_id}/restart
**Description** : Redémarre l'agent ou le système à distance (nouveau ✨)

**Paramètres** :
- `agent_id` (string, path) : Identifiant de l'agent
- `target` (string, query, optionnel) : Cible du restart
  - `"agent"` (défaut) : Redémarre seulement l'agent
  - `"system"` : Redémarre le système complet
- `delay` (integer, query, optionnel) : Délai avant restart en secondes
  - Plage : 0-300 secondes
  - Défaut : 5 secondes

**Réponse** :
```json
{
  "task_id": "57d5574c-d3bf-4921-9a30-5a65ec86df3d",
  "agent_id": "TITO",
  "plugin": "system_restart",
  "status": "pending",
  "created_at": "2025-11-04T19:40:48.235585+00:00",
  "message": "Agent restart scheduled in 5s"
}
```

**Codes d'état** :
- `200 OK` : Tâche créée avec succès
- `404 Not Found` : Agent non connecté
- `400 Bad Request` : Plugin system_restart non disponible ou paramètres invalides
- `500 Internal Server Error` : Erreur serveur

**Workflow** :
1. Hub envoie tâche `system_restart` à l'agent via WebSocket
2. Agent attend le délai configuré
3. Agent détecte présence watchdog tray
4. Agent fait `os._exit(0)` (watchdog relance automatiquement)
5. Agent reconnexion WebSocket (3-5 secondes)

**Exemples curl** :
```bash
# Restart agent (délai 5s par défaut)
curl -X POST http://localhost:8000/api/agents/TITO/restart

# Restart agent avec délai 10s
curl -X POST http://localhost:8000/api/agents/TITO/restart?delay=10

# Restart système complet avec délai 30s
curl -X POST http://localhost:8000/api/agents/TITO/restart?target=system&delay=30
```

---

### POST /api/agents/{agent_id}/update
**Description** : Met à jour l'agent vers une version spécifique ou la dernière (nouveau ✨)

**Paramètres** :
- `agent_id` (string, path) : Identifiant de l'agent
- `version` (string, query, optionnel) : Version cible (ex: "1.0.37")
  - Si omis : Auto-détection de la dernière version depuis `checksums.json`
- `force` (boolean, query, optionnel) : Force l'update même si déjà à jour
  - Défaut : `false`

**Réponse** :
```json
{
  "task_id": "c83066e0-ad96-4a15-bf83-f56283d21f26",
  "agent_id": "TITO",
  "plugin": "self_update",
  "status": "pending",
  "current_version": "1.0.35",
  "target_version": "1.0.37",
  "created_at": "2025-11-04T20:56:29.464000+00:00",
  "message": "Update from 1.0.35 to 1.0.37 initiated"
}
```

**Codes d'état** :
- `200 OK` : Tâche créée avec succès
- `404 Not Found` : Agent non connecté
- `400 Bad Request` : 
  - Agent déjà à jour (utiliser `force=true` pour forcer)
  - Plugin self_update non disponible
  - Version cible invalide ou introuvable
- `500 Internal Server Error` : Erreur serveur

**Workflow Auto-Update Complet** :
1. Hub lit `static/agents/checksums.json` (si version non spécifiée)
2. Hub compare `current_version` vs `target_version`
3. Hub génère URL : `http://localhost:8000/static/agents/agent_vX.X.X.zip`
4. Hub envoie tâche `self_update` à l'agent avec URL + checksum
5. Agent télécharge le package (vérification SHA256)
6. Agent crée backup : `.backup/agent_vX.X.X_YYYYMMDD_HHMMSS`
7. Agent extrait et remplace fichiers
8. Agent **redémarre automatiquement** (asyncio.create_task + watchdog)
9. Agent reconnexion avec nouvelle version (3-5 secondes)

**Exemples curl** :
```bash
# Update vers dernière version (auto-détection)
curl -X POST http://localhost:8000/api/agents/TITO/update

# Update vers version spécifique
curl -X POST 'http://localhost:8000/api/agents/TITO/update?version=1.0.37'

# Force update même si déjà à jour
curl -X POST 'http://localhost:8000/api/agents/TITO/update?force=true'
```

---

### POST /api/agents/{agent_id}/tasks/{plugin_name}
**Description** : Exécute une tâche plugin sur un agent

**Paramètres** :
- `agent_id` (string, path) : Identifiant de l'agent
- `plugin_name` (string, path) : Nom du plugin à exécuter
- `timeout` (integer, query, optionnel) : Timeout en secondes (défaut: 60)

**Body** :
```json
{
  "param1": "value1",
  "param2": "value2"
}
```

**Réponse** :
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "agent_id": "TITO",
  "plugin": "system_info",
  "status": "pending",
  "created_at": "2025-11-04T20:00:00.000000+00:00"
}
```

**Codes d'état** :
- `200 OK` : Tâche créée
- `404 Not Found` : Agent non connecté
- `500 Internal Server Error` : Erreur serveur

**Exemple curl** :
```bash
curl -X POST http://localhost:8000/api/agents/TITO/tasks/system_info \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

### GET /api/agents/tasks/{task_id}
**Description** : Récupère le résultat d'une tâche

**Paramètres** :
- `task_id` (string, path) : Identifiant unique de la tâche

**Réponse (pending)** :
```json
{
  "task_id": "57d5574c-d3bf-4921-9a30-5a65ec86df3d",
  "agent_id": "TITO",
  "plugin": "system_restart",
  "params": {
    "target": "agent",
    "delay": 5
  },
  "timeout": 60,
  "status": "pending",
  "created_at": "2025-11-04T19:40:48.235585+00:00",
  "result": null,
  "updated_at": "2025-11-04T19:40:48.285247+00:00"
}
```

**Réponse (success)** :
```json
{
  "task_id": "c83066e0-ad96-4a15-bf83-f56283d21f26",
  "agent_id": "TITO",
  "plugin": "self_update",
  "params": {
    "version": "1.0.37",
    "download_url": "http://localhost:8000/static/agents/agent_v1.0.37.zip",
    "checksum": "765becb2f678f628a2ebfa503b23d79988cb856150b8e4ad6d0bebf17a7d6b69",
    "force": false
  },
  "timeout": 300,
  "status": "success",
  "created_at": "2025-11-04T20:56:29.464000+00:00",
  "result": {
    "status": "success",
    "message": "Update to version 1.0.37 completed. Agent restarting...",
    "data": {
      "old_version": "1.0.35",
      "new_version": "1.0.37",
      "backup_path": "C:\\Program Files\\333HOME Agent\\.backup\\agent_v1.0.35_20251104_205629",
      "restart_required": false,
      "auto_restart": true
    }
  },
  "updated_at": "2025-11-04T20:56:42.983000+00:00"
}
```

**Réponse (error)** :
```json
{
  "task_id": "abc123...",
  "status": "error",
  "result": {
    "status": "error",
    "message": "Plugin execution failed",
    "error": "FileNotFoundError: [Errno 2] No such file or directory"
  }
}
```

**Statuts possibles** :
- `pending` : Tâche en attente d'exécution
- `acknowledged` : Tâche reçue par l'agent
- `success` : Tâche terminée avec succès
- `error` : Tâche échouée
- `timeout` : Tâche expirée

**Codes d'état** :
- `200 OK` : Tâche trouvée
- `404 Not Found` : Tâche introuvable
- `500 Internal Server Error` : Erreur serveur

**Exemple curl** :
```bash
curl http://localhost:8000/api/agents/tasks/57d5574c-d3bf-4921-9a30-5a65ec86df3d
```

---

### GET /api/agents/{agent_id}/logs
**Description** : Récupère les logs en temps réel d'un agent

**Paramètres** :
- `agent_id` (string, path) : Identifiant de l'agent
- `level` (string, query, optionnel) : Niveau de log minimum
  - Valeurs : `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
  - Défaut : `INFO`
- `limit` (integer, query, optionnel) : Nombre max de lignes
  - Défaut : 100

**Réponse** :
```json
{
  "agent_id": "TITO",
  "logs": [
    {
      "timestamp": "2025-11-04T20:56:29.465000+00:00",
      "level": "INFO",
      "logger": "plugin.self_update",
      "message": "[Update] Starting self-update to version 1.0.37"
    },
    {
      "timestamp": "2025-11-04T20:56:42.981000+00:00",
      "level": "INFO",
      "logger": "plugin.self_update",
      "message": "[Update] Update completed successfully!"
    }
  ],
  "total": 2
}
```

**Codes d'état** :
- `200 OK` : Logs récupérés
- `404 Not Found` : Agent non connecté
- `500 Internal Server Error` : Erreur serveur

**Exemple curl** :
```bash
# Logs INFO et supérieur (100 dernières lignes)
curl http://localhost:8000/api/agents/TITO/logs

# Logs ERROR seulement (50 dernières lignes)
curl 'http://localhost:8000/api/agents/TITO/logs?level=ERROR&limit=50'
```

---

### WebSocket /api/ws/agents
**Description** : Connexion WebSocket pour les agents

**Paramètres Query** :
- `agent_id` (string, required) : Identifiant unique de l'agent
- `token` (string, optional) : JWT token d'authentification

**URL Exemple** :
```
ws://localhost:8000/api/ws/agents?agent_id=TITO
```

**Messages Entrants (Hub → Agent)** :
```json
{
  "type": "task",
  "task_id": "abc123...",
  "plugin": "system_info",
  "params": {},
  "timeout": 60
}
```

**Messages Sortants (Agent → Hub)** :
```json
// Handshake
{
  "type": "handshake",
  "agent_id": "TITO",
  "version": "1.0.37",
  "platform": "Windows-10",
  "plugins": ["self_update", "system_restart"]
}

// Task acknowledgement
{
  "type": "task_ack",
  "task_id": "abc123..."
}

// Task result
{
  "type": "task_result",
  "task_id": "abc123...",
  "status": "success",
  "message": "Task completed",
  "data": {}
}

// Logs streaming
{
  "type": "log",
  "level": "INFO",
  "logger": "plugin.self_update",
  "message": "[Update] Downloading package...",
  "timestamp": "2025-11-04T20:56:30.000000+00:00"
}

// Heartbeat
{
  "type": "heartbeat",
  "timestamp": "2025-11-04T20:57:00.000000+00:00"
}
```

---

### Plugins Disponibles

#### self_update
**Description** : Mise à jour automatique de l'agent
**Paramètres** :
- `version` (string) : Version cible
- `download_url` (string) : URL du package
- `checksum` (string) : SHA256 du package
- `force` (boolean) : Force l'update

**Workflow** :
1. Download package (vérification checksum SHA256)
2. Backup version actuelle
3. Extract nouvelle version
4. Replace fichiers
5. Auto-restart agent (watchdog tray)

#### system_restart
**Description** : Redémarre l'agent ou le système
**Paramètres** :
- `target` (string) : `"agent"` ou `"system"`
- `delay` (integer) : Délai avant restart (0-300s)

**Workflow** :
1. Attente délai configuré
2. Détection watchdog tray (Windows) ou systemd (Linux)
3. Exit propre (`os._exit(0)`)
4. Watchdog relance automatiquement

#### system_info
**Description** : Informations système de l'agent
**Paramètres** : Aucun

**Retourne** :
- OS, version, architecture
- CPU, RAM, disque
- Réseau, interfaces
- Processus, uptime

#### logmein_rescue
**Description** : Contrôle LogMeIn Rescue
**Paramètres** :
- `action` (string) : `"start"` ou `"stop"`

---

## 📊 Pagination et Limites

### Limites par Défaut
- **Historique réseau** : 7 jours par défaut
- **Logs système** : 10 dernières entrées
- **Résultats scan** : Tous les appareils
- **Timeout requêtes** : 30 secondes

### Paramètres de Pagination
```
GET /api/network/history?days=30
GET /api/system/logs?limit=50
```

---

**📅 Documentation API créée :** 19 octobre 2025  
**🔄 Dernière mise à jour :** 4 novembre 2025 (Agents API v1.0.37)  
**🔄 Version :** 2.1.0 (Architecture modulaire + Agents auto-gérés)  
**📖 Statut :** Documentation complète et à jour