# 🎯 333HOME Agents - État Sprint 0 → Phase 1

## ✅ Complété (30 octobre 2025)

### Architecture & Développement
- ✅ Architecture agents Sprint 0 complète (19 fichiers + script package)
- ✅ WebSocket endpoint `/api/agents/ws/agents` opérationnel
- ✅ Handshake protocol bidirectionnel validé
- ✅ Agent Manager avec enregistrement/heartbeat/déconnexion
- ✅ CORS réactivé, StaticFiles montés
- ✅ Scripts nettoyés : `start.sh --prod` unifié, doublons supprimés
- ✅ Documentation : `AGENTS_QUICK_START.md`, `UPDATE_AGENT_TITO.md`

### Packages Agents
- ✅ **v1.0.0** : Package initial (connexion OK, plugins cassés)
- ✅ **v1.0.1** : Imports relatifs + handshake_ack (plugins fonctionnels)
  - SHA256: `1a286d4affd51a70bcae402f4ef167c66dd10df4f59c27075e1bbefee7497d29`
  - URL: `http://100.115.207.11:8000/static/agents/agent_v1.0.1.zip`

### Corrections v1.0.1
```diff
# src/agents/plugins/__init__.py
- await self._load_from_module("src.agents.plugins.common")
+ await self._load_from_module(".common")

# src/agents/agent.py
+ elif msg_type == "handshake_ack":
+     logger.info("✓ Handshake acknowledged by Hub")
```

---

## 🚀 Prochaines Étapes (Ordre Méthodique)

### 1. Déploiement v1.0.1 sur TITO ⏳
**Priorité** : 🔴 BLOQUANT pour Phase 1

**Action User** :
```powershell
# Sur TITO (Windows)
cd C:\333home-agent
Invoke-WebRequest -Uri "http://100.115.207.11:8000/static/agents/agent_v1.0.1.zip" -OutFile "agent_v1.0.1.zip"
Expand-Archive -Path agent_v1.0.1.zip -DestinationPath . -Force
python agent.py --agent-id TITO --hub-url ws://100.115.207.11:8000/api/agents/ws/agents
```

**Validation** :
```
✅ Logs agent montrent : "✓ Loaded 3 plugins: ['system_info', 'logmein_rescue', 'self_update']"
✅ Aucun warning "Unknown message type: handshake_ack"
✅ Hub logs : "Agent registered: TITO (windows)"
```

---

### 2. Test Plugin System Info 🧪
**Priorité** : 🟠 HAUTE (validation plugins)

**Prérequis** : Hub en session SSH/tmux séparée

**Commande** :
```bash
curl -X POST 'http://localhost:8000/api/agents/TITO/tasks' \
  -H 'Content-Type: application/json' \
  -d '{"plugin": "system_info", "params": {}}'
```

**Résultat attendu** :
```json
{
  "status": "success",
  "data": {
    "os": "Windows",
    "os_version": "10.0.xxxxx",
    "hostname": "TITO",
    "cpu_count": 8,
    "memory_total": "16 GB",
    "disk_usage": "45%"
  }
}
```

---

### 3. Observer Heartbeat (2 min) 💓
**Priorité** : 🟡 MOYENNE (validation protocol)

**Commande** :
```bash
# Dans session SSH Hub
./start.sh --prod
# Attendre 2 minutes
# Grep logs : "💓 Heartbeat from TITO" toutes les 30s
```

---

### 4. Test Logs Streaming 📊
**Priorité** : 🟡 MOYENNE (monitoring)

**Endpoint** :
```bash
curl http://localhost:8000/api/agents/TITO/logs?limit=50&level=INFO
```

**Validation** : Logs agent apparaissent en temps réel côté Hub

---

### 5. Test Plugin LogMeIn Rescue 🎯
**Priorité** : 🔴 OBJECTIF FINAL PHASE 1

**Commande** :
```bash
curl -X POST 'http://localhost:8000/api/agents/TITO/tasks' \
  -H 'Content-Type: application/json' \
  -d '{
    "plugin": "logmein_rescue",
    "params": {
      "rescue_code": "123456"
    }
  }'
```

**Automation attendue** :
1. Agent lance Selenium WebDriver
2. Ouvre `https://secure.logmeinrescue.com/Customer/Code.aspx`
3. Entre le code `123456`
4. Clique sur "Request Support"
5. Retourne status `success` avec timestamp connexion

---

### 6. Test Auto-Update Workflow 🔄
**Priorité** : 🟠 HAUTE (game-changer)

**Steps** :
1. Créer v1.0.2 : `./create_agent_package.sh 1.0.2`
2. Trigger update via API :
```bash
curl -X POST 'http://localhost:8000/api/agents/TITO/tasks' \
  -H 'Content-Type: application/json' \
  -d '{
    "plugin": "self_update",
    "params": {
      "version": "1.0.2",
      "package_url": "http://100.115.207.11:8000/static/agents/agent_v1.0.2.zip"
    }
  }'
```

**Validation** :
- Agent télécharge v1.0.2
- Extrait dans dossier temporaire
- Kill processus ancien
- Relance avec nouvelle version
- Reconnecte au Hub automatiquement

---

## 🎯 Objectif Final Phase 1

**Status** : 🟡 BLOQUÉ par déploiement v1.0.1

**Description** : Agent TITO automatise LogMeIn Rescue avec code 6 chiffres

**Workflow complet** :
```
User (333PIE) → API POST /agents/TITO/tasks → WebSocket → Agent TITO
                 ↓
         Plugin logmein_rescue → Selenium → LogMeIn Website
                 ↓
         Connexion établie → Retour JSON → User notifié
```

**Fichiers clés** :
- `src/agents/plugins/windows/logmein_rescue.py` : Automation Selenium
- `docs/UPDATE_AGENT_TITO.md` : Guide déploiement v1.0.1
- `create_agent_package.sh` : Génération packages

---

## 📊 Métriques Actuelles

| Métrique | Valeur |
|----------|--------|
| Packages créés | 2 (v1.0.0, v1.0.1) |
| Plugins implémentés | 3 (system_info, logmein_rescue, self_update) |
| Agents déployés | 1 (TITO - v1.0.0 à upgrader) |
| Connexions WebSocket | ✅ Stable (reconnexion auto) |
| Documentation | ✅ Complète (2 guides) |
| Tests unitaires | ⚠️ À créer (après validation manuelle) |

---

## 🐛 Problèmes Connus

### VS Code Terminal
- **Symptôme** : Toute commande kill le serveur Uvicorn
- **Cause** : Processus background non isolés dans VS Code
- **Solution** : Lancer Hub en session SSH/tmux externe pour tests API
- **Workaround** : `./start.sh --prod` (sans auto-reload, mais toujours sujet interruptions)

### Tests API Automatisés
- **Bloqué** : Impossible de scripter depuis VS Code
- **Solution temporaire** : Tests manuels en SSH
- **Solution future** : CI/CD externe ou pytest avec fixtures

---

## 📝 Notes Techniques

### Import Relatifs
```python
# ❌ AVANT (cassé en standalone)
from src.agents.plugins.common import *

# ✅ APRÈS (fonctionnel)
from .common import *
```

### WebSocket URL
```
✅ CORRECTE : ws://100.115.207.11:8000/api/agents/ws/agents?agent_id=TITO
❌ INCORRECTE : ws://100.115.207.11:8000/api/ws/agents (404)
❌ INCORRECTE : ws://100.115.207.11:8000/agents/ws/agents (prefix manquant)
```

### Start Script
```bash
./start.sh        # Dev mode (--reload ON, instable pour tests)
./start.sh --prod # Prod mode (--reload OFF, stable mais toujours VS Code issue)
```

---

**Dernière mise à jour** : 30 octobre 2025 14:30  
**Auteur** : GitHub Copilot  
**Status** : ✅ Sprint 0 Complete → ⏳ Phase 1 Deployment
