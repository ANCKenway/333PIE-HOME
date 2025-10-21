# 🚀 Déploiement et Installation 333HOME

## 🎯 Objectif
Guide complet pour installer, configurer et déployer 333HOME sur différents environnements.

---

## 📋 Prérequis Système

### 🐧 Système d'Exploitation
- **Recommandé** : Raspberry Pi OS (Debian-based)
- **Compatible** : Ubuntu 20.04+, Debian 11+
- **Testé** : Raspberry Pi 4/5 (4GB+ RAM recommandé)

### 🐍 Dépendances
```bash
# Version Python
Python 3.8+ (testé avec 3.9)

# Paquets système requis
sudo apt update
sudo apt install -y python3-pip python3-venv git curl nmap

# Optionnel pour monitoring avancé
sudo apt install -y htop iotop nethogs
```

### 🔧 Hardware Minimum
- **RAM** : 2GB minimum, 4GB recommandé
- **Stockage** : 8GB minimum, 32GB recommandé
- **Réseau** : Ethernet/WiFi avec accès internet
- **Ports** : Port 8000 disponible

---

## 📥 Installation Standard

### 🔄 Installation Automatique
```bash
#!/bin/bash
# install_333home.sh - Installation automatique

echo "🏠 Installation 333HOME"
echo "======================"

# Vérifications prérequis
echo "🔍 Vérification prérequis..."
python3 --version || { echo "❌ Python 3 requis"; exit 1; }
git --version || { echo "❌ Git requis"; exit 1; }

# Création utilisateur dédié (optionnel)
if [[ $EUID -eq 0 ]]; then
    echo "🔧 Création utilisateur 333home..."
    useradd -m -s /bin/bash 333home
    usermod -aG sudo 333home
    cd /home/333home
    sudo -u 333home bash -c "
        git clone https://github.com/ANCKenway/333PIE-HOME.git
        cd 333PIE-HOME
    "
else
    # Installation utilisateur normal
    echo "📥 Clone du repository..."
    git clone https://github.com/ANCKenway/333PIE-HOME.git
    cd 333PIE-HOME
fi

# Environnement virtuel
echo "🐍 Configuration environnement Python..."
python3 -m venv venv
source venv/bin/activate

# Installation dépendances
echo "📦 Installation dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Configuration
echo "⚙️ Configuration initiale..."
mkdir -p data config logs
chmod 755 data config logs

# Copie fichiers de configuration par défaut
if [ ! -f config/devices.json ]; then
    echo '{"devices": []}' > config/devices.json
fi

# Permissions
echo "🔐 Configuration permissions..."
chmod +x start.sh stop.sh update.sh
chmod -R 644 web/static/

# Test installation
echo "🧪 Test installation..."
if python app_new.py --help > /dev/null 2>&1; then
    echo "✅ Installation réussie!"
else
    echo "❌ Problème installation"
    exit 1
fi

echo "🎉 333HOME installé avec succès!"
echo "📝 Prochaines étapes:"
echo "   1. ./start.sh pour démarrer"
echo "   2. http://localhost:8000 pour accéder à l'interface"
echo "   3. Consulter docs/ pour la configuration"
```

### 📱 Installation Manuelle
```bash
# 1. Clone du projet
git clone https://github.com/ANCKenway/333PIE-HOME.git
cd 333PIE-HOME

# 2. Environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 3. Dépendances
pip install -r requirements.txt

# 4. Structure
mkdir -p data config logs

# 5. Configuration par défaut
echo '{"devices": []}' > config/devices.json

# 6. Permissions
chmod +x *.sh
chmod -R 644 web/static/

# 7. Test
python app_new.py
```

---

## ⚙️ Configuration

### 📝 Configuration Basique
```bash
# Variables d'environnement (optionnel)
export HOME_333_HOST="0.0.0.0"
export HOME_333_PORT="8000"
export HOME_333_DEBUG="false"
export HOME_333_DATA_DIR="./data"
export HOME_333_CONFIG_DIR="./config"

# Fichier de configuration .env
cat > .env << EOF
# Configuration 333HOME
HOST=0.0.0.0
PORT=8000
DEBUG=false
DATA_DIR=./data
CONFIG_DIR=./config
LOG_LEVEL=INFO
EOF
```

### 🔧 Configuration Avancée
```json
// config/app_config.json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 1,
    "reload": false
  },
  "network": {
    "default_scan_target": "192.168.1.0/24",
    "scan_timeout": 30,
    "ping_timeout": 5,
    "default_ports": [22, 23, 53, 80, 443, 993, 995]
  },
  "monitoring": {
    "refresh_interval": 30,
    "history_retention_days": 30,
    "max_concurrent_scans": 3
  },
  "security": {
    "enable_auth": false,
    "api_rate_limit": 100,
    "cors_origins": ["*"]
  }
}
```

### 🔒 Configuration Tailscale
```json
// config/tailscale.json
{
  "tailnet": "votre-tailnet.ts.net",
  "api_key": "tskey-auth-xxxxxxxxxxxxx"
}
```

---

## 🔧 Déploiement Service Système

### 📱 Service Systemd
```ini
# /etc/systemd/system/333home.service

[Unit]
Description=333HOME - Système de domotique et gestion de parc informatique
After=network.target

[Service]
Type=simple
User=333home
Group=333home
WorkingDirectory=/home/333home/333PIE-HOME
Environment=PATH=/home/333home/333PIE-HOME/venv/bin
ExecStart=/home/333home/333PIE-HOME/venv/bin/python app_new.py
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=333home

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/333home/333PIE-HOME/data
ReadWritePaths=/home/333home/333PIE-HOME/config
ReadWritePaths=/home/333home/333PIE-HOME/logs

[Install]
WantedBy=multi-user.target
```

### 🚀 Installation Service
```bash
#!/bin/bash
# install_service.sh

echo "🔧 Installation service 333HOME"
echo "==============================="

# Copier le service
sudo cp 333home.service /etc/systemd/system/

# Recharger systemd
sudo systemctl daemon-reload

# Activer le service
sudo systemctl enable 333home

# Démarrer le service
sudo systemctl start 333home

# Vérifier le statut
sudo systemctl status 333home

echo "✅ Service 333HOME installé et démarré"
echo "📝 Commandes utiles:"
echo "   sudo systemctl status 333home    # Statut"
echo "   sudo systemctl restart 333home   # Redémarrer"
echo "   sudo systemctl stop 333home      # Arrêter"
echo "   sudo journalctl -u 333home -f    # Logs temps réel"
```

---

## 🐳 Déploiement Docker

### 📦 Dockerfile
```dockerfile
# Dockerfile
FROM python:3.9-slim

# Métadonnées
LABEL maintainer="333HOME Project"
LABEL description="Système de domotique et gestion de parc informatique"

# Dépendances système
RUN apt-get update && apt-get install -y \
    nmap \
    iputils-ping \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Utilisateur non-root
RUN useradd -m -u 1000 333home
USER 333home
WORKDIR /home/333home

# Copie des fichiers
COPY --chown=333home:333home requirements.txt .
COPY --chown=333home:333home . .

# Installation dépendances Python
RUN pip install --user --no-cache-dir -r requirements.txt

# Structure des données
RUN mkdir -p data config logs

# Variables d'environnement
ENV PATH="/home/333home/.local/bin:$PATH"
ENV PYTHONPATH="/home/333home"

# Port exposé
EXPOSE 8000

# Sanity check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/api/system/status || exit 1

# Point d'entrée
CMD ["python", "app_new.py"]
```

### 🔧 Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  333home:
    build: .
    container_name: 333home
    restart: unless-stopped
    
    ports:
      - "8000:8000"
    
    volumes:
      - ./data:/home/333home/data
      - ./config:/home/333home/config
      - ./logs:/home/333home/logs
    
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - DEBUG=false
    
    networks:
      - 333home-net
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/system/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

networks:
  333home-net:
    driver: bridge
```

### 🚀 Déploiement Docker
```bash
#!/bin/bash
# deploy_docker.sh

echo "🐳 Déploiement Docker 333HOME"
echo "============================="

# Construction de l'image
echo "🔧 Construction de l'image..."
docker build -t 333home:latest .

# Démarrage avec compose
echo "🚀 Démarrage des services..."
docker-compose up -d

# Vérification
echo "🧪 Vérification du déploiement..."
sleep 10
curl -f http://localhost:8000/api/system/status

if [ $? -eq 0 ]; then
    echo "✅ 333HOME déployé avec succès!"
    echo "🌐 Interface disponible: http://localhost:8000"
else
    echo "❌ Problème de déploiement"
    docker-compose logs
fi

echo "📝 Commandes utiles:"
echo "   docker-compose logs -f        # Logs temps réel"
echo "   docker-compose restart        # Redémarrer"
echo "   docker-compose down           # Arrêter"
echo "   docker-compose pull && docker-compose up -d  # Mise à jour"
```

---

## ☁️ Déploiement Cloud

### 🌐 Déploiement VPS
```bash
#!/bin/bash
# deploy_vps.sh - Déploiement sur VPS

echo "☁️ Déploiement VPS 333HOME"
echo "=========================="

# Variables
SERVER_IP="votre.vps.ip"
SERVER_USER="root"
DOMAIN="333home.votre-domaine.com"

# Connexion et installation
ssh $SERVER_USER@$SERVER_IP << 'EOF'
# Mise à jour système
apt update && apt upgrade -y

# Installation Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Installation Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone du projet
cd /opt
git clone https://github.com/ANCKenway/333PIE-HOME.git 333home
cd 333home

# Configuration
mkdir -p data config logs
echo '{"devices": []}' > config/devices.json

# Déploiement
docker-compose up -d

# Nginx proxy (optionnel)
apt install -y nginx
cat > /etc/nginx/sites-available/333home << 'NGINX'
server {
    listen 80;
    server_name 333home.votre-domaine.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX

ln -s /etc/nginx/sites-available/333home /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# SSL avec Certbot (optionnel)
apt install -y certbot python3-certbot-nginx
certbot --nginx -d 333home.votre-domaine.com

echo "✅ Déploiement VPS terminé!"
EOF

echo "🌐 333HOME déployé sur: http://$DOMAIN"
```

### 🔒 Configuration Sécurisée
```bash
#!/bin/bash
# secure_deployment.sh

echo "🔒 Sécurisation déploiement"
echo "=========================="

# Firewall
ufw allow ssh
ufw allow 80
ufw allow 443
ufw allow 8000/tcp comment "333HOME"
ufw --force enable

# Fail2ban
apt install -y fail2ban
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true

[nginx-noscript]
enabled = true

[nginx-badbots]
enabled = true
EOF

systemctl enable fail2ban
systemctl start fail2ban

# Authentification clé SSH
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

# Monitoring automatique
crontab -l > mycron
echo "*/5 * * * * curl -f http://localhost:8000/api/system/status > /dev/null || systemctl restart 333home" >> mycron
crontab mycron
rm mycron

echo "✅ Sécurisation terminée"
```

---

## 🔄 Mise à Jour

### 📦 Script de Mise à Jour
```bash
#!/bin/bash
# update.sh - Mise à jour 333HOME

echo "🔄 Mise à jour 333HOME"
echo "====================="

# Sauvegarde des données
echo "💾 Sauvegarde des données..."
cp -r data data_backup_$(date +%Y%m%d_%H%M%S)
cp -r config config_backup_$(date +%Y%m%d_%H%M%S)

# Arrêt du service
echo "🔴 Arrêt du service..."
if systemctl is-active --quiet 333home; then
    sudo systemctl stop 333home
    SERVICE_WAS_RUNNING=true
else
    pkill -f "python.*app" || true
    SERVICE_WAS_RUNNING=false
fi

# Mise à jour du code
echo "📥 Mise à jour du code..."
git fetch origin
git pull origin master

# Mise à jour des dépendances
echo "📦 Mise à jour dépendances..."
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Migration des données (si nécessaire)
echo "🔄 Migration des données..."
if [ -f scripts/migrate_data.py ]; then
    python scripts/migrate_data.py
fi

# Test de l'application
echo "🧪 Test de l'application..."
timeout 10s python app_new.py --test-config || {
    echo "❌ Test échoué, restauration..."
    git checkout HEAD~1
    pip install -r requirements.txt
    echo "⚠️ Restauration effectuée"
    exit 1
}

# Redémarrage du service
echo "🚀 Redémarrage du service..."
if [ "$SERVICE_WAS_RUNNING" = true ]; then
    sudo systemctl start 333home
    sudo systemctl status 333home
else
    echo "ℹ️ Démarrez manuellement avec: python app_new.py"
fi

echo "✅ Mise à jour terminée!"
echo "🌐 Interface: http://localhost:8000"
```

### 🐳 Mise à Jour Docker
```bash
#!/bin/bash
# update_docker.sh

echo "🐳 Mise à jour Docker 333HOME"
echo "============================="

# Sauvegarde
docker-compose exec 333home tar czf /tmp/backup.tar.gz data config

# Mise à jour
git pull origin master
docker-compose pull
docker-compose up -d --build

# Vérification
sleep 10
curl -f http://localhost:8000/api/system/status

echo "✅ Mise à jour Docker terminée"
```

---

## 📊 Monitoring Déploiement

### 📈 Script de Monitoring
```bash
#!/bin/bash
# monitor.sh - Monitoring 333HOME

echo "📊 Monitoring 333HOME"
echo "===================="

# Statut service
if systemctl is-active --quiet 333home; then
    echo "✅ Service: Actif"
else
    echo "❌ Service: Inactif"
fi

# Statut application
if curl -f http://localhost:8000/api/system/status > /dev/null 2>&1; then
    echo "✅ Application: Répondante"
else
    echo "❌ Application: Non répondante"
fi

# Ressources système
echo "💻 CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "💾 RAM: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
echo "💿 Disque: $(df -h / | awk 'NR==2{print $5}')"

# Logs récents
echo "📜 Dernières erreurs:"
journalctl -u 333home --since "1 hour ago" --grep "ERROR" --no-pager -n 5

# Processus
echo "🔍 Processus:"
ps aux | grep "python.*app" | grep -v grep
```

### 🚨 Alerting Automatique
```bash
#!/bin/bash
# alerting.sh - Système d'alertes

WEBHOOK_URL="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
EMAIL="admin@votre-domaine.com"

check_health() {
    if ! curl -f http://localhost:8000/api/system/status > /dev/null 2>&1; then
        send_alert "🚨 333HOME DOWN" "L'application 333HOME ne répond plus!"
        return 1
    fi
    
    # Vérifier la mémoire
    MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ "$MEM_USAGE" -gt 90 ]; then
        send_alert "⚠️ Mémoire critique" "Utilisation mémoire: ${MEM_USAGE}%"
    fi
    
    return 0
}

send_alert() {
    local title="$1"
    local message="$2"
    
    # Slack
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"$title: $message\"}" \
        "$WEBHOOK_URL"
    
    # Email
    echo "$message" | mail -s "$title" "$EMAIL"
    
    # Log
    echo "$(date): $title - $message" >> /var/log/333home_alerts.log
}

# Exécution
check_health
```

---

**📅 Guide déploiement créé :** 19 octobre 2025  
**🚀 Couverture :** Installation + Configuration + Docker + Cloud  
**🔧 Production ready :** Scripts automatisés et monitoring  
**🔒 Sécurisé :** Bonnes pratiques de déploiement