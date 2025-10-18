#!/bin/bash
# Script d'arrêt pour Home Automation

echo "🛑 Arrêt de Home Automation..."
sudo systemctl stop home-automation.service
pkill -f "python main.py" 2>/dev/null || true
echo "✅ Service arrêté"
