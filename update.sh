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
