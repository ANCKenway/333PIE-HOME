# 📖 Référence des Modules Python 333HOME

## 🎯 Objectif
Documentation technique complète de tous les modules Python de 333HOME avec leurs classes, méthodes et interfaces.

---

## ⚠️ AVERTISSEMENT IMPORTANT

**🚧 État Actuel du Projet :**
- Le code actuel est **expérimental** et en **développement actif**
- L'architecture est un **"champ de mine"** qui nécessitera probablement une **restructuration complète**
- Les fonctionnalités décrites **ne sont pas toutes stables** ou finalisées
- Cette documentation reflète l'état actuel mais **tout peut changer**

**🎯 Vision Future :**
- Intégration majeure avec **333srv (192.168.1.175)** - serveur Linux principal
- Création d'une **API commune** entre le Raspberry Pi et le serveur principal
- **Consoles interactives**, **prise en main à distance**, gestion centralisée
- **Restructuration architecturale** probable pour atteindre ces objectifs

---

## 📱 Module Devices

### 🔧 DeviceManager
```python
# modules/devices/__init__.py

class DeviceManager:
    """
    ⚠️ EN DÉVELOPPEMENT - Gestionnaire des appareils réseau
    Fonctionnalités actuelles basiques, évolution prévue pour intégration 333srv
    """
    
    def __init__(self, data_dir: Path):
        """
        Initialise le gestionnaire d'appareils
        
        Args:
            data_dir: Répertoire de stockage des données
        """
        self.data_dir = data_dir
        self.devices_file = data_dir / "devices.json"
        self._devices = []
        self._load_devices()
    
    def get_devices(self) -> List[Dict]:
        """
        Récupère la liste des appareils
        
        Returns:
            Liste des appareils avec leurs propriétés
            
        Note:
            Structure actuelle basique, évoluera pour 333srv
        """
        return self._devices.copy()
    
    def get_device(self, device_id: str) -> Optional[Dict]:
        """
        Récupère un appareil par son ID
        
        Args:
            device_id: Identifiant unique de l'appareil
            
        Returns:
            Dictionnaire de l'appareil ou None
        """
        for device in self._devices:
            if device.get('id') == device_id:
                return device.copy()
        return None
    
    def add_device(self, device_data: Dict) -> Dict:
        """
        ⚠️ TEMPORAIRE - Ajoute un nouvel appareil
        
        Args:
            device_data: Données de l'appareil
            
        Returns:
            Appareil créé avec ID généré
            
        Future:
            Synchronisation avec base de données 333srv
        """
        device = device_data.copy()
        device['id'] = self._generate_device_id()
        device['created_at'] = datetime.now().isoformat()
        
        self._devices.append(device)
        self._save_devices()
        
        return device
    
    def update_device(self, device_id: str, updates: Dict) -> Optional[Dict]:
        """
        Met à jour un appareil existant
        
        Args:
            device_id: ID de l'appareil
            updates: Modifications à appliquer
            
        Returns:
            Appareil mis à jour ou None
        """
        for i, device in enumerate(self._devices):
            if device.get('id') == device_id:
                self._devices[i].update(updates)
                self._devices[i]['updated_at'] = datetime.now().isoformat()
                self._save_devices()
                return self._devices[i].copy()
        return None
    
    def delete_device(self, device_id: str) -> bool:
        """
        Supprime un appareil
        
        Args:
            device_id: ID de l'appareil à supprimer
            
        Returns:
            True si supprimé, False sinon
        """
        for i, device in enumerate(self._devices):
            if device.get('id') == device_id:
                del self._devices[i]
                self._save_devices()
                return True
        return False
    
    def wake_device(self, mac_address: str) -> bool:
        """
        ⚠️ BASIQUE - Envoie un packet Wake-on-LAN
        
        Args:
            mac_address: Adresse MAC de l'appareil
            
        Returns:
            True si packet envoyé
            
        Future:
            Intégration avec système de contrôle 333srv
        """
        try:
            # Implementation basique Wake-on-LAN
            mac_bytes = bytes.fromhex(mac_address.replace(':', ''))
            magic_packet = b'\xff' * 6 + mac_bytes * 16
            
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic_packet, ('<broadcast>', 9))
            sock.close()
            
            return True
        except Exception:
            return False
```

### 📊 DeviceMonitor
```python
# modules/devices/monitor.py

class DeviceMonitor:
    """
    ⚠️ EXPÉRIMENTAL - Monitoring des appareils
    Version actuelle basique, refonte prévue pour 333srv
    """
    
    def __init__(self):
        """Initialise le moniteur d'appareils"""
        self._cache = {}
        self._cache_timeout = 60  # secondes
    
    def check_device_status(self, ip_address: str) -> Dict:
        """
        ⚠️ BASIQUE - Vérifie le statut d'un appareil
        
        Args:
            ip_address: Adresse IP de l'appareil
            
        Returns:
            Dictionnaire avec statut et métriques
            
        Future:
            Monitoring avancé via 333srv avec métriques détaillées
        """
        cache_key = f"status_{ip_address}"
        
        # Vérifier cache
        if cache_key in self._cache:
            cached_time, cached_result = self._cache[cache_key]
            if time.time() - cached_time < self._cache_timeout:
                return cached_result
        
        # Test ping basique
        try:
            import subprocess
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '2', ip_address],
                capture_output=True,
                timeout=5
            )
            
            status = {
                'ip': ip_address,
                'status': 'online' if result.returncode == 0 else 'offline',
                'response_time': None,  # À extraire du ping
                'last_check': datetime.now().isoformat()
            }
            
            # Cache du résultat
            self._cache[cache_key] = (time.time(), status)
            return status
            
        except Exception as e:
            error_status = {
                'ip': ip_address,
                'status': 'error',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
            return error_status
    
    def check_vpn_device(self, vpn_ip: str) -> Dict:
        """
        ⚠️ TEMPORAIRE - Vérifie statut VPN via ping
        
        Args:
            vpn_ip: IP VPN (Tailscale) de l'appareil
            
        Returns:
            Statut de la connexion VPN
            
        Future:
            Intégration API Tailscale + monitoring 333srv
        """
        return self.check_device_status(vpn_ip)
```

---

## 🌐 Module Network

### 🔍 NetworkScanner
```python
# modules/network/network_unified.py

class NetworkScanner:
    """
    ⚠️ EN DÉVELOPPEMENT - Scanner réseau unifié
    Version actuelle fonctionnelle mais sera étendue pour 333srv
    """
    
    def __init__(self):
        """Initialise le scanner réseau"""
        self.default_ports = [22, 23, 53, 80, 443, 993, 995]
        self.timeout = 5
    
    def quick_scan(self, target: str) -> List[Dict]:
        """
        ⚠️ BASIQUE - Scan rapide du réseau
        
        Args:
            target: Cible du scan (ex: 192.168.1.0/24)
            
        Returns:
            Liste des appareils découverts
            
        Future:
            Scan avancé avec intégration 333srv pour détection services
        """
        devices = []
        
        try:
            # Scan ping simple pour discovery
            import subprocess
            import ipaddress
            
            network = ipaddress.IPv4Network(target, strict=False)
            
            for ip in network.hosts():
                try:
                    result = subprocess.run(
                        ['ping', '-c', '1', '-W', '1', str(ip)],
                        capture_output=True,
                        timeout=2
                    )
                    
                    if result.returncode == 0:
                        device = {
                            'ip': str(ip),
                            'hostname': self._get_hostname(str(ip)),
                            'mac': self._get_mac_address(str(ip)),
                            'open_ports': [],  # Scan ports basique
                            'last_seen': datetime.now().isoformat()
                        }
                        devices.append(device)
                        
                except subprocess.TimeoutExpired:
                    continue
                except Exception:
                    continue
        
        except Exception as e:
            print(f"Erreur scan: {e}")
        
        return devices
    
    def full_scan(self, target: str, ports: List[int]) -> List[Dict]:
        """
        ⚠️ EXPÉRIMENTAL - Scan complet avec ports
        
        Args:
            target: Cible du scan
            ports: Liste des ports à scanner
            
        Returns:
            Liste détaillée des appareils
            
        Future:
            Scan professionnel avec nmap + intégration 333srv
        """
        devices = self.quick_scan(target)
        
        # Scan des ports pour chaque appareil trouvé
        for device in devices:
            device['open_ports'] = self._scan_ports(device['ip'], ports)
            device['services'] = self._identify_services(device['open_ports'])
        
        return devices
    
    def _scan_ports(self, ip: str, ports: List[int]) -> List[int]:
        """
        ⚠️ BASIQUE - Scan des ports TCP
        
        Args:
            ip: Adresse IP cible
            ports: Liste des ports à tester
            
        Returns:
            Liste des ports ouverts
            
        Note:
            Implementation basique, sera remplacée par nmap
        """
        open_ports = []
        
        import socket
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
            except:
                continue
        
        return open_ports
```

### 💾 ScanStorage
```python
# modules/network/scan_storage.py

class ScanStorage:
    """
    ⚠️ TEMPORAIRE - Stockage des scans réseau
    Stockage JSON basique, migration prévue vers base de données 333srv
    """
    
    def __init__(self, data_dir: Path):
        """
        Initialise le stockage des scans
        
        Args:
            data_dir: Répertoire de stockage
            
        Future:
            Migration vers base de données partagée 333srv
        """
        self.data_dir = data_dir
        self.scan_file = data_dir / "last_scan.json"
    
    def save_scan(self, scan_data: Dict) -> bool:
        """
        ⚠️ BASIQUE - Sauvegarde un scan
        
        Args:
            scan_data: Données du scan
            
        Returns:
            True si sauvegardé
            
        Future:
            API 333srv pour stockage centralisé
        """
        try:
            with open(self.scan_file, 'w') as f:
                json.dump(scan_data, f, indent=2)
            return True
        except Exception:
            return False
    
    def get_last_scan(self) -> Optional[Dict]:
        """
        Récupère le dernier scan
        
        Returns:
            Données du dernier scan ou None
        """
        try:
            if self.scan_file.exists():
                with open(self.scan_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None
```

---

## 🔒 Module Tailscale

### 🛡️ TailscaleService
```python
# services/tailscale_service.py

class TailscaleService:
    """
    ⚠️ FONCTIONNEL MAIS LIMITÉ - Service Tailscale
    Version actuelle basique, évolution prévue pour intégration 333srv
    """
    
    def __init__(self, config_dir: Path):
        """
        Initialise le service Tailscale
        
        Args:
            config_dir: Répertoire de configuration
            
        Future:
            Configuration centralisée via 333srv
        """
        self.config_dir = config_dir
        self.config_file = config_dir / "tailscale.json"
        self._config = None
        self._load_config()
    
    def is_configured(self) -> bool:
        """
        Vérifie si Tailscale est configuré
        
        Returns:
            True si configuré
        """
        return (self._config is not None and 
                'tailnet' in self._config and 
                'api_key' in self._config)
    
    async def get_devices(self) -> List[Dict]:
        """
        ⚠️ BASIQUE - Récupère les appareils Tailscale
        
        Returns:
            Liste des appareils VPN
            
        Future:
            Intégration avec monitoring 333srv pour métriques avancées
        """
        if not self.is_configured():
            return []
        
        try:
            import httpx
            
            headers = {
                'Authorization': f"Bearer {self._config['api_key']}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.tailscale.com/api/v2/tailnet/{self._config['tailnet']}/devices",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get('devices', [])
                
        except Exception as e:
            print(f"Erreur Tailscale API: {e}")
        
        return []
    
    def save_config(self, tailnet: str, api_key: str) -> bool:
        """
        ⚠️ TEMPORAIRE - Sauvegarde la configuration
        
        Args:
            tailnet: Nom du tailnet
            api_key: Clé API Tailscale
            
        Returns:
            True si sauvegardé
            
        Future:
            Configuration sécurisée via 333srv
        """
        try:
            config = {
                'tailnet': tailnet,
                'api_key': api_key,
                'configured_at': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self._config = config
            return True
            
        except Exception:
            return False
```

---

## 🚧 Modules en Développement

### 🔮 Future - Intégration 333srv

```python
# modules/server_integration/333srv_client.py (PLANIFIÉ)

class Server333Client:
    """
    🚧 FUTUR - Client pour intégration avec 333srv (192.168.1.175)
    
    Objectifs:
    - API commune entre Raspberry Pi et serveur principal
    - Consoles interactives distantes
    - Prise en main à distance
    - Gestion centralisée du parc
    """
    
    def __init__(self, server_ip: str = "192.168.1.175"):
        """
        Futur client pour 333srv
        
        Args:
            server_ip: IP du serveur principal
        """
        self.server_ip = server_ip
        self.api_base = f"http://{server_ip}:8080"  # Port à définir
    
    async def register_pi(self) -> bool:
        """
        PLANIFIÉ - Enregistre ce Raspberry Pi auprès du serveur principal
        """
        pass
    
    async def get_managed_devices(self) -> List[Dict]:
        """
        PLANIFIÉ - Récupère les appareils gérés par le serveur
        """
        pass
    
    async def execute_remote_command(self, target: str, command: str) -> Dict:
        """
        PLANIFIÉ - Exécute une commande sur un appareil distant via 333srv
        """
        pass
    
    async def start_remote_console(self, target: str) -> str:
        """
        PLANIFIÉ - Démarre une console interactive distante
        
        Returns:
            WebSocket URL pour la console
        """
        pass
```

### 🖥️ Future - Console Management

```python
# modules/console_management/remote_console.py (PLANIFIÉ)

class RemoteConsoleManager:
    """
    🚧 FUTUR - Gestionnaire de consoles interactives
    
    Fonctionnalités prévues:
    - Consoles SSH/RDP intégrées
    - Sessions partagées
    - Enregistrement des sessions
    - Contrôle multi-utilisateur
    """
    
    def __init__(self, server_client: Server333Client):
        """
        Futur gestionnaire de consoles
        
        Args:
            server_client: Client de connexion au serveur principal
        """
        self.server_client = server_client
        self.active_sessions = {}
    
    async def create_ssh_session(self, target: str, credentials: Dict) -> str:
        """
        PLANIFIÉ - Crée une session SSH interactive
        """
        pass
    
    async def create_rdp_session(self, target: str, credentials: Dict) -> str:
        """
        PLANIFIÉ - Crée une session RDP via navigateur
        """
        pass
    
    async def share_session(self, session_id: str, user_id: str) -> bool:
        """
        PLANIFIÉ - Partage une session avec un autre utilisateur
        """
        pass
```

---

## ⚠️ Notes Importantes pour les Développeurs

### 🚧 État Actuel du Code
1. **Architecture expérimentale** : Le code actuel fonctionne mais est instable
2. **Modules incomplets** : Beaucoup de fonctionnalités sont basiques ou manquantes
3. **Restructuration prévue** : L'architecture changera probablement complètement
4. **Tests limités** : La couverture de tests est insuffisante

### 🎯 Objectifs Futurs Critiques
1. **Intégration 333srv** : Connexion avec le serveur principal (192.168.1.175)
2. **API unifiée** : Création d'une API commune entre tous les systèmes
3. **Gestion centralisée** : Le serveur principal orchestrera tout
4. **Consoles distantes** : Interface de contrôle avancée
5. **Scalabilité** : Architecture pour supporter plusieurs Raspberry Pi

### 📋 Actions Recommandées
1. **NE PAS** considérer le code actuel comme stable
2. **TESTER** avant toute modification importante
3. **DOCUMENTER** les changements et problèmes rencontrés
4. **PLANIFIER** l'intégration avec 333srv dès le début
5. **CONSULTER** la documentation avant de développer

---

**📅 Documentation créée :** 19 octobre 2025  
**⚠️ Statut :** Code expérimental en développement  
**🎯 Future :** Intégration majeure avec 333srv prévue  
**🔄 Révision :** À mettre à jour après chaque restructuration