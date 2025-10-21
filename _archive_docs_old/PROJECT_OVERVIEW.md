# 🏠 333HOME - Vue d'Ensemble du Projet

## 🎯 Objectif Principal

333HOME est une **application de domotique et gestion de parc informatique** conçue pour fonctionner sur Raspberry Pi. Elle permet de contrôler, surveiller et gérer tous les appareils d'un réseau domestique depuis une interface web moderne.

## 🌟 Fonctionnalités Principales

### 📱 Gestion des Appareils
- **Inventaire complet** : Liste de tous les appareils réseau
- **Wake-on-LAN** : Démarrage à distance des PC
- **Monitoring temps réel** : Statut en ligne/hors ligne
- **Classification** : Types d'appareils (PC, serveur, mobile, etc.)
- **Favoris** : Accès rapide aux appareils importants

### 🌐 Scanning Réseau
- **Découverte automatique** : Scan du réseau local
- **Analyse des ports** : Détection des services ouverts
- **Historique** : Suivi de l'évolution du réseau
- **Topologie** : Cartographie des appareils
- **Performance** : Scan rapide ou détaillé

### 🔒 VPN Tailscale
- **Intégration complète** : Gestion du VPN Tailscale
- **Monitoring VPN** : Statut des connexions distantes
- **Configuration** : Interface pour paramétrer Tailscale
- **Sécurité** : Accès sécurisé aux appareils

### 📊 Monitoring Système
- **Métriques temps réel** : CPU, mémoire, disque
- **Surveillance réseau** : Statistiques de connectivité
- **Logs système** : Journaux d'activité
- **Alertes** : Notifications de problèmes

### 🎨 Interface Web
- **Responsive** : Optimisée mobile et desktop
- **Moderne** : Design professionnel avec cartes
- **Temps réel** : Mise à jour automatique des statuts
- **Navigation** : Menu latéral intuitif

## 🏗️ Architecture Technique

### 🔧 Backend (Python)
- **FastAPI** : API REST moderne et rapide
- **Architecture modulaire** : Séparation par domaines
- **Services** : Gestion des appareils, réseau, VPN
- **Base de données** : JSON pour la simplicité

### 🎨 Frontend (JavaScript ES6)
- **Architecture modulaire** : 4 managers spécialisés
- **Vanilla JS** : Pas de framework lourd
- **CSS moderne** : Variables, Grid, Flexbox
- **Mobile-first** : Responsive design

### 🔗 Communication
- **API REST** : Endpoints organisés par domaine
- **JSON** : Format d'échange de données
- **WebSockets** : Pour le temps réel (futur)
- **CORS** : Support multi-origine

## 📁 Structure du Projet

```
333HOME/
├── 📂 api/                    # API modulaire
│   ├── dependencies.py       # Dépendances partagées
│   ├── router.py             # Router principal
│   └── routes/               # Routes par domaine
│       ├── devices.py        # Gestion appareils
│       ├── network.py        # Scan réseau
│       ├── tailscale.py      # VPN Tailscale
│       ├── monitoring.py     # Surveillance
│       ├── system.py         # Administration
│       └── static.py         # Fichiers web
├── 📂 web/                   # Interface web
│   ├── static/
│   │   ├── css/             # Styles modulaires
│   │   └── js/              # JavaScript ES6
│   └── templates/           # Pages HTML
├── 📂 modules/              # Services Python
│   ├── devices/             # Gestion appareils
│   ├── network/             # Scanning réseau
│   └── services/            # Services système
├── 📂 config/               # Configuration
└── 📂 data/                 # Données persistantes
```

## 🚀 Technologies Utilisées

### Backend
- **Python 3.8+** : Langage principal
- **FastAPI** : Framework web moderne
- **Uvicorn** : Serveur ASGI
- **psutil** : Métriques système
- **httpx** : Client HTTP asynchrone

### Frontend
- **JavaScript ES6** : Modules natifs
- **CSS3** : Variables, Grid, Flexbox
- **HTML5** : Sémantique moderne
- **Fetch API** : Requêtes HTTP

### Infrastructure
- **Raspberry Pi** : Plateforme cible
- **Linux** : Système d'exploitation
- **systemd** : Service système
- **JSON** : Stockage de données

## 🎯 Cas d'Usage Principaux

### 🏠 Administration Domestique
- Démarrer le PC du salon depuis le lit
- Vérifier si tous les appareils sont connectés
- Surveiller la consommation réseau
- Accéder aux serveurs domestiques

### 👨‍💻 Gestion IT
- Inventaire automatique du parc
- Monitoring de la connectivité
- Détection de nouveaux appareils
- Analyse de la sécurité réseau

### 🔒 Accès à Distance
- Connexion VPN sécurisée
- Contrôle des appareils en déplacement
- Surveillance continue du réseau
- Alertes de sécurité

## 📊 Métriques de Réussite

### Performance
- ⚡ **Démarrage** : < 5 secondes
- 🌐 **Scan réseau** : < 30 secondes
- 📱 **Interface** : < 2 secondes de réponse
- 💾 **Mémoire** : < 256MB sur Raspberry Pi

### Fiabilité
- 🔄 **Uptime** : > 99%
- 🛡️ **Sécurité** : Accès contrôlé
- 💽 **Sauvegarde** : Configuration persistante
- 🔧 **Maintenance** : Auto-réparation

### Expérience Utilisateur
- 📱 **Mobile** : Interface responsive
- 🎨 **Design** : Professionnel et moderne
- ⚡ **Réactivité** : Temps réel
- 🧭 **Navigation** : Intuitive

## 🛣️ Roadmap

### Version 2.0 (Actuelle)
- ✅ Architecture modulaire backend
- ✅ Interface web responsive
- ✅ Intégration Tailscale
- ✅ Scanning réseau avancé

### Version 2.1 (Prochaine)
- 🔄 WebSockets temps réel
- 📊 Dashboard métriques
- 🔔 Système de notifications
- 🎨 Thèmes personnalisables
- Focus sur de nouvelles fonctionnalités pour lié l'api avec le serveur 333srv (192.168.1.175) serveur linux principale du réseau et crée une api commune avec ce serveur.

### Version 3.0 (Future)
- 🤖 Intelligence artificielle
- 📈 Prédictions réseau
- 🔐 Authentification avancée
- ☁️ Synchronisation cloud

## 📚 Ressources Complémentaires

- **GitHub** : [333PIE-HOME](https://github.com/ANCKenway/333PIE-HOME)
- **Documentation API** : `/docs` (FastAPI auto-docs)
- **Architecture** : [`ARCHITECTURE.md`](./ARCHITECTURE.md)
- **Guide développement** : [`DEVELOPMENT_GUIDE.md`](./DEVELOPMENT_GUIDE.md)

---

**📅 Créé :** 19 octobre 2025  
**🎯 Vision :** Domotique simple, puissante et élégante  
**🔧 Statut :** En développement actif