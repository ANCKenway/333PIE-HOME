# Guide de Configuration - Home Automation

## Configuration des appareils

### 1. Modifier le fichier de configuration

Éditez le fichier `config/devices.json` pour ajouter vos appareils :

```bash
nano config/devices.json
```

### 2. Configuration des ordinateurs (Wake-on-LAN)

Pour chaque PC que vous voulez contrôler :

1. **Activez Wake-on-LAN dans le BIOS/UEFI** :
   - Cherchez "Wake on LAN", "WOL", ou "Network Boot"
   - Activez cette option

2. **Activez Wake-on-LAN dans Windows** :
   ```cmd
   # Ouvrir une invite de commande en administrateur
   powercfg -devicequery wake_armed
   ```

3. **Configurez la carte réseau** :
   - Gestionnaire de périphériques → Cartes réseau
   - Propriétés de votre carte réseau → Gestion de l'alimentation
   - Cochez "Autoriser ce périphérique à sortir l'ordinateur du mode veille"

4. **Trouvez l'adresse MAC** :
   ```cmd
   ipconfig /all
   ```
   Cherchez "Adresse physique" de votre carte réseau.

### 3. Configuration exemple

```json
{
  "computers": [
    {
      "name": "PC Bureau",
      "ip": "192.168.1.100",
      "mac": "AA:BB:CC:DD:EE:FF",
      "description": "Ordinateur principal du bureau"
    }
  ],
  "services": [
    {
      "name": "Plex Media Server",
      "host": "192.168.1.100",
      "port": 32400,
      "type": "plex",
      "description": "Serveur multimédia Plex"
    }
  ]
}
```

## Installation et lancement

### Installation automatique

```bash
# Exécuter le script d'installation
./install.sh
```

### Lancement manuel

```bash
# Démarrage en mode développement
./start.sh

# Ou démarrage du service système
sudo systemctl start home-automation
```

## Accès à l'application

1. **Local** : http://localhost:8000
2. **Réseau** : http://[IP-de-votre-Pi]:8000

Pour trouver l'IP de votre Pi :
```bash
hostname -I
```

## Dépannage

### Vérifier le service
```bash
sudo systemctl status home-automation
sudo journalctl -f -u home-automation
```

### Tester Wake-on-LAN manuellement
```bash
# Installer wakeonlan si pas déjà fait
sudo apt install wakeonlan

# Tester
wakeonlan AA:BB:CC:DD:EE:FF
```

### Vérifier la connectivité réseau
```bash
ping 192.168.1.100
nmap -p 32400 192.168.1.100
```

## Sécurité

### Changer le mot de passe par défaut

1. Connectez-vous avec : `admin` / `admin123`
2. Changez le mot de passe dans l'interface
3. Ou modifiez `config/users.json` directement

### Accès depuis Internet (optionnel)

⚠️ **Attention** : Configurez un reverse proxy avec HTTPS pour sécuriser l'accès distant.

Exemple avec nginx :
```nginx
server {
    listen 80;
    server_name votre-domaine.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Extensions possibles

### Ajouter d'autres appareils

1. Modifiez `config/devices.json`
2. Redémarrez l'application
3. Les nouveaux appareils apparaîtront automatiquement

### Intégration avec d'autres services

- Home Assistant
- MQTT
- Smart switches
- Caméras IP

## Support réseau

### Ports utilisés

- **8000** : Interface web principale
- **Sortant** : Ping, HTTP pour vérifications

### Firewall (si activé)

```bash
sudo ufw allow 8000
sudo ufw allow out 80
sudo ufw allow out 443
```