#!/bin/bash
# ===== 333HOME DOMOTIQUE ULTRA - SCRIPT D'ARRÊT PROPRE =====

echo "🛑 Arrêt de 333HOME Domotique Ultra..."

# Arrêter tous les processus liés à server.py
if pgrep -f "server.py" > /dev/null; then
    echo "📋 Arrêt du serveur principal..."
    pkill -f "server.py"
    
    # Attendre que les processus se terminent proprement
    for i in {1..5}; do
        if ! pgrep -f "server.py" > /dev/null; then
            break
        fi
        echo "⏳ Attente de l'arrêt des processus... ($i/5)"
        sleep 1
    done
    
    # Force kill si nécessaire
    if pgrep -f "server.py" > /dev/null; then
        echo "⚠️ Arrêt forcé des processus restants..."
        pkill -9 -f "server.py"
    fi
    
    echo "✅ Serveur arrêté"
else
    echo "📋 Aucun processus 333HOME en cours"
fi

# Vérifier si le port 8000 est libéré
if lsof -i:8000 &> /dev/null; then
    echo "⚠️ Port 8000 encore occupé, tentative de libération..."
    fuser -k 8000/tcp 2>/dev/null || true
fi

echo "🏠 333HOME Domotique Ultra arrêté"