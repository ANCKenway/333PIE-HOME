# Plan de Refactoring Web - 333HOME

## 🎯 Objectif
Transformer l'architecture web monolithique en système modulaire selon RULES.md

## 📊 État actuel
- `index.html`: 270 lignes (monolithique)
- `main.css`: 528 lignes (monolithique) 
- `app.js`: 2588 lignes (énorme!)

## 🏗️ Nouvelle architecture

### Structure des fichiers
```
web/
├── templates/
│   ├── base/
│   │   ├── layout.html          # Layout principal
│   │   └── page-template.html   # Template de page standard
│   ├── components/
│   │   ├── navigation.html      # Navigation principale
│   │   ├── status-cards.html    # Cartes de statut
│   │   └── device-list.html     # Liste d'appareils
│   └── pages/
│       ├── status.html          # Page statut
│       ├── devices.html         # Page appareils  
│       ├── network.html         # Page réseau
│       └── vpn.html            # Page VPN
├── static/
│   ├── css/
│   │   ├── core/
│   │   │   ├── reset.css        # Reset CSS
│   │   │   ├── variables.css    # Variables globales
│   │   │   └── layout.css       # Layout principal
│   │   └── components/
│   │       ├── buttons.css      # Système de boutons
│   │       ├── cards.css        # Cartes/widgets
│   │       ├── forms.css        # Formulaires
│   │       ├── navigation.css   # Navigation
│   │       └── status.css       # Indicateurs de statut
│   └── js/
│       ├── core/
│       │   ├── utils.js         # Utilitaires
│       │   ├── api.js           # Client API
│       │   └── app.js           # Application principale
│       └── modules/
│           ├── navigation.js    # Logique navigation
│           ├── status.js        # Module statut
│           ├── devices.js       # Module appareils
│           ├── network.js       # Module réseau
│           └── vpn.js           # Module VPN
```

## 🔄 Phases de migration

### Phase 1: CSS modulaire ✅
- [x] Créer structure CSS modulaire
- [x] Variables CSS centralisées
- [x] Reset CSS minimal
- [x] Layout principal
- [x] Composant boutons

### Phase 2: Templates HTML (EN COURS)
- [ ] Extraire navigation en composant
- [ ] Créer templates de pages
- [ ] Composants réutilisables (cartes, listes)
- [ ] Nouveau index.html modulaire

### Phase 3: JavaScript modulaire
- [ ] Extraire modules par fonctionnalité
- [ ] Core utilities et API client
- [ ] Gestionnaire de navigation
- [ ] Modules métier (status, devices, network, vpn)

### Phase 4: Migration progressive
- [ ] Nouveau système en parallèle de l'ancien
- [ ] Tests de fonctionnalité
- [ ] Remplacement définitif
- [ ] Suppression ancien code

## 🎨 Avantages attendus

1. **Maintenabilité**: Code organisé par responsabilité
2. **Réutilisabilité**: Composants modulaires
3. **Performance**: Chargement CSS/JS optimisé  
4. **Scalabilité**: Facile d'ajouter de nouveaux modules
5. **Debug**: Problèmes isolés par module
6. **Cohérence**: Design system unifié

## 🔧 Prochaines étapes

1. Finir les composants CSS manquants
2. Créer les templates de pages
3. Développer le nouveau index.html modulaire
4. Tester en parallèle de l'ancien système
5. Migration progressive module par module