# 📚 Documentation 333HOME v6.0

Documentation complète du projet 333HOME - HUB de domotique unifié.

## 🗂️ Organisation de la documentation

### 📖 Documentation principale

- **[HUB_ARCHITECTURE.md](./HUB_ARCHITECTURE.md)** - Architecture complète du HUB v6.0 ⭐
- **[QUICK_START_HUB.md](./QUICK_START_HUB.md)** - Guide de démarrage rapide
- **[FRONTEND_STRUCTURE_HUB.md](./FRONTEND_STRUCTURE_HUB.md)** - Structure frontend détaillée
- **[ARCHITECTURE_DIAGRAMS.md](./ARCHITECTURE_DIAGRAMS.md)** - Diagrammes d'architecture

### � Documentation technique

- **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** - Documentation complète de l'API REST
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Architecture backend Python
- **[DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)** - Guide pour développeurs

### 📦 Features spécifiques

- **[DEVICES_FEATURE.md](./DEVICES_FEATURE.md)** - Feature Devices (Wake-on-LAN, CRUD)
- **[NETWORK_ARCHITECTURE.md](./NETWORK_ARCHITECTURE.md)** - Feature Network (Scanner, Monitoring)

### 📋 Règles et conventions

- **[RULES.md](./RULES.md)** - Règles de développement du projet ⚠️ **IMPORTANT**

## 🗄️ Archives

- **[archive_v5/](./archive_v5/)** - Documentation de la version 5 (Network-focused)

## 🚀 Démarrage rapide

1. **Lire d'abord** : [QUICK_START_HUB.md](./QUICK_START_HUB.md)
2. **Architecture** : [HUB_ARCHITECTURE.md](./HUB_ARCHITECTURE.md)
3. **API** : [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

## 📊 Structure du HUB v6.0

```
333HOME HUB
├── 📊 Dashboard    → Vue d'ensemble, stats globales
├── 📱 Devices      → Gestion appareils, Wake-on-LAN
├── 🌐 Network      → Scanner, monitoring réseau
├── 🔒 Tailscale    → VPN, accès distant
└── ⚙️  System       → Monitoring Raspberry Pi
```

## 🎯 Version actuelle : 6.0

**Architecture** : SPA avec routing moderne et modules lazy-loaded  
**Backend** : FastAPI (Python 3.11+)  
**Frontend** : Vanilla JS ES6, design professionnel compact

## 📝 État des Features

| Feature | État | Documentation |
|---------|------|---------------|
| **Devices** | ✅ Complet | [DEVICES_FEATURE.md](DEVICES_FEATURE.md) |
| **Network** | ✅ Complet | [NETWORK_ARCHITECTURE.md](NETWORK_ARCHITECTURE.md) |
| **Dashboard** | 🔄 En cours | Interface créée, backend TODO |
| **Tailscale** | 🔄 TODO | Interface créée, backend TODO |
| **System** | 🔄 TODO | Interface créée, backend TODO |

---

*Dernière mise à jour : 21 octobre 2025 - Version 6.0*
