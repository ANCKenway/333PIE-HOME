# 🚀 ROADMAP - 333HOME Remote Management

**Date de mise à jour** : 30 octobre 2025  
**Version** : 3.0.0  
**Focus** : Contrôle à distance multi-OS (Windows + Linux)

---

## 🎯 Vision Globale

**Objectif** : Transformer 333HOME en plateforme de gestion centralisée avec **contrôle total** sur les postes Windows (TITO) et Linux (333srv).

### Postes Cibles

#### 🖥️ TITO (Windows)
- **IP LAN** : `192.168.1.174`
- **VPN** : `100.93.236.71`
- **OS** : Windows 10/11
- **Rôle** : Poste client principal
- **Besoins** : Télémaintenance LogMeIn Rescue automatisée

#### 🐧 333srv (Linux/Ubuntu Server)
- **IP LAN** : `192.168.1.175`
- **VPN** : `100.80.31.55`
- **OS** : Ubuntu Server (avec GUI installée)
- **Rôle** : Serveur principal
- **Besoins** : Console SSH web + accès GUI distant

---

## 🎯 Principes Architecturaux

## 🎯 Principes Architecturaux

### 1. Sécurité First
- ✅ **Authentification** : JWT tokens, sessions chiffrées
- ✅ **Communications** : HTTPS/WSS obligatoire, VPN préféré
- ✅ **Isolation** : Agents locaux privilégiés > exécution distante
- ✅ **Audit** : Logs complets actions sensibles

### 2. Architecture Agent-Based
```
┌─────────────────────────────────────────────────────────────┐
│                    333HOME Web Interface                    │
│                   (192.168.1.150:8000)                      │
└────────────────────────┬────────────────────────────────────┘
                         │ API REST/WebSocket
          ┌──────────────┴──────────────┐
          │                             │
    ┌─────▼─────┐                 ┌─────▼─────┐
    │ TITO Agent│                 │ 333srv    │
    │ (Windows) │                 │ Agent     │
    │ 192.168   │                 │ (Linux)   │
    │ 1.174     │                 │ 192.168   │
    │           │                 │ 1.175     │
    └───────────┘                 └───────────┘
```

**Flux** :
1. Interface web → API 333HOME
2. API → Agent local (via VPN prioritaire)
3. Agent → Exécution OS-specific
4. Agent → Retour résultat API
5. API → Push temps réel interface (WebSocket)

### 3. Évolutivité
- 🔧 **Modulaire** : Un module = une feature
- � **Pluggable** : Nouveaux postes = nouveau agent
- � **Versionné** : Agents auto-update
- 📊 **Observable** : Monitoring actions + perfs

---

## 📋 PHASES DE DÉVELOPPEMENT

---

## 🔥 PHASE 1 : LogMeIn Rescue Automation (TITO - Windows)

**Priorité** : 🔴 CRITIQUE  
**Durée estimée** : 5-7 jours  
**Complexité** : ⭐⭐⭐⭐ (4/5)

### 🎯 Objectif

Automatiser complètement la connexion LogMeIn Rescue depuis l'interface web :
1. User saisit code 6 chiffres dans interface 333HOME
2. Interface envoie code à TITO via API
3. Agent Windows sur TITO :
   - Ouvre navigateur sur `https://secure.logmeinrescue.com/Customer/Code.aspx`
   - Entre le code automatiquement
   - Télécharge l'applet LogMeIn
   - Lance applet en admin (UAC bypass si configuré)
   - Accepte automatiquement toutes demandes de droits

### 📐 Architecture Technique

#### 1.1 - Agent Windows (TITO)

**Stack** :
- **Langage** : Python 3.11+ ou Go (compilé → `.exe`)
- **GUI Automation** : `pyautogui` + `pywinauto` (contrôle fenêtres Windows)
- **Browser** : Selenium WebDriver (Chrome/Edge)
- **Admin** : `ctypes` Windows API (élévation privilèges)
- **Communication** : WebSocket client vers 333HOME

**Fichiers** :
```
tito-agent/
├── agent.py              # Main service
├── logmein_handler.py    # LogMeIn automation logic
├── browser_controller.py # Selenium wrapper
├── windows_admin.py      # UAC bypass + admin actions
├── config.yaml           # Config (VPN IP, API endpoint)
└── requirements.txt      # Dependencies
```

**Installation** :
- Service Windows (`sc create TitoAgent`)
- Démarrage auto avec session
- Logs dans `C:\ProgramData\333HOME\logs\`

#### 1.2 - API 333HOME (Backend)

**Nouveau router** : `src/features/remote/routers/tito_router.py`

**Endpoints** :
```python
POST /api/remote/tito/logmein-rescue
Body: {"code": "123456"}
Response: {
    "task_id": "uuid",
    "status": "pending",
    "device": "TITO",
    "action": "logmein_rescue"
}

GET /api/remote/tito/logmein-rescue/{task_id}
Response: {
    "task_id": "uuid",
    "status": "in_progress|completed|failed",
    "steps": [
        {"step": "browser_opened", "timestamp": "...", "status": "ok"},
        {"step": "code_entered", "timestamp": "...", "status": "ok"},
        {"step": "applet_downloaded", "timestamp": "...", "status": "ok"},
        {"step": "applet_launched", "timestamp": "...", "status": "ok"},
        {"step": "rights_accepted", "timestamp": "...", "status": "ok"}
    ],
    "error": null
}

# WebSocket pour updates temps réel
WS /api/remote/tito/stream
```

**Structure données** :
```python
# src/features/remote/models.py
class RemoteTask(BaseModel):
    task_id: str
    device_id: str
    action: str
    params: Dict[str, Any]
    status: Literal["pending", "in_progress", "completed", "failed"]
    steps: List[TaskStep]
    created_at: datetime
    completed_at: Optional[datetime]

class LogMeInRescueRequest(BaseModel):
    code: str = Field(..., regex=r'^\d{6}$')  # Validation 6 chiffres
```

#### 1.3 - Interface Web

**Nouveau composant** : Modal "Télémaintenance TITO"

```html
<!-- web/index.html - Ajout dans section TITO -->
<button @click="openLogMeInModal('TITO')" class="btn-primary">
    🛠️ Télémaintenance LogMeIn
</button>

<!-- Modal -->
<div x-show="showLogMeInModal" class="modal">
    <h3>Télémaintenance TITO</h3>
    <input 
        type="text" 
        x-model="logmeinCode" 
        placeholder="Code 6 chiffres"
        maxlength="6"
        pattern="\d{6}"
    />
    <button @click="startLogMeInRescue()">
        ▶️ Lancer
    </button>
    
    <!-- Progress steps -->
    <div class="steps-progress">
        <template x-for="step in logmeinSteps">
            <div class="step" :class="step.status">
                <span x-text="step.label"></span>
                <span x-show="step.status === 'loading'">⏳</span>
                <span x-show="step.status === 'ok'">✅</span>
                <span x-show="step.status === 'error'">❌</span>
            </div>
        </template>
    </div>
</div>
```

**JavaScript** :
```javascript
async function startLogMeInRescue() {
    const response = await fetch('/api/remote/tito/logmein-rescue', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({code: logmeinCode})
    });
    
    const {task_id} = await response.json();
    
    // WebSocket pour updates temps réel
    const ws = new WebSocket('ws://localhost:8000/api/remote/tito/stream');
    ws.onmessage = (event) => {
        const update = JSON.parse(event.data);
        if (update.task_id === task_id) {
            updateLogMeInSteps(update.steps);
        }
    };
}
```

### 🔧 Implémentation Détaillée

#### Étape 1.1 : Selenium Automation (3 jours)

**Fichier** : `tito-agent/logmein_handler.py`

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class LogMeInRescueAutomation:
    def __init__(self, code: str):
        self.code = code
        self.driver = None
        
    def setup_browser(self):
        """Configure Chrome en mode headless ou visible"""
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        # options.add_argument('--headless')  # Décommenter pour invisible
        self.driver = webdriver.Chrome(options=options)
    
    def navigate_and_enter_code(self):
        """Étape 1 : Naviguer et entrer code"""
        self.driver.get('https://secure.logmeinrescue.com/Customer/Code.aspx')
        
        # Attendre chargement page
        code_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'code-input-field'))
        )
        
        # Entrer code caractère par caractère (simulation humaine)
        for digit in self.code:
            code_input.send_keys(digit)
            time.sleep(0.2)  # Délai humain
        
        # Cliquer bouton submit
        submit_btn = self.driver.find_element(By.ID, 'submit-button')
        submit_btn.click()
    
    def download_applet(self):
        """Étape 2 : Télécharger applet"""
        download_btn = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.ID, 'download-applet-btn'))
        )
        download_btn.click()
        
        # Attendre fin téléchargement (surveiller Downloads/)
        applet_path = self.wait_for_download('LogMeInRescue.exe')
        return applet_path
    
    def launch_applet_as_admin(self, applet_path: str):
        """Étape 3 : Lancer applet en admin"""
        import ctypes
        import subprocess
        
        # Méthode 1 : Via ShellExecute avec runas
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas",  # Élévation admin
            applet_path, 
            None, 
            None, 
            1  # SW_SHOWNORMAL
        )
        
        # Alternative : Via subprocess (nécessite UAC configuré)
        # subprocess.Popen(['runas', '/user:Administrator', applet_path])
    
    def accept_uac_prompts(self):
        """Étape 4 : Accepter UAC automatiquement"""
        import pywinauto
        from pywinauto.application import Application
        
        # Attendre fenêtre UAC
        time.sleep(2)
        
        # Trouver fenêtre UAC (titre contient "User Account Control")
        uac_window = pywinauto.findwindows.find_windows(title_re=".*User Account Control.*")
        
        if uac_window:
            app = Application().connect(handle=uac_window[0])
            # Cliquer bouton "Yes" / "Oui"
            app.window().child_window(title="Yes", control_type="Button").click()
    
    def run_full_automation(self):
        """Orchestration complète"""
        try:
            self.setup_browser()
            self.navigate_and_enter_code()
            applet_path = self.download_applet()
            self.launch_applet_as_admin(applet_path)
            self.accept_uac_prompts()
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
        finally:
            if self.driver:
                self.driver.quit()
```

#### Étape 1.2 : Agent Windows Service (2 jours)

**Fichier** : `tito-agent/agent.py`

```python
import asyncio
import websockets
import json
from logmein_handler import LogMeInRescueAutomation

class TitoAgent:
    def __init__(self, api_url: str):
        self.api_url = api_url  # ws://192.168.1.150:8000/api/remote/tito/stream
        self.ws = None
    
    async def connect(self):
        """Connexion persistante WebSocket"""
        self.ws = await websockets.connect(self.api_url)
        print(f"✅ Connected to 333HOME: {self.api_url}")
    
    async def listen_commands(self):
        """Écouter commandes depuis 333HOME"""
        async for message in self.ws:
            data = json.loads(message)
            action = data.get('action')
            
            if action == 'logmein_rescue':
                await self.handle_logmein_rescue(data)
    
    async def handle_logmein_rescue(self, data):
        """Gérer commande LogMeIn Rescue"""
        task_id = data['task_id']
        code = data['code']
        
        # Envoyer update: démarrage
        await self.send_update(task_id, 'in_progress', {
            'step': 'starting',
            'message': 'Démarrage automation...'
        })
        
        # Lancer automation
        automation = LogMeInRescueAutomation(code)
        
        try:
            # Étape 1
            await self.send_update(task_id, 'in_progress', {'step': 'browser_opened'})
            automation.setup_browser()
            
            # Étape 2
            await self.send_update(task_id, 'in_progress', {'step': 'code_entered'})
            automation.navigate_and_enter_code()
            
            # Étape 3
            await self.send_update(task_id, 'in_progress', {'step': 'applet_downloaded'})
            applet_path = automation.download_applet()
            
            # Étape 4
            await self.send_update(task_id, 'in_progress', {'step': 'applet_launched'})
            automation.launch_applet_as_admin(applet_path)
            
            # Étape 5
            await self.send_update(task_id, 'in_progress', {'step': 'rights_accepted'})
            automation.accept_uac_prompts()
            
            # Succès
            await self.send_update(task_id, 'completed', {'step': 'completed'})
            
        except Exception as e:
            await self.send_update(task_id, 'failed', {
                'step': 'error',
                'error': str(e)
            })
    
    async def send_update(self, task_id: str, status: str, data: dict):
        """Envoyer update via WebSocket"""
        message = {
            'task_id': task_id,
            'status': status,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        await self.ws.send(json.dumps(message))
    
    async def run(self):
        """Boucle principale agent"""
        while True:
            try:
                await self.connect()
                await self.listen_commands()
            except Exception as e:
                print(f"❌ Error: {e}. Reconnecting in 5s...")
                await asyncio.sleep(5)

if __name__ == '__main__':
    agent = TitoAgent('ws://100.80.31.55:8000/api/remote/tito/stream')  # Via VPN
    asyncio.run(agent.run())
```

#### Étape 1.3 : Configuration UAC Bypass (1 jour)

**Problème** : UAC bloque exécution admin sans interaction.

**Solutions** :

1. **Via Registre Windows** (recommandé pour environnement contrôlé) :
```powershell
# Désactiver UAC pour applications signées (nécessite admin initial)
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "ConsentPromptBehaviorAdmin" -Value 0
```

2. **Via Task Scheduler** (lancer applet via tâche admin pré-configurée) :
```python
import win32com.client

scheduler = win32com.client.Dispatch('Schedule.Service')
scheduler.Connect()
root_folder = scheduler.GetFolder('\\')

# Créer tâche "LogMeInRescueLauncher" avec privilèges admin
task_def = scheduler.NewTask(0)
task_def.RegistrationInfo.Description = '333HOME LogMeIn Rescue Launcher'
task_def.Principal.RunLevel = 1  # TASK_RUNLEVEL_HIGHEST (admin)
task_def.Settings.Enabled = True

# Action: Lancer exe
action = task_def.Actions.Create(0)  # TASK_ACTION_EXEC
action.Path = r'C:\Downloads\LogMeInRescue.exe'

# Enregistrer tâche
root_folder.RegisterTaskDefinition(
    'LogMeInRescueLauncher',
    task_def,
    6,  # TASK_CREATE_OR_UPDATE
    None, None, 3  # TASK_LOGON_INTERACTIVE_TOKEN
)

# Puis lancer via
os.system('schtasks /Run /TN "LogMeInRescueLauncher"')
```

3. **Via AutoIt Script** (wrapper externe) :
```autoit
; logmein_launcher.au3
#RequireAdmin
Run("C:\Downloads\LogMeInRescue.exe")
WinWait("User Account Control")
ControlClick("User Account Control", "", "[CLASS:Button; TEXT:Yes]")
```

### ✅ Critères de Validation Phase 1

- [ ] Agent Windows installé sur TITO

- [ ] Connexion WebSocket stable avec 333HOME
- [ ] Code 6 chiffres validé côté API
- [ ] Automation Selenium fonctionnelle (browser → code → download)
- [ ] UAC bypass configuré et testé
- [ ] Applet LogMeIn lancé avec droits admin
- [ ] Interface web : modal + progress steps temps réel
- [ ] Test end-to-end : code saisi → connexion établie en <60s
- [ ] Logs complets actions sensibles
- [ ] Documentation agent + déploiement
- [ ] RULES.md compliant (architecture modulaire, pas doublon)

---

## 🐧 PHASE 2 : Console SSH Web + GUI Distant (333srv - Linux)

**Priorité** : 🟠 HAUTE  
**Durée estimée** : 4-6 jours  
**Complexité** : ⭐⭐⭐⭐ (4/5)

### 🎯 Objectif

Accès complet au serveur Linux 333srv depuis l'interface web :
1. **Console SSH web** : Terminal intégré dans navigateur
2. **Accès GUI distant** : VNC/NoVNC pour interface graphique Ubuntu
3. **Gestion fichiers** : Upload/download fichiers
4. **Monitoring** : CPU, RAM, disk, services status

### 📐 Architecture Technique

#### 2.1 - Console SSH Web

**Solution** : [xterm.js](https://xtermjs.org/) + WebSocket + SSH backend

**Stack** :
- **Frontend** : xterm.js (terminal émulateur)
- **Backend** : FastAPI WebSocket + paramiko (SSH client Python)
- **Auth** : JWT token + clé SSH (pas de password stocké)

**Nouveau router** : `src/features/remote/routers/linux_router.py`

```python
# src/features/remote/routers/linux_router.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import paramiko
import asyncio

router = APIRouter(prefix="/linux", tags=["remote-linux"])

@router.websocket("/console/{device_id}")
async def ssh_console(websocket: WebSocket, device_id: str):
    """
    Console SSH temps réel via WebSocket
    """
    await websocket.accept()
    
    # Récupérer config SSH du device
    device = get_device_config(device_id)  # 333srv
    
    # Connexion SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=device['vpn_ip'],  # 100.80.31.55 (VPN prioritaire)
        username=device['ssh_user'],
        key_filename='/home/pie333/.ssh/id_rsa_333srv'
    )
    
    # Ouvrir shell interactif
    channel = ssh.invoke_shell()
    
    try:
        # Task 1: Lire output SSH → envoyer au WebSocket
        async def read_ssh_output():
            while True:
                if channel.recv_ready():
                    output = channel.recv(1024).decode('utf-8')
                    await websocket.send_text(output)
                await asyncio.sleep(0.01)
        
        # Task 2: Lire input WebSocket → envoyer au SSH
        async def write_ssh_input():
            while True:
                data = await websocket.receive_text()
                channel.send(data)
        
        # Exécuter les 2 tasks en parallèle
        await asyncio.gather(read_ssh_output(), write_ssh_input())
        
    except WebSocketDisconnect:
        channel.close()
        ssh.close()
```

**Interface Web** :

```html
<!-- web/index.html - Nouveau composant SSH Console -->
<div id="ssh-console-container">
    <div id="terminal"></div>
</div>

<script src="https://cdn.jsdelivr.net/npm/xterm@5.0.0/lib/xterm.js"></script>
<script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.7.0/lib/xterm-addon-fit.js"></script>

<script>
function open333srvConsole() {
    const term = new Terminal({
        cursorBlink: true,
        theme: {background: '#1e1e1e', foreground: '#d4d4d4'}
    });
    
    const fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon);
    term.open(document.getElementById('terminal'));
    fitAddon.fit();
    
    // WebSocket vers backend SSH
    const ws = new WebSocket('ws://localhost:8000/api/remote/linux/console/333srv');
    
    // SSH output → Terminal
    ws.onmessage = (event) => {
        term.write(event.data);
    };
    
    // Terminal input → SSH
    term.onData((data) => {
        ws.send(data);
    });
}
</script>
```

#### 2.2 - Accès GUI Distant (VNC/NoVNC)

**Solution** : noVNC (VNC client HTML5) + TightVNC/x11vnc sur 333srv

**Installation 333srv** :
```bash
# Sur 333srv
sudo apt install x11vnc

# Créer service x11vnc
sudo tee /etc/systemd/system/x11vnc.service <<EOF
[Unit]
Description=X11 VNC Server
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/x11vnc -display :0 -auth guess -forever -loop -noxdamage -repeat -rfbport 5900 -shared
Restart=on-failure

[Install]
WantedBy=multi-user.target
