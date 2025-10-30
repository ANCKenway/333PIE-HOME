# 🪟 333HOME Agent - Installation Service Windows

## 📋 Table des Matières

- [Prérequis](#prérequis)
- [Installation Rapide](#installation-rapide)
- [Installation Détaillée](#installation-détaillée)
- [Gestion du Service](#gestion-du-service)
- [Mise à Jour](#mise-à-jour)
- [Logs et Monitoring](#logs-et-monitoring)
- [Désinstallation](#désinstallation)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## 🎯 Prérequis

### Système
- **Windows 10/11** ou Windows Server 2016+
- **Python 3.11+** installé ([python.org](https://www.python.org/downloads/))
- **Droits administrateur** (UAC)

### Réseau
- Accès au Hub 333HOME (via LAN ou Tailscale VPN)
- Connexion Internet pour téléchargement dépendances

### Vérification Python

```powershell
# Vérifier version Python
python --version

# Doit afficher: Python 3.11.x ou supérieur
# Si erreur: installer Python depuis python.org
```

---

## 🚀 Installation Rapide

### Installation en 1 Commande

```powershell
# 1. Ouvrir PowerShell en ADMINISTRATEUR (clic droit > "Exécuter en tant qu'administrateur")

# 2. Naviguer vers dossier déploiement
cd "C:\path\to\333HOME\src\agents\deployments\windows"

# 3. Lancer installation automatique
.\setup.ps1

# C'est tout ! L'agent est installé et démarre automatiquement
```

**Durée installation** : 2-3 minutes

**Ce qui se passe automatiquement** :
1. ✅ Vérification prérequis (Python, droits admin)
2. ✅ Téléchargement NSSM (service manager)
3. ✅ Téléchargement package agent depuis Hub
4. ✅ Installation dépendances Python
5. ✅ Configuration service Windows
6. ✅ Démarrage automatique agent
7. ✅ Connexion au Hub validée

### Installation Personnalisée

```powershell
# Avec paramètres personnalisés
.\setup.ps1 `
    -AgentId "LAPTOP01" `
    -HubUrl "ws://100.115.207.11:8000/api/agents/ws/agents" `
    -InstallPath "D:\333HOME Agent"
```

---

## 📚 Installation Détaillée

### Étape 1 : Télécharger Scripts

```powershell
# Option A : Clone Git repo complet
git clone https://github.com/ANCKenway/333PIE-HOME.git
cd 333PIE-HOME\src\agents\deployments\windows

# Option B : Télécharger seulement scripts Windows
Invoke-WebRequest -Uri "http://100.115.207.11:8000/static/agents/windows_installer.zip" -OutFile "installer.zip"
Expand-Archive installer.zip -DestinationPath .
```

### Étape 2 : Configurer Paramètres

Éditer les paramètres dans `setup.ps1` ou passer en arguments :

```powershell
# Paramètres disponibles
-AgentId "TITO"           # ID unique agent (défaut: nom PC)
-HubUrl "ws://..."        # URL WebSocket Hub
-InstallPath "C:\..."     # Dossier installation (défaut: Program Files)
-ServiceName "333HOME-Agent"  # Nom service Windows
-SkipNssm                 # Ne pas télécharger NSSM (déjà présent)
```

### Étape 3 : Lancer Installation

```powershell
# PowerShell en ADMINISTRATEUR obligatoire
.\setup.ps1 -AgentId "TITO" -HubUrl "ws://100.115.207.11:8000/api/agents/ws/agents"
```

### Étape 4 : Vérifier Installation

```powershell
# Vérifier statut service
.\service_manager.ps1 -Action status

# Ou via services.msc
services.msc
# Chercher "333HOME-Agent" dans la liste
```

**Output attendu** :
```
================================================================
  333HOME Agent - Service Status
================================================================

Service Name:    333HOME-Agent
Display Name:    333HOME-Agent
Status:          Running
Start Type:      Auto
Uptime:          2 hour(s) 15 min(s)

Install Path:    C:\Program Files\333HOME Agent
Stdout Log:      C:\Program Files\333HOME Agent\logs\agent_stdout.log
Stderr Log:      C:\Program Files\333HOME Agent\logs\agent_stderr.log

Recent logs (last 10 lines):
  2025-10-30 16:45:32 - INFO - [Agent] 333HOME Universal Agent v1.0.15
  2025-10-30 16:45:32 - INFO - Agent ID: TITO
  2025-10-30 16:45:33 - INFO - [OK] 3 plugins loaded
  2025-10-30 16:45:33 - INFO - [OK] Connected to Hub
  2025-10-30 16:45:33 - INFO - [HB] Heartbeat started (30s interval)
```

---

## 🎛️ Gestion du Service

### Via Script service_manager.ps1

```powershell
# Statut détaillé
.\service_manager.ps1 -Action status

# Démarrer service
.\service_manager.ps1 -Action start

# Arrêter service
.\service_manager.ps1 -Action stop

# Redémarrer service
.\service_manager.ps1 -Action restart

# Afficher logs temps réel
.\service_manager.ps1 -Action logs

# Mettre à jour agent
.\service_manager.ps1 -Action update -Version "1.0.16"
```

### Via PowerShell natif

```powershell
# Démarrer
Start-Service 333HOME-Agent

# Arrêter
Stop-Service 333HOME-Agent

# Redémarrer
Restart-Service 333HOME-Agent

# Statut
Get-Service 333HOME-Agent

# Statut détaillé
Get-Service 333HOME-Agent | Format-List *
```

### Via Interface Graphique services.msc

1. Appuyer sur **Win + R**
2. Taper `services.msc` et Entrée
3. Chercher `333HOME-Agent` dans la liste
4. Clic droit > **Démarrer / Arrêter / Redémarrer**
5. Double-clic > Onglet **Récupération** pour config restart automatique

**Configuration recommandée Récupération** :
- Première défaillance : **Redémarrer le service**
- Deuxième défaillance : **Redémarrer le service**
- Défaillances suivantes : **Redémarrer le service**
- Réinitialiser le compteur après : **1 jour**
- Redémarrer après : **5 secondes**

---

## 🔄 Mise à Jour

### Mise à Jour Automatique (Recommandé)

```powershell
# Depuis Hub 333PIE - Envoyer tâche self_update à l'agent
curl -X POST 'http://localhost:8000/api/agents/TITO/tasks' `
  -H 'Content-Type: application/json' `
  -d '{
    "plugin": "self_update",
    "params": {
      "version": "1.0.16",
      "download_url": "http://100.115.207.11:8000/static/agents/agent_v1.0.16.zip",
      "checksum": "abc123...",
      "force": false
    }
  }'

# Agent télécharge automatiquement, backup, extrait et signale restart requis
# Redémarrer service pour charger nouvelle version:
.\service_manager.ps1 -Action restart
```

**Workflow auto-update** :
1. Hub envoie tâche `self_update` via WebSocket
2. Agent télécharge package depuis Hub
3. Agent vérifie checksum SHA256
4. Agent crée backup dans `.backup/`
5. Agent extrait nouvelle version
6. Agent remplace fichiers
7. **Agent retourne succès** (reste connecté)
8. **User redémarre service manuellement** pour charger nouvelle version

### Mise à Jour Manuelle (Script)

```powershell
# Avec service_manager.ps1
.\service_manager.ps1 -Action update -Version "1.0.16"

# OU version latest
.\service_manager.ps1 -Action update -Version "latest"
```

**Ce qui se passe** :
1. Service arrêté
2. Backup version actuelle dans `.backup_YYYYMMDD_HHMMSS/`
3. Téléchargement nouvelle version depuis Hub
4. Extraction et remplacement fichiers
5. Service redémarré automatiquement
6. Validation connexion Hub

### Rollback Version Précédente

```powershell
# Arrêter service
Stop-Service 333HOME-Agent

# Naviguer vers installation
cd "C:\Program Files\333HOME Agent"

# Lister backups disponibles
Get-ChildItem -Filter ".backup*"

# Restaurer backup
$backupDir = ".backup_20251030_163400"
Copy-Item -Path "$backupDir\*" -Destination . -Recurse -Force

# Redémarrer service
Start-Service 333HOME-Agent

# Vérifier version restaurée
.\service_manager.ps1 -Action status
```

---

## 📊 Logs et Monitoring

### Localisation Logs

```
C:\Program Files\333HOME Agent\logs\
├── agent_stdout.log       # Logs principaux (INFO, WARNING, ERROR)
├── agent_stderr.log       # Erreurs Python (tracebacks)
└── archive\               # Logs archivés (rotation automatique)
```

### Afficher Logs Temps Réel

```powershell
# Via service_manager
.\service_manager.ps1 -Action logs

# Via PowerShell natif (tail -f style)
Get-Content "C:\Program Files\333HOME Agent\logs\agent_stdout.log" -Tail 50 -Wait

# Chercher erreurs
Select-String -Path "C:\Program Files\333HOME Agent\logs\agent_stdout.log" -Pattern "ERROR"
```

### Rotation Logs Automatique

Configuré via NSSM :
- **Taille max fichier** : 10 MB
- **Rotation** : Automatique quand limite atteinte
- **Nom fichier roté** : `agent_stdout.log.1`, `agent_stdout.log.2`, etc.

### Monitoring Service

```powershell
# Statut détaillé avec uptime
.\service_manager.ps1 -Action status

# Vérifier connexion au Hub depuis 333PIE
curl http://localhost:8000/api/agents | ConvertFrom-Json

# Output attendu:
# {
#   "agent_id": "TITO",
#   "connected": true,
#   "plugins": ["self_update", "system_info", "logmein_rescue"],
#   "last_heartbeat": "2025-10-30T18:45:32.123456"
# }
```

### Logs Windows Event Viewer

Le service génère aussi des événements dans **Event Viewer** :
1. Ouvrir **Event Viewer** (eventvwr.msc)
2. Naviguer : **Windows Logs > Application**
3. Filtrer par source : **333HOME-Agent**

---

## 🗑️ Désinstallation

### Désinstallation Complète

```powershell
# PowerShell en ADMINISTRATEUR
cd "C:\path\to\333HOME\src\agents\deployments\windows"

# Désinstallation avec confirmation
.\uninstall.ps1

# Désinstallation sans confirmation + conservation logs
.\uninstall.ps1 -Force -KeepLogs
```

**Ce qui est supprimé** :
- ✅ Service Windows 333HOME-Agent
- ✅ Dossier `C:\Program Files\333HOME Agent\`
- ✅ Fichiers temporaires
- ⚠️ Logs conservés si `-KeepLogs` spécifié (dans `Documents\333HOME\logs_backup_*`)

### Désinstallation Manuelle

Si script échoue :

```powershell
# 1. Arrêter et supprimer service
Stop-Service 333HOME-Agent -Force
sc.exe delete 333HOME-Agent

# 2. Supprimer dossier installation
Remove-Item -Recurse -Force "C:\Program Files\333HOME Agent"

# 3. Vérifier services.msc
services.msc
# Service ne doit plus apparaître dans la liste
```

---

## 🔧 Troubleshooting

### Service ne démarre pas

**Symptômes** : Service status "Stopped" immédiatement après démarrage

**Diagnostic** :
```powershell
# Vérifier logs stderr
Get-Content "C:\Program Files\333HOME Agent\logs\agent_stderr.log" -Tail 50

# Chercher erreurs Python
Select-String -Pattern "Error|Exception|Traceback" -Path "C:\Program Files\333HOME Agent\logs\*.log"
```

**Causes fréquentes** :
1. **Python non trouvé** : Vérifier `python --version` en console admin
2. **Dépendances manquantes** : Réinstaller `pip install -r requirements.txt`
3. **Port déjà utilisé** : Vérifier aucun autre agent actif
4. **Permissions** : Service doit avoir droits lecture/écriture sur dossier install

**Solution** :
```powershell
# Tester agent manuellement
cd "C:\Program Files\333HOME Agent"
python agent.py --agent-id TITO --hub-url ws://100.115.207.11:8000/api/agents/ws/agents

# Si fonctionne en manuel mais pas en service: problème droits NSSM
# Réinstaller avec setup.ps1
```

### Agent ne se connecte pas au Hub

**Symptômes** : Service running mais pas visible dans Hub dashboard

**Diagnostic** :
```powershell
# Vérifier logs connexion
Select-String -Pattern "Connected|Connection|WebSocket" -Path "C:\Program Files\333HOME Agent\logs\agent_stdout.log" -Tail 20

# Tester connectivité réseau
Test-NetConnection -ComputerName 100.115.207.11 -Port 8000

# Vérifier URL Hub correcte
Get-Content "C:\Program Files\333HOME Agent\agent_config.txt"
```

**Causes fréquentes** :
1. **Hub URL incorrecte** : Vérifier `ws://` vs `wss://`, IP, port
2. **Firewall bloque** : Autoriser Python dans Windows Defender Firewall
3. **Hub offline** : Vérifier Hub 333PIE actif sur port 8000
4. **VPN Tailscale** : Si utilise Tailscale, vérifier IP VPN correcte

**Solution** :
```powershell
# Tester Hub accessible
curl http://100.115.207.11:8000/api/agents

# Si timeout: problème réseau/firewall
# Si 200 OK: problème URL WebSocket dans agent

# Corriger URL et redémarrer
# Éditer C:\Program Files\333HOME Agent\agent_config.txt
.\service_manager.ps1 -Action restart
```

### Logs erreurs Unicode (Windows cp1252)

**Symptômes** : `UnicodeEncodeError: 'charmap' codec can't encode character`

**Solution** : Mettre à jour vers **v1.0.13+** (corrections Unicode appliquées)

```powershell
.\service_manager.ps1 -Action update -Version "latest"
```

### Service crash après update

**Symptômes** : Service running avant update, stopped après

**Diagnostic** :
```powershell
# Vérifier logs erreur
Get-Content "C:\Program Files\333HOME Agent\logs\agent_stderr.log" -Tail 50

# Lister backups disponibles
Get-ChildItem "C:\Program Files\333HOME Agent" -Filter ".backup*"
```

**Solution Rollback** :
```powershell
# Arrêter service
Stop-Service 333HOME-Agent

# Restaurer backup le plus récent
$latestBackup = Get-ChildItem "C:\Program Files\333HOME Agent" -Filter ".backup*" | 
                Sort-Object LastWriteTime -Descending | 
                Select-Object -First 1

Copy-Item -Path "$($latestBackup.FullName)\*" -Destination "C:\Program Files\333HOME Agent" -Recurse -Force

# Redémarrer
Start-Service 333HOME-Agent
```

### Service redémarre en boucle

**Symptômes** : Service démarre puis crash toutes les 5 secondes

**Cause** : Configuration NSSM restart automatique + erreur au démarrage

**Solution** :
```powershell
# Désactiver restart auto temporairement
$nssmPath = "C:\path\to\nssm.exe"
& $nssmPath set 333HOME-Agent AppExit Default Exit

# Tester démarrage manuel
cd "C:\Program Files\333HOME Agent"
python agent.py --agent-id TITO --hub-url ws://... --log-level DEBUG

# Corriger erreur identifiée
# Réactiver restart auto
& $nssmPath set 333HOME-Agent AppExit Default Restart
```

---

## ❓ FAQ

### Puis-je installer plusieurs agents sur le même PC ?

Oui, mais nécessite configurations distinctes :

```powershell
# Agent 1
.\setup.ps1 -AgentId "LAPTOP-WORK" -ServiceName "333HOME-Work" -InstallPath "C:\Program Files\333HOME Work"

# Agent 2  
.\setup.ps1 -AgentId "LAPTOP-PERSO" -ServiceName "333HOME-Perso" -InstallPath "C:\Program Files\333HOME Perso"
```

### Le service démarre-t-il au boot Windows ?

Oui ! Configuré en démarrage automatique (`SERVICE_AUTO_START`). L'agent démarre **avant** le login utilisateur.

### Puis-je utiliser un proxy ?

Oui, configurer variables environnement Python :

```powershell
# Éditer service NSSM
$nssmPath = "C:\path\to\nssm.exe"
& $nssmPath set 333HOME-Agent AppEnvironmentExtra HTTP_PROXY=http://proxy:8080
& $nssmPath set 333HOME-Agent AppEnvironmentExtra HTTPS_PROXY=http://proxy:8080

# Redémarrer
Restart-Service 333HOME-Agent
```

### Comment changer l'URL du Hub après installation ?

```powershell
# Arrêter service
Stop-Service 333HOME-Agent

# Éditer configuration
notepad "C:\Program Files\333HOME Agent\agent_config.txt"
# Modifier ligne HUB_URL=...

# Redémarrer
Start-Service 333HOME-Agent
```

### Le service utilise-t-il beaucoup de ressources ?

Non, très léger :
- **CPU** : < 1% (idle), 2-5% (tâches actives)
- **RAM** : ~50 MB
- **Réseau** : ~1 KB/s (heartbeat 30s)

### Puis-je voir l'agent dans le gestionnaire de tâches ?

Oui ! Chercher processus **python.exe** avec ligne de commande contenant `agent.py`.

**Détails processus** :
- **Nom** : python.exe
- **Utilisateur** : SYSTEM (service)
- **Command Line** : `python.exe agent.py --agent-id TITO --hub-url ws://...`

---

## 📞 Support

### Logs utiles pour debugging

Avant de demander du support, collecter :

```powershell
# 1. Version agent
Get-Content "C:\Program Files\333HOME Agent\agent.py" | Select-String -Pattern "version"

# 2. Logs récents
Get-Content "C:\Program Files\333HOME Agent\logs\agent_stdout.log" -Tail 100 > debug_stdout.txt
Get-Content "C:\Program Files\333HOME Agent\logs\agent_stderr.log" -Tail 100 > debug_stderr.txt

# 3. Statut service
Get-Service 333HOME-Agent | Format-List * > debug_service.txt

# 4. Configuration
Get-Content "C:\Program Files\333HOME Agent\agent_config.txt" > debug_config.txt

# 5. Version Python
python --version > debug_python.txt
```

### Contact

- **Repository** : https://github.com/ANCKenway/333PIE-HOME
- **Issues** : https://github.com/ANCKenway/333PIE-HOME/issues
- **Documentation** : `/docs/`

---

## 🎉 C'est tout !

Votre agent 333HOME est maintenant installé en tant que **service Windows professionnel** :

✅ Démarrage automatique au boot  
✅ Restart automatique en cas de crash  
✅ Gestion via services.msc  
✅ Logs persistants et rotation automatique  
✅ Mise à jour simplifiée  
✅ Aucune console visible  

**Profitez de votre agent 24/7 en arrière-plan !** 🚀
