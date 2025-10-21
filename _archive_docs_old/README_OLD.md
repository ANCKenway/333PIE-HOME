# 🏠 333HOME - Système de Domotique Raspberry Pi

## 🚀 NOUVELLE IA ? COMMENCE PAR ICI !

### 👋 Bienvenue sur 333HOME !

Si tu es une **nouvelle IA** qui prend la suite de ce projet, **va directement lire** :

📖 **[docs/AI_WELCOME_PROMPT.md](docs/AI_WELCOME_PROMPT.md)**

Ce fichier contient **TOUT** ce que tu dois savoir pour commencer :
- 🎯 **Contexte complet** du projet
- 📚 **Par où commencer** la lecture des docs
- 🛠️ **Options de développement** (tu as carte blanche !)
- ⚠️ **État actuel** et points d'attention
- 🚀 **Guide de démarrage rapide**

---

## 📊 Statut Projet

**🎯 Version :** 2.0.0 - Architecture Modulaire  
**📅 Date :** 19 octobre 2025  
**✅ Statut :** Fonctionnel - Prêt pour développement  
**⚠️ État :** Architecture expérimentale - "champ de mine"  

### 🏗️ Architecture Actuelle
- **Backend :** FastAPI modulaire (6 routes, 46+ endpoints)
- **Frontend :** HTML/CSS/JS (ES6 modules)
- **Système :** Raspberry Pi + systemd service
- **Objectif :** Intégration 333srv (192.168.1.175)

---

## 🎯 Pour les Développeurs Humains

### 🔧 Démarrage Rapide
```bash
# Démarrer l'application
cd /home/pie333/333HOME
python3 app.py

# Interface web
http://192.168.1.XXX:8000

# API Documentation
http://192.168.1.XXX:8000/docs
```

### 📚 Documentation Technique
- **[docs/README.md](docs/README.md)** - Navigation documentation
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Architecture technique
- **[docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)** - Référence API
- **[docs/DEVELOPMENT_GUIDE.md](docs/DEVELOPMENT_GUIDE.md)** - Guide développement

### ⚠️ Important
- **Lire [docs/RULES.md](docs/RULES.md)** - Règles développement
- **Consulter [docs/EMERGENCY_GUIDE.md](docs/EMERGENCY_GUIDE.md)** - En cas de problème
- **Architecture expérimentale** - Tester avant modifications majeures

---

## 🎯 Objectifs du Projet

### 🏠 Fonctionnalités Actuelles
- ✅ **Scan réseau** local et discovery d'appareils
- ✅ **Wake-on-LAN** pour démarrer les PC à distance
- ✅ **Intégration Tailscale** (VPN)
- ✅ **Monitoring système** Raspberry Pi
- ✅ **Interface web** de contrôle
- ✅ **API REST** complète (46+ endpoints)

### 🚀 Vision Future - Intégration 333srv
- 🎯 **Serveur principal** Linux (192.168.1.175)
- 🎯 **Consoles interactives** à distance (SSH/RDP)
- 🎯 **API unifiée** Pi ↔ Serveur
- 🎯 **Gestion centralisée** du parc informatique
- 🎯 **Multi-Pi support** avec orchestration

---

## 📁 Structure Projet

```
333HOME/
├── app.py                    # Point d'entrée FastAPI (106 lignes)
├── app_old.py               # Sauvegarde monolithique (1288 lignes)
├── api/                     # Architecture modulaire
│   ├── dependencies.py      # Services partagés
│   ├── router.py           # Router principal
│   └── routes/             # 6 modules de routes
├── src/                     # Services et utilitaires
├── web/                     # Interface HTML/CSS/JS
├── config/                  # Configuration JSON
└── docs/                    # Documentation complète (16 fichiers)
```

---

## 🔧 Technologies

- **Backend :** Python 3.x, FastAPI, Uvicorn
- **Frontend :** HTML5, CSS3, JavaScript ES6
- **Système :** Raspberry Pi OS, systemd
- **Réseau :** Tailscale VPN, scanner réseau
- **Stockage :** Fichiers JSON (pas de DB actuellement)

---

## 📞 Support et Documentation

### 🆘 En cas de problème
- **[docs/EMERGENCY_GUIDE.md](docs/EMERGENCY_GUIDE.md)** - Procédures d'urgence
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Résolution problèmes
- **Logs système :** `sudo journalctl -u 333home.service -f`

### 📖 Documentation Complète
16 fichiers de documentation couvrant tous les aspects :
- Architecture et développement
- API et modules Python
- Frontend et interface
- Déploiement et production
- Tests et maintenance

---

## 🎯 Message Final

### 🤖 Pour les IA
**👉 Commence par [docs/AI_WELCOME_PROMPT.md](docs/AI_WELCOME_PROMPT.md)**

Tu y trouveras TOUT ce qu'il faut pour prendre la suite du développement avec carte blanche !

### 👨‍💻 Pour les Développeurs
Ce projet est **fonctionnel mais expérimental**. L'architecture modulaire récente est stable mais l'objectif final est l'intégration avec le serveur principal 333srv.

**Bonne exploration et bon développement ! 🚀**

---

**📅 Dernière mise à jour :** 19 octobre 2025  
**🔄 Version :** v2.0.0 - Architecture Modulaire  
**🎯 Statut :** Prêt pour développement continu