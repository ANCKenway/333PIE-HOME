# 🧹 Plan de Cleanup & Solidification Complet 333HOME
**Date:** 4 novembre 2025  
**Objectif:** Solidifier le projet de A à Z avant développements futurs

---

## 🎯 Phase 1: Cleanup Fichiers & Structure (30min)

### 1.1 Data & Backups
- [ ] Supprimer backups anciens (data/backups/reset_20251030_*, reset_20251031_*)
- [ ] Garder seulement backup le plus récent
- [ ] Ajouter .gitignore pour data/*.json (runtime data)
- [ ] Documenter structure data/ dans README

### 1.2 Packages Agents
- [ ] Supprimer versions dev intermédiaires (v1.0.20-27, v1.0.30-31, v1.0.34)
- [ ] Garder milestones: v1.0.28, v1.0.32, v1.0.35, v1.0.37
- [ ] Optimiser checksums.json (ajouter metadata: date, size, description, stable flag)
- [ ] Créer manifest.json enrichi (versions, changelog, breaking changes)

### 1.3 Tests Orphelins
- [ ] Déplacer test_agents_endpoints.py → tests/features/agents/
- [ ] Créer tests/features/agents/__init__.py
- [ ] Nettoyer test_results.json (généré, à ignorer)

### 1.4 Config
- [ ] Valider tailscale_config.json (credentials masqués?)
- [ ] Créer config/settings.py centralisé (paths, retention, versions)
- [ ] Variables d'environnement (.env support)

---

## 🏗️ Phase 2: Refactoring Frontend (45min)

### 2.1 Séparation Fichiers
- [ ] Extraire CSS: web/assets/css/main.css, variables.css, components.css
- [ ] Extraire JS: web/assets/js/app.js, api.js, components.js, utils.js
- [ ] web/index.html → HTML pur (structure seulement)
- [ ] Créer web/assets/js/agents.js (logique agents spécifique)

### 2.2 Organisation Assets
```
web/
├── index.html (structure HTML pure)
├── assets/
│   ├── css/
│   │   ├── variables.css (couleurs, spacing)
│   │   ├── base.css (reset, typography)
│   │   ├── components.css (cards, modals, buttons)
│   │   └── main.css (import all)
│   ├── js/
│   │   ├── config.js (API URLs, constants)
│   │   ├── api.js (fetch wrappers)
│   │   ├── components.js (UI components)
│   │   ├── agents.js (agents management)
│   │   ├── devices.js (devices management)
│   │   ├── network.js (network management)
│   │   └── app.js (init, routing)
│   └── icons/ (si nécessaire)
```

### 2.3 Standardisation UI
- [ ] Variables CSS (couleurs, spacing, fonts)
- [ ] Classes utilitaires réutilisables
- [ ] Components documentés (modal, toast, card, badge)
- [ ] Responsive breakpoints cohérents

---

## 🔧 Phase 3: Backend Solidification (60min)

### 3.1 Code Quality
- [ ] Type hints complets (src/features/, src/core/)
- [ ] Docstrings standardisées (Google style)
- [ ] Supprimer code mort / commentaires debug
- [ ] pylint / ruff cleanup (warnings à 0)

### 3.2 Logging Unifié
- [ ] Format logging standardisé partout
- [ ] Niveaux cohérents (DEBUG dev, INFO prod)
- [ ] Rotation logs (size-based)
- [ ] Cleanup anciens logs

### 3.3 Error Handling
- [ ] Custom exceptions centralisées (src/shared/exceptions.py)
- [ ] Messages d'erreur utilisateur-friendly
- [ ] Logging erreurs avec contexte
- [ ] HTTP status codes cohérents

### 3.4 Validation API
- [ ] Pydantic models pour tous endpoints
- [ ] Validation paramètres (regex, ranges)
- [ ] Réponses standardisées (success/error format)
- [ ] OpenAPI docs à jour (tags, descriptions)

### 3.5 Agents Backend
- [ ] Validation version format (semver regex)
- [ ] Vérifier existence version avant update
- [ ] Rate limiting restart/update (max 1/min)
- [ ] Logs audit actions critiques

---

## 📊 Phase 4: Configuration Centralisée (30min)

### 4.1 Settings Module
```python
# config/settings.py
class Settings(BaseSettings):
    # Paths
    DATA_DIR: Path
    STATIC_DIR: Path
    AGENTS_DIR: Path
    
    # Agents
    AGENT_VERSIONS_TO_KEEP: int = 4
    AGENT_UPDATE_TIMEOUT: int = 300
    AGENT_RESTART_RATE_LIMIT: int = 60
    
    # Network
    NETWORK_SCAN_INTERVAL: int = 300
    NETWORK_HISTORY_RETENTION_DAYS: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_MAX_SIZE: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    class Config:
        env_file = ".env"
```

### 4.2 Environment Variables
- [ ] Créer .env.example
- [ ] .env dans .gitignore
- [ ] Documentation variables obligatoires vs optionnelles
- [ ] Validation au startup

---

## 🧪 Phase 5: Tests & CI/CD (45min)

### 5.1 Tests Coverage
- [ ] Tests agents API (endpoints restart/update)
- [ ] Tests WebSocket (handshake, tasks, logs)
- [ ] Tests plugins (system_restart, self_update)
- [ ] Coverage > 80% sur features critiques

### 5.2 Tests Structure
```
tests/
├── __init__.py
├── conftest.py (fixtures globales)
├── features/
│   ├── agents/
│   │   ├── test_agents_api.py
│   │   ├── test_agents_websocket.py
│   │   └── test_plugins.py
│   ├── devices/
│   └── network/
└── integration/
    └── test_full_workflow.py
```

### 5.3 CI/CD
- [ ] GitHub Actions (pytest, lint, type check)
- [ ] Pre-commit hooks (black, ruff, mypy)
- [ ] Auto-bump version on merge
- [ ] Auto-generate changelog

---

## 📚 Phase 6: Documentation (30min)

### 6.1 README Principal
- [ ] Badges (version, tests, coverage)
- [ ] Quick start (3 commandes max)
- [ ] Architecture overview
- [ ] Features list avec screenshots
- [ ] Troubleshooting section

### 6.2 Docs Structure
```
docs/
├── README.md (index)
├── INSTALLATION.md (setup complet)
├── ARCHITECTURE.md (design patterns, flow)
├── API_DOCUMENTATION.md (✅ déjà fait)
├── AGENTS_GUIDE.md (deployment, plugins)
├── FRONTEND_GUIDE.md (UI components, customization)
├── DEVELOPMENT.md (contributing, setup dev)
└── CHANGELOG.md (versions history)
```

### 6.3 Code Documentation
- [ ] Inline comments (pourquoi, pas quoi)
- [ ] Docstrings (params, returns, raises)
- [ ] Type hints (mypy strict)
- [ ] README par module (src/features/*/README.md)

---

## 🔒 Phase 7: Sécurité & Performance (30min)

### 7.1 Sécurité
- [ ] Rate limiting endpoints sensibles
- [ ] Input sanitization (paths, commands)
- [ ] JWT tokens pour agents WebSocket
- [ ] CORS configuration propre
- [ ] Secrets management (.env)

### 7.2 Performance
- [ ] Cache checksums.json (reload on change)
- [ ] Connection pooling DB (si SQLite)
- [ ] WebSocket heartbeat optimisé
- [ ] Logs asynchrones (queue)
- [ ] Static files compression

### 7.3 Monitoring
- [ ] Health check endpoint (/health)
- [ ] Metrics endpoint (/metrics)
- [ ] Prometheus export (optionnel)
- [ ] Error tracking (Sentry optionnel)

---

## ✅ Phase 8: Validation Finale (30min)

### 8.1 Tests End-to-End
- [ ] Démarrage serveur propre (no warnings)
- [ ] Agent connexion/déconnexion
- [ ] Update complet (download → restart)
- [ ] Restart agent (watchdog)
- [ ] UI fonctionnelle (toutes features)

### 8.2 Documentation
- [ ] README à jour
- [ ] API docs complètes
- [ ] Code commenté
- [ ] Changelog mis à jour

### 8.3 Git
- [ ] .gitignore complet
- [ ] Branches clean
- [ ] Tags versions (v1.0.37)
- [ ] Release notes

---

## 📦 Checklist Finale

### Must Have (Critique)
- [ ] Aucun code mort
- [ ] Aucun warning Python
- [ ] Tests passent (100%)
- [ ] Documentation API à jour
- [ ] .gitignore complet
- [ ] Type hints complets
- [ ] Error handling robuste

### Nice to Have (Bonus)
- [ ] CI/CD GitHub Actions
- [ ] Pre-commit hooks
- [ ] Code coverage > 80%
- [ ] Performance monitoring
- [ ] Changelog automatique

### Future (Après cleanup)
- [ ] JWT authentication agents
- [ ] Dashboard metrics
- [ ] Update groupé
- [ ] Rollback automatique
- [ ] Plugins marketplace

---

## 🎯 Ordre d'Exécution Recommandé

1. **Data & Backups** (5min) → Gain espace immédiat
2. **Packages Agents** (10min) → Cleanup repo
3. **Config Centralisé** (20min) → Base solide
4. **Backend Solidification** (60min) → Code quality
5. **Frontend Refactoring** (45min) → Maintenabilité
6. **Tests** (45min) → Confiance
7. **Documentation** (30min) → Knowledge
8. **Sécurité** (30min) → Production-ready
9. **Validation Finale** (30min) → Ship it!

**Total estimé:** ~4h30 pour un projet solide comme le roc 🪨

---

**Notes:**
- Chaque phase peut être committée individuellement
- Priorité: stabilité > features
- Documentation = code
- Tests = assurance qualité
