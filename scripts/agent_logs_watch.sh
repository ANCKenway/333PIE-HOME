#!/bin/bash
# Script pour suivre les logs d'un agent en temps réel (watch mode)

AGENT_ID="${1:-TITO}"
INTERVAL="${2:-2}"
HUB_URL="http://localhost:8000"

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Garder trace du dernier log vu
LAST_TIMESTAMP=""

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  📡 Streaming Logs: ${AGENT_ID}${NC}"
echo -e "${BLUE}  Refresh: ${INTERVAL}s | Ctrl+C to stop${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

while true; do
    # Vérifier connexion
    STATUS=$(curl -s "${HUB_URL}/api/agents/${AGENT_ID}" 2>/dev/null | jq -r '.connected // false')
    
    if [ "$STATUS" != "true" ]; then
        echo -e "${RED}⚠️  Agent disconnected... waiting${NC}"
        sleep $INTERVAL
        continue
    fi
    
    # Récupérer logs
    RESPONSE=$(curl -s "${HUB_URL}/api/agents/${AGENT_ID}/logs?limit=20" 2>/dev/null)
    
    # Afficher seulement nouveaux logs
    echo "$RESPONSE" | jq -r --arg last "$LAST_TIMESTAMP" '
        .logs[] |
        select(.timestamp > $last) |
        if .level == "ERROR" then
            "\u001b[31m[\(.timestamp | split("T")[1] | split(".")[0])] ERROR\u001b[0m \(.message)"
        elif .level == "WARNING" then
            "\u001b[33m[\(.timestamp | split("T")[1] | split(".")[0])] WARN\u001b[0m  \(.message)"
        elif .level == "INFO" then
            "\u001b[32m[\(.timestamp | split("T")[1] | split(".")[0])] INFO\u001b[0m  \(.message)"
        elif .level == "DEBUG" then
            "\u001b[36m[\(.timestamp | split("T")[1] | split(".")[0])] DEBUG\u001b[0m \(.message)"
        else
            "[\(.timestamp | split("T")[1] | split(".")[0])] \(.level) \(.message)"
        end
    '
    
    # Mettre à jour dernier timestamp
    NEW_LAST=$(echo "$RESPONSE" | jq -r '.logs[-1].timestamp // empty')
    if [ -n "$NEW_LAST" ]; then
        LAST_TIMESTAMP="$NEW_LAST"
    fi
    
    sleep $INTERVAL
done
