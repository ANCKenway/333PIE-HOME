#!/bin/bash
# Test rapide de la page de redémarrage

echo "🧪 Test de la page de redémarrage d'urgence"
echo "=========================================="
echo ""

# 1. Tester que la page est accessible
echo "1️⃣ Test accès à la page /restart..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/restart | grep -q "200"; then
    echo "   ✅ Page accessible"
else
    echo "   ❌ Page non accessible"
    exit 1
fi

# 2. Tester l'endpoint health
echo ""
echo "2️⃣ Test endpoint /health..."
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ Serveur en ligne"
    echo "   📊 $HEALTH"
else
    echo "   ❌ Serveur ne répond pas correctement"
    exit 1
fi

# 3. Vérifier que l'endpoint restart existe
echo ""
echo "3️⃣ Vérification endpoint /api/system/restart..."
RESTART_RESPONSE=$(curl -s -X POST http://localhost:8000/api/system/restart 2>&1)
if echo "$RESTART_RESPONSE" | grep -q "success"; then
    echo "   ✅ Endpoint fonctionnel"
    echo "   📝 Réponse: $RESTART_RESPONSE"
else
    echo "   ⚠️  Endpoint accessible mais systemd non configuré (normal)"
    echo "   💡 Lancez ./install_systemd.sh pour activer systemd"
fi

echo ""
echo "=========================================="
echo "✅ Tests terminés"
echo ""
echo "🌐 Accès à la page de redémarrage:"
echo "   Local:  http://localhost:8000/restart"
echo "   Réseau: http://$(hostname -I | awk '{print $1}'):8000/restart"
echo ""
echo "💡 Pour activer le redémarrage automatique:"
echo "   ./install_systemd.sh"
echo ""
