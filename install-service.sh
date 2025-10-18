#!/bin/bash
# 333HOME - Installation Service Production

echo "🏠 Installation de 333HOME comme service système..."

# Copie du fichier service
sudo cp 333home.service /etc/systemd/system/

# Activation du service
sudo systemctl daemon-reload
sudo systemctl enable 333home.service

echo "✅ Service installé ! Commandes utiles :"
echo "  - Démarrer : sudo systemctl start 333home"
echo "  - Arrêter  : sudo systemctl stop 333home"
echo "  - Status   : sudo systemctl status 333home"
echo "  - Logs     : sudo journalctl -u 333home -f"
echo ""
echo "🚀 333HOME démarrera automatiquement au boot !"