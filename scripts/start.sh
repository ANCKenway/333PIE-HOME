#!/bin/bash
# 🏠 333HOME - Script de démarrage
# Gestion de parc informatique domestique

echo "🏠 ===== 333HOME v4.0.0 ====="
echo "🚀 Démarrage de la gestion de parc informatique..."

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 non trouvé"
    exit 1
fi

# Vérifier le répertoire
if [ ! -f "core/server.py" ]; then
    echo "❌ Fichier core/server.py non trouvé"
    echo "   Lancez depuis le répertoire 333HOME"
    exit 1
fi

# Créer les dossiers de données
mkdir -p data

echo "📋 Vérifications OK"
echo ""
echo "🌐 ===== CONNEXIONS ====="
echo "🔗 Interface: http://localhost:8000"
echo "🔗 Réseau: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "📊 Fonctionnalités disponibles:"
echo "   • Monitoring système Raspberry Pi"
echo "   • Scan réseau et découverte appareils"
echo "   • Gestion appareils favoris"
echo "   • Interface web responsive"
echo ""
echo "🛑 Arrêt: Ctrl+C"
echo "================================"
echo ""

# Lancer l'application
cd core && python3 server.py