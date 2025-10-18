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
