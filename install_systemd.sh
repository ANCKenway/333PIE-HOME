#!/bin/bash
# Installation du service systemd pour 333HOME

echo "🔧 Installation du service systemd 333HOME..."

# Créer le répertoire si nécessaire
mkdir -p ~/.config/systemd/user

# Créer le fichier service
cat > ~/.config/systemd/user/333home.service << 'EOF'
[Unit]
Description=333HOME Domotique Server
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/pie333/333HOME
ExecStart=/usr/bin/python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

# Recharger systemd
systemctl --user daemon-reload

echo ""
echo "✅ Service installé !"
echo ""
echo "📋 Commandes disponibles :"
echo "   systemctl --user start 333home      # Démarrer"
echo "   systemctl --user stop 333home       # Arrêter"
echo "   systemctl --user restart 333home    # Redémarrer"
echo "   systemctl --user status 333home     # Voir le statut"
echo "   systemctl --user enable 333home     # Démarrage auto au boot"
echo ""
echo "🌐 Accessible via Cockpit (interface web) :"
echo "   http://192.168.1.150:9090"
echo ""
