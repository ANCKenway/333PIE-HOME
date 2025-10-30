# 🤖 333HOME Agents - Architecture Complète

## 📋 Vue d'ensemble

Le système d'agents 333HOME permet de contrôler à distance les postes Windows et Linux depuis le Hub central (333PIE). Architecture **modulaire** et **extensible** via système de plugins.

---

## 🎯 Objectifs

### Phase 1: Windows (TITO) 🔥 PRIORITÉ
- **LogMeIn Rescue automation**: Code 6 chiffres → session active en <60s
- **UAC bypass**: Élévation admin automatique
- **Auto-accept**: Acceptation droits sans intervention manuelle

### Phase 2: Linux (333srv)
- **Console SSH web**: Terminal interactif (xterm.js)
- **VNC distant**: Accès GUI via noVNC
- **Gestionnaire fichiers**: Upload/download SFTP
- **Monitoring système**: CPU, RAM, Disk, Services

### Phase 3: Extensibilité
- **Architecture plugin**: Ajout facile nouvelles fonctionnalités
- **Multi-postes**: Support postes additionnels plug & play
- **Cross-platform**: Windows, Linux, macOS

---

## 🏗️ Architecture Globale

```
┌─────────────────────────────────────────────────────────────────┐
│                      333HOME HUB (333PIE)                        │
│                                                                   │
│  FastAPI App (app.py)                                            │
│  ├── API REST: /api/agents/*                                     │
│  │   ├── GET /agents                   (liste agents)            │
│  │   ├── POST /agents/{id}/tasks       (envoyer tâche)           │
│  │   ├── GET /agents/{id}/plugins      (liste plugins)           │
│  │   └── GET /agents/{id}/status       (statut agent)            │
│  │                                                                │
│  └── WebSocket: /ws/agents             (connexion agents)        │
│      ├── Handshake (authentification)                            │
│      ├── Heartbeat (30s keepalive)                               │
│      ├── Tasks (envoi tâches)                                    │
│      └── Results (réception résultats)                           │
└─────────────────────────────────────────────────────────────────┘
                              ↑ ↓
                     WebSocket Persistent
                  (wss://333pie.local:8000/ws/agents)
                              ↑ ↓
      ┌───────────────────────┴────────────────────────┐
      │                                                 │
┌─────▼──────────────┐                    ┌───────────▼──────────┐
│   AGENT WINDOWS    │                    │    AGENT LINUX       │
│      (TITO)        │                    │     (333srv)         │
│                    │                    │                      │
│  agent.py          │                    │  agent.py            │
│  ├── PluginManager │                    │  ├── PluginManager   │
│  ├── WebSocket     │                    │  ├── WebSocket       │
│  └── Heartbeat     │                    │  └── Heartbeat       │
│                    │                    │                      │
│  Plugins:          │                    │  Plugins:            │
│  ├── logmein_rescue│                    │  ├── ssh_console     │
│  ├── rdp (futur)   │                    │  ├── docker          │
│  ├── powershell    │                    │  ├── systemd         │
│  └── system_info   │                    │  └── system_info     │
│                    │                    │                      │
│  192.168.1.174     │                    │  192.168.1.175       │
│  100.93.236.71     │                    │  100.80.31.55        │
└────────────────────┘                    └──────────────────────┘
```

---

## 📁 Structure Fichiers

```
333HOME/
├── app.py                              # FastAPI app (Hub)
├── src/
│   ├── agents/                         # 🤖 MODULE AGENTS
│   │   ├── __init__.py
│   │   ├── README.md                   # Documentation module
│   │   ├── agent.py                    # ⭐ Agent universel
│   │   ├── config.py                   # Configuration agents
│   │   ├── requirements.txt            # Dépendances agents
│   │   │
│   │   ├── plugins/                    # 🔌 SYSTÈME PLUGINS
│   │   │   ├── __init__.py             # PluginManager
│   │   │   ├── base.py                 # BasePlugin abstract
│   │   │   │
│   │   │   ├── windows/                # 🪟 Plugins Windows
│   │   │   │   ├── __init__.py
│   │   │   │   ├── logmein_rescue.py   # ⭐ LogMeIn automation
│   │   │   │   ├── rdp.py              # (futur)
│   │   │   │   └── powershell.py       # (futur)
│   │   │   │
│   │   │   ├── linux/                  # 🐧 Plugins Linux
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ssh_console.py      # (Phase 2)
│   │   │   │   ├── docker.py           # (Phase 2)
│   │   │   │   └── systemd.py          # (Phase 2)
│   │   │   │
│   │   │   └── common/                 # 🌐 Cross-platform
│   │   │       ├── __init__.py
│   │   │       └── system_info.py      # ⭐ Plugin test
│   │   │
│   │   └── deployments/                # 📦 Déploiement
│   │       ├── windows/
│   │       │   ├── install.ps1         # Installation TITO
│   │       │   └── agent-service.xml   # Service Windows
│   │       └── linux/
│   │           ├── install.sh          # Installation 333srv
│   │           └── agent.service       # Systemd service
│   │
│   └── features/
│       └── agents/                     # API Hub côté 333PIE
│           ├── __init__.py
│           └── routers/
│               ├── __init__.py
│               └── agents_router.py    # ⭐ Routes API + WebSocket
│
└── docs/
    ├── AGENTS_ARCHITECTURE.md          # ⭐ Ce fichier
    ├── AGENTS_DEPLOYMENT.md            # Guide déploiement
    └── PLUGIN_DEVELOPMENT.md           # Guide création plugins
```

---

## 🔌 Système de Plugins

### Classe de Base

Tous les plugins héritent de `BasePlugin` :

```python
from src.agents.plugins.base import BasePlugin, PluginParams, PluginResult

class MyPlugin(BasePlugin):
    """Mon plugin custom."""
    
    # Métadonnées
    name = "my_plugin"
    description = "Description du plugin"
    version = "1.0.0"
    os_platform = "windows"  # "windows", "linux", "darwin", ou "all"
    
    async def execute(self, params: PluginParams) -> PluginResult:
        """Logique principale du plugin."""
        # ... implémentation ...
        return PluginResult(
            status="success",
            message="Plugin executed successfully",
            data={"key": "value"}
        )
    
    def validate_params(self, params: dict) -> bool:
        """Validation des paramètres."""
        try:
            MyPluginParams(**params)
            return True
        except:
            return False
    
    def get_schema(self) -> dict:
        """Schéma JSON des paramètres."""
        return MyPluginParams.schema()
```

### Plugins Disponibles

#### 🪟 Windows

| Plugin | Description | Statut | Priorité |
|--------|-------------|--------|----------|
| `logmein_rescue` | Automation LogMeIn Rescue complète | ✅ Phase 1 | 🔴 CRITIQUE |
| `rdp` | Remote Desktop Protocol | 📅 Futur | 🟡 Basse |
| `powershell` | Exécution scripts PowerShell | 📅 Futur | 🟡 Basse |

#### 🐧 Linux

| Plugin | Description | Statut | Priorité |
|--------|-------------|--------|----------|
| `ssh_console` | Terminal SSH interactif (xterm.js) | 📅 Phase 2 | 🟠 Haute |
| `docker` | Contrôle containers Docker | 📅 Phase 2 | 🟡 Moyenne |
| `systemd` | Gestion services systemd | 📅 Phase 2 | 🟡 Moyenne |
| `vnc` | Accès GUI via VNC/noVNC | 📅 Phase 2 | 🟠 Haute |

#### 🌐 Cross-platform

| Plugin | Description | Statut | Priorité |
|--------|-------------|--------|----------|
| `system_info` | Collecte info système (CPU/RAM/Disk) | ✅ Complet | 🟢 Test |
| `self_update` | Auto-mise à jour agent depuis Hub | ✅ Complet | 🔴 CRITIQUE |

---

## 🔄 Auto-Update & Logs Streaming

### Auto-Update Agent

Le plugin `self_update` permet de déployer automatiquement une nouvelle version de l'agent depuis le Hub **sans intervention manuelle** sur le poste distant.

**Workflow:**
1. Hub détecte nouvelle version disponible
2. POST `/api/agents/{agent_id}/update` avec URL package + checksum
3. Agent télécharge package, vérifie checksum SHA256
4. Agent backup version actuelle (rollback si échec)
5. Agent extrait et remplace fichiers
6. Agent se restart automatiquement avec nouvelle version

**Sécurité:**
- Vérification checksum SHA256 obligatoire
- Backup automatique ancienne version
- Rollback en cas d'échec
- Validation version (pas de downgrade involontaire)

**Exemple usage:**
```bash
# Hub déclenche update TITO vers v1.1.0
curl -X POST "http://333pie:8000/api/agents/TITO/update?version=1.1.0&download_url=http://333pie:8000/static/agents/agent_v1.1.0.zip&checksum=abc123..."
```

### Logs Streaming Temps Réel

Le système de **remote logging** envoie tous les logs de l'agent vers le Hub via WebSocket en temps réel.

**Fonctionnalités:**
- Streaming logs automatique (niveaux DEBUG, INFO, WARNING, ERROR)
- Buffer 1000 logs en cas de déconnexion temporaire
- Formatage JSON structuré (timestamp, level, module, function, line)
- Endpoint `/api/agents/{agent_id}/logs` pour consulter logs

**Exemple usage:**
```bash
# Consulter logs TITO (100 derniers)
curl "http://333pie:8000/api/agents/TITO/logs?limit=100"
```

**Avantage développement:**
- **0 accès SSH/RDP** nécessaire pour debug
- Logs centralisés sur Hub
- Monitoring temps réel depuis interface web
- Historique logs persisté

---

## 🌐 API REST Hub

### Liste Agents

### 1. Connexion & Handshake

```javascript
// Agent → Hub
{
    "type": "handshake",
    "agent_id": "TITO",
    "hostname": "DESKTOP-TITO",
    "os_platform": "windows",
    "version": "1.0.0",
    "plugins": ["logmein_rescue", "system_info"],
    "timestamp": "2025-10-30T12:00:00Z"
}

// Hub → Agent
{
    "type": "handshake_ack",
    "message": "Agent registered successfully"
}
```

### 2. Heartbeat (30s)

```javascript
// Agent → Hub
{
    "type": "heartbeat",
    "timestamp": "2025-10-30T12:00:30Z",
    "plugins_loaded": ["logmein_rescue", "system_info"]
}
```

### 3. Envoi Tâche

```javascript
// Hub → Agent
{
    "type": "task",
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "plugin": "logmein_rescue",
    "params": {
        "rescue_code": "123456",
        "timeout": 120
    }
}

// Agent → Hub (acquittement)
{
    "type": "task_ack",
    "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 4. Résultat Tâche

```javascript
// Agent → Hub
{
    "type": "task_result",
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "success",  // "success", "error", "timeout"
    "message": "LogMeIn session started successfully",
    "data": {
        "rescue_code": "123456",
        "applet_path": "C:\\Temp\\logmein\\rescue.exe",
        "session_active": true
    },
    "duration_ms": 45230
}
```

---

## 🌐 API REST Hub

### Liste Agents

```http
GET /api/agents
```

**Response:**
```json
[
    {
        "agent_id": "TITO",
        "hostname": "DESKTOP-TITO",
        "os_platform": "windows",
        "version": "1.0.0",
        "connected": true,
        "plugins": ["logmein_rescue", "system_info"],
        "last_heartbeat": "2025-10-30T12:00:30Z",
        "connected_at": "2025-10-30T11:00:00Z"
    }
]
```

### Envoyer Tâche

```http
POST /api/agents/{agent_id}/tasks
Content-Type: application/json

{
    "plugin": "logmein_rescue",
    "params": {
        "rescue_code": "123456",
        "timeout": 120
    }
}
```

**Response:**
```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "agent_id": "TITO",
    "plugin": "logmein_rescue",
    "status": "pending",
    "created_at": "2025-10-30T12:00:00Z",
    "message": "Task sent to agent"
}
```

### Statut Tâche

```http
GET /api/agents/tasks/{task_id}
```

**Response:**
```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "agent_id": "TITO",
    "plugin": "logmein_rescue",
    "status": "success",
    "created_at": "2025-10-30T12:00:00Z",
    "updated_at": "2025-10-30T12:00:45Z",
    "result": {
        "status": "success",
        "message": "LogMeIn session started successfully",
        "data": {...},
        "duration_ms": 45230
    }
}
```

### Logs Agent

```http
GET /api/agents/{agent_id}/logs?limit=100
```

**Response:**
```json
{
    "agent_id": "TITO",
    "logs": [
        {
            "timestamp": "2025-10-30T12:00:00Z",
            "level": "INFO",
            "logger": "agent",
            "message": "Starting LogMeIn automation...",
            "module": "logmein_rescue",
            "function": "execute",
            "line": 123
        }
    ],
    "total_count": 450,
    "returned_count": 100
}
```

### Déclencher Update Agent

```http
POST /api/agents/{agent_id}/update?version=1.1.0&download_url=...&checksum=...&force=false
```

**Response:**
```json
{
    "task_id": "uuid",
    "agent_id": "TITO",
    "plugin": "self_update",
    "status": "pending",
    "created_at": "2025-10-30T12:00:00Z",
    "message": "Update to version 1.1.0 initiated"
}
```

---

## 🔒 Sécurité

### Authentication
- **JWT tokens**: Validation côté Hub (expiration 15min)
- **API keys**: Fallback pour agents statiques

### Transport
- **WSS uniquement**: WebSocket sécurisé (TLS)
- **VPN Tailscale**: Communication prioritaire via VPN chiffré

### Validation
- **Pydantic schemas**: Validation stricte tous paramètres
- **Input sanitization**: Protection injection
- **Rate limiting**: Protection contre abus

### Audit
- **Logs complets**: Toutes connexions/tâches loggées
- **Timestamps UTC**: Traçabilité complète
- **Error tracking**: Captures erreurs détaillées

---

## 🚀 Workflow Complet

### Exemple: LogMeIn Rescue TITO

```
1. User ouvre interface 333HOME
   └─> Clic "Télémaintenance TITO"
   └─> Saisit code rescue "123456"

2. Interface → Hub API
   POST /api/agents/TITO/tasks
   {
     "plugin": "logmein_rescue",
     "params": {"rescue_code": "123456"}
   }

3. Hub → Agent TITO (WebSocket)
   {
     "type": "task",
     "task_id": "uuid",
     "plugin": "logmein_rescue",
     "params": {"rescue_code": "123456"}
   }

4. Agent TITO exécute plugin
   ├─> Setup Selenium WebDriver Chrome
   ├─> Navigate to secure.logmeinrescue.com
   ├─> Enter code "123456"
   ├─> Wait for applet download
   ├─> Launch applet as admin (UAC bypass)
   └─> Auto-accept all permissions

5. Agent TITO → Hub (résultat)
   {
     "type": "task_result",
     "task_id": "uuid",
     "status": "success",
     "message": "Session LogMeIn active",
     "duration_ms": 45000
   }

6. Hub → Interface (notification)
   ✅ "Session TITO démarrée avec succès (45s)"
```

---

## 📊 Métriques Performance

| Métrique | Cible | Mesure |
|----------|-------|--------|
| **Connexion agent** | <5s | - |
| **Heartbeat latency** | <100ms | - |
| **Task ack** | <500ms | - |
| **LogMeIn automation** | <60s | - |
| **SSH console latency** | <100ms | - |
| **VNC FPS** | >15fps | - |

---

## 🎯 Extensibilité

### Ajouter un Plugin

1. **Créer fichier plugin**
   ```bash
   touch src/agents/plugins/windows/mon_plugin.py
   ```

2. **Hériter de BasePlugin**
   ```python
   from ..base import WindowsPlugin
   
   class MonPlugin(WindowsPlugin):
       name = "mon_plugin"
       ...
   ```

3. **Auto-découverte**
   - PluginManager charge automatiquement
   - Compatible si `os_platform` match
   - Setup au démarrage agent

### Ajouter un Agent

1. **Installer agent sur nouveau poste**
   ```bash
   python agent.py --agent-id NOUVEAU --hub-url wss://...
   ```

2. **Configuration**
   ```python
   config = AgentConfig(
       agent_id="NOUVEAU",
       hub_url="wss://333pie.local:8000/ws/agents"
   )
   ```

3. **Connexion automatique**
   - Handshake → Hub enregistre agent
   - Heartbeat → Monitoring actif
   - Plugins → Chargés selon OS

---

## 🛠️ Développement

### Tests Plugin

```bash
# Test unitaire plugin
pytest tests/agents/plugins/test_logmein_rescue.py -v

# Test intégration WebSocket
pytest tests/agents/test_agent_integration.py -v
```

### Debug Mode

```bash
# Agent avec logs DEBUG
python src/agents/agent.py --log-level DEBUG

# Hub avec logs DEBUG
LOG_LEVEL=DEBUG python app.py
```

---

## 📚 Voir Aussi

- **[AGENTS_DEPLOYMENT.md](AGENTS_DEPLOYMENT.md)**: Guide déploiement complet
- **[PLUGIN_DEVELOPMENT.md](PLUGIN_DEVELOPMENT.md)**: Créer plugins custom
- **[DEVELOPMENT_ROADMAP.md](../DEVELOPMENT_ROADMAP.md)**: Roadmap complète
- **[API_INVENTORY.md](API_INVENTORY.md)**: Inventaire tous endpoints

---

**Version**: 1.0.0  
**Date**: 30 octobre 2025  
**Statut**: Sprint 0 - Structure repository ✅
