#!/bin/bash
# ===== 333HOME v4.0.0 - SERVEUR UNIFIÉ =====
# FastAPI avec système de contrôle intégré
# Port 8000 unique - API activable/désactivable

SERVER_PORT=8000
PID_FILE="data/unified_server.pid"

echo "🏠 ===== 333HOME SERVEUR UNIFIÉ ====="

# Vérifier si un serveur tourne déjà
EXISTING_PID=$(ps aux | grep "uvicorn.*app:app" | grep -v grep | awk '{print $2}')
if [ ! -z "$EXISTING_PID" ]; then
    echo "⚠️  Serveur déjà en cours (PID: $EXISTING_PID)"
    echo "🛑 Utilisez ./stop.sh pour l'arrêter d'abord"
    exit 1
fi

# Vérifications préalables
echo "📋 Vérifications système..."

# Vérifier Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "app.py" ]; then
    echo "❌ Fichier app.py non trouvé"
    exit 1
fi

# Créer le répertoire data si nécessaire
mkdir -p data

# Vérifier les dépendances
echo "📦 Vérification des dépendances..."
if ! python3 -c "import fastapi, uvicorn, psutil" &> /dev/null; then
    echo "⚠️  Dépendances manquantes. Installation..."
    if ! pip3 install fastapi uvicorn[standard] psutil --break-system-packages; then
        echo "❌ Impossible d'installer les dépendances"
        exit 1
    fi
fi

# Vérifier que le port 8000 est libre
if lsof -i:$SERVER_PORT &> /dev/null 2>&1; then
    echo "⚠️  Port $SERVER_PORT occupé. Libération..."
    lsof -ti :$SERVER_PORT | xargs kill -9 2>/dev/null
    sleep 1
fi

# Afficher les informations de connexion
echo ""
echo "🌐 ===== INFORMATIONS DE CONNEXION ====="
echo "🎯 Serveur unifié: http://localhost:$SERVER_PORT"
echo "🔗 Accès réseau: http://$(hostname -I | awk '{print $1}'):$SERVER_PORT"
echo "📖 Documentation API: http://localhost:$SERVER_PORT/docs"
echo ""
echo "🚀 Fonctionnalités disponibles:"
echo "   • Interface web 333HOME (toujours disponible)"
echo "   • API FastAPI sur /api/* (activée par défaut)"
echo "   • Contrôle à distance via l'onglet Server (secours)"
echo "   • Monitoring en temps réel"
echo "   • WebSocket agents sur /api/ws/agents"
echo ""
echo "🛑 Arrêt: Ctrl+C ou ./stop.sh"
echo "================================"
echo ""

# Démarrage du serveur unifié
echo "🚀 Lancement du serveur unifié..."
python3 -m uvicorn app:app --host 0.0.0.0 --port $SERVER_PORT --reload &
SERVER_PID=$!

# Sauvegarder le PID
echo "$SERVER_PID" > "$PID_FILE"

echo "✅ Serveur unifié démarré (PID: $SERVER_PID)"
echo "🌐 Ouvrez http://localhost:$SERVER_PORT dans votre navigateur"
echo ""
echo "✅ L'API est activée et opérationnelle"
echo "🔧 En cas de problème, utilisez l'onglet Server pour Stop/Start"

# Attendre le processus
wait $SERVER_PID

# Cleanup
rm -f "$PID_FILE"
echo "👋 Serveur arrêté"
