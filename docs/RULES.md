# 📖 Règles de Développement 333HOME

## 🎯 Objectif
Règles strictes à respecter pour maintenir la qualité et la cohérence du projet 333HOME. Ces règles sont **NON NÉGOCIABLES**.

---

## 🚫 INTERDICTIONS ABSOLUES

### 1. 📁 Gestion des Fichiers
- ❌ **JAMAIS** créer des versions multiples d'un fichier :
  - `app_simple.py`, `app_clean.py`, `app_modern.py` = **INTERDIT**
  - `style_old.css`, `style_new.css` = **INTERDIT**
  - `main_backup.js`, `main_v2.js` = **INTERDIT**

- ✅ **OBLIGATOIRE** : Un fichier = un nom définitif
  - Si problème → debug d'abord
  - En dernier recours → recréation avec même nom + suppression original

### 2. 🏗️ Architecture
- ❌ **Éviter** les "gros pâtés" de code monolithique
- ❌ **Pas de raccourcis** : corriger les problèmes à la racine
- ❌ **Pas d'improvisation** : suivre le plan architectural

### 3. 💻 Code Quality
- ❌ **Pas de code mort** : supprimer le code inutilisé
- ❌ **Pas de TODO permanents** : résoudre ou créer une issue
- ❌ **Pas de hacks temporaires** : solutions propres uniquement

---

## ✅ OBLIGATIONS STRICTES

### 1. 🎯 Développement Méthodique
- 📋 **Planification** : Réfléchir avant d'agir
- 🔍 **Debug complet** : Corriger à la racine, pas de "pansements"
- 📈 **Progression pas à pas** : Ne pas s'emballer
- ❓ **En cas de doute** : Poser la question avant d'agir

### 2. 🏗️ Architecture Modulaire
- 📁 **Structure claire** : Chaque module a une responsabilité définie
- 🔗 **Faible couplage** : Modules indépendants
- 💪 **Forte cohésion** : Fonctionnalités liées regroupées
- 📦 **Réutilisabilité** : Code modulaire et réutilisable

### 3. 🧪 Qualité du Code
- 🔧 **Code propre** : Lisible, commenté, documenté
- ⚡ **Performance** : Optimisé sans compromis
- 🛡️ **Sécurité** : Validation complète des entrées
- 🧪 **Tests** : Couverture appropriée

### 4. 📝 Documentation
- 📖 **Code self-explanatory** : Noms explicites
- 💬 **Commentaires utiles** : Expliquer le "pourquoi", pas le "quoi"
- 📋 **Documentation à jour** : Maintenir la cohérence
- 🎯 **Objectifs clairs** : Chaque modification a un but précis

---

## 🔄 WORKFLOW OBLIGATOIRE

### 1. 📋 Avant de Commencer
```
1. Analyser → Comprendre le problème
2. Planifier → Définir la solution
3. Vérifier → Architecture et dépendances
4. Estimer → Effort et timeline
```

### 2. 💻 Pendant le Développement
```
1. Coder → Respecter les standards
2. Tester → Validation au fur et à mesure
3. Documenter → Commentaires nécessaires
4. Review → Relecture critique
```

### 3. ✅ Avant de Finaliser
```
1. Tests complets → Validation fonctionnelle
2. Performance → Vérification optimisation
3. Documentation → Mise à jour si nécessaire
4. Cleanup → Suppression code inutile
```

---

## 🚨 EN CAS DE PROBLÈME

### 🔍 Procédure de Debug
1. **Identifier** → Localiser la cause racine
2. **Analyser** → Comprendre l'impact
3. **Planifier** → Solution méthodique
4. **Implémenter** → Fix propre et testé
5. **Valider** → Vérification complète

### 🔧 Cas Extrêmes Uniquement
Si impossible de débugger :
1. **Documenter** → Problème précis rencontré
2. **Sauvegarder** → État actuel si nécessaire
3. **Recréer** → Avec le MÊME nom de fichier
4. **Supprimer** → Ancien fichier défaillant
5. **Tester** → Validation complète nouvelle version

---

## 📏 STANDARDS DE CODE

### 🐍 Python Backend
```python
# Imports groupés et ordonnés
import os
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.dependencies import get_service

# Docstrings obligatoires
def function_name(param: type) -> return_type:
    """
    Description claire de la fonction
    
    Args:
        param: Description du paramètre
        
    Returns:
        Description du retour
        
    Raises:
        HTTPException: Cas d'erreur
    """
    pass

# Gestion d'erreurs systématique
try:
    result = risky_operation()
    return {"data": result}
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

### 💻 JavaScript Frontend
```javascript
// Classes ES6 avec documentation
class ModuleName {
    constructor() {
        this.property = null;
    }
    
    /**
     * Description claire de la méthode
     * @param {type} param - Description paramètre
     * @returns {type} Description retour
     */
    methodName(param) {
        // Logique claire et commentée
        try {
            return result;
        } catch (error) {
            console.error('Erreur:', error);
            UIManager.showNotification('Erreur: ' + error.message, 'error');
        }
    }
}

// Gestion d'erreurs robuste
async function apiCall(endpoint) {
    try {
        const response = await APIClient.get(endpoint);
        return response;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}
```

### 🎨 CSS Styles
```css
/* Variables CSS obligatoires */
:root {
    --primary-color: #2563eb;
    --spacing-md: 1rem;
}

/* Classes sémantiques */
.component-name {
    /* Propriétés groupées logiquement */
    display: flex;
    align-items: center;
    
    /* Variables utilisées */
    color: var(--primary-color);
    padding: var(--spacing-md);
    
    /* Responsive */
    @media (max-width: 768px) {
        flex-direction: column;
    }
}

/* Commentaires pour logique complexe */
/* Layout grid pour cartes appareils responsive */
.devices-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--spacing-lg);
}
```

---

## 🔍 REVIEW CHECKLIST

### ✅ Code Review Obligatoire
- [ ] **Lisibilité** : Code compréhensible par autre développeur
- [ ] **Performance** : Pas de goulots d'étranglement
- [ ] **Sécurité** : Validation des entrées
- [ ] **Tests** : Fonctionnalité testée
- [ ] **Documentation** : Commentaires appropriés
- [ ] **Standards** : Conformité aux règles
- [ ] **Modularité** : Architecture respectée
- [ ] **Robustesse** : Gestion d'erreurs

### 🧪 Tests Obligatoires
- [ ] **Fonctionnel** : Feature fonctionne comme attendu
- [ ] **Edge cases** : Cas limites gérés
- [ ] **Performance** : Temps de réponse acceptable
- [ ] **Cross-browser** : Compatibilité navigateurs
- [ ] **Mobile** : Responsive design OK
- [ ] **API** : Endpoints retournent réponses correctes
- [ ] **Erreurs** : Messages d'erreur appropriés

---

## 📊 MÉTRIQUES QUALITÉ

### 🎯 Objectifs Mesurables
- **Performance API** : < 2 secondes réponse
- **Taille modules** : < 500 lignes par fichier
- **Couverture tests** : > 80%
- **Time to fix** : < 1 jour pour bugs critiques
- **Documentation** : 100% fonctions documentées
- **Code duplication** : < 5%

### 📈 Monitoring Continu
```bash
# Vérifications automatiques
find . -name "*.py" -exec wc -l {} + | sort -n
find . -name "*_old.*" -o -name "*_backup.*" -o -name "*_v2.*"
grep -r "TODO" --include="*.py" --include="*.js"
grep -r "FIXME" --include="*.py" --include="*.js"
```

---

## 🚨 VIOLATIONS ET SANCTIONS

### 🔴 Violations Graves
1. **Création fichiers multiples** → Refactoring obligatoire
2. **Code monolithique** → Architecture modulaire forcée
3. **Pas de tests** → Développement bloqué
4. **Documentation manquante** → Code rejeté

### ⚡ Actions Correctives
1. **Warning** → Correction immédiate demandée
2. **Blocking** → Développement suspendu jusqu'à correction
3. **Rollback** → Retour version précédente
4. **Rework** → Refonte complète si nécessaire

---

## 🎓 FORMATION ET RÉFÉRENCES

### 📚 Lectures Obligatoires
- **Clean Code** : Robert C. Martin
- **Refactoring** : Martin Fowler
- **JavaScript Patterns** : Stoyan Stefanov
- **FastAPI Documentation** : Documentation officielle

### 🔗 Références Projet
- [`ARCHITECTURE.md`](./ARCHITECTURE.md) - Architecture système
- [`DEVELOPMENT_GUIDE.md`](./DEVELOPMENT_GUIDE.md) - Guide développement
- [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md) - API référence
- [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) - Résolution problèmes

---

## 💡 PHILOSOPHY & MINDSET

### 🎯 Principes Fondamentaux
1. **Simplicité** : La solution la plus simple est souvent la meilleure
2. **Cohérence** : Maintenir l'uniformité du code
3. **Évolutivité** : Penser à la maintenance future
4. **Collaboration** : Code lisible par tous
5. **Excellence** : Viser la qualité, pas la rapidité

### 🧠 État d'Esprit
- **Patience** : Prendre le temps de bien faire
- **Humilité** : Accepter les feedbacks et critiques
- **Curiosité** : Toujours chercher à améliorer
- **Responsabilité** : Assumer la qualité de son code
- **Collaboration** : Aider les autres développeurs

---

**📅 Règles établies :** 18 octobre 2025  
**🔒 Statut :** NON NÉGOCIABLES  
**🎯 Objectif :** Excellence technique et maintenabilité  
**🔄 Révision :** Annuelle ou si besoin critique