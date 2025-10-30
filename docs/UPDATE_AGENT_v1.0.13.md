# 🔄 Guide Mise à Jour Agent v1.0.13 - Corrections Unicode

## Changements v1.0.13

### ✅ Corrections Unicode Windows cp1252
**Problème résolu** : Erreurs `UnicodeEncodeError: 'charmap' codec can't encode character` au démarrage agent Windows.

**Cause** : Console PowerShell utilise encoding cp1252 par défaut, incompatible avec emojis UTF-8 dans logs.

**Solution** : Remplacement tous emojis par marqueurs ASCII :
- `🤖` → `[Agent]` (bannière démarrage)
- `✓` → `[OK]` (succès opérations)
- `💓` → `[HB]` (heartbeat)
- `📋` → `[Task]` (réception tâche)
- `🚀` → `[Exec]` (exécution plugin)
- `⚠️` → `[WARNING]` (avertissements)
- `✗` → `[X]` (échecs)
- `⊘` → `[Skip]` (plugins incompatibles)

### 📦 Package Info
- **Fichier** : `agent_v1.0.13.zip`
- **Taille** : 32K
- **Checksum** : `e8e52daf7de75bc4e4192566dacf0ac33fdbe2c9c92dd7398835edae79959c88`
- **URL** : `http://100.115.207.11:8000/static/agents/agent_v1.0.13.zip`

### 📝 Fichiers modifiés
- `src/agents/agent.py` : 10 remplacements emojis → ASCII
- `src/agents/plugins/__init__.py` : 3 remplacements emojis → ASCII

---

## 🚀 Méthode 1 : Mise à Jour Manuelle (Windows TITO)

### Étapes sur Windows

```powershell
# 1. Arrêter l'agent en cours (Ctrl+C dans le terminal)

# 2. Télécharger v1.0.13
cd C:\333home-agent
Invoke-WebRequest -Uri "http://100.115.207.11:8000/static/agents/agent_v1.0.13.zip" -OutFile "agent_v1.0.13.zip"

# 3. Backup version actuelle (optionnel mais recommandé)
if (Test-Path "agent_backup") { Remove-Item -Recurse -Force agent_backup }
New-Item -ItemType Directory -Name agent_backup
Copy-Item agent.py, config.py, remote_logging.py, plugins -Destination agent_backup -Recurse

# 4. Extraire nouvelle version
Expand-Archive -Path agent_v1.0.13.zip -DestinationPath . -Force

# 5. Vérifier contenu
Get-ChildItem

# 6. Relancer agent
python agent.py --agent-id TITO --hub-url ws://100.115.207.11:8000/api/agents/ws/agents
```

### ✅ Vérification Logs Propres

**Avant v1.0.13** (avec erreurs Unicode) :
```
Traceback (most recent call last):
  File "C:\...\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f916' in position 44: character maps to <undefined>
```

**Après v1.0.13** (logs propres) :
```
2025-10-30 XX:XX:XX - INFO - ======================================================================
2025-10-30 XX:XX:XX - INFO - [Agent] 333HOME Universal Agent v1.0.0
2025-10-30 XX:XX:XX - INFO - Agent ID: TITO
2025-10-30 XX:XX:XX - INFO - Hostname: TITO
2025-10-30 XX:XX:XX - INFO - OS Platform: windows
2025-10-30 XX:XX:XX - INFO - Hub URL: ws://100.115.207.11:8000/api/agents/ws/agents
2025-10-30 XX:XX:XX - INFO - ======================================================================
2025-10-30 XX:XX:XX - INFO - Loading plugins...
2025-10-30 XX:XX:XX - INFO - [OK] 3 plugins loaded
2025-10-30 XX:XX:XX - INFO -   [OK] Loaded plugin: system_info v1.0.0
2025-10-30 XX:XX:XX - INFO -   [OK] Loaded plugin: logmein_rescue v2.0.0
2025-10-30 XX:XX:XX - INFO -   [OK] Loaded plugin: self_update v1.0.0
2025-10-30 XX:XX:XX - INFO - [OK] Connected to Hub
```

---

## 🤖 Méthode 2 : Auto-Update via API (RECOMMANDÉ)

**Prérequis** : Agent TITO connecté au Hub

### Depuis Hub (333PIE)

```bash
# Envoyer tâche self_update à TITO
curl -X POST 'http://localhost:8000/api/agents/TITO/tasks' \
  -H 'Content-Type: application/json' \
  -d '{
    "plugin": "self_update",
    "params": {
      "version": "1.0.13",
      "package_url": "http://100.115.207.11:8000/static/agents/agent_v1.0.13.zip",
      "checksum": "e8e52daf7de75bc4e4192566dacf0ac33fdbe2c9c92dd7398835edae79959c88"
    }
  }'
```

### Workflow automatique attendu

1. **Agent TITO reçoit tâche** `self_update`
2. **Téléchargement** : `agent_v1.0.13.zip` depuis Hub
3. **Vérification checksum** : SHA256 validé
4. **Backup automatique** : `agent_backup/` créé avec v1.0.12
5. **Extraction** : Nouvelle version extraite dans `C:\333home-agent`
6. **Redémarrage** : Script PowerShell relance agent automatiquement
7. **Reconnexion** : WebSocket rétabli avec Hub

### Logs Hub pendant auto-update

```
2025-10-30 XX:XX:XX - INFO - [Task] Task received: <task_id> (plugin: self_update)
2025-10-30 XX:XX:XX - INFO - [Exec] Executing plugin: self_update
2025-10-30 XX:XX:XX - INFO - Downloading package from http://100.115.207.11:8000/static/agents/agent_v1.0.13.zip
2025-10-30 XX:XX:XX - INFO - [OK] Download completed (32K)
2025-10-30 XX:XX:XX - INFO - [OK] Checksum verified: e8e52daf7de75bc4e4192566dacf0ac33fdbe2c9c92dd7398835edae79959c88
2025-10-30 XX:XX:XX - INFO - Creating backup in agent_backup/
2025-10-30 XX:XX:XX - INFO - [OK] Backup completed
2025-10-30 XX:XX:XX - INFO - Extracting new version...
2025-10-30 XX:XX:XX - INFO - [OK] Extraction completed
2025-10-30 XX:XX:XX - INFO - Restarting agent...
[WEBSOCKET DISCONNECTED]
...
[30-60 secondes plus tard]
2025-10-30 XX:XX:XX - INFO - [Agent] Agent registered: TITO (windows)
2025-10-30 XX:XX:XX - INFO - [Agent] Plugins: ['system_info', 'logmein_rescue', 'self_update']
```

---

## 🧪 Tests Post-Mise à Jour

### Test 1 : Logs Propres (Sans erreurs Unicode)

```powershell
# Chercher erreurs UnicodeEncodeError dans logs
Select-String -Path "agent.log" -Pattern "UnicodeEncodeError"
# Résultat attendu : AUCUN match ✅
```

### Test 2 : Plugins Toujours Fonctionnels

```bash
# Depuis Hub - Test system_info
curl -X POST 'http://localhost:8000/api/agents/TITO/tasks' \
  -H 'Content-Type: application/json' \
  -d '{
    "plugin": "system_info",
    "params": {}
  }'
```

### Test 3 : LogMeIn Rescue Toujours OK

```bash
# Depuis Hub - Test LogMeIn avec code réel
curl -X POST 'http://localhost:8000/api/agents/TITO/tasks' \
  -H 'Content-Type: application/json' \
  -d '{
    "plugin": "logmein_rescue",
    "params": {
      "code": "123456"
    }
  }'
```

**Workflow attendu** :
- ✅ Navigateur ouvert
- ✅ Téléchargement applet
- ✅ Lancement admin
- ✅ Validation automatique Tab+Enter (Windows SendKeys API)
- ✅ Session établie

---

## 📊 Comparaison v1.0.12 vs v1.0.13

| Aspect | v1.0.12 | v1.0.13 |
|--------|---------|---------|
| Erreurs Unicode Windows | ❌ UnicodeEncodeError cp1252 | ✅ Logs propres ASCII |
| LogMeIn automation | ✅ Fonctionnelle (SendKeys API) | ✅ Fonctionnelle (inchangé) |
| Plugins chargés | ✅ 3 plugins | ✅ 3 plugins |
| Lisibilité logs | ⚠️ Emojis pollués | ✅ Marqueurs ASCII clairs |
| Compatibilité Windows | ⚠️ Encoding issues | ✅ 100% compatible cp1252 |

---

## 🆘 Troubleshooting

### Problème : Toujours erreurs Unicode après update

```powershell
# Vérifier version extraite
Get-Content agent.py | Select-String -Pattern "\[Agent\]"

# Output attendu : Ligne avec "[Agent] 333HOME Universal Agent"
# Si toujours emoji 🤖 : extraction incomplète
```

**Solution** : Réextraire avec `-Force`
```powershell
Expand-Archive -Path agent_v1.0.13.zip -DestinationPath . -Force
```

### Problème : Agent ne redémarre pas après auto-update

**Cause possible** : Script redémarrage bloqué par UAC

**Solution temporaire** : Relancer manuellement
```powershell
cd C:\333home-agent
python agent.py --agent-id TITO --hub-url ws://100.115.207.11:8000/api/agents/ws/agents
```

### Rollback vers v1.0.12

```powershell
cd C:\333home-agent

# Si backup existe
if (Test-Path "agent_backup") {
    Copy-Item agent_backup\* -Destination . -Recurse -Force
    python agent.py --agent-id TITO --hub-url ws://100.115.207.11:8000/api/agents/ws/agents
}

# Sinon, retélécharger v1.0.12
Invoke-WebRequest -Uri "http://100.115.207.11:8000/static/agents/agent_v1.0.12.zip" -OutFile "agent_v1.0.12.zip"
Expand-Archive -Path agent_v1.0.12.zip -DestinationPath . -Force
python agent.py --agent-id TITO --hub-url ws://100.115.207.11:8000/api/agents/ws/agents
```

---

## ✅ Checklist Validation

- [ ] Agent v1.0.12 arrêté proprement
- [ ] v1.0.13.zip téléchargé (32K)
- [ ] Backup v1.0.12 créé (optionnel)
- [ ] Archive extraite avec `-Force`
- [ ] Agent relancé
- [ ] **Logs propres sans UnicodeEncodeError** ✅
- [ ] Connexion WebSocket établie
- [ ] Hub affiche "Agent registered: TITO"
- [ ] 3 plugins chargés (system_info, logmein_rescue, self_update)
- [ ] Test system_info fonctionnel
- [ ] Test LogMeIn automation fonctionnelle

---

## 🎯 Objectif Phase 2

**Phase 1** : ✅ Automation LogMeIn complète (v1.0.12 avec Windows SendKeys API)

**Phase 2 Tâche 1** : ✅ **Corrections Unicode terminées** (v1.0.13)

**Phase 2 Tâche 2** : ⏳ Validation auto-update
- Attente connexion agent TITO pour test auto-update complet
- Workflow automatique à valider : téléchargement → checksum → backup → extraction → redémarrage

---

**Date** : 30 octobre 2025  
**Version Hub** : 3.0.0  
**Version Agent** : v1.0.12 → **v1.0.13** ✅  
**Corrections** : Erreurs Unicode Windows cp1252 résolues
