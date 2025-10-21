# 🚀 Guide de Développement 333HOME

## 🎯 Objectif
Ce guide vous permettra de reprendre le développement de 333HOME, comprendre l'environnement et suivre les bonnes pratiques.

## 🏗️ Setup Environnement de Développement

### 📋 Prérequis
- **Python 3.8+** (testé avec 3.9)
- **Raspberry Pi 4/5** (recommandé) ou Linux
- **Git** pour le versioning
- **Éditeur** : VS Code recommandé

### 🔧 Installation
```bash
# Cloner le projet
git clone https://github.com/ANCKenway/333PIE-HOME.git
cd 333PIE-HOME

# Installer les dépendances
pip install -r requirements.txt

# Créer les répertoires nécessaires
mkdir -p data config

# Démarrer l'application
python app_new.py
```

### 📂 Structure de Travail
```
333HOME/
├── 🟢 PRODUCTION    app_new.py (architecture modulaire)
├── 🔴 LEGACY        app.py (monolithique - à remplacer)
├── 📁 api/          # Backend modulaire
├── 📁 web/          # Frontend modulaire
├── 📁 modules/      # Services Python
├── 📁 docs/         # Documentation complète
└── 📁 config/       # Configuration système
```

## 📖 Règles de Développement STRICTES

### 🚫 INTERDICTIONS ABSOLUES
1. **Pas de versions multiples** : `app_simple.py`, `app_clean.py`, etc.
2. **Pas de "pâtés" de code** : Tout doit être modulaire
3. **Pas d'improvisation** : Suivre le plan établi
4. **Pas de raccourcis** : Corriger les problèmes à la racine

### ✅ OBLIGATIONS
1. **Architecture modulaire** : Respecter la séparation des responsabilités
2. **Code propre** : Commentaires, nommage explicite
3. **Tests** : Valider chaque modification
4. **Documentation** : Mettre à jour si nécessaire

## 🔄 Workflow de Développement

### 1. 📋 Analyse du Besoin
```
Questions à se poser :
- Quel est le problème exact ?
- Dans quel module cela s'intègre-t-il ?
- Y a-t-il des dépendances ?
- Comment tester la solution ?
```

### 2. 🎯 Planification
```
Étapes :
1. Identifier le module concerné
2. Lister les fichiers à modifier
3. Définir les points de test
4. Estimer la complexité
```

### 3. 💻 Implémentation
```
Bonnes pratiques :
- Modifier un seul module à la fois
- Tester après chaque modification
- Respecter les conventions de nommage
- Documenter les changements complexes
```

### 4. ✅ Validation
```
Tests obligatoires :
- Démarrage application ✓
- Interface web fonctionnelle ✓
- Endpoints API opérationnels ✓
- Pas de régression ✓
```

## 🏗️ Architecture de Développement

### 📱 Backend Development

#### 🔧 Ajouter un Endpoint
```python
# Dans api/routes/[domain].py
@router.get("/nouveau-endpoint")
async def nouveau_endpoint():
    """
    📝 Description de l'endpoint
    """
    try:
        # Logique métier
        result = service.do_something()
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 🔗 Ajouter un Service
```python
# Dans modules/[domain]/
class NouveauService:
    def __init__(self):
        self.config = load_config()
    
    def do_something(self):
        # Implémentation
        pass

# Dans api/dependencies.py
nouveau_service = NouveauService()

def get_nouveau_service():
    return nouveau_service
```

### 🎨 Frontend Development

#### 📊 Ajouter une Page
```javascript
// Dans web/templates/components/
<div id="nouvelle-page" class="page">
    <h2>Nouvelle Page</h2>
    <div class="content">
        <!-- Contenu -->
    </div>
</div>

// Dans modules/[manager].js
renderNouvellePage() {
    // Logique d'affichage
}
```

#### 🎨 Ajouter un Style
```css
/* Dans web/static/css/components/ */
.nouveau-composant {
    /* Variables CSS */
    color: var(--primary-color);
    padding: var(--spacing-md);
}
```

## 🔍 Debug et Résolution de Problèmes

### 🚨 Problèmes Courants

#### 1. Import Errors
```bash
# Vérifier la structure des modules
ls -la modules/
ls -la api/

# Vérifier les __init__.py
find . -name "__init__.py"
```

#### 2. API Non Responsive
```bash
# Vérifier les logs
tail -f debug.log

# Tester les endpoints
curl http://localhost:8000/api/status
```

#### 3. Frontend Cassé
```bash
# Vérifier la console navigateur (F12)
# Tester le chargement des modules
curl http://localhost:8000/static/js/app.js
```

### 🔧 Outils de Debug

#### Backend
```python
# Logging dans le code
import logging
logger = logging.getLogger(__name__)
logger.info(f"Debug: {variable}")

# FastAPI debug mode
uvicorn.run("app:app", reload=True, log_level="debug")
```

#### Frontend
```javascript
// Console debugging
console.log('Debug:', data);
console.table(devices);

// Error handling
try {
    // Code
} catch (error) {
    console.error('Erreur:', error);
    UIManager.showNotification('Erreur: ' + error.message, 'error');
}
```

## 📊 Monitoring du Développement

### 🎯 KPIs à Surveiller
- **Temps de démarrage** : < 5 secondes
- **Temps de réponse API** : < 2 secondes
- **Taille des modules** : < 500 lignes
- **Couverture tests** : > 80%

### 📈 Métriques de Qualité
```bash
# Compter les lignes de code
find api/ -name "*.py" -exec wc -l {} + | tail -1

# Vérifier la complexité
python -m py_compile api/routes/*.py

# Tests de performance
curl -w "%{time_total}\n" http://localhost:8000/api/status
```

## 🧪 Tests et Validation

### ✅ Tests Manuels Obligatoires
```bash
# 1. Démarrage application
python app_new.py

# 2. Test interface web
curl http://localhost:8000/

# 3. Test API devices
curl http://localhost:8000/api/devices/

# 4. Test scan réseau
curl -X POST http://localhost:8000/api/network/scan

# 5. Test monitoring
curl http://localhost:8000/api/monitoring/stats
```

### 🤖 Tests Automatisés (Futur)
```python
# tests/test_api.py
def test_devices_endpoint():
    response = client.get("/api/devices/")
    assert response.status_code == 200
    assert "devices" in response.json()
```

## 📚 Ressources de Développement

### 📖 Documentation
- **FastAPI** : https://fastapi.tiangolo.com/
- **JavaScript ES6** : https://developer.mozilla.org/en-US/docs/Web/JavaScript
- **CSS Grid/Flexbox** : https://css-tricks.com/

### 🔧 Outils Recommandés
- **Postman** : Test des APIs
- **Browser DevTools** : Debug frontend
- **VS Code Extensions** :
  - Python
  - JavaScript ES6
  - REST Client

## 🚨 Procédures d'Urgence

### 🔴 Rollback Rapide
```bash
# Si problème critique
git checkout HEAD~1  # Revenir au commit précédent
python app.py        # Utiliser l'ancien monolithe en urgence
```

### 🔧 Reset Complet
```bash
# Reset données
rm -rf data/* config/*

# Reset git
git reset --hard origin/master

# Redémarrage clean
python app_new.py
```

## 📝 Checklist de Développement

### Avant de Commencer
- [ ] Lire la documentation du module concerné
- [ ] Comprendre l'architecture existante
- [ ] Identifier les dépendances
- [ ] Planifier les tests

### Pendant le Développement
- [ ] Respecter la structure modulaire
- [ ] Commenter le code complexe
- [ ] Tester au fur et à mesure
- [ ] Vérifier les imports

### Avant de Finaliser
- [ ] Tests complets application
- [ ] Vérification interface web
- [ ] Validation des endpoints
- [ ] Mise à jour documentation si nécessaire

---

**📅 Guide créé :** 19 octobre 2025  
**🎯 Objectif :** Développement efficace et maintenable  
**📖 Statut :** Guide de référence officiel