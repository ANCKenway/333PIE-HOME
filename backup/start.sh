#!/bin/bash
# ===== 333HOME DOMOTIQUE ULTRA - SCRIPT DE DÉMARRAGE PROPRE =====

echo "🏠 ===== 333HOME DOMOTIQUE ULTRA ====="
echo "🚀 Démarrage de l'application..."

# Vérifications préalables
echo "📋 Vérifications système..."

# Vérifier que Python 3 est disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "server.py" ]; then
    echo "❌ Fichier server.py non trouvé. Lancez depuis le répertoire 333HOME"
    exit 1
fi

# Vérifier les dépendances critiques
echo "📦 Vérification des dépendances..."
if ! python3 -c "import fastapi, uvicorn" &> /dev/null; then
    echo "⚠️ Dépendances manquantes. Tentative d'installation..."
    if ! pip3 install fastapi uvicorn --break-system-packages; then
        echo "❌ Impossible d'installer les dépendances"
        exit 1
    fi
fi

# Vérifier que le port 8000 est libre
if lsof -i:8000 &> /dev/null; then
    echo "⚠️ Port 8000 occupé. Tentative d'arrêt du processus..."
    pkill -f "server.py" || true
    sleep 2
fi

# Afficher les informations de connexion
echo ""
echo "🌐 ===== INFORMATIONS DE CONNEXION ====="
echo "🔗 Interface locale: http://localhost:8000"
echo "🔗 Accès réseau: http://$(hostname -I | awk '{print $1}'):8000"
echo "📋 API Documentation: http://localhost:8000/docs"
echo ""
echo "📊 Dashboard: http://localhost:8000#dashboard"
echo "📡 Scanner Réseau: http://localhost:8000#network"
echo "💻 Appareils: http://localhost:8000#devices"
echo ""
echo "🛑 Pour arrêter: Ctrl+C ou ./stop.sh"
echo "════════════════════════════════════════════════"
echo ""

# Lancer l'application
exec python3 server.py