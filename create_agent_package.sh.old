#!/bin/bash
# create_agent_package.sh - Utilitaire création package agent
# Usage: ./create_agent_package.sh 1.0.1

set -e

VERSION="${1:-1.0.0}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$SCRIPT_DIR/src/agents"
OUTPUT_DIR="$SCRIPT_DIR/static/agents"
PACKAGE_NAME="agent_v${VERSION}.zip"
PACKAGE_PATH="$OUTPUT_DIR/$PACKAGE_NAME"

echo "╔════════════════════════════════════════════════════════╗"
echo "║   📦 333HOME Agent Package Creator                     ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Version: $VERSION"
echo "Source:  $AGENTS_DIR"
echo "Output:  $PACKAGE_PATH"
echo ""

# Créer dossier output
mkdir -p "$OUTPUT_DIR"

# Supprimer ancien package si existe
if [ -f "$PACKAGE_PATH" ]; then
    echo "⚠️  Removing existing package..."
    rm "$PACKAGE_PATH"
fi

# Créer package ZIP
echo "📦 Creating package..."
cd "$AGENTS_DIR"
zip -r "$PACKAGE_PATH" . \
    -x "*.pyc" \
    -x "__pycache__/*" \
    -x "*/__pycache__/*" \
    -x "*/*/__pycache__/*" \
    -x ".backup/*" \
    -x ".update_temp/*" \
    -x "agent.log" \
    -x ".git/*" \
    -q

# Calculer checksum
echo "🔐 Calculating checksum..."
CHECKSUM=$(sha256sum "$PACKAGE_PATH" | awk '{print $1}')

# Afficher résumé
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║   ✅ PACKAGE CREATED SUCCESSFULLY                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Package:  $PACKAGE_NAME"
echo "Size:     $(du -h "$PACKAGE_PATH" | awk '{print $1}')"
echo "Checksum: $CHECKSUM"
echo ""
echo "📋 CURL COMMAND TO UPDATE TITO:"
echo "--------------------------------"
echo "curl -X POST 'http://333pie.local:8000/api/agents/TITO/update?version=${VERSION}&download_url=http://333pie.local:8000/static/agents/${PACKAGE_NAME}&checksum=${CHECKSUM}&force=false'"
echo ""
echo "📋 CURL COMMAND TO UPDATE 333srv:"
echo "----------------------------------"
echo "curl -X POST 'http://333pie.local:8000/api/agents/333srv/update?version=${VERSION}&download_url=http://333pie.local:8000/static/agents/${PACKAGE_NAME}&checksum=${CHECKSUM}&force=false'"
echo ""
echo "✅ Ready to deploy!"
