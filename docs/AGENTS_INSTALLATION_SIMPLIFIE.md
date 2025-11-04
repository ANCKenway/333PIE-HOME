# 🚀 Installation Agents 333HOME - Processus Simplifié

**Date**: 4 novembre 2025  
**Version**: 2.0 (Unifié & Automatisé)

---

## 🎯 Problèmes Identifiés (Avant Simplification)

### ❌ **État Actuel - Complexe et Fragmenté**

1. **Scripts packaging multiples**:
   - `create_agent_package.sh` (ancien)
   - `create_agent_v1.0.17.sh` (récent)
   - Duplication logique, confusion version

2. **Installation Windows manuelle**:
   - `install.bat` hardcodé avec IP statique Hub
   - Config `tray_config.json` manuel
   - Pas d'auto-découverte Hub activée
   - Dépendances pip une par une (lent)

3. **Pas d'installation Linux**:
   - Aucun script install automatique
   - Pas de systemd service configuré
   - Process manuel complet

4. **Pas de gestion centralisée**:
   - Création package Hub → Agents séparée
   - Pas de versionning auto
   - Pas de rollback si échec update

5. **Scripts Hub dispersés**:
   - `start.sh` pour Hub (FastAPI)
   - `stop.sh` nettoyage
   - Pas de script agents séparé

---

## ✅ Solution - Architecture Unifiée

### 🏗️ **Nouvelle Structure**

```
333HOME/
├── scripts/
│   ├── hub/                        # Scripts Hub uniquement
│   │   ├── start.sh                # Démarrer Hub FastAPI
│   │   ├── stop.sh                 # Arrêter Hub
│   │   └── restart.sh              # Redémarrer Hub
│   │
│   └── agents/                     # Scripts Agents
│       ├── package_agent.sh        # ⭐ Script unique packaging
│       ├── deploy_windows.ps1      # Installation Windows auto
│       ├── deploy_linux.sh         # Installation Linux auto
│       └── README.md               # Documentation
│
├── src/agents/
│   ├── agent.py                    # Agent principal
│   ├── agent_tray.pyw              # Tray icon Windows
│   ├── config.py                   # Config auto-découverte Hub
│   ├── hub_discovery.py            # Auto-discovery mDNS + Tailscale
│   ├── version.py                  # Version centralisée
│   ├── requirements.txt            # Dépendances agents
│   │
│   ├── plugins/                    # Plugins extensibles
│   │   ├── common/
│   │   │   ├── system_info.py
│   │   │   ├── self_update.py      # ⭐ À améliorer (auto-restart)
│   │   │   └── system_restart.py   # ⭐ NOUVEAU
│   │   └── windows/
│   │       └── logmein_rescue.py
│   │
│   └── installers/                 # ⭐ NOUVEAU - Templates installers
│       ├── windows/
│       │   ├── install_template.bat
│       │   └── uninstall.bat
│       └── linux/
│           ├── install_template.sh
│           ├── uninstall.sh
│           └── agent.service       # Systemd service
│
└── static/agents/                  # Packages agents déployés
    ├── agent_v1.0.18.zip
    ├── agent_latest.zip -> agent_v1.0.18.zip
    └── checksums.json              # ⭐ NOUVEAU - Historique versions
```

---

## 🚀 Workflow Simplifié

### **1. Package Agent (Hub)** - 1 commande

```bash
# Script unique avec auto-incrément version
./scripts/agents/package_agent.sh

# Génère automatiquement:
# - static/agents/agent_vX.Y.Z.zip (nouvelle version)
# - static/agents/agent_latest.zip (symlink)
# - static/agents/checksums.json (historique)
# - scripts/agents/installers/ (templates avec version injectée)
```

**Fonctionnalités**:
- ✅ Auto-incrément version (lit `version.py`)
- ✅ Build ZIP propre (exclusion __pycache__, .backup, etc.)
- ✅ Calcul checksum SHA256
- ✅ Génération installers avec version/checksum injectés
- ✅ Historique versions JSON
- ✅ Affichage commandes curl deploy prêtes à copier

---

### **2. Installation Windows** - 1 fichier

```powershell
# Télécharger installer depuis Hub
curl -O http://333pie.local:8000/static/agents/installers/install_windows.bat

# Double-clic install_windows.bat
# → Auto-détection Hub (mDNS → Tailscale)
# → Download dernière version
# → Installation dépendances
# → Tray icon auto-start
# → Service Windows (démarrage auto)
```

**Améliorations vs Ancien**:
- ✅ **Auto-découverte Hub** (pas d'IP hardcodée)
- ✅ **Version dynamique** (télécharge `agent_latest.zip`)
- ✅ **Dépendances bulk** (`pip install -r requirements.txt`)
- ✅ **Service Windows** (au lieu de tâche planifiée)
- ✅ **Logs structurés** (rotation automatique)

---

### **3. Installation Linux** - 1 commande

```bash
# Installation one-liner
curl -fsSL http://333pie.local:8000/static/agents/installers/install_linux.sh | sudo bash

# Ou manuel
wget http://333pie.local:8000/static/agents/installers/install_linux.sh
chmod +x install_linux.sh
sudo ./install_linux.sh
```

**Fonctionnalités**:
- ✅ **Systemd service** (démarrage auto, restart si crash)
- ✅ **User dédié** `333agent` (isolation sécurité)
- ✅ **Auto-découverte Hub** (mDNS prioritaire)
- ✅ **Logs systemd** (`journalctl -u 333agent`)
- ✅ **Uninstall propre** (`sudo systemctl disable 333agent`)

---

## 📋 Scripts à Créer

### **1. `scripts/agents/package_agent.sh`** ⭐ PRIORITÉ

**Objectif**: Script unique pour packager agents avec toutes les métadonnées.

**Fonctionnalités**:
```bash
#!/bin/bash
# Package agent avec auto-incrément version

# 1. Lire version actuelle (version.py)
CURRENT_VERSION=$(grep '__version__' src/agents/version.py | cut -d'"' -f2)

# 2. Incrémenter patch (1.0.17 → 1.0.18)
NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{$NF+=1; print $1"."$2"."$NF}')

# 3. Confirmer utilisateur
echo "Version actuelle: $CURRENT_VERSION"
echo "Nouvelle version: $NEW_VERSION"
read -p "Continuer? (y/N) " -n 1 -r
[[ ! $REPLY =~ ^[Yy]$ ]] && exit 0

# 4. Mettre à jour version.py
sed -i "s/__version__ = \"$CURRENT_VERSION\"/__version__ = \"$NEW_VERSION\"/" src/agents/version.py

# 5. Créer ZIP propre
cd src/agents
zip -r "../../static/agents/agent_v${NEW_VERSION}.zip" . \
    -x "*.pyc" "*__pycache__*" "*.backup*" "*.log" "test_*"

# 6. Calculer checksum
CHECKSUM=$(sha256sum "../../static/agents/agent_v${NEW_VERSION}.zip" | awk '{print $1}')

# 7. Créer symlink latest
cd ../../static/agents
ln -sf "agent_v${NEW_VERSION}.zip" agent_latest.zip

# 8. Mettre à jour checksums.json
echo "{\"version\":\"$NEW_VERSION\",\"checksum\":\"$CHECKSUM\",\"date\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" \
    | jq ".versions[\"$NEW_VERSION\"] = ." checksums.json > checksums.json.tmp
mv checksums.json.tmp checksums.json

# 9. Générer installers avec version injectée
sed "s/{{VERSION}}/$NEW_VERSION/g; s/{{CHECKSUM}}/$CHECKSUM/g" \
    src/agents/installers/windows/install_template.bat > \
    static/agents/installers/install_windows.bat

sed "s/{{VERSION}}/$NEW_VERSION/g; s/{{CHECKSUM}}/$CHECKSUM/g" \
    src/agents/installers/linux/install_template.sh > \
    static/agents/installers/install_linux.sh

# 10. Afficher résumé + commandes deploy
echo "✅ Package v${NEW_VERSION} créé!"
echo ""
echo "📦 Fichiers générés:"
echo "  - static/agents/agent_v${NEW_VERSION}.zip"
echo "  - static/agents/agent_latest.zip (symlink)"
echo "  - static/agents/checksums.json (updated)"
echo "  - static/agents/installers/install_windows.bat"
echo "  - static/agents/installers/install_linux.sh"
echo ""
echo "🚀 Commandes déploiement:"
echo ""
echo "# Windows (TITO)"
echo "curl -O http://333pie.local:8000/static/agents/installers/install_windows.bat"
echo ""
echo "# Linux (333srv)"
echo "curl -fsSL http://333pie.local:8000/static/agents/installers/install_linux.sh | sudo bash"
echo ""
echo "# Update via API"
echo "curl -X POST http://333pie.local:8000/api/agents/TITO/update"
```

---

### **2. `src/agents/installers/windows/install_template.bat`** ⭐ PRIORITÉ

**Améliorations vs ancien install.bat**:

```bat
@echo off
REM Auto-généré par package_agent.sh
REM Version: {{VERSION}}
REM Checksum: {{CHECKSUM}}

REM ⭐ AMÉLIORATION 1: Auto-découverte Hub (pas d'IP hardcodée)
set "HUB_URL=auto"
set "AUTO_DISCOVER=true"

REM ⭐ AMÉLIORATION 2: Version dynamique (pas hardcodée)
set "AGENT_VERSION={{VERSION}}"
set "PACKAGE_CHECKSUM={{CHECKSUM}}"

REM ⭐ AMÉLIORATION 3: Installation dépendances bulk
python -m pip install -r "%INSTALL_DIR%\requirements.txt" --quiet

REM ⭐ AMÉLIORATION 4: Service Windows (pas tâche planifiée)
REM Utiliser NSSM (Non-Sucking Service Manager) pour robustesse
nssm install "333HOME Agent" "%PYTHONW_PATH%" "%INSTALL_DIR%\agent_tray.pyw"
nssm set "333HOME Agent" AppDirectory "%INSTALL_DIR%"
nssm set "333HOME Agent" DisplayName "333HOME Remote Agent"
nssm set "333HOME Agent" Start SERVICE_AUTO_START
sc start "333HOME Agent"

REM ⭐ AMÉLIORATION 5: Config auto-découverte
REM Pas de tray_config.json, utilise hub_discovery.py

REM ⭐ AMÉLIORATION 6: Logs rotation automatique
REM Configuré dans agent.py avec RotatingFileHandler
```

---

### **3. `src/agents/installers/linux/install_template.sh`** ⭐ NOUVEAU

```bash
#!/bin/bash
# Auto-généré par package_agent.sh
# Version: {{VERSION}}
# Checksum: {{CHECKSUM}}

set -e

VERSION="{{VERSION}}"
CHECKSUM="{{CHECKSUM}}"
INSTALL_DIR="/opt/333home-agent"
SERVICE_USER="333agent"
HUB_URL="http://333pie.local:8000"

echo "================================================================"
echo "  333HOME Agent Linux Installer v${VERSION}"
echo "================================================================"

# Vérifier root
[[ $EUID -ne 0 ]] && echo "❌ Doit être exécuté en root (sudo)" && exit 1

# Installer dépendances système
apt-get update -qq
apt-get install -y python3 python3-pip python3-venv curl unzip

# Créer user dédié
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/false -d "$INSTALL_DIR" "$SERVICE_USER"
fi

# Télécharger package
mkdir -p "$INSTALL_DIR"
curl -fsSL "${HUB_URL}/static/agents/agent_latest.zip" -o /tmp/agent.zip

# Vérifier checksum
DOWNLOADED_CHECKSUM=$(sha256sum /tmp/agent.zip | awk '{print $1}')
[[ "$DOWNLOADED_CHECKSUM" != "$CHECKSUM" ]] && \
    echo "❌ Checksum mismatch" && exit 1

# Extraire
unzip -q /tmp/agent.zip -d "$INSTALL_DIR"
rm /tmp/agent.zip

# Créer venv et installer dépendances
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install -q -r "$INSTALL_DIR/requirements.txt"

# Permissions
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
chmod 750 "$INSTALL_DIR"

# Créer systemd service
cat > /etc/systemd/system/333agent.service <<EOF
[Unit]
Description=333HOME Remote Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/agent.py --agent-id $(hostname)
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Activer et démarrer
systemctl daemon-reload
systemctl enable 333agent
systemctl start 333agent

echo "✅ Installation terminée!"
echo ""
echo "📋 Commandes utiles:"
echo "  systemctl status 333agent      # Statut"
echo "  journalctl -u 333agent -f      # Logs temps réel"
echo "  systemctl restart 333agent     # Redémarrer"
echo "  systemctl stop 333agent        # Arrêter"
echo ""
```

---

### **4. `src/agents/plugins/common/system_restart.py`** ⭐ NOUVEAU

```python
"""
Plugin System Restart - Redémarrer agent ou machine
"""

from ..base import BasePlugin, PluginParams, PluginResult
from pydantic import Field
import subprocess
import platform
import sys
import os

class SystemRestartParams(PluginParams):
    target: str = Field(
        default="agent",
        description="Cible restart: 'agent' ou 'system'"
    )
    delay: int = Field(
        default=5,
        ge=0,
        le=300,
        description="Délai avant restart (secondes)"
    )

class SystemRestartPlugin(BasePlugin):
    name = "system_restart"
    description = "Redémarrer agent ou machine"
    version = "1.0.0"
    os_platform = "all"
    
    async def execute(self, params: dict) -> PluginResult:
        params = SystemRestartParams(**params)
        
        if params.target == "agent":
            return await self._restart_agent(params.delay)
        elif params.target == "system":
            return await self._restart_system(params.delay)
        else:
            return PluginResult(
                status="error",
                message=f"Invalid target: {params.target}"
            )
    
    async def _restart_agent(self, delay: int) -> PluginResult:
        """Redémarre l'agent lui-même"""
        os_name = platform.system()
        
        if os_name == "Windows":
            # Windows: Restart service via sc
            subprocess.Popen(
                f'timeout {delay} && sc stop "333HOME Agent" && sc start "333HOME Agent"',
                shell=True,
                creationflags=subprocess.DETACHED_PROCESS
            )
        else:
            # Linux: Restart systemd service
            subprocess.Popen(
                f"sleep {delay} && systemctl restart 333agent",
                shell=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        
        return PluginResult(
            status="success",
            message=f"Agent restart scheduled in {delay}s"
        )
    
    async def _restart_system(self, delay: int) -> PluginResult:
        """Redémarre la machine"""
        os_name = platform.system()
        
        if os_name == "Windows":
            subprocess.Popen(
                f"shutdown /r /t {delay}",
                shell=True
            )
        else:
            subprocess.Popen(
                f"sleep {delay} && shutdown -r now",
                shell=True,
                start_new_session=True
            )
        
        return PluginResult(
            status="success",
            message=f"System restart scheduled in {delay}s"
        )
```

---

## 🔄 Améliorations Self-Update

### **Modification `self_update.py`** - Auto-restart

```python
# Dans self_update.py, ligne ~330 (après replace files successful)

# ⭐ NOUVEAU: Auto-restart après update
async def _restart_agent_after_update(self):
    """Redémarre l'agent après update réussi"""
    
    logger.info("🔄 Restarting agent after successful update...")
    
    os_name = platform.system()
    
    if os_name == "Windows":
        # Windows: Restart via service
        try:
            subprocess.Popen(
                'timeout 3 && sc stop "333HOME Agent" && sc start "333HOME Agent"',
                shell=True,
                creationflags=subprocess.DETACHED_PROCESS
            )
            logger.info("✅ Agent restart scheduled (service)")
        except Exception as e:
            logger.warning(f"Service restart failed, trying process restart: {e}")
            # Fallback: Restart pythonw.exe
            pythonw = sys.executable.replace("python.exe", "pythonw.exe")
            agent_tray = Path(self.agent_dir) / "agent_tray.pyw"
            subprocess.Popen([pythonw, str(agent_tray)], start_new_session=True)
            # Kill current process
            os._exit(0)
    
    else:
        # Linux: Restart systemd service
        try:
            subprocess.Popen(
                "sleep 3 && systemctl restart 333agent",
                shell=True,
                start_new_session=True
            )
            logger.info("✅ Agent restart scheduled (systemd)")
            # Exit current process pour laisser systemd restart
            os._exit(0)
        except Exception as e:
            logger.error(f"Failed to restart agent: {e}")

# Appeler à la fin de execute() si status=success
if result.status == "success":
    await self._restart_agent_after_update()
```

---

## 📊 Comparaison Avant/Après

| Aspect | ❌ Avant | ✅ Après |
|--------|----------|----------|
| **Scripts packaging** | 2 scripts différents | 1 script unifié |
| **Version management** | Manuel, hardcodé | Auto-incrément, centralisé |
| **Install Windows** | IP hardcodée, manuel | Auto-découverte, service |
| **Install Linux** | Aucun script | Systemd service complet |
| **Dépendances** | Une par une (lent) | Bulk requirements.txt |
| **Auto-restart update** | ❌ Manuel | ✅ Automatique |
| **Logs** | Fichiers manuels | Rotation auto / journald |
| **Démarrage auto** | Tâche planifiée | Service Windows/Linux |
| **Désinstallation** | Scripts séparés | Templates générés |
| **Checksums tracking** | Manuel README | JSON historique auto |
| **Deploy one-liner** | ❌ Non | ✅ curl pipe bash |

---

## 🎯 Plan de Migration

### **Phase 1: Packaging Unifié** (1h)
1. ✅ Créer `scripts/agents/package_agent.sh`
2. ✅ Créer templates installers
3. ✅ Tester génération package
4. ✅ Git commit "Packaging unifié agents"

### **Phase 2: Auto-Restart Self-Update** (30min)
1. ✅ Modifier `self_update.py` avec `_restart_agent_after_update()`
2. ✅ Tester update TITO avec auto-restart
3. ✅ Git commit "Auto-restart après self-update"

### **Phase 3: Installation Linux** (1h)
1. ✅ Créer `install_template.sh` + `agent.service`
2. ✅ Tester installation 333srv
3. ✅ Valider systemd service (status, logs, restart)
4. ✅ Git commit "Installation Linux systemd"

### **Phase 4: Backend Actions** (2h)
1. ✅ Créer plugin `system_restart.py`
2. ✅ Créer endpoints `/api/agents/{id}/restart` et `/api/agents/{id}/update`
3. ✅ Connecter boutons frontend
4. ✅ Tester actions depuis UI
5. ✅ Git commit "Backend actions Restart/Update"

### **Phase 5: Tests Production** (1h)
1. ✅ Test installation Windows propre (uninstall + reinstall)
2. ✅ Test installation Linux 333srv
3. ✅ Test auto-update avec restart automatique
4. ✅ Test crash recovery (kill pythonw → auto-restart)
5. ✅ Documentation finale

---

## ✅ Checklist Validation

- [ ] Script `package_agent.sh` créé et testé
- [ ] Templates installers Windows/Linux créés
- [ ] Plugin `system_restart.py` créé
- [ ] Self-update auto-restart implémenté
- [ ] Endpoints backend Restart/Update créés
- [ ] Boutons frontend connectés
- [ ] Installation Windows testée (TITO)
- [ ] Installation Linux testée (333srv)
- [ ] Auto-update testé avec restart auto
- [ ] Documentation mise à jour
- [ ] Git commits propres avec messages descriptifs

---

**Auteur**: 333HOME Team  
**Date**: 4 novembre 2025  
**Objectif**: Simplifier et stabiliser déploiement agents production-ready
