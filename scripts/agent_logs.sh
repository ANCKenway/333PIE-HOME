#!/bin/bash
# Script pour consulter les logs d'un agent en temps réel depuis le Hub

AGENT_ID="${1:-TITO}"
LIMIT="${2:-50}"
HUB_URL="http://localhost:8000"

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  📋 Logs Agent: ${AGENT_ID}${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Vérifier si agent connecté
STATUS=$(curl -s "${HUB_URL}/api/agents/${AGENT_ID}" | jq -r '.connected // false')

if [ "$STATUS" != "true" ]; then
    echo -e "${RED}❌ Agent ${AGENT_ID} not connected${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Agent connected${NC}"
echo ""

# Récupérer et afficher les logs
curl -s "${HUB_URL}/api/agents/${AGENT_ID}/logs?limit=${LIMIT}" | jq -r '
    .logs[] |
    if .level == "ERROR" then
        "\u001b[31m[\(.level)]\u001b[0m \(.message)"
    elif .level == "WARNING" then
        "\u001b[33m[\(.level)]\u001b[0m \(.message)"
    elif .level == "INFO" then
        "\u001b[32m[\(.level)]\u001b[0m \(.message)"
    else
        "[\(.level)] \(.message)"
    end
'

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Total logs: ${LIMIT}${NC}"
echo -e "${BLUE}========================================${NC}"
