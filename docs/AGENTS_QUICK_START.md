# 333HOME Agents - Quick Start Guide

## 📦 Installation Agent

### Windows

```powershell
# 1. Créer dossier agent
New-Item -ItemType Directory -Force -Path "C:\333home-agent"
cd C:\333home-agent

# 2. Télécharger package depuis Hub
Invoke-WebRequest -Uri "http://HUB_IP:8000/static/agents/agent_v1.0.0.zip" -OutFile "agent_v1.0.0.zip"

# 3. Extraire
Expand-Archive -Path "agent_v1.0.0.zip" -DestinationPath "." -Force

# 4. Installer dépendances
pip install -r requirements.txt

# 5. Lancer agent
python agent.py --agent-id VOTRE_ID --hub-url ws://HUB_IP:8000/api/agents/ws/agents
```

### Linux

```bash
# 1. Créer dossier agent
mkdir -p ~/333home-agent
cd ~/333home-agent

# 2. Télécharger package depuis Hub
curl -O http://HUB_IP:8000/static/agents/agent_v1.0.0.zip

# 3. Extraire
unzip agent_v1.0.0.zip

# 4. Installer dépendances
pip3 install -r requirements.txt

# 5. Lancer agent
python3 agent.py --agent-id VOTRE_ID --hub-url ws://HUB_IP:8000/api/agents/ws/agents
```

## ⚙️ Configuration

### Arguments CLI

```bash
python agent.py [OPTIONS]

Options:
  --agent-id TEXT       ID unique de l'agent (ex: TITO, 333srv)
  --hub-url TEXT        URL WebSocket du Hub
                        Format: ws://IP:PORT/api/agents/ws/agents
  --log-level TEXT      Niveau de log (DEBUG, INFO, WARNING, ERROR)
                        [default: INFO]
```

### Variables d'environnement

```bash
# Alternative aux arguments CLI
export AGENT_ID="TITO"
export HUB_URL="ws://192.168.1.150:8000/api/agents/ws/agents"
export LOG_LEVEL="INFO"

python agent.py
```

## 🌐 URLs WebSocket

### ⚠️ URL CORRECTE

```
ws://HUB_IP:8000/api/agents/ws/agents?agent_id=YOUR_ID
```

**Exemples:**
- Réseau local: `ws://192.168.1.150:8000/api/agents/ws/agents`
- Tailscale VPN: `ws://100.115.207.11:8000/api/agents/ws/agents`

### ❌ URLs INCORRECTES (retournent 403)

```
ws://HUB_IP:8000/api/ws/agents           # ❌ Mauvais path
ws://HUB_IP:8000/agents/ws/agents        # ❌ Prefix manquant
```

## 🔌 Test de Connexion

### 1. Vérifier Hub accessible

```bash
# Ping Hub
ping HUB_IP

# Test HTTP
curl http://HUB_IP:8000/api/agents

# Test téléchargement package
curl -I http://HUB_IP:8000/static/agents/agent_v1.0.0.zip
```

### 2. Lancer agent en mode debug

```bash
python agent.py \
  --agent-id TEST \
  --hub-url ws://HUB_IP:8000/api/agents/ws/agents \
  --log-level DEBUG
```

### 3. Logs de connexion réussie

```
2025-10-30 14:04:25 - __main__ - INFO - Connecting to Hub: ws://100.115.207.11:8000/api/agents/ws/agents?agent_id=TITO
2025-10-30 14:04:25 - __main__ - INFO - ✓ Connected to Hub
2025-10-30 14:04:25 - __main__ - INFO - ✓ Handshake sent
```

### 4. Vérifier depuis Hub

```bash
# Liste agents connectés
curl http://HUB_IP:8000/api/agents | jq

# Statut agent spécifique
curl http://HUB_IP:8000/api/agents/TITO/status | jq

# Logs agent
curl "http://HUB_IP:8000/api/agents/TITO/logs?limit=50" | jq
```

## 🔧 Troubleshooting

### Erreur 403 Forbidden

**Symptôme:**
```
ERROR - Connection error: server rejected WebSocket connection: HTTP 403
```

**Solutions:**
1. Vérifier URL WebSocket correcte: `/api/agents/ws/agents`
2. Vérifier agent_id dans query params: `?agent_id=YOUR_ID`
3. Vérifier firewall Hub (port 8000)

### Erreur 404 Not Found

**Symptôme:**
```
ERROR - Connection error: server rejected WebSocket connection: HTTP 404
```

**Solutions:**
1. Vérifier Hub démarré: `ps aux | grep uvicorn`
2. Vérifier router agents monté dans logs Hub
3. Tester endpoint REST: `curl http://HUB_IP:8000/api/agents`

### Plugins ne chargent pas

**Symptôme:**
```
WARNING - Could not import module src.agents.plugins.common: No module named 'src'
INFO - Loaded 0 plugins: []
```

**Solution:**
- Package v1.0.0 a des imports absolus incompatibles
- Attendre v1.0.1 avec imports relatifs corrigés
- Ou modifier manuellement `plugins/__init__.py`

### Unicode errors Windows

**Symptôme:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f916'
```

**Info:**
- Erreur non-bloquante (PowerShell cp1252)
- N'empêche pas la connexion
- Logs fonctionnent quand même

## 📊 API Endpoints

### Liste agents connectés

```bash
GET /api/agents

Response:
{
  "TITO": {
    "agent_id": "TITO",
    "hostname": "TiTo",
    "platform": "windows",
    "python_version": "3.14.0",
    "connected_at": "2025-10-30T14:04:25.230Z",
    "last_heartbeat": "2025-10-30T14:05:15.123Z",
    "uptime_seconds": 50,
    "plugins": []
  }
}
```

### Statut agent spécifique

```bash
GET /api/agents/{agent_id}/status
```

### Plugins disponibles

```bash
GET /api/agents/{agent_id}/plugins
```

### Logs agent

```bash
GET /api/agents/{agent_id}/logs?limit=50&level=INFO
```

### Envoyer tâche

```bash
POST /api/agents/{agent_id}/tasks

Body:
{
  "plugin": "system_info",
  "params": {}
}
```

## 🚀 Prochaines Étapes

1. ✅ Connexion WebSocket établie
2. ⏳ Corriger imports plugins (v1.0.1)
3. ⏳ Tester plugin system_info
4. ⏳ Tester plugin logmein_rescue
5. ⏳ Tester auto-update workflow

---

**Version:** 1.0.0  
**Date:** 2025-10-30  
**Statut:** Connexion WebSocket validée ✅
