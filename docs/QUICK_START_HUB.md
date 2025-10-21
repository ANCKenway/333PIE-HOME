# 🚀 Démarrage Rapide - 333HOME HUB v6.0

## ⚡ Lancement immédiat

```bash
cd /home/pie333/333HOME
./start.sh
```

Puis ouvrir : **http://localhost:8000/hub**

## 🎯 Qu'est-ce que c'est ?

**333HOME** est maintenant un **HUB unifié** de domotique pour Raspberry Pi. Au lieu d'avoir des pages séparées pour chaque feature, tout est centralisé dans une seule interface moderne.

## 🏗️ Architecture HUB

```
┌─────────────────────────────────────────┐
│  🏠 333HOME HUB                         │
│  ┌───────────┬──────────────────────┐   │
│  │ Sidebar   │  Content Area        │   │
│  │           │                      │   │
│  │ 📊 Dash   │  ┌────────────────┐  │   │
│  │ 📱 Dev    │  │  Module actif  │  │   │
│  │ 🌐 Net    │  │                │  │   │
│  │ 🔒 VPN    │  │  (chargement   │  │   │
│  │ ⚙️ Sys    │  │   dynamique)   │  │   │
│  │           │  └────────────────┘  │   │
│  └───────────┴──────────────────────┘   │
└─────────────────────────────────────────┘
```

## 📦 Features disponibles

### ✅ Opérationnelles

#### 📊 **Dashboard**
- Vue d'ensemble de tout le système
- Stats globales (devices, network, VPN, system)
- Quick actions vers autres modules
- **URL** : `#/dashboard`

#### 📱 **Devices** (Complet)
- Liste de tous vos appareils
- CRUD complet (Créer, Modifier, Supprimer)
- **Wake-on-LAN** ⚡ pour démarrer un PC
- **Ping** 📡 pour tester la connexion
- Modal pour édition
- **URL** : `#/devices`
- **Backend** : 9 endpoints

#### 🌐 **Network** (Complet)
- Scan réseau complet (ARP + Port scanning)
- Historique des scans
- **Bandwidth monitoring** (usage réseau)
- **Latency monitoring** (ping, jitter, packet loss)
- Timeline des événements
- **URL** : `#/network`
- **Backend** : 13 endpoints

### ⚠️ En développement

#### 🔒 **Tailscale VPN** (Placeholder)
- Status VPN (à venir)
- Liste devices Tailscale (à venir)
- Configuration (à venir)
- **URL** : `#/tailscale`
- **Backend** : ❌ À créer

#### ⚙️ **System** (Placeholder)
- Monitoring CPU/RAM/Disk (à venir)
- Uptime (à venir)
- Température Raspberry Pi (à venir)
- Services status (à venir)
- **URL** : `#/system`
- **Backend** : ❌ À créer

## 🎮 Utilisation

### Navigation

**Desktop** :
- Cliquez sur les icônes dans la sidebar
- Ou utilisez les URLs directement : `/hub#/devices`, `/hub#/network`, etc.

**Mobile** :
- Appuyez sur le menu hamburger ☰
- Sélectionnez votre module
- Le menu se ferme automatiquement

### Devices

1. **Ajouter un appareil** :
   - Click "➕ Ajouter un appareil"
   - Remplir nom, IP, MAC (optionnel), type
   - Sauvegarder

2. **Wake-on-LAN** :
   - Click "⚡ Wake" sur un appareil
   - Le magic packet est envoyé
   - L'appareil démarre (si compatible WOL)

3. **Ping** :
   - Click "📡 Ping"
   - Affiche latence ou erreur

4. **Modifier/Supprimer** :
   - Click "✏️ Modifier" → Modal d'édition
   - Click "🗑️ Supprimer" → Confirmation

### Network

1. **Scanner le réseau** :
   - Click "🔍 Scan"
   - Choisir type : Quick, Full, Custom
   - Activer port scanning (optionnel)
   - Lancer le scan

2. **Voir les devices** :
   - Table avec IP, MAC, hostname, vendor
   - Ports ouverts si scan activé
   - Device role auto-détecté

3. **Bandwidth** :
   - Widget temps réel
   - Top talkers
   - Statistiques

4. **Latency** :
   - Ping automatique vers devices
   - Quality score
   - Jitter & packet loss

## 🔧 Configuration

### Fichiers importants

```
/home/pie333/333HOME/
├── app.py                    # Backend FastAPI
├── start.sh                  # Démarrage
├── stop.sh                   # Arrêt
├── web/
│   ├── hub.html             # ⭐ HUB principal (nouveau)
│   ├── index.html           # Ancien (legacy)
│   └── static/
│       └── js/
│           ├── app-hub.js   # App HUB
│           ├── core/        # Router, API, etc.
│           └── modules/     # Modules features
├── src/
│   └── features/
│       ├── devices/         # ✅ Backend devices
│       ├── network/         # ✅ Backend network
│       ├── tailscale/       # ⚠️ À créer
│       └── system/          # ⚠️ À créer
└── data/
    ├── devices.json         # DB devices
    └── scan_history.json    # Historique scans
```

### Variables d'environnement

Par défaut dans `src/core/config.py` :
- `HOST=0.0.0.0`
- `PORT=8000`
- `DEBUG=True`

## 📱 Mobile

Le HUB est **fully responsive** :

- **Desktop** : Sidebar fixe à gauche
- **Tablet** : Sidebar rétractable
- **Mobile** : Menu hamburger

Navigation mobile :
1. Appuyer sur ☰
2. Sidebar glisse depuis la gauche
3. Overlay opaque
4. Click sur item → Navigation + fermeture auto

## 🎨 Design

**Dark Theme** par défaut (modern.css) :
- Couleurs : Gris sombres, accents bleus
- Typography : System fonts
- Icons : Emojis natifs
- Responsive : Mobile-first

## 🐛 Debugging

### Console browser

```javascript
// Accéder à l'app
window.hubApp

// Voir les modules chargés
window.hubApp.modules

// Naviguer manuellement
window.hubApp.router.navigate('devices')

// Voir les routes
window.hubApp.router.getRoutes()
```

### Logs backend

```bash
# Logs en temps réel
tail -f logs/app.log

# Ou dans le terminal où tourne start.sh
```

## 🚨 Problèmes courants

### Le HUB ne charge pas

1. Vérifier que le backend tourne :
   ```bash
   curl http://localhost:8000/health
   ```

2. Vérifier la console browser (F12)

3. Vérifier les logs backend

### Module ne s'affiche pas

1. Ouvrir console browser (F12)
2. Regarder les erreurs JavaScript
3. Vérifier que le fichier module existe :
   ```bash
   ls web/static/js/modules/
   ```

### API ne répond pas

1. Vérifier les endpoints :
   ```bash
   curl http://localhost:8000/api/devices/
   curl http://localhost:8000/api/network/devices
   ```

2. Vérifier les routes dans `app.py`

3. Regarder logs backend

## 📚 Documentation complète

- **Architecture** : `docs/HUB_ARCHITECTURE.md`
- **API Devices** : `docs/DEVICES_FEATURE.md`
- **API Network** : `docs/NETWORK_ARCHITECTURE.md`
- **Développement** : `docs/DEVELOPER_GUIDE.md`

## 🛠️ Prochaines étapes

### Pour toi (développeur)

1. **Implémenter System backend** :
   ```bash
   # Créer src/features/system/
   # Ajouter CPU/RAM/Disk monitoring
   ```

2. **Implémenter Tailscale backend** :
   ```bash
   # Créer src/features/tailscale/
   # Intégrer avec Tailscale CLI
   ```

3. **Améliorer Dashboard** :
   ```bash
   # Endpoint /api/system/stats
   # Vraies données au lieu de placeholders
   ```

### Pour les utilisateurs

1. **Ajouter vos devices** dans module Devices
2. **Scanner votre réseau** dans module Network
3. **Explorer les features** disponibles

## 💡 Tips

- **Bookmark** : Sauvegardez `/hub#/devices` pour accès rapide à vos devices
- **Mobile** : Ajoutez `/hub` à l'écran d'accueil (PWA bientôt disponible)
- **Auto-refresh** : Les modules se rafraîchissent automatiquement (30s)
- **Keyboard** : Back/Forward browser fonctionnent avec le routing

---

**Version** : 6.0.0  
**Support** : Raspberry Pi 5, Linux  
**License** : Privé (projet perso)  
**Contact** : Voir RULES.md

🎉 **Enjoy your new unified HUB!**
