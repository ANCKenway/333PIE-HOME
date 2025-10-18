#!/bin/bash

# 🏠 333HOME - Script d'arrêt
# Arrêt propre du serveur de gestion de parc informatique

echo "🛑 ===== ARRÊT 333HOME ====="
echo "🔍 Recherche des processus serveur..."

# Rechercher les processus Python du serveur
PIDS=$(ps aux | grep "python.*server.py" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "ℹ️  Aucun serveur 333HOME en cours d'exécution"
else
    echo "🎯 Processus trouvés: $PIDS"
    
    for PID in $PIDS; do
        echo "🛑 Arrêt du processus $PID..."
        kill -TERM $PID 2>/dev/null
        
        # Attendre 3 secondes pour un arrêt propre
        sleep 3
        
        # Vérifier si le processus est toujours en cours
        if kill -0 $PID 2>/dev/null; then
            echo "⚠️  Forçage de l'arrêt du processus $PID..."
            kill -KILL $PID 2>/dev/null
        fi
        
        echo "✅ Processus $PID arrêté"
    done
fi

# Vérifier les ports occupés
PORT_CHECK=$(lsof -i :8000 2>/dev/null)
if [ ! -z "$PORT_CHECK" ]; then
    echo "⚠️  Port 8000 toujours occupé:"
    echo "$PORT_CHECK"
    echo "🔧 Libération forcée du port..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null
fi

echo "🧹 Nettoyage des fichiers temporaires..."
# Nettoyer les fichiers de cache Python s'ils existent
find /home/pie333/333HOME -name "*.pyc" -delete 2>/dev/null
find /home/pie333/333HOME -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

echo "✅ 333HOME arrêté proprement"
echo "================================"