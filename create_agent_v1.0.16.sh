#!/bin/bash
# Package agent v1.0.16 avec tray icon

VERSION="1.0.16"
PACKAGE_NAME="agent_v${VERSION}"
BUILD_DIR="/tmp/${PACKAGE_NAME}"
OUTPUT_DIR="./static/agents"

echo "================================================================"
echo "  Creating 333HOME Agent Package v${VERSION}"
echo "================================================================"
echo ""

# Nettoyer build précédent
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
mkdir -p "$OUTPUT_DIR"

echo "[+] Copying files..."

# Copier fichiers principaux
cp src/agents/agent.py "$BUILD_DIR/"
cp src/agents/agent_tray.pyw "$BUILD_DIR/"
cp src/agents/config.py "$BUILD_DIR/"
cp src/agents/remote_logging.py "$BUILD_DIR/"
cp src/agents/__init__.py "$BUILD_DIR/"
cp src/agents/requirements.txt "$BUILD_DIR/"

# Copier plugins
cp -r src/agents/plugins "$BUILD_DIR/"

# Nettoyer __pycache__
find "$BUILD_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR" -type f -name "*.pyc" -delete

echo "[OK] Files copied to $BUILD_DIR"
echo ""

# Lister contenu
echo "[+] Package contents:"
cd "$BUILD_DIR"
find . -type f | sort
echo ""

# Créer archive ZIP
echo "[+] Creating ZIP archive..."
cd /tmp
zip -r "${PACKAGE_NAME}.zip" "${PACKAGE_NAME}" -q

# Calculer checksum
CHECKSUM=$(sha256sum "${PACKAGE_NAME}.zip" | awk '{print $1}')
SIZE=$(du -h "${PACKAGE_NAME}.zip" | awk '{print $1}')

echo "[OK] Archive created: ${PACKAGE_NAME}.zip ($SIZE)"
echo "[OK] SHA256: $CHECKSUM"
echo ""

# Déplacer vers static/agents
mv "${PACKAGE_NAME}.zip" "$OUTPUT_DIR/"

# Créer lien symbolique agent_latest.zip
cd "$OUTPUT_DIR"
rm -f agent_latest.zip
ln -s "${PACKAGE_NAME}.zip" agent_latest.zip

echo "[+] Package deployed to: $OUTPUT_DIR"
echo ""

# Liste packages disponibles
echo "[+] Available packages:"
ls -lh agent_*.zip
echo ""

echo "================================================================"
echo "  Package v${VERSION} Ready!"
echo "================================================================"
echo ""
echo "Download URL: http://100.115.207.11:8000/static/agents/${PACKAGE_NAME}.zip"
echo "Latest URL:   http://100.115.207.11:8000/static/agents/agent_latest.zip"
echo "Checksum:     $CHECKSUM"
echo ""
