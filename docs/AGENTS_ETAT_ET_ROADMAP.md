# 🤖 État des Lieux Agents 333HOME + Roadmap Évolutions

**Date**: 4 novembre 2025  
**Version Agent**: 1.0.17  
**Statut**: ✅ Production Ready

---

## 📊 État Actuel - Fonctionnalités Existantes

### 🏗️ Architecture Agent (Côté Client)

#### **Agent Core** (`agent.py`)
- ✅ **WebSocket persistent** vers Hub (wss://333pie.local:8000/api/ws/agents)
- ✅ **Auto-découverte Hub** intelligente (mDNS → Tailscale → Fallback IPs)
- ✅ **Heartbeat automatique** (30s)
- ✅ **Reconnexion auto** en cas de perte connexion
- ✅ **Streaming logs temps réel** vers Hub
- ✅ **Cross-platform**: Windows, Linux, macOS
- ✅ **Versionning unifié** (version.py centralisé)

#### **Système Plugins** (`plugins/`)
Architecture modulaire extensible avec plugins chargés dynamiquement selon OS.

**Plugins Communs** (Windows/Linux/macOS):
1. **`system_info`** v1.0.0 ✅
   - Collecte infos système (CPU, RAM, Disk, Network, Processes)
   - Utilisé pour monitoring basique
   - Cross-platform via psutil

2. **`self_update`** v1.0.0 ✅
   - Auto-mise à jour agent depuis Hub
   - Download → Checksum SHA256 → Backup → Extract → Replace
   - ⚠️ **Limitation**: Restart manuel nécessaire après update

**Plugins Windows**:
3. **`logmein_rescue`** v2.0.0 ✅
   - Automation LogMeIn Rescue SANS Selenium
   - Ouvre navigateur + télécharge applet + lance avec UAC + auto-accept
   - Workflow: Code 6 chiffres → Session active en <60s
   - ⚠️ **Dépendances**: win32com.client, navigateur par défaut configuré

#### **Tray Icon Windows** (`agent_tray.pyw`)
- ✅ Icône système tray avec menu contextuel
- ✅ Actions: View Logs, Restart, About, Quit
- ✅ Démarrage auto (startup folder Windows)
- ✅ Watchdog crash recovery (auto-restart si agent.py crash)
- ✅ Désinstallation propre (uninstall.bat avec backup logs)

---

### 🖥️ Backend Hub (Côté Serveur)

#### **API REST** (`/api/agents/*`)
- `GET /api/agents` - Liste agents connectés ✅
- `POST /api/agents/{id}/tasks` - Envoyer tâche à agent ✅
- `GET /api/agents/{id}/plugins` - Liste plugins agent ✅
- `GET /api/agents/{id}/status` - Statut agent ✅
- `GET /api/agents/{id}/logs?tail=N` - Derniers N logs agent ✅

#### **WebSocket** (`/api/ws/agents`)
- ✅ Handshake (agent_id, hostname, os_platform, version, plugins)
- ✅ Heartbeat (30s keepalive)
- ✅ Tasks (envoi tâches plugin avec params)
- ✅ Results (réception résultats execution)
- ✅ Logs streaming (buffer 100 derniers logs par agent)

#### **AgentManager** (`agents_router.py`)
- ✅ Gestion connexions agents in-memory (Dict[agent_id, AgentConnection])
- ✅ File tâches par agent (pending_tasks Dict[task_id, task_data])
- ✅ Buffer logs par agent (100 derniers messages)
- ✅ Update heartbeat automatique

#### **Enrichissement Registry** (`registry_router.py`)
- ✅ Croisement agents WebSocket avec Registry devices
- ✅ Détection agents par IP ou hostname
- ✅ Champs registry: `is_agent_connected`, `agent_id`, `agent_version`
- ✅ Refresh toutes les 5s (arrière-plan léger)

---

### 🌐 Frontend Web (Interface Utilisateur)

#### **Onglet Agents** (`web/index.html`)
- ✅ Dashboard stats (Agents connectés, Windows, Linux)
- ✅ Table agents complète:
  - Colonnes: Agent ID, Status, Version, OS, Plugins, Last Seen, Actions
  - ✅ **Status**: Badge vert "Connected" ou gris "Offline"
  - ✅ **Actions**: View Logs, Restart, Update, LogMeIn

#### **Modal Logs Temps Réel**
- ✅ Auto-refresh 5s si modal ouverte
- ✅ Affichage logs structurés (timestamp, level, message)
- ✅ Scroll auto vers bas (derniers logs)
- ✅ Bouton Fermer

#### **Badges Agent Unifiés**
- ✅ **Dashboard** (Cards Appareils): Badge violet 🤖 Agent si connecté
- ✅ **Page Appareils** (Table): Badge violet si agent actif
- ✅ **Page Réseau** (Table complète): Badge violet visible
- ✅ **Badges grisés**: Si agent attendu mais déconnecté (metadata.expect_agent)
- ✅ **Checkboxes contrôle manuel**: Modal Edit Device avec cases expect_vpn/expect_agent

#### **Actions Agents** (Frontend)
1. **View Logs** → Modal logs temps réel
2. **Restart** → POST /api/agents/{id}/restart (TODO backend)
3. **Update** → POST /api/agents/{id}/update (TODO backend)
4. **LogMeIn** → Input code rescue → Tâche logmein_rescue plugin

---

## 📈 Métriques & Performance

### **Agents Déployés**
- **TITO** (Windows 10/11): PC principal, agent v1.0.17 ✅
- **333srv** (Linux): Serveur, agent NON DÉPLOYÉ ❌

### **Performance**
- WebSocket latency: **~50ms** (réseau local)
- Heartbeat overhead: **~100 bytes/30s** par agent
- Logs streaming: **Buffer 100 messages** (mémoire faible)
- Task execution: **Variable selon plugin** (system_info ~1s, logmein_rescue ~60s)

### **Charge Serveur**
- Registry refresh: **5s** (arrière-plan, enrichissement agents léger)
- UI refresh: **30s** (confortable, devices + agents)
- Agents refresh: **5s** (si modal logs ouverte, sinon 30s avec UI)

---

## 🚀 Roadmap Nouvelles Fonctionnalités

### 🔴 PRIORITÉ HAUTE - Améliorer Existant

#### **1. Auto-Restart après Self-Update** ⏱️ 1h
**Problème**: Actuellement après self_update, restart manuel nécessaire via tray icon.

**Solution**: 
- Modifier `self_update.py` pour exécuter restart automatique après replace fichiers
- Windows: Relancer `pythonw agent_tray.pyw` via subprocess detached
- Linux: Utiliser systemd restart ou script watchdog

**Avantages**:
- ✅ Update totalement automatisé
- ✅ Zéro intervention utilisateur
- ✅ Downtime réduit (<5s)

---

#### **2. Fix Fichier Lock lors Replace** ⏱️ 30min
**Problème**: Edge case ancien agent.py verrouillé si watchdog rate le kill.

**Solution**:
- Ajouter retry logic avec timeout dans `self_update.py`
- Forcer kill processus Python avant replace (psutil.kill())
- Fallback: Renommer ancien fichier au lieu de delete

---

#### **3. Métriques Succès/Échecs Auto-Update** ⏱️ 1h
**Objectif**: Tracking fiabilité auto-update production.

**Solution**:
- Logger structured outcomes (`update_success`, `update_failed`, `checksum_mismatch`, etc.)
- Endpoint `/api/agents/{id}/update-history` pour afficher historique
- Frontend: Section "Update History" onglet Agents

---

#### **4. Backend Actions Restart/Update** ⏱️ 2h
**Problème**: Boutons Restart et Update frontend non fonctionnels (backend manquant).

**Solution**:
- Endpoint `POST /api/agents/{id}/restart`:
  ```python
  async def restart_agent(agent_id: str):
      task_id = await agent_manager.send_task(
          agent_id, 
          plugin="system_restart",  # Nouveau plugin
          params={"delay": 5}
      )
      return {"task_id": task_id}
  ```
  
- Endpoint `POST /api/agents/{id}/update`:
  ```python
  async def update_agent(agent_id: str, version: str):
      # Vérifier version disponible
      # Générer checksum
      # Envoyer task self_update
  ```

- Plugin `system_restart`:
  - Windows: `subprocess.Popen(["shutdown", "/r", "/t", "5"])`
  - Linux: `subprocess.run(["sudo", "reboot"])`

---

### 🟡 PRIORITÉ MOYENNE - Nouvelles Capacités

#### **5. Remote Command Execution (Shell)** ⏱️ 3h
**Use Case**: Exécuter commandes shell/PowerShell depuis Hub.

**Plugin**: `remote_shell`
- Paramètres: `command` (string), `shell` (bool), `timeout` (int)
- Sécurité: Whitelist commandes autorisées (éviter `rm -rf /`)
- Output: stdout + stderr + exit_code
- Frontend: Bouton "Shell" → Modal input commande → Affichage output

**Exemple**:
```python
# Task
{
  "plugin": "remote_shell",
  "params": {
    "command": "ipconfig /all",
    "shell": true,
    "timeout": 30
  }
}

# Result
{
  "stdout": "...",
  "stderr": "",
  "exit_code": 0,
  "execution_time": 1.2
}
```

---

#### **6. File Transfer (Upload/Download)** ⏱️ 4h
**Use Case**: Envoyer/récupérer fichiers depuis agents.

**Plugin**: `file_transfer`
- Actions: `upload` (Hub → Agent), `download` (Agent → Hub)
- Chunking: Fichiers >10MB découpés en chunks 1MB
- Checksum: Validation SHA256 après transfer
- Frontend: Bouton "Files" → Interface drag-drop upload + liste fichiers downloadables

**Workflow Upload**:
1. Hub envoie task `file_transfer` avec `action=upload`, `filename`, `chunks_count`
2. Agent prépare buffer réception
3. Hub envoie chunks via WebSocket (messages séquentiels)
4. Agent reconstruit fichier + vérifie checksum
5. Agent retourne `status=success`

**Workflow Download**:
1. Hub envoie task `file_transfer` avec `action=download`, `filepath`
2. Agent lit fichier, découpe en chunks, calcule checksum
3. Agent envoie chunks via WebSocket
4. Hub reconstruit + vérifie checksum

---

#### **7. Screenshot Capture** ⏱️ 2h
**Use Case**: Capturer écran agent (troubleshooting, monitoring).

**Plugin**: `screenshot`
- Paramètres: `quality` (1-100), `display` (int, multi-écrans)
- Output: Image PNG encodée base64
- Frontend: Bouton "Screenshot" → Affichage image + download

**Implémentation**:
- Windows: `PIL.ImageGrab.grab()`
- Linux: `scrot` ou `import` (ImageMagick)
- macOS: `screencapture`

---

#### **8. Process Manager** ⏱️ 3h
**Use Case**: Lister/killer/relancer processus agents.

**Plugin**: `process_manager`
- Actions: `list`, `kill`, `start`
- Sécurité: Whitelist processus tuables (éviter system processes)
- Frontend: Table processus (PID, Name, CPU%, RAM%, Actions)

**Exemple**:
```python
# Liste processus
{
  "plugin": "process_manager",
  "params": {"action": "list", "sort_by": "cpu"}
}

# Kill processus
{
  "plugin": "process_manager",
  "params": {"action": "kill", "pid": 12345}
}
```

---

#### **9. Service Manager (Windows/Linux)** ⏱️ 3h
**Use Case**: Gérer services système (start/stop/restart/status).

**Plugin**: `service_manager`
- Windows: `sc.exe` ou `pywin32` services API
- Linux: `systemctl` (systemd)
- Actions: `list`, `start`, `stop`, `restart`, `status`, `enable`, `disable`
- Frontend: Table services (Name, Status, Startup Type, Actions)

---

#### **10. Network Diagnostics** ⏱️ 2h
**Use Case**: Tester connectivité réseau depuis agents.

**Plugin**: `network_diagnostics`
- Tests: `ping`, `traceroute`, `dns_lookup`, `port_scan`, `speedtest`
- Output: Résultats structurés (latency, packet_loss, route, etc.)
- Frontend: Modal "Network Tools" avec sélection test + params

---

### 🔵 PRIORITÉ BASSE - Nice-to-Have

#### **11. Registry Editor (Windows)** ⏱️ 4h
**Use Case**: Modifier registre Windows à distance (configs avancées).

**Plugin**: `registry_editor`
- Actions: `read`, `write`, `delete`, `export`
- Sécurité: **CRITIQUE** - Whitelist clés autorisées, confirmation obligatoire
- Frontend: Interface arbre registry + éditeur valeurs

---

#### **12. Event Viewer (Windows)** ⏱️ 3h
**Use Case**: Consulter logs événements Windows (troubleshooting).

**Plugin**: `event_viewer`
- Paramètres: `log_name` (System, Application, Security), `level` (Error, Warning, Info)
- Output: Liste événements avec timestamp, source, message
- Frontend: Table événements filtrable

---

#### **13. Cron/Task Scheduler** ⏱️ 4h
**Use Case**: Planifier tâches récurrentes sur agents.

**Plugin**: `task_scheduler`
- Windows: Task Scheduler API
- Linux: crontab
- Actions: `list`, `create`, `delete`, `enable`, `disable`
- Frontend: Interface création tâches planifiées

---

#### **14. Docker Management (Linux)** ⏱️ 3h
**Use Case**: Gérer containers Docker sur agents Linux (333srv).

**Plugin**: `docker_manager`
- Actions: `list_containers`, `start`, `stop`, `restart`, `logs`, `inspect`
- Dépendance: Docker installé + agent user dans groupe docker
- Frontend: Table containers (ID, Image, Status, Ports, Actions)

---

#### **15. Video Stream (Webcam/Desktop)** ⏱️ 6h
**Use Case**: Stream vidéo temps réel depuis agent (surveillance, demo).

**Plugin**: `video_stream`
- Sources: Webcam, Desktop capture
- Codec: H.264 (compression)
- Transport: WebRTC ou MJPEG stream
- Frontend: Player vidéo intégré

---

## 🔒 Sécurité & Bonnes Pratiques

### **Authentification Agents**
- ✅ **Actuel**: Agent ID simple (pas d'auth forte)
- 🔴 **TODO**: Token JWT ou certificat client (TLS mutual auth)

### **Chiffrement Communications**
- ✅ WebSocket TLS (wss://)
- ✅ Checksum SHA256 fichiers transferts

### **Isolation Plugins**
- ⚠️ **Limitation**: Plugins exécutés dans même process agent
- 🟡 **Amélioration**: Sandbox subprocess ou containers (isolation mémoire)

### **Rate Limiting**
- ⚠️ **Manquant**: Aucun rate limit tasks Hub → Agent
- 🟡 **TODO**: Max 10 tasks/minute par agent (éviter flood)

### **Audit Logs**
- ✅ Logs streaming vers Hub (buffer 100 messages)
- 🟡 **Amélioration**: Persistance logs long-terme (DB ou fichiers)

---

## 📊 Matrice Priorisation Fonctionnalités

| Feature | Priorité | Temps | Complexité | Impact | Status |
|---------|----------|-------|------------|--------|--------|
| Auto-restart après update | 🔴 Haute | 1h | Faible | Élevé | TODO |
| Fix file lock replace | 🔴 Haute | 30m | Faible | Moyen | TODO |
| Métriques auto-update | 🔴 Haute | 1h | Faible | Moyen | TODO |
| Backend Restart/Update | 🔴 Haute | 2h | Moyen | Élevé | TODO |
| Remote shell exec | 🟡 Moyenne | 3h | Moyen | Élevé | TODO |
| File transfer | 🟡 Moyenne | 4h | Élevé | Élevé | TODO |
| Screenshot capture | 🟡 Moyenne | 2h | Faible | Moyen | TODO |
| Process manager | 🟡 Moyenne | 3h | Moyen | Moyen | TODO |
| Service manager | 🟡 Moyenne | 3h | Moyen | Moyen | TODO |
| Network diagnostics | 🟡 Moyenne | 2h | Faible | Moyen | TODO |
| Registry editor | 🔵 Basse | 4h | Élevé | Faible | TODO |
| Event Viewer | 🔵 Basse | 3h | Moyen | Faible | TODO |
| Task Scheduler | 🔵 Basse | 4h | Élevé | Faible | TODO |
| Docker manager | 🔵 Basse | 3h | Moyen | Faible | TODO |
| Video stream | 🔵 Basse | 6h | Très élevé | Faible | TODO |

---

## 🎯 Recommandations Prochaines Étapes

### **Sprint 1: Stabilisation Existant** (4h)
1. ✅ Auto-restart après self-update
2. ✅ Fix file lock replace
3. ✅ Métriques auto-update
4. ✅ Backend actions Restart/Update

**Objectif**: Rendre système actuel production-ready 100%

---

### **Sprint 2: Capacités Critiques** (8h)
1. ✅ Remote shell execution
2. ✅ File transfer (upload/download)
3. ✅ Screenshot capture

**Objectif**: Ajouter fonctionnalités essentielles contrôle à distance

---

### **Sprint 3: Monitoring Avancé** (8h)
1. ✅ Process manager
2. ✅ Service manager
3. ✅ Network diagnostics

**Objectif**: Outils troubleshooting et monitoring complets

---

### **Sprint 4: Fonctionnalités Avancées** (selon besoins)
- Registry editor
- Event Viewer
- Task Scheduler
- Docker manager
- Video stream

**Objectif**: Extensions selon use cases spécifiques

---

## 📝 Notes Techniques

### **Dépendances Python Agents**
```txt
websockets>=12.0      # WebSocket client
requests>=2.31.0      # HTTP requests (download updates)
psutil>=5.9.0         # System info cross-platform
pystray>=0.19.0       # Tray icon (Windows)
Pillow>=10.0.0        # Images (screenshots, tray icon)
pywin32>=306          # Windows API (LogMeIn, services, registry)
```

### **Plugins à Créer**
- `system_restart.py` (common)
- `remote_shell.py` (common)
- `file_transfer.py` (common)
- `screenshot.py` (common)
- `process_manager.py` (common)
- `service_manager.py` (windows/linux)
- `network_diagnostics.py` (common)

---

## ✅ Conclusion

**Système actuel**: Architecture solide, agents connectés, plugins fonctionnels, interface complète.

**Axes amélioration**:
1. **Stabilisation**: Auto-restart, métriques, actions backend
2. **Nouvelles capacités**: Remote shell, file transfer, screenshot
3. **Monitoring**: Process/service manager, network diagnostics
4. **Sécurité**: Auth forte, rate limiting, audit logs persistants

**Prêt pour**: Intégrer nouvelles fonctionnalités de manière incrémentale et testée.

---

**Auteur**: 333HOME Team  
**Dernière mise à jour**: 4 novembre 2025
