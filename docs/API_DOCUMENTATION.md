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
**🔄 Version :** 2.0.0 (Architecture modulaire)  
**📖 Statut :** Documentation complète et à jour