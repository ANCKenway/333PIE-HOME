# 🪟 333HOME Agent - Déploiement Windows

Installation automatique ultra-simple avec **icône dans la barre des tâches** pour contrôler l'agent facilement !

## 🚀 Installation Rapide (RECOMMANDÉ)

```batch
# Clic droit > "Exécuter en tant qu'administrateur"
install.bat
```

**C'est tout !** L'agent s'installe automatiquement avec :
- ✅ Icône tray (🟢 H) dans la barre des tâches
- ✅ Démarrage automatique au login Windows
- ✅ Menu clic droit : View Logs, Restart, Settings, Quit
- ✅ Configuration automatique (hostname → agent_id)

**Durée** : 30 secondes ⚡

---

## 📁 Fichiers

| Fichier | Description |
|---------|-------------|
| **install.bat** | 🎯 Installation automatique complète (RECOMMANDÉ) |
| **uninstall.bat** | 🗑️ Désinstallation propre avec backup logs |
| **agent_tray.pyw** | 🖼️ Wrapper avec icône tray (lancé automatiquement) |
| ~~setup.ps1~~ | ❌ Ancien script complexe (déprécié) |
| ~~service_manager.ps1~~ | ❌ Remplacé par menu tray |

---

## 🎛️ Utilisation

### Icône Tray

Après installation, cherchez l'icône **🟢 H** près de l'horloge (coins bas-droite).

**Clic droit sur l'icône** :
- **🟢/🔴 Agent Status** : Connected / Disconnected
- **📄 View Logs** : Ouvre le fichier de logs
- **🔄 Restart Agent** : Redémarre l'agent
- **⚙️ Settings** : Configuration (à venir)
- **ℹ️ About** : Informations agent
- **🚪 Quit** : Quitter (arrête l'agent)

### Couleurs Icône

- **🟢 Vert** : Agent connecté au Hub
- **🔴 Rouge** : Agent déconnecté
- **🟡 Jaune** : Agent en démarrage

---

## 🧪 Cas d'Usage

### Installation Standard

```batch
REM Clic droit > "Exécuter en tant qu'administrateur"
install.bat

REM L'agent utilise automatiquement :
REM - Agent ID : Nom de l'ordinateur (ex: TITO, LAPTOP01)
REM - Hub URL : ws://100.115.207.11:8000/api/agents/ws/agents
```

### Vérifier Installation

```batch
REM Chercher icône "H" dans la barre des tâches
REM Clic droit > About pour voir infos

REM OU vérifier processus
tasklist | findstr pythonw.exe

REM OU vérifier logs
notepad "%ProgramFiles%\333HOME Agent\logs\agent_stdout.log"
```

### Désinstallation

```batch
REM Clic droit > "Exécuter en tant qu'administrateur"
uninstall.bat

REM Supprime tout proprement + backup logs dans Documents\333HOME
```

---

## 🏗️ Architecture

### Avant (Scripts PowerShell Complexes)
```
❌ Scripts PowerShell multiples
❌ NSSM à télécharger
❌ Configuration manuelle nécessaire
❌ Gestion via services.msc seulement
❌ Logs difficiles d'accès
```

### Maintenant (Simple .BAT + Tray Icon)
```
✅ 1 seul fichier install.bat
✅ Tout automatique (0 configuration)
✅ Icône tray pour contrôle facile
✅ Clic droit > View Logs / Restart
✅ Démarrage auto au login
✅ Raccourci Bureau créé
```

### Workflow install.bat

```
install.bat
├── 1. Vérifier droits admin
├── 2. Vérifier Python installé
├── 3. Créer dossier C:\Program Files\333HOME Agent
├── 4. Télécharger agent_latest.zip depuis Hub
├── 5. Extraire fichiers agent + agent_tray.pyw
├── 6. Installer dépendances pip (websockets, pystray, Pillow)
├── 7. Générer tray_config.json auto (hostname, hub URL)
├── 8. Créer tâche planifiée (trigger: login utilisateur)
├── 9. Créer raccourci Bureau "333HOME Agent"
└── 10. Lancer agent_tray.pyw (icône apparaît dans tray)
```

### Architecture agent_tray.pyw

```
agent_tray.pyw (pythonw = pas de console)
├── Lance agent.py en subprocess
├── Crée icône tray avec menu contextuel
├── Thread monitoring :
│   ├── Vérifie processus agent actif
│   ├── Restart auto si crash
│   ├── Parse logs pour status connexion
│   └── Met à jour couleur icône (vert/rouge)
└── Gestion événements menu :
    ├── View Logs → ouvre notepad
    ├── Restart → kill + relance agent
    ├── Settings → dialog config (TODO)
    └── Quit → arrête agent + ferme tray
```

---

## 🔧 Prérequis

### Système
- **Windows 10/11** ou Windows Server 2016+
- **Python 3.11+** ([python.org](https://www.python.org/downloads/))
- **Droits administrateur** (UAC)

### Réseau
- Accès au Hub 333HOME (LAN ou Tailscale VPN)
- Hub doit servir `agent_latest.zip` sur `http://HUB_IP:8000/static/agents/`

### Vérification

```powershell
# Python OK ?
python --version
# Output: Python 3.11.x ou supérieur

# Admin OK ?
[Security.Principal.WindowsIdentity]::GetCurrent().Groups -contains 'S-1-5-32-544'
# Output: True

# Hub accessible ?
Test-NetConnection -ComputerName 100.115.207.11 -Port 8000
# Output: TcpTestSucceeded : True
```

---

## 📊 Service Configuration (NSSM)

### Paramètres Service

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| **Service Name** | 333HOME-Agent | Nom interne Windows |
| **Display Name** | 333HOME-Agent | Nom affiché services.msc |
| **Description** | 333HOME Remote Control Agent | Description service |
| **Start Type** | Automatic | Démarrage auto au boot |
| **Account** | LocalSystem | Compte exécution (droits admin) |

### Paramètres Application

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| **Path** | C:\...\python.exe | Exécutable Python |
| **Startup Directory** | C:\Program Files\333HOME Agent | Dossier travail |
| **Arguments** | agent.py --agent-id ... --hub-url ... | Arguments agent |

### Paramètres Restart

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| **Action on Exit** | Restart | Toujours redémarrer |
| **Restart Delay** | 5000 ms | Délai avant restart |
| **Throttle** | 1500 ms | Délai minimum entre restarts |

### Paramètres Logs

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| **Stdout** | logs\agent_stdout.log | Logs standard |
| **Stderr** | logs\agent_stderr.log | Logs erreurs |
| **Rotate** | Enabled | Rotation automatique |
| **Rotate Size** | 10485760 bytes (10 MB) | Taille max avant rotation |

---

## 🧪 Tests

### Test Installation

```powershell
# Après setup.ps1, vérifier :

# 1. Service existe et running
Get-Service 333HOME-Agent
# Status: Running

# 2. Processus Python actif
Get-Process | Where-Object { $_.Name -eq "python" -and $_.Path -like "*333HOME Agent*" }
# Doit retourner processus

# 3. Logs générés
Get-ChildItem "C:\Program Files\333HOME Agent\logs"
# Doit lister agent_stdout.log et agent_stderr.log

# 4. Agent connecté au Hub (depuis 333PIE)
curl http://localhost:8000/api/agents
# Doit afficher agent TITO connected:true
```

### Test Restart Automatique

```powershell
# Simuler crash agent
Stop-Process -Name python -Force

# Attendre 5 secondes
Start-Sleep -Seconds 6

# Vérifier service redémarré
Get-Service 333HOME-Agent
# Status devrait être "Running" à nouveau
```

### Test Démarrage Auto Boot

```powershell
# Redémarrer Windows
Restart-Computer

# Après login, vérifier service démarré automatiquement
Get-Service 333HOME-Agent
# Status: Running (démarré avant login)
```

---

## 🐛 Troubleshooting Rapide

| Problème | Solution Rapide |
|----------|-----------------|
| ❌ Service ne démarre pas | Vérifier logs stderr : `Get-Content "C:\...\agent_stderr.log" -Tail 20` |
| ❌ Agent pas visible dans Hub | Tester URL : `Test-NetConnection -ComputerName HUB_IP -Port 8000` |
| ❌ Python not found | Réinstaller Python et cocher "Add to PATH" |
| ❌ Access denied | Lancer PowerShell en ADMINISTRATEUR |
| ❌ Module not found (aiohttp) | Réinstaller dépendances : `pip install -r requirements.txt` |

Voir **[SERVICE_INSTALLATION.md](../../../docs/SERVICE_INSTALLATION.md#troubleshooting)** pour troubleshooting détaillé.

---

## 🔗 Liens Utiles

- **Documentation complète** : [SERVICE_INSTALLATION.md](../../../docs/SERVICE_INSTALLATION.md)
- **Architecture agents** : [AGENTS_ARCHITECTURE.md](../../../docs/AGENTS_ARCHITECTURE.md)
- **Mise à jour agent** : [UPDATE_AGENT_v1.0.13.md](../../../docs/UPDATE_AGENT_v1.0.13.md)
- **NSSM Documentation** : [nssm.cc](https://nssm.cc/)
- **Repository GitHub** : [333PIE-HOME](https://github.com/ANCKenway/333PIE-HOME)

---

## 📝 Changelog Scripts

### v1.0.0 (2025-10-30)
- ✅ setup.ps1 : Installation automatique complète
- ✅ uninstall.ps1 : Désinstallation propre avec backup logs
- ✅ service_manager.ps1 : Gestion service (start/stop/restart/logs/update)
- ✅ download_nssm.ps1 : Téléchargement NSSM depuis nssm.cc
- ✅ Documentation SERVICE_INSTALLATION.md complète
- ✅ Intégration self_update plugin avec restart manuel
- ✅ Configuration NSSM : restart auto, logs rotatifs, démarrage auto

---

## 🎉 Résultat Final

**Avant** : Console PowerShell à laisser ouverte, arrêt manuel, pas de logs

**Après** :
```powershell
PS C:\> Get-Service 333HOME-Agent

Status   Name               DisplayName
------   ----               -----------
Running  333HOME-Agent      333HOME-Agent
```

✨ **Service Windows professionnel 24/7** ✨

**Aucune console visible, démarrage automatique, restart auto, logs persistants !**
