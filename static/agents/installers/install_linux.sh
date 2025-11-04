#!/bin/bash
# 333HOME Agent - Linux Installer (systemd service)
# Version: 1.0.18
# Checksum: 5954330f1d43eebf5ad0490229e4caa862d651dde060736f1603ea4f9d744489

set -e

VERSION="1.0.18"
CHECKSUM="5954330f1d43eebf5ad0490229e4caa862d651dde060736f1603ea4f9d744489"
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
