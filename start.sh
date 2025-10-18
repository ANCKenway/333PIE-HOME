#!/bin/bash
# ===== 333HOME v4.0.0 - SCRIPT DE DÉMARRAGE FASTAPI =====

echo "🏠 ===== 333HOME v4.0.0 FastAPI ====="
echo "🚀 Démarrage de l'application..."

# Vérifier si un serveur tourne déjà
EXISTING_PID=$(ps aux | grep "uvicorn.*app:app" | grep -v grep | awk '{print $2}')
if [ ! -z "$EXISTING_PID" ]; then
    echo "⚠️  Serveur FastAPI déjà en cours (PID: $EXISTING_PID)"
    echo "🛑 Arrêt du serveur existant..."
    ./stop.sh
    sleep 2
fi

# Vérifications préalables
echo "📋 Vérifications système..."

# Vérifier que Python 3 est disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "app.py" ]; then
    echo "❌ Fichier app.py non trouvé. Lancez depuis le répertoire 333HOME"
    exit 1
fi

# Vérifier les dépendances critiques
echo "📦 Vérification des dépendances FastAPI..."
if ! python3 -c "import fastapi, uvicorn, pydantic" &> /dev/null; then
    echo "⚠️ Dépendances FastAPI manquantes. Installation..."
    if ! pip3 install fastapi uvicorn[standard] pydantic python-multipart --break-system-packages; then
        echo "❌ Impossible d'installer les dépendances FastAPI"
        exit 1
    fi
fi

# Vérifier les dépendances scanner réseau
echo "📦 Vérification des dépendances scanner réseau..."
if ! python3 -c "import nmap, scapy, netifaces, requests, psutil" &> /dev/null; then
    echo "⚠️ Dépendances scanner manquantes. Installation..."
    if ! pip3 install python-nmap scapy netifaces requests psutil --break-system-packages; then
        echo "⚠️ Certaines dépendances scanner n'ont pas pu être installées"
        echo "🔄 Le serveur va démarrer mais le scanner peut être limité"
    fi
fi

# Vérifier que le port 8000 est libre
if lsof -i:8000 &> /dev/null; then
    echo "⚠️ Port 8000 occupé. Libération forcée..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null
    sleep 2
fi

# Afficher les informations de connexion
echo ""
echo "🌐 ===== INFORMATIONS DE CONNEXION ====="
echo "🔗 Interface locale: http://localhost:8000"
echo "🔗 Accès réseau: http://$(hostname -I | awk '{print $1}'):8000"
echo "📖 Documentation API: http://localhost:8000/api/docs"
echo ""
echo "🚀 Fonctionnalités disponibles:"
echo "   • Scanner réseau avancé avec nmap + APIs"
echo "   • Identification automatique d'appareils"
echo "   • Monitoring système Raspberry Pi"
echo "   • Interface web moderne responsive"
echo "   • API REST complète avec FastAPI"
echo ""
echo "🛑 Arrêt: Ctrl+C ou ./stop.sh"
echo "================================"
echo ""

# Démarrage du serveur FastAPI
echo "🚀 Lancement du serveur FastAPI..."
exec python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload