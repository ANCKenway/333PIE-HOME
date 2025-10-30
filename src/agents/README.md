# 🤖 333HOME Agents - Architecture Universelle

## 📋 Vue d'ensemble

Système d'agents de contrôle à distance **cross-platform** pour gérer les postes TITO (Windows) et 333srv (Linux) depuis le Hub 333HOME.

### 🎯 Objectifs

- **Phase 1 (Windows)**: Automation LogMeIn Rescue pour TITO
- **Phase 2 (Linux)**: Console SSH + VNC pour 333srv  
- **Phase 3**: Architecture extensible multi-postes

## 🏗️ Architecture

```
src/agents/
├── agent.py                    # Agent universel WebSocket
├── config.py                   # Configuration agents
├── plugins/
│   ├── __init__.py
│   ├── base.py                 # BasePlugin abstract
│   ├── windows/                # 🔥 PRIORITÉ PHASE 1
│   │   ├── __init__.py
│   │   ├── logmein_rescue.py   # Plugin LogMeIn (TITO)
│   │   ├── rdp.py              # Remote Desktop (futur)
│   │   └── powershell.py       # Exec PowerShell (futur)
│   ├── linux/                  # Phase 2
│   │   ├── __init__.py
│   │   ├── ssh_console.py      # Console SSH web
│   │   ├── docker.py           # Contrôle Docker
│   │   └── systemd.py          # Gestion services
│   └── common/                 # Cross-platform
│       ├── __init__.py
│       └── system_info.py      # Info système (test)
└── deployments/
    ├── windows/
    │   ├── install.ps1         # Installation agent TITO
    │   └── agent-service.xml   # Service Windows
    └── linux/
        ├── install.sh          # Installation agent 333srv
        └── agent.service       # Systemd service
```

## 🔌 Système de Plugins

### Classe de Base

```python
from src.agents.plugins.base import BasePlugin

class MyPlugin(BasePlugin):
    name = "my_plugin"
    os_platform = "windows"  # "windows", "linux", ou "all"
    
    async def execute(self, params: dict) -> dict:
        # Logique du plugin
        return {"status": "success", "data": result}
    
    def validate_params(self, params: dict) -> bool:
        # Validation des paramètres
        return True
```

### Plugins Disponibles

#### 🪟 Windows (Phase 1 - PRIORITÉ)
- **logmein_rescue**: Automation complète LogMeIn Rescue
  - Entrée code 6 chiffres
  - Téléchargement applet
  - Élévation admin (UAC bypass)
  - Acceptation droits auto

#### 🐧 Linux (Phase 2)
- **ssh_console**: Terminal SSH interactif (xterm.js)
- **docker**: Gestion containers Docker
- **systemd**: Contrôle services systemd

#### 🌐 Common (Cross-platform)
- **system_info**: Collecte info système (CPU, RAM, Disk)

## 🚀 Démarrage Rapide

### Installation Hub (333PIE)

```bash
# Ajouter dépendances agents
pip install websockets selenium pywinauto paramiko

# Démarrer Hub avec support agents
python app.py
```

### Déploiement Agent Windows (TITO)

```powershell
# Sur TITO (192.168.1.174)
cd C:\333home-agent
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python install_service.py
```

### Déploiement Agent Linux (333srv)

```bash
# Sur 333srv (192.168.1.175)
cd /opt/333home-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo ./install_service.sh
```

## 🔒 Sécurité

- **JWT tokens**: Expiration 15min, refresh auto
- **WSS uniquement**: Pas de WebSocket non chiffré
- **VPN Tailscale**: Communication prioritaire via VPN
- **Validation stricte**: Pydantic schemas pour tous les paramètres
- **Audit logs**: Toutes actions sensibles loggées

## 📊 Communication Hub ↔ Agent

### Protocol WebSocket

```python
# Connexion agent
ws://333pie.local:8000/ws/agents/{agent_id}?token={jwt_token}

# Messages
{
    "type": "task",
    "task_id": "uuid",
    "plugin": "logmein_rescue",
    "params": {"rescue_code": "123456"}
}

# Réponses
{
    "type": "task_result",
    "task_id": "uuid",
    "status": "success",
    "data": {...}
}

# Heartbeat (30s)
{
    "type": "heartbeat",
    "timestamp": 1698765432,
    "plugins_loaded": ["logmein_rescue", "system_info"]
}
```

## 🛠️ Développement

### Ajouter un Plugin

1. Créer fichier dans `plugins/windows/` ou `plugins/linux/`
2. Hériter de `BasePlugin`
3. Implémenter `execute()` et `validate_params()`
4. Auto-découverte par `PluginManager`

### Tests

```bash
# Tester agent localement
pytest tests/agents/ -v

# Tester plugin spécifique
pytest tests/agents/test_logmein_rescue.py -v
```

## 📚 Documentation Complète

- [AGENTS_ARCHITECTURE.md](../../docs/AGENTS_ARCHITECTURE.md) - Architecture détaillée
- [AGENTS_DEPLOYMENT.md](../../docs/AGENTS_DEPLOYMENT.md) - Guide déploiement
- [PLUGIN_DEVELOPMENT.md](../../docs/PLUGIN_DEVELOPMENT.md) - Créer plugins custom

## 🎯 Roadmap

- [x] **Sprint 0**: Structure repository agents
- [ ] **Sprint 1**: Agent de base + plugin system
- [ ] **Sprint 2**: Plugin LogMeIn Windows (TITO)
- [ ] **Sprint 3**: Console SSH Linux (333srv)
- [ ] **Sprint 4**: Interface web Hub

---

**Priorité**: Windows (TITO) sans perdre de vue Linux (333srv) 🎯
**Règles**: Respect strict RULES.md - architecture modulaire, code propre, pas de duplication
