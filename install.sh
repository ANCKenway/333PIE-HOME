#!/bin/bash

# Script d'installation pour Home Automation sur Raspberry Pi

echo "🏠 Installation de Home Automation sur Raspberry Pi"
echo "=================================================="

# Vérifier si on est sur un système Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ Ce script est conçu pour Linux/Raspberry Pi OS"
    exit 1
fi

# Mettre à jour le système
echo "📦 Mise à jour du système..."
sudo apt update && sudo apt upgrade -y

# Installer Python 3 et pip si nécessaire
echo "🐍 Vérification de Python..."
if ! command -v python3 &> /dev/null; then
    echo "📦 Installation de Python 3..."
    sudo apt install python3 python3-pip python3-venv -y
fi

# Installer les dépendances système pour certains packages Python
echo "📦 Installation des dépendances système..."
sudo apt install -y \
    build-essential \
    python3-dev \
    libssl-dev \
    libffi-dev \
    net-tools \
    iputils-ping

# Créer un environnement virtuel
echo "🔧 Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances Python
echo "📦 Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Créer le fichier de configuration système pour le service
echo "🔧 Configuration du service système..."
sudo tee /etc/systemd/system/home-automation.service > /dev/null <<EOF
[Unit]
Description=Home Automation Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Recharger systemd et activer le service
sudo systemctl daemon-reload
sudo systemctl enable home-automation.service

# Créer le script de démarrage rapide
echo "🔧 Création du script de démarrage..."
cat > start.sh << 'EOF'
#!/bin/bash
# Script de démarrage rapide pour Home Automation

echo "🏠 Démarrage de Home Automation..."

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier les dépendances
if ! pip check &> /dev/null; then
    echo "📦 Installation des dépendances manquantes..."
    pip install -r requirements.txt
fi

# Démarrer l'application
echo "🚀 Lancement de l'application sur http://0.0.0.0:8000"
echo "🌐 Accès local: http://localhost:8000"
echo "🌐 Accès réseau: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter"

python main.py
EOF

chmod +x start.sh

# Créer le script d'arrêt
cat > stop.sh << 'EOF'
#!/bin/bash
# Script d'arrêt pour Home Automation

echo "🛑 Arrêt de Home Automation..."
sudo systemctl stop home-automation.service
pkill -f "python main.py" 2>/dev/null || true
echo "✅ Service arrêté"
EOF

chmod +x stop.sh

# Créer le script de mise à jour
cat > update.sh << 'EOF'
#!/bin/bash
# Script de mise à jour pour Home Automation

echo "🔄 Mise à jour de Home Automation..."

# Arrêter le service
./stop.sh

# Sauvegarder la configuration
if [ -f "config/devices.json" ]; then
    cp config/devices.json config/devices.json.backup
    echo "✅ Configuration sauvegardée"
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Mettre à jour les dépendances
pip install --upgrade -r requirements.txt

# Redémarrer le service
echo "🚀 Redémarrage du service..."
sudo systemctl restart home-automation.service
sudo systemctl status home-automation.service --no-pager
EOF

chmod +x update.sh

echo ""
echo "✅ Installation terminée!"
echo ""
echo "🔧 Configuration:"
echo "   - Modifiez config/devices.json avec vos appareils"
echo "   - Le service démarre automatiquement au boot"
echo ""
echo "🚀 Commandes disponibles:"
echo "   ./start.sh          - Démarrer en mode développement"
echo "   ./stop.sh           - Arrêter le service"
echo "   ./update.sh         - Mettre à jour l'application"
echo ""
echo "📊 Service système:"
echo "   sudo systemctl start home-automation    - Démarrer le service"
echo "   sudo systemctl stop home-automation     - Arrêter le service"
echo "   sudo systemctl status home-automation   - Voir l'état"
echo "   sudo journalctl -f -u home-automation   - Voir les logs"
echo ""
echo "🌐 Accès web:"

# Afficher les adresses IP disponibles
IP=$(hostname -I | awk '{print $1}')
if [ ! -z "$IP" ]; then
    echo "   http://$IP:8000"
else
    echo "   http://localhost:8000"
fi

echo ""
echo "📝 Étapes suivantes:"
echo "   1. Modifiez config/devices.json avec vos appareils"
echo "   2. Lancez: ./start.sh"
echo "   3. Ouvrez votre navigateur à l'adresse ci-dessus"
echo ""