#!/bin/bash
# ===== 333HOME DOMOTIQUE ULTRA - REDÉMARRAGE PROPRE =====

echo "🔄 Redémarrage de 333HOME Domotique Ultra..."

# Arrêter proprement
./stop-clean.sh

# Attendre un peu
echo "⏳ Pause avant redémarrage..."
sleep 3

# Redémarrer
echo "🚀 Redémarrage en cours..."
./start-clean.sh