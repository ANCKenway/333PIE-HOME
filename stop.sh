#!/bin/bash
# ===== 333HOME v4.0.0 - ARRÊT SERVEUR UNIFIÉ =====

PID_FILE="data/unified_server.pid"

echo "🛑 Arrêt du serveur 333HOME..."

# Méthode 1: Utiliser le PID file
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE" 2>/dev/null)
    if [ ! -z "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        echo "🔍 Serveur trouvé (PID: $PID)"
        kill -TERM "$PID" 2>/dev/null
        
        # Attendre jusqu'à 5 secondes
        for i in {1..10}; do
            if ! kill -0 "$PID" 2>/dev/null; then
                echo "✅ Serveur arrêté proprement"
                rm -f "$PID_FILE"
                exit 0
            fi
            sleep 0.5
        done
        
        # Forcer si nécessaire
        echo "⚠️  Arrêt forcé..."
        kill -9 "$PID" 2>/dev/null
        rm -f "$PID_FILE"
        echo "✅ Serveur arrêté (forcé)"
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

# Méthode 2: Chercher le processus uvicorn
PID=$(ps aux | grep "uvicorn.*app:app" | grep -v grep | awk '{print $2}')
if [ ! -z "$PID" ]; then
    echo "🔍 Serveur trouvé (PID: $PID)"
    kill -TERM $PID 2>/dev/null
    sleep 2
    
    # Vérifier si arrêté
    if ! kill -0 $PID 2>/dev/null; then
        echo "✅ Serveur arrêté proprement"
    else
        echo "⚠️  Arrêt forcé..."
        kill -9 $PID 2>/dev/null
        echo "✅ Serveur arrêté (forcé)"
    fi
    rm -f "$PID_FILE"
    exit 0
fi

echo "ℹ️  Aucun serveur en cours d'exécution"
rm -f "$PID_FILE"
exit 0
