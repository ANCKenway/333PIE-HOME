# 🎨 Frontend Guide 333HOME

## 🎯 Objectif
Guide complet du frontend modularisé de 333HOME avec architecture ES6, CSS modulaire et interface responsive.

## 🏗️ Architecture Frontend

### 📁 Structure Modulaire
```
web/
├── templates/
│   ├── index.html              # 🏠 Page principale SPA
│   ├── debug.html              # 🔧 Page de debug
│   ├── test-api.html          # 🧪 Tests API
│   └── components/            # 📦 Templates HTML
│       ├── dashboard.html     # 📊 Tableau de bord
│       ├── devices.html       # 📱 Gestion appareils
│       ├── network.html       # 🌐 Analyse réseau
│       ├── monitoring.html    # 📈 Surveillance
│       ├── services.html      # ⚙️ Services
│       └── sidebar.html       # 🧭 Navigation
└── static/
    ├── css/                   # 🎨 Styles modulaires
    │   ├── main.css          # Point d'entrée
    │   ├── components/       # Composants UI
    │   ├── core/            # Base styles
    │   └── sections/        # Styles par page
    └── js/                   # 💻 JavaScript ES6
        ├── app.js           # Point d'entrée
        ├── core/            # Framework core
        └── modules/         # Managers spécialisés
```

## 💻 JavaScript Architecture

### 🚀 Point d'Entrée (app.js)
```javascript
// web/static/js/app.js
class App {
    constructor() {
        this.dataManager = new DataManager();
        this.deviceManager = new DeviceManager();
        this.networkManager = new NetworkManager();
        this.uiManager = new UIManager();
        this.router = new Router();
    }

    async init() {
        await this.setupMobileMenu();
        await this.setupDeviceButtons();
        await this.router.init();
        await this.dataManager.loadInitialData();
    }
}

// Démarrage automatique
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
    window.app.init();
});
```

### 🧩 Managers Spécialisés

#### 📊 Data Manager
```javascript
// modules/data-manager.js
class DataManager {
    constructor() {
        this.devices = [];
        this.networkData = null;
        this.monitoringData = null;
        this.refreshInterval = 30000; // 30 secondes
    }

    // Chargement des données
    async loadDevices() {
        const response = await APIClient.get('/api/devices/');
        this.devices = response.devices;
        this.renderDevices();
    }

    // Indicateur VPN intelligent
    getVpnIndicator(device) {
        if (!device.is_vpn || !device.ip_secondary) return '';
        
        const vpnStatus = device.vpn_status;
        if (!vpnStatus) return '';
        
        const statusClass = vpnStatus.status === 'online' ? 'online' : 'offline';
        return `<span class="vpn-badge ${statusClass}">VPN</span>`;
    }

    // Actualisation automatique
    startAutoRefresh() {
        setInterval(() => this.refreshData(), this.refreshInterval);
    }
}
```

#### 📱 Device Manager
```javascript
// modules/device-manager.js
class DeviceManager {
    constructor() {
        this.selectedDevice = null;
        this.configModal = null;
    }

    // Rendu des appareils
    renderDevices(devices) {
        const container = document.getElementById('devices-grid');
        container.innerHTML = devices.map(device => `
            <div class="device-card ${device.is_favorite ? 'favorite' : ''}" 
                 data-device-id="${device.id}">
                <div class="device-header">
                    <h3>${device.name}</h3>
                    ${DataManager.getVpnIndicator(device)}
                </div>
                <div class="device-info">
                    <div class="device-ip">${device.ip}</div>
                    <div class="device-type">${device.device_type}</div>
                </div>
                <div class="device-actions">
                    ${this.getDeviceButtons(device)}
                </div>
                <div class="device-status">
                    ${this.getStatusDot(device)}
                </div>
            </div>
        `).join('');
        
        this.setupDeviceEvents();
    }

    // Boutons d'action
    getDeviceButtons(device) {
        let buttons = [];
        
        if (device.wake_on_lan) {
            buttons.push(`
                <button class="btn-action wake" data-device-id="${device.id}">
                    ⚡ Wake
                </button>
            `);
        }
        
        buttons.push(`
            <button class="btn-action config" data-device-id="${device.id}">
                ⚙️ Config
            </button>
        `);
        
        return buttons.join('');
    }

    // Wake-on-LAN
    async handleWakeOnLan(deviceId) {
        try {
            UIManager.showLoading(`Démarrage de l'appareil...`);
            
            const response = await APIClient.post('/api/devices/wake', {
                device_id: deviceId
            });
            
            UIManager.showNotification(response.message, 'success');
        } catch (error) {
            UIManager.showNotification(`Erreur Wake-on-LAN: ${error.message}`, 'error');
        }
    }
}
```

#### 🌐 Network Manager
```javascript
// modules/network-manager.js
class NetworkManager {
    constructor() {
        this.currentScan = null;
        this.scanInProgress = false;
    }

    // Page réseau
    renderNetworkPage() {
        const content = `
            <div class="network-controls">
                <button id="start-scan" class="btn-primary">
                    🔍 Scanner le Réseau
                </button>
                <button id="view-history" class="btn-secondary">
                    📈 Historique
                </button>
                <button id="network-topology" class="btn-secondary">
                    🗺️ Topologie
                </button>
            </div>
            <div id="scan-results" class="scan-results">
                <!-- Résultats du scan -->
            </div>
            <div id="network-stats" class="network-stats">
                <!-- Statistiques réseau -->
            </div>
        `;
        
        document.getElementById('content').innerHTML = content;
        this.setupNetworkEvents();
    }

    // Démarrage scan
    async startNetworkScan() {
        if (this.scanInProgress) return;
        
        this.scanInProgress = true;
        UIManager.showLoading('Scan réseau en cours...');
        
        try {
            await APIClient.post('/api/network/scan', {
                target: '192.168.1.0/24',
                fast: true
            });
            
            // Polling pour les résultats
            this.pollScanResults();
        } catch (error) {
            UIManager.showNotification(`Erreur scan: ${error.message}`, 'error');
            this.scanInProgress = false;
        }
    }
}
```

#### 🎨 UI Manager
```javascript
// modules/ui-manager.js
class UIManager {
    constructor() {
        this.notificationContainer = null;
        this.loadingOverlay = null;
        this.mobileMenuOpen = false;
    }

    // Notifications
    static showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-suppression
        setTimeout(() => {
            notification.remove();
        }, duration);
    }

    // Indicateur de chargement
    static showLoading(message = 'Chargement...') {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="spinner"></div>
                <div class="loading-message">${message}</div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        return overlay;
    }

    // Menu mobile
    setupMobileMenu() {
        const menuToggle = document.getElementById('mobile-menu-toggle');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobile-overlay');
        
        menuToggle?.addEventListener('click', () => {
            this.toggleMobileMenu();
        });
        
        overlay?.addEventListener('click', () => {
            this.closeMobileMenu();
        });
    }
}
```

## 🎨 CSS Architecture

### 📂 Structure CSS Modulaire
```css
/* main.css - Point d'entrée */
@import url('./core/variables.css');
@import url('./core/reset.css');
@import url('./core/layout.css');

@import url('./components/cards.css');
@import url('./components/buttons.css');
@import url('./components/navigation.css');
@import url('./components/forms.css');
@import url('./components/status.css');
@import url('./components/feedback.css');

@import url('./sections/dashboard.css');
@import url('./sections/devices.css');
@import url('./sections/network.css');
@import url('./sections/monitoring.css');
```

### 🎨 Variables CSS
```css
/* core/variables.css */
:root {
    /* Couleurs principales */
    --primary-color: #2563eb;
    --primary-hover: #1d4ed8;
    --secondary-color: #64748b;
    
    /* Couleurs de statut */
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --error-color: #ef4444;
    --info-color: #3b82f6;
    
    /* Couleurs neutres */
    --bg-primary: #ffffff;
    --bg-secondary: #f8fafc;
    --bg-dark: #1e293b;
    --text-primary: #0f172a;
    --text-secondary: #64748b;
    --border-color: #e2e8f0;
    
    /* Espacements */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
    
    /* Tailles */
    --border-radius: 8px;
    --shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.1);
    
    /* Responsive breakpoints */
    --mobile: 768px;
    --tablet: 1024px;
    --desktop: 1280px;
}
```

### 🎴 Cartes d'Appareils
```css
/* components/cards.css */
.device-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: var(--spacing-md);
    min-height: 280px;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow);
    transition: all 0.2s ease;
    position: relative;
}

.device-card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}

.device-card.favorite {
    border-color: var(--primary-color);
    background: linear-gradient(145deg, var(--bg-primary), #f1f5f9);
}

.device-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-md);
}

.device-header h3 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
}

.vpn-badge {
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
}

.vpn-badge.online {
    background: var(--success-color);
    color: white;
}

.vpn-badge.offline {
    background: var(--error-color);
    color: white;
}

.device-actions {
    display: flex;
    gap: var(--spacing-sm);
    margin-top: auto;
}

.btn-action {
    padding: 6px 12px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s ease;
    height: 28px;
    display: flex;
    align-items: center;
    gap: 4px;
}

.btn-action:hover {
    background: var(--bg-secondary);
    border-color: var(--primary-color);
}

.device-status {
    position: absolute;
    top: var(--spacing-sm);
    right: var(--spacing-sm);
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}

.status-dot.online {
    background: var(--success-color);
}

.status-dot.offline {
    background: var(--error-color);
}
```

### 📱 Responsive Design
```css
/* core/layout.css */
.main-container {
    display: flex;
    min-height: 100vh;
}

.sidebar {
    width: 250px;
    background: var(--bg-dark);
    color: white;
    transition: transform 0.3s ease;
}

.content {
    flex: 1;
    padding: var(--spacing-lg);
    background: var(--bg-secondary);
}

/* Mobile */
@media (max-width: 768px) {
    .sidebar {
        position: fixed;
        top: 0;
        left: 0;
        height: 100vh;
        z-index: 1000;
        transform: translateX(-100%);
    }
    
    .sidebar.open {
        transform: translateX(0);
    }
    
    .mobile-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.5);
        z-index: 999;
        display: none;
    }
    
    .mobile-overlay.visible {
        display: block;
    }
    
    .content {
        padding: var(--spacing-md);
    }
    
    .devices-grid {
        grid-template-columns: 1fr;
        gap: var(--spacing-md);
    }
}

/* Tablet */
@media (min-width: 769px) and (max-width: 1024px) {
    .devices-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

/* Desktop */
@media (min-width: 1025px) {
    .devices-grid {
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: var(--spacing-lg);
    }
}
```

## 🔧 Core Framework

### 🌐 API Client
```javascript
// core/api.js
class APIClient {
    static async request(url, options = {}) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
    
    static get(url, options = {}) {
        return this.request(url, { method: 'GET', ...options });
    }
    
    static post(url, body, options = {}) {
        return this.request(url, { method: 'POST', body, ...options });
    }
    
    static put(url, body, options = {}) {
        return this.request(url, { method: 'PUT', body, ...options });
    }
    
    static delete(url, options = {}) {
        return this.request(url, { method: 'DELETE', ...options });
    }
}
```

### 🧭 Router SPA
```javascript
// core/router.js
class Router {
    constructor() {
        this.routes = {
            'dashboard': () => this.renderDashboard(),
            'devices': () => this.renderDevices(),
            'network': () => this.renderNetwork(),
            'monitoring': () => this.renderMonitoring(),
            'services': () => this.renderServices()
        };
        this.currentRoute = 'dashboard';
    }
    
    init() {
        // Gérer les liens de navigation
        document.querySelectorAll('[data-route]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const route = e.target.dataset.route;
                this.navigate(route);
            });
        });
        
        // Route par défaut
        this.navigate('dashboard');
    }
    
    navigate(route) {
        if (this.routes[route]) {
            this.currentRoute = route;
            this.updateActiveNavigation(route);
            this.routes[route]();
        }
    }
    
    updateActiveNavigation(route) {
        document.querySelectorAll('[data-route]').forEach(link => {
            link.classList.remove('active');
        });
        
        document.querySelector(`[data-route="${route}"]`)?.classList.add('active');
    }
}
```

## 📊 Pages et Composants

### 🏠 Dashboard
```html
<!-- templates/components/dashboard.html -->
<div id="dashboard" class="page">
    <div class="dashboard-header">
        <h1>🏠 Tableau de Bord</h1>
        <div class="dashboard-stats">
            <div class="stat-card">
                <div class="stat-value" id="total-devices">-</div>
                <div class="stat-label">Appareils</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="online-devices">-</div>
                <div class="stat-label">En ligne</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="vpn-devices">-</div>
                <div class="stat-label">VPN</div>
            </div>
        </div>
    </div>
    
    <div class="dashboard-content">
        <div class="favorite-devices">
            <h2>📱 Appareils Favoris</h2>
            <div id="favorite-devices-grid" class="devices-grid">
                <!-- Appareils favoris -->
            </div>
        </div>
        
        <div class="recent-activity">
            <h2>📈 Activité Récente</h2>
            <div id="recent-activity-list">
                <!-- Activité récente -->
            </div>
        </div>
    </div>
</div>
```

### 📱 Devices Page
```html
<!-- templates/components/devices.html -->
<div id="devices" class="page">
    <div class="page-header">
        <h1>📱 Gestion des Appareils</h1>
        <div class="page-actions">
            <button id="refresh-devices" class="btn-primary">
                🔄 Actualiser
            </button>
            <button id="add-device" class="btn-secondary">
                ➕ Ajouter
            </button>
        </div>
    </div>
    
    <div class="devices-filters">
        <div class="filter-group">
            <label for="device-type-filter">Type :</label>
            <select id="device-type-filter">
                <option value="">Tous</option>
                <option value="computer">Ordinateur</option>
                <option value="mobile">Mobile</option>
                <option value="server">Serveur</option>
            </select>
        </div>
        
        <div class="filter-group">
            <label for="status-filter">Statut :</label>
            <select id="status-filter">
                <option value="">Tous</option>
                <option value="online">En ligne</option>
                <option value="offline">Hors ligne</option>
            </select>
        </div>
    </div>
    
    <div id="devices-grid" class="devices-grid">
        <!-- Cartes des appareils -->
    </div>
</div>
```

## 🚀 Performance et Optimisation

### ⚡ Lazy Loading
```javascript
// core/lazy-loader.js
class LazyLoader {
    static async loadComponent(componentName) {
        const response = await fetch(`/static/templates/components/${componentName}.html`);
        const html = await response.text();
        return html;
    }
    
    static async loadCSS(cssPath) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = cssPath;
        document.head.appendChild(link);
    }
}
```

### 🎨 CSS Manager
```javascript
// core/css-manager.js
class CSSManager {
    static loadedStyles = new Set();
    
    static async loadPageStyles(pageName) {
        const stylePath = `/static/css/sections/${pageName}.css`;
        
        if (!this.loadedStyles.has(stylePath)) {
            await LazyLoader.loadCSS(stylePath);
            this.loadedStyles.add(stylePath);
        }
    }
}
```

## 📱 Mobile-First Design

### 🎯 Approche Responsive
1. **Mobile First** : Styles de base pour mobile
2. **Progressive Enhancement** : Améliorations pour tablette/desktop
3. **Touch-Friendly** : Boutons et zones tactiles appropriées
4. **Performance** : Optimisation pour réseaux lents

### 📐 Breakpoints
```css
/* Système de breakpoints */
:root {
    --mobile: 768px;
    --tablet: 1024px;
    --desktop: 1280px;
}

/* Mixins responsive */
@media (max-width: 768px) { /* Mobile */ }
@media (min-width: 769px) and (max-width: 1024px) { /* Tablet */ }
@media (min-width: 1025px) { /* Desktop */ }
```

## 🧪 Testing et Debug

### 🔍 Debug Tools
```javascript
// Debug helpers
window.debug = {
    app: () => window.app,
    devices: () => window.app.dataManager.devices,
    apiTest: (endpoint) => APIClient.get(endpoint),
    triggerScan: () => window.app.networkManager.startNetworkScan()
};
```

### 📊 Performance Monitoring
```javascript
// Performance tracking
const performanceMonitor = {
    measurePageLoad: () => {
        window.addEventListener('load', () => {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            console.log(`Page load time: ${loadTime}ms`);
        });
    }
};
```

---

**📅 Guide Frontend créé :** 19 octobre 2025  
**🎨 Architecture :** ES6 Modulaire + CSS Variables  
**📱 Responsive :** Mobile-First Design  
**🚀 Performance :** Lazy Loading + Optimisations