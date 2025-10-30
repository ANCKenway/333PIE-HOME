# Aliases Utilitaires 333HOME Hub

# Ajouter ces aliases à votre ~/.bashrc ou ~/.zshrc

# === LOGS AGENTS ===

# Voir les logs d'un agent
alias alogs='~/333HOME/scripts/agent_logs.sh'

# Suivre les logs en temps réel
alias awatch='~/333HOME/scripts/agent_logs_watch.sh'

# Logs TITO (raccourci)
alias tlogs='~/333HOME/scripts/agent_logs.sh TITO'
alias twatch='~/333HOME/scripts/agent_logs_watch.sh TITO 1'

# === API AGENTS ===

# Lister tous les agents
alias alist='curl -s http://localhost:8000/api/agents | jq ".[] | {agent_id, version, connected}"'

# Status d'un agent
alias astatus='function _astatus() { curl -s http://localhost:8000/api/agents/$1 | jq .; }; _astatus'

# Plugins d'un agent
alias aplugins='function _aplugins() { curl -s http://localhost:8000/api/agents/$1/plugins | jq .; }; _aplugins'

# === LOGS HUB ===

# Logs Hub temps réel
alias hlogs='tail -f ~/333HOME/hub.log'

# Logs Hub dernières erreurs
alias herrors='grep -i error ~/333HOME/hub.log | tail -20'

# === EXEMPLES D'USAGE ===
# 
# alogs TITO 50         # Afficher 50 derniers logs de TITO
# awatch TITO 2         # Suivre logs TITO (refresh 2s)
# tlogs                 # Logs TITO (raccourci)
# twatch                # Watch TITO (refresh 1s)
# alist                 # Lister agents connectés
# astatus TITO          # Status de TITO
# aplugins TITO         # Plugins de TITO
# hlogs                 # Logs Hub temps réel
# herrors               # Dernières erreurs Hub
