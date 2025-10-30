# 🔄 Guide Mise à Jour Agent TITO vers v1.0.1

## Changements v1.0.1

### ✅ Corrections
- **Imports plugins** : Correction imports absolus `src.*` → imports relatifs (plugins se chargent maintenant)
- **Message `handshake_ack`** : Ajout gestion message Hub → Agent (plus de warning)

### 📦 Package Info
- **Fichier** : `agent_v1.0.1.zip`
- **Taille** : 28K
- **Checksum** : `1a286d4affd51a70bcae402f4ef167c66dd10df4f59c27075e1bbefee7497d29`
- **URL** : `http://100.115.207.11:8000/static/agents/agent_v1.0.1.zip`

---

## 🚀 Méthode 1 : Mise à Jour Manuelle (RECOMMANDÉ)

### Étapes sur Windows (TITO)

```powershell
# 1. Arrêter l'agent en cours (Ctrl+C dans le terminal)

# 2. Télécharger v1.0.1
cd C:\333home-agent
Invoke-WebRequest -Uri "http://100.115.207.11:8000/static/agents/agent_v1.0.1.zip" -OutFile "agent_v1.0.1.zip"

# 3. Backup version actuelle (optionnel)
if (Test-Path "agent_backup") { Remove-Item -Recurse -Force agent_backup }
New-Item -ItemType Directory -Name agent_backup
Copy-Item agent.py, config.py, remote_logging.py, plugins -Destination agent_backup -Recurse

# 4. Extraire nouvelle version
Expand-Archive -Path agent_v1.0.1.zip -DestinationPath . -Force

# 5. Vérifier contenu
Get-ChildItem

# 6. Relancer agent
python agent.py --agent-id TITO --hub-url ws://100.115.207.11:8000/api/agents/ws/agents
```

### Vérification Plugins Chargés

Après relance, vous devriez voir dans les logs :

```
2025-10-30 XX:XX:XX - INFO - Loading plugins for windows...
2025-10-30 XX:XX:XX - INFO -   ✓ Loaded plugin: system_info v1.0.0
2025-10-30 XX:XX:XX - INFO -   ✓ Loaded plugin: logmein_rescue v1.0.0
2025-10-30 XX:XX:XX - INFO -   ✓ Loaded plugin: self_update v1.0.0
2025-10-30 XX:XX:XX - INFO - ✓ Loaded 3 plugins: ['system_info', 'logmein_rescue', 'self_update']
```

**Attendu** : 3 plugins au lieu de 0 ✅

---

## 🤖 Méthode 2 : Auto-Update via API (FUTUR)

*Note : Nécessite plugin `self_update` fonctionnel (débloqué après v1.0.1)*

```bash
# Depuis le Hub (333PIE)
curl -X POST 'http://localhost:8000/api/agents/TITO/tasks' \
  -H 'Content-Type: application/json' \
  -d '{
    "plugin": "self_update",
    "params": {
      "version": "1.0.1",
      "package_url": "http://100.115.207.11:8000/static/agents/agent_v1.0.1.zip",
      "checksum": "1a286d4affd51a70bcae402f4ef167c66dd10df4f59c27075e1bbefee7497d29"
    }
  }'
```

---

## 🧪 Tests Post-Mise à Jour

### Test 1 : Plugins Chargés
```powershell
# Chercher dans logs agent
Select-String -Path "agent.log" -Pattern "Loaded.*plugins"
```

### Test 2 : Handshake Propre
```powershell
# Vérifier absence warning handshake_ack
Select-String -Path "agent.log" -Pattern "Unknown message type: handshake_ack"
# Résultat attendu : AUCUN match
```

### Test 3 : Plugin System Info
*Note : Test API depuis Hub nécessite session SSH/tmux séparée*

```bash
# Depuis Hub (en SSH ou tmux)
curl -X POST 'http://localhost:8000/api/agents/TITO/tasks' \
  -H 'Content-Type: application/json' \
  -d '{
    "plugin": "system_info",
    "params": {}
  }'
```

---

## 📊 Comparaison v1.0.0 vs v1.0.1

| Aspect | v1.0.0 | v1.0.1 |
|--------|--------|--------|
| Plugins chargés | ❌ 0 (imports cassés) | ✅ 3 (system_info, logmein_rescue, self_update) |
| Warning handshake_ack | ⚠️ Oui | ✅ Non |
| Fonctionnalités | ❌ Limitées | ✅ Complètes |
| LogMeIn automation | ❌ Non disponible | ✅ Disponible |

---

## 🆘 Troubleshooting

### Problème : Plugins toujours à 0

```powershell
# Vérifier fichiers extraits
Get-ChildItem plugins -Recurse | Select-Object Name

# Output attendu :
# __init__.py
# base.py
# common/
# windows/
# linux/
```

### Problème : Erreur import

```powershell
# Vérifier version Python
python --version
# Minimum requis : Python 3.8+

# Réinstaller dépendances
pip install -r requirements.txt
```

### Rollback vers v1.0.0

```powershell
cd C:\333home-agent
Copy-Item agent_backup\* -Destination . -Recurse -Force
python agent.py --agent-id TITO --hub-url ws://100.115.207.11:8000/api/agents/ws/agents
```

---

## ✅ Checklist Validation

- [ ] Agent arrêté proprement (Ctrl+C)
- [ ] v1.0.1.zip téléchargé
- [ ] Backup créé (optionnel)
- [ ] Archive extraite avec `-Force`
- [ ] Agent relancé avec bonne URL
- [ ] Logs montrent 3 plugins chargés
- [ ] Aucun warning "Unknown message type: handshake_ack"
- [ ] Connexion WebSocket établie
- [ ] Hub affiche "Agent registered: TITO (windows)"

---

**Date** : 30 octobre 2025  
**Version Hub** : 3.0.0  
**Version Agent** : 1.0.0 → **1.0.1** ✅
