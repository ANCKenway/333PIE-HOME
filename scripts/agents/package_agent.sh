#!/bin/bash
# ================================================================
# 333HOME Agent - Script Packaging Unifié
# ================================================================
# Crée package agent avec auto-incrément version et génération installers
# Usage: ./package_agent.sh [--major|--minor|--patch]
# ================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
AGENTS_DIR="$PROJECT_ROOT/src/agents"
STATIC_DIR="$PROJECT_ROOT/static/agents"
INSTALLERS_DIR="$STATIC_DIR/installers"
VERSION_FILE="$AGENTS_DIR/version.py"
CHECKSUMS_FILE="$STATIC_DIR/checksums.json"

echo "╔════════════════════════════════════════════════════════╗"
echo "║   📦 333HOME Agent - Packaging Unifié                 ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# ================================================================
# 1. Lire version actuelle
# ================================================================

if [[ ! -f "$VERSION_FILE" ]]; then
    echo "❌ Fichier version.py introuvable: $VERSION_FILE"
    exit 1
fi

CURRENT_VERSION=$(grep '__version__' "$VERSION_FILE" | cut -d'"' -f2)
echo "📌 Version actuelle: $CURRENT_VERSION"

# ================================================================
# 2. Calculer nouvelle version
# ================================================================

# Parse version (ex: 1.0.17 → MAJOR=1, MINOR=0, PATCH=17)
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Déterminer type incrémentation (par défaut: patch)
INCREMENT_TYPE="${1:-patch}"

case "$INCREMENT_TYPE" in
    --major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    --minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    --patch|*)
        PATCH=$((PATCH + 1))
        ;;
esac

NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
echo "🆕 Nouvelle version: $NEW_VERSION"
echo ""

# ================================================================
# 3. Confirmation utilisateur
# ================================================================

read -p "❓ Continuer avec v${NEW_VERSION}? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Packaging annulé"
    exit 0
fi

# ================================================================
# 4. Mettre à jour version.py
# ================================================================

echo "📝 Mise à jour version.py..."
sed -i "s/__version__ = \"$CURRENT_VERSION\"/__version__ = \"$NEW_VERSION\"/" "$VERSION_FILE"
echo "✅ version.py → v${NEW_VERSION}"
echo ""

# ================================================================
# 5. Créer dossiers output
# ================================================================

mkdir -p "$STATIC_DIR"
mkdir -p "$INSTALLERS_DIR"

# ================================================================
# 6. Créer package ZIP
# ================================================================

echo "📦 Création du package ZIP..."
PACKAGE_NAME="agent_v${NEW_VERSION}.zip"
PACKAGE_PATH="$STATIC_DIR/$PACKAGE_NAME"

# Se placer dans le dossier agents
cd "$AGENTS_DIR"

# Créer ZIP en excluant fichiers temporaires
zip -r "$PACKAGE_PATH" . \
    -x "*.pyc" \
    -x "*__pycache__*" \
    -x "*/__pycache__*" \
    -x "*/*/__pycache__*" \
    -x ".backup/*" \
    -x ".update_temp/*" \
    -x "*.log" \
    -x "agent.log" \
    -x "test_*" \
    -x "deployments/*" \
    -q

# Vérifier création
if [[ ! -f "$PACKAGE_PATH" ]]; then
    echo "❌ Échec création package ZIP"
    exit 1
fi

SIZE=$(du -h "$PACKAGE_PATH" | awk '{print $1}')
echo "✅ Package créé: $PACKAGE_NAME ($SIZE)"
echo ""

# ================================================================
# 7. Calculer checksum SHA256
# ================================================================

echo "🔐 Calcul checksum SHA256..."
CHECKSUM=$(sha256sum "$PACKAGE_PATH" | awk '{print $1}')
echo "✅ SHA256: $CHECKSUM"
echo ""

# ================================================================
# 8. Créer/mettre à jour symlink latest
# ================================================================

echo "🔗 Création symlink agent_latest.zip..."
cd "$STATIC_DIR"
rm -f agent_latest.zip
ln -s "$PACKAGE_NAME" agent_latest.zip
echo "✅ Symlink créé: agent_latest.zip → $PACKAGE_NAME"
echo ""

# ================================================================
# 9. Mettre à jour checksums.json
# ================================================================

echo "📋 Mise à jour checksums.json..."

# Créer fichier si n'existe pas
if [[ ! -f "$CHECKSUMS_FILE" ]]; then
    echo '{"versions":{}}' > "$CHECKSUMS_FILE"
fi

# Ajouter nouvelle version (utiliser jq si disponible, sinon python)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if command -v jq &> /dev/null; then
    # Avec jq (propre)
    jq ".versions[\"$NEW_VERSION\"] = {\"checksum\":\"$CHECKSUM\",\"date\":\"$TIMESTAMP\",\"size\":\"$SIZE\"}" \
        "$CHECKSUMS_FILE" > "${CHECKSUMS_FILE}.tmp"
    mv "${CHECKSUMS_FILE}.tmp" "$CHECKSUMS_FILE"
else
    # Sans jq (fallback python)
    python3 <<EOF
import json
with open('$CHECKSUMS_FILE', 'r') as f:
    data = json.load(f)
data['versions']['$NEW_VERSION'] = {
    'checksum': '$CHECKSUM',
    'date': '$TIMESTAMP',
    'size': '$SIZE'
}
with open('$CHECKSUMS_FILE', 'w') as f:
    json.dump(data, f, indent=2)
EOF
fi

echo "✅ checksums.json mis à jour"
echo ""

# ================================================================
# 10. Copier scripts deployment existants vers static/
# ================================================================

echo "📋 Copie scripts deployment existants..."

# Copier scripts Windows depuis deployments/
WINDOWS_INSTALL_SRC="$AGENTS_DIR/deployments/windows/install.bat"
WINDOWS_UNINSTALL_SRC="$AGENTS_DIR/deployments/windows/uninstall.bat"

if [[ -f "$WINDOWS_INSTALL_SRC" ]]; then
    cp "$WINDOWS_INSTALL_SRC" "$INSTALLERS_DIR/install_windows.bat"
    echo "✅ install_windows.bat (copié depuis deployments/)"
else
    echo "⚠️  install.bat non trouvé dans deployments/windows/"
fi

if [[ -f "$WINDOWS_UNINSTALL_SRC" ]]; then
    cp "$WINDOWS_UNINSTALL_SRC" "$INSTALLERS_DIR/uninstall_windows.bat"
    echo "✅ uninstall_windows.bat (copié depuis deployments/)"
fi

# Linux : Créer installer systemd si besoin
LINUX_OUTPUT="$INSTALLERS_DIR/install_linux.sh"

if [[ ! -f "$LINUX_OUTPUT" ]]; then
    echo "📝 Création install_linux.sh (systemd)..."
    
    cat > "$LINUX_OUTPUT" <<'EOFLINUX'
#!/bin/bash
# 333HOME Agent - Linux Installer (systemd service)
# Version: {{VERSION}}
# Checksum: {{CHECKSUM}}

set -e

VERSION="{{VERSION}}"
CHECKSUM="{{CHECKSUM}}"
INSTALL_DIR="/opt/333home-agent"
SERVICE_USER="333agent"
HUB_URL="http://333pie.local:8000"
PACKAGE_URL="${HUB_URL}/static/agents/agent_latest.zip"

echo "================================================================"
echo "  333HOME Agent v${VERSION} - Installation Linux"
echo "================================================================"

# Vérifier root
[[ $EUID -ne 0 ]] && echo "❌ Root requis (sudo)" && exit 1

# Install deps système
apt-get update -qq && apt-get install -y -qq python3 python3-pip python3-venv curl unzip avahi-daemon 2>/dev/null || \
yum install -y -q python3 python3-pip curl unzip avahi 2>/dev/null || \
dnf install -y -q python3 python3-pip curl unzip avahi 2>/dev/null

# Créer user service
id "$SERVICE_USER" &>/dev/null || useradd -r -s /bin/false -d "$INSTALL_DIR" "$SERVICE_USER"

# Télécharger + vérifier checksum
curl -fsSL "$PACKAGE_URL" -o /tmp/agent.zip
DOWNLOADED_CHECKSUM=$(sha256sum /tmp/agent.zip | awk '{print $1}')
[[ "$DOWNLOADED_CHECKSUM" != "$CHECKSUM" ]] && echo "❌ Checksum mismatch" && exit 1

# Extraire
rm -rf "$INSTALL_DIR" && mkdir -p "$INSTALL_DIR"
unzip -q /tmp/agent.zip -d "$INSTALL_DIR" && rm /tmp/agent.zip

# Venv + deps
cd "$INSTALL_DIR"
python3 -m venv venv
venv/bin/pip install -q -r requirements.txt

# Permissions
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

# Service systemd
cat > /etc/systemd/system/333agent.service <<EOF
[Unit]
Description=333HOME Remote Agent v${VERSION}
After=network-online.target avahi-daemon.service
Wants=network-online.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/agent.py --agent-id \$(hostname)
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable 333agent
systemctl start 333agent

echo "✅ Installation terminée!"
echo "   systemctl status 333agent"
EOFLINUX
    
    # Remplacer placeholders
    sed -i "s/{{VERSION}}/$NEW_VERSION/g; s/{{CHECKSUM}}/$CHECKSUM/g" "$LINUX_OUTPUT"
    chmod +x "$LINUX_OUTPUT"
    echo "✅ install_linux.sh (systemd service)"
fi

echo ""

# ================================================================
# 12. Résumé et commandes de déploiement
# ================================================================

echo "╔════════════════════════════════════════════════════════╗"
echo "║   ✅ PACKAGE v${NEW_VERSION} CRÉÉ AVEC SUCCÈS!            "
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📦 Fichiers générés:"
echo "  • $PACKAGE_NAME ($SIZE)"
echo "  • agent_latest.zip (symlink)"
echo "  • checksums.json (updated)"
echo "  • install_windows.bat (depuis deployments/)"
echo "  • uninstall_windows.bat (depuis deployments/)"
echo "  • install_linux.sh (systemd)"
echo ""
echo "🔐 Checksum SHA256:"
echo "  $CHECKSUM"
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║   🚀 COMMANDES DÉPLOIEMENT                            ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📌 Windows (TITO):"
echo "-------------------"
echo "# Télécharger installer"
echo "curl -O http://333pie.local:8000/static/agents/installers/install_windows.bat"
echo ""
echo "# Exécuter (admin)"
echo "./install_windows.bat"
echo ""
echo ""
echo "📌 Linux (333srv):"
echo "-------------------"
echo "# Installation one-liner"
echo "curl -fsSL http://333pie.local:8000/static/agents/installers/install_linux.sh | sudo bash"
echo ""
echo ""
echo "📌 Update via API:"
echo "-------------------"
echo "# Update TITO"
echo "curl -X POST 'http://333pie.local:8000/api/agents/TITO/update'"
echo ""
echo "# Update 333srv"
echo "curl -X POST 'http://333pie.local:8000/api/agents/333srv/update'"
echo ""
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║   📋 PROCHAINES ÉTAPES                                ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "1. Commit changements:"
echo "   git add src/agents/version.py static/agents/"
echo "   git commit -m \"📦 Agent v${NEW_VERSION} package\""
echo ""
echo "2. Tester installation:"
echo "   - Windows: Double-clic install_windows.bat"
echo "   - Linux: curl | sudo bash"
echo ""
echo "3. Valider agents connectés:"
echo "   curl http://333pie.local:8000/api/agents"
echo ""
echo "✅ Package prêt pour déploiement!"
echo ""
