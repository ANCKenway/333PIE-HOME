# Scripts Utilitaires Agents

Scripts pour administrer et monitorer les agents 333HOME depuis le Hub.

## 📋 agent_logs.sh

Affiche les logs d'un agent connecté au Hub.

### Usage

```bash
./scripts/agent_logs.sh [AGENT_ID] [LIMIT]
```

### Paramètres

- `AGENT_ID` : ID de l'agent (défaut: `TITO`)
- `LIMIT` : Nombre de logs à afficher (défaut: `50`)

### Exemples

```bash
# Afficher les 50 derniers logs de TITO
./scripts/agent_logs.sh TITO

# Afficher les 100 derniers logs de 333srv
./scripts/agent_logs.sh 333srv 100

# Afficher les 10 derniers logs
./scripts/agent_logs.sh TITO 10
```

### Output

```
========================================
  📋 Logs Agent: TITO
========================================

✅ Agent connected

[INFO] 2025-10-30 18:36:35,451 - __main__ - INFO - [OK] Remote logging enabled
[INFO] 2025-10-30 18:36:35,451 - __main__ - INFO - Connecting to Hub
[INFO] 2025-10-30 18:36:35,469 - __main__ - INFO - [OK] Connected to Hub
...
```

**Codes couleur** :
- 🟢 **INFO** : Vert
- 🟡 **WARNING** : Jaune
- 🔴 **ERROR** : Rouge

---

## 📡 agent_logs_watch.sh

Suit les logs d'un agent en temps réel (mode streaming).

### Usage

```bash
./scripts/agent_logs_watch.sh [AGENT_ID] [INTERVAL]
```

### Paramètres

- `AGENT_ID` : ID de l'agent (défaut: `TITO`)
- `INTERVAL` : Intervalle de rafraîchissement en secondes (défaut: `2`)

### Exemples

```bash
# Suivre les logs de TITO (refresh 2s)
./scripts/agent_logs_watch.sh TITO

# Suivre les logs avec refresh rapide (1s)
./scripts/agent_logs_watch.sh TITO 1

# Suivre un autre agent
./scripts/agent_logs_watch.sh 333srv 3
```

### Output

```
========================================
  📡 Streaming Logs: TITO
  Refresh: 2s | Ctrl+C to stop
========================================

[18:36:35] INFO  [OK] Remote logging enabled
[18:36:35] INFO  Connecting to Hub
[18:36:35] INFO  [OK] Connected to Hub
...
```

**Arrêt** : `Ctrl+C`

**Avantages** :
- ✅ Affiche seulement les **nouveaux logs** (pas de répétitions)
- ✅ Détection reconnexion agent automatique
- ✅ Timestamp formaté (HH:MM:SS)
- ✅ Codes couleur par niveau

---

## 🔧 Architecture Remote Logging

### Workflow

```
Agent (TITO)                Hub (333PIE)                    Terminal
     │                           │                              │
     │  1. Logs émis             │                              │
     │ ──────────────────────>   │                              │
     │  (WebSocket stream)       │                              │
     │                           │  2. Buffer (max 100 logs)    │
     │                           │                              │
     │                           │  3. API GET /api/agents/{id}/logs
     │                           │ <──────────────────────────  │
     │                           │                              │
     │                           │  4. Retourne logs            │
     │                           │ ──────────────────────────>  │
```

### API Endpoint

**GET** `/api/agents/{agent_id}/logs?limit=50`

**Response** :
```json
{
  "agent_id": "TITO",
  "logs": [
    {
      "timestamp": "2025-10-30T18:36:35.451806",
      "level": "INFO",
      "logger": "__main__",
      "message": "[OK] Connected to Hub"
    }
  ],
  "total_count": 5,
  "returned_count": 5
}
```

### Configuration Agent

Le remote logging est **activé par défaut** dans `agent.py` :

```python
from remote_logging import setup_remote_logging

self._remote_log_handler = setup_remote_logging(self, level=logging.DEBUG)
```

**Buffer Hub** : 100 logs max par agent (circular buffer)

---

## 🚀 Usage Rapide

### Consulter les logs actuels

```bash
./scripts/agent_logs.sh TITO 20
```

### Suivre en temps réel

```bash
./scripts/agent_logs_watch.sh TITO 2
```

### Via API directement

```bash
# Logs JSON
curl http://localhost:8000/api/agents/TITO/logs | jq .

# Logs formatés
curl -s http://localhost:8000/api/agents/TITO/logs | \
  jq -r '.logs[] | "[\(.level)] \(.message)"'
```

---

## 📝 Notes

- **Buffer limité** : Le Hub garde seulement les 100 derniers logs par agent
- **Temps réel** : Les logs sont streamés via WebSocket dès leur émission
- **Reconnexion** : Si l'agent se déconnecte, le buffer est vidé
- **Performance** : Impact minimal (logs async, pas de blocage)

---

**Auteur** : 333HOME Team  
**Date** : 30 octobre 2025  
**Version** : 1.0
