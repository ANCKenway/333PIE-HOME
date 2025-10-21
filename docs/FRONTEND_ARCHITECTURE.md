# 🎨 Frontend Architecture - Design System Moderne

## Problème identifié
> "C'est une grosse partie où on a galéré. Il faut un truc structuré, modulable, pas faire une page / un style. Il faut vraiment que ce soit facilement modulable, qu'on incorpore des nouvelles features facilement et que le style visuel soit vraiment unifié."

## Solution : Architecture à Composants

### Vision
Un **Design System** moderne avec :
- 🧩 Composants réutilisables (boutons, cartes, modals, etc.)
- 🎨 Thème unifié (couleurs, typographie, espacements)
- 📦 Modules par feature (devices, network, etc.)
- ⚡ Framework CSS moderne (Tailwind CSS recommandé)
- 🔄 Structure facilement extensible

---

## Architecture Frontend

```
web/
├── index.html                  # Point d'entrée principal
│
├── assets/
│   ├── logo.svg
│   └── icons/                  # Icônes SVG
│
├── css/
│   ├── main.css               # CSS principal (Tailwind build)
│   ├── theme.css              # Variables CSS (couleurs, fonts)
│   └── components.css         # Styles composants custom
│
├── js/
│   ├── main.js                # Point d'entrée JS
│   ├── api.js                 # Client API (fetch wrapper)
│   ├── router.js              # Router SPA (optionnel)
│   │
│   ├── components/            # Composants UI réutilisables
│   │   ├── Button.js          # Bouton standardisé
│   │   ├── Card.js            # Carte info
│   │   ├── Modal.js           # Modale
│   │   ├── Badge.js           # Badge de statut
│   │   ├── Table.js           # Tableau
│   │   ├── Toast.js           # Notifications
│   │   └── Loader.js          # Indicateur de chargement
│   │
│   ├── features/              # Modules par feature
│   │   ├── devices/
│   │   │   ├── DevicesList.js
│   │   │   ├── DeviceCard.js
│   │   │   ├── DeviceModal.js
│   │   │   └── DeviceActions.js
│   │   │
│   │   ├── network/
│   │   │   ├── NetworkDashboard.js
│   │   │   ├── ScannerControl.js
│   │   │   ├── NetworkTimeline.js
│   │   │   └── DeviceHistory.js
│   │   │
│   │   └── tailscale/
│   │       ├── VPNStatus.js
│   │       └── VPNDevices.js
│   │
│   └── utils/
│       ├── formatters.js      # Format dates, bytes, etc.
│       ├── validators.js      # Validation IP, MAC, etc.
│       └── helpers.js         # Fonctions utilitaires
│
└── templates/                 # Templates HTML (optionnel)
    └── components/
```

---

## Design System

### 1. Thème CSS (Variables)

**`css/theme.css`** :
```css
:root {
  /* Couleurs principales */
  --color-primary: #3b82f6;      /* Bleu */
  --color-secondary: #8b5cf6;    /* Violet */
  --color-success: #10b981;      /* Vert */
  --color-warning: #f59e0b;      /* Orange */
  --color-danger: #ef4444;       /* Rouge */
  --color-info: #06b6d4;         /* Cyan */
  
  /* Couleurs grises */
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;
  
  /* Typographie */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  /* Espacements */
  --spacing-xs: 0.25rem;   /* 4px */
  --spacing-sm: 0.5rem;    /* 8px */
  --spacing-md: 1rem;      /* 16px */
  --spacing-lg: 1.5rem;    /* 24px */
  --spacing-xl: 2rem;      /* 32px */
  
  /* Bordures */
  --radius-sm: 0.375rem;   /* 6px */
  --radius-md: 0.5rem;     /* 8px */
  --radius-lg: 0.75rem;    /* 12px */
  
  /* Ombres */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}

/* Mode sombre (optionnel) */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: var(--color-gray-900);
    --color-text: var(--color-gray-100);
  }
}
```

### 2. Composants de base

#### Button Component

**`js/components/Button.js`** :
```javascript
/**
 * Composant Button standardisé
 * 
 * @param {string} label - Texte du bouton
 * @param {string} variant - primary|secondary|success|danger
 * @param {string} size - sm|md|lg
 * @param {Function} onClick - Handler de clic
 * @param {boolean} loading - État de chargement
 * @param {boolean} disabled - Bouton désactivé
 */
class Button {
  constructor({ label, variant = 'primary', size = 'md', onClick, loading = false, disabled = false }) {
    this.label = label;
    this.variant = variant;
    this.size = size;
    this.onClick = onClick;
    this.loading = loading;
    this.disabled = disabled;
  }
  
  render() {
    const baseClasses = 'btn';
    const variantClass = `btn-${this.variant}`;
    const sizeClass = `btn-${this.size}`;
    const disabledClass = (this.disabled || this.loading) ? 'btn-disabled' : '';
    
    return `
      <button 
        class="${baseClasses} ${variantClass} ${sizeClass} ${disabledClass}"
        ${this.disabled ? 'disabled' : ''}
        onclick="${this.onClick}"
      >
        ${this.loading ? '<span class="spinner"></span>' : ''}
        ${this.label}
      </button>
    `;
  }
}

// CSS correspondant
const buttonStyles = `
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  font-weight: 500;
  border-radius: var(--radius-md);
  transition: all 0.2s;
  cursor: pointer;
  border: none;
}

.btn-sm { padding: var(--spacing-sm) var(--spacing-md); font-size: 0.875rem; }
.btn-md { padding: var(--spacing-md) var(--spacing-lg); font-size: 1rem; }
.btn-lg { padding: var(--spacing-lg) var(--spacing-xl); font-size: 1.125rem; }

.btn-primary { background: var(--color-primary); color: white; }
.btn-primary:hover { background: #2563eb; }

.btn-success { background: var(--color-success); color: white; }
.btn-danger { background: var(--color-danger); color: white; }

.btn-disabled { opacity: 0.5; cursor: not-allowed; }
`;
```

#### Card Component

**`js/components/Card.js`** :
```javascript
/**
 * Composant Card pour afficher du contenu
 */
class Card {
  constructor({ title, content, footer, variant = 'default' }) {
    this.title = title;
    this.content = content;
    this.footer = footer;
    this.variant = variant;
  }
  
  render() {
    return `
      <div class="card card-${this.variant}">
        ${this.title ? `<div class="card-header">${this.title}</div>` : ''}
        <div class="card-body">${this.content}</div>
        ${this.footer ? `<div class="card-footer">${this.footer}</div>` : ''}
      </div>
    `;
  }
}

const cardStyles = `
.card {
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.card-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-gray-200);
  font-weight: 600;
  font-size: 1.125rem;
}

.card-body {
  padding: var(--spacing-lg);
}

.card-footer {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--color-gray-200);
  background: var(--color-gray-50);
}
`;
```

---

## Structure par Feature

### Exemple : Feature Devices

**`js/features/devices/DevicesList.js`** :
```javascript
class DevicesList {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.devices = [];
  }
  
  async load() {
    try {
      const response = await API.get('/api/devices/');
      this.devices = response;
      this.render();
    } catch (error) {
      Toast.error('Erreur chargement appareils');
    }
  }
  
  render() {
    const html = this.devices.map(device => {
      return new DeviceCard(device).render();
    }).join('');
    
    this.container.innerHTML = `
      <div class="devices-grid">
        ${html}
      </div>
    `;
  }
}
```

**`js/features/devices/DeviceCard.js`** :
```javascript
class DeviceCard {
  constructor(device) {
    this.device = device;
  }
  
  render() {
    const statusBadge = new Badge({
      label: this.device.online ? 'Online' : 'Offline',
      variant: this.device.online ? 'success' : 'danger'
    });
    
    return new Card({
      title: `
        ${this.device.name}
        ${statusBadge.render()}
      `,
      content: `
        <div class="device-info">
          <div class="info-row">
            <span class="label">IP:</span>
            <span class="value">${this.device.ip}</span>
          </div>
          <div class="info-row">
            <span class="label">MAC:</span>
            <span class="value">${this.device.mac || 'N/A'}</span>
          </div>
          <div class="info-row">
            <span class="label">Type:</span>
            <span class="value">${this.device.type}</span>
          </div>
        </div>
      `,
      footer: `
        <div class="device-actions">
          ${new Button({ 
            label: 'Ping', 
            variant: 'secondary', 
            size: 'sm',
            onClick: `DeviceActions.ping('${this.device.id}')`
          }).render()}
          ${this.device.mac ? new Button({ 
            label: '⚡ Wake', 
            variant: 'primary', 
            size: 'sm',
            onClick: `DeviceActions.wake('${this.device.id}')`
          }).render() : ''}
        </div>
      `
    }).render();
  }
}
```

---

## Framework CSS Recommandé : Tailwind CSS

### Pourquoi Tailwind ?
- ✅ **Utility-first** : Classes CSS atomiques
- ✅ **Hautement customisable** : Configuration complète
- ✅ **Moderne** : Bien maintenu, grande communauté
- ✅ **Petite taille** : PurgeCSS enlève le CSS inutilisé
- ✅ **Responsive** : Mobile-first par défaut

### Configuration Tailwind

**`tailwind.config.js`** :
```javascript
module.exports = {
  content: [
    './web/**/*.html',
    './web/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        secondary: '#8b5cf6',
        success: '#10b981',
        danger: '#ef4444',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
```

### Exemple avec Tailwind

```html
<!-- Card Device avec Tailwind -->
<div class="bg-white rounded-lg shadow-md overflow-hidden">
  <!-- Header -->
  <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
    <h3 class="text-lg font-semibold text-gray-900">PC Gaming</h3>
    <span class="px-3 py-1 text-sm font-medium text-white bg-green-500 rounded-full">
      Online
    </span>
  </div>
  
  <!-- Body -->
  <div class="px-6 py-4 space-y-3">
    <div class="flex justify-between">
      <span class="text-sm text-gray-500">IP:</span>
      <span class="text-sm font-medium text-gray-900">192.168.1.100</span>
    </div>
    <div class="flex justify-between">
      <span class="text-sm text-gray-500">MAC:</span>
      <span class="text-sm font-mono text-gray-900">aa:bb:cc:dd:ee:ff</span>
    </div>
  </div>
  
  <!-- Footer -->
  <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex gap-2">
    <button class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700">
      Ping
    </button>
    <button class="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700">
      ⚡ Wake
    </button>
  </div>
</div>
```

---

## API Client Standardisé

**`js/api.js`** :
```javascript
/**
 * Client API standardisé
 */
class API {
  static baseURL = '/api';
  
  static async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };
    
    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      Toast.error(error.message);
      throw error;
    }
  }
  
  static get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }
  
  static post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
  
  static patch(endpoint, data) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }
  
  static delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

// Usage
const devices = await API.get('/devices/');
const newDevice = await API.post('/devices/', { name: 'PC', ip: '192.168.1.1' });
```

---

## Layout Principal

**`web/index.html`** :
```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>333HOME - Domotique</title>
  
  <!-- Tailwind CSS (via CDN ou build) -->
  <link href="/css/main.css" rel="stylesheet">
  <link href="/css/theme.css" rel="stylesheet">
</head>
<body class="bg-gray-50">
  <!-- Sidebar -->
  <aside id="sidebar" class="sidebar">
    <div class="sidebar-header">
      <h1>333HOME</h1>
    </div>
    <nav class="sidebar-nav">
      <a href="#devices" class="nav-item active">📱 Appareils</a>
      <a href="#network" class="nav-item">🌐 Réseau</a>
      <a href="#tailscale" class="nav-item">🔒 VPN</a>
      <a href="#monitoring" class="nav-item">📊 Monitoring</a>
      <a href="#settings" class="nav-item">⚙️ Paramètres</a>
    </nav>
  </aside>
  
  <!-- Main Content -->
  <main id="main-content" class="main-content">
    <!-- Header -->
    <header class="header">
      <h2 id="page-title">Appareils</h2>
      <div id="header-actions"></div>
    </header>
    
    <!-- Content Area -->
    <div id="content" class="content">
      <!-- Contenu dynamique injecté ici -->
    </div>
  </main>
  
  <!-- Toast Container -->
  <div id="toast-container"></div>
  
  <!-- Scripts -->
  <script src="/js/api.js"></script>
  <script src="/js/components/Button.js"></script>
  <script src="/js/components/Card.js"></script>
  <script src="/js/components/Toast.js"></script>
  <script src="/js/features/devices/DevicesList.js"></script>
  <script src="/js/main.js"></script>
</body>
</html>
```

---

## Avantages de cette architecture

### ✅ Modulaire
- Chaque feature = dossier isolé
- Ajout d'une feature = créer un nouveau dossier
- Pas de conflit entre features

### ✅ Composants réutilisables
- Button, Card, Modal utilisables partout
- Style unifié automatiquement
- Maintenance centralisée

### ✅ Facilement extensible
```javascript
// Ajouter une nouvelle feature
js/features/monitoring/
  ├── MonitoringDashboard.js
  ├── CPUGraph.js
  └── MemoryGraph.js
```

### ✅ API standardisée
- Un seul client API pour tout
- Gestion d'erreurs centralisée
- Authentification facile à ajouter

### ✅ Design system cohérent
- Variables CSS pour tout
- Thème modifiable en un point
- Mode sombre facile à implémenter

---

## Prochaines étapes

1. ✅ Architecture définie (ce document)
2. 🔄 Installer Tailwind CSS
3. 🔄 Créer composants de base (Button, Card, Modal)
4. 🔄 Créer layout principal
5. 🔄 Implémenter feature Devices
6. 🔄 Implémenter feature Network
7. 🔄 Tests frontend

---

**Vision** : Frontend modulaire, composants réutilisables, design unifié, facilement extensible. ✨
