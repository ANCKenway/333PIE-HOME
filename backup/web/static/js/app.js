/* ===== 333HOME DOMOTIQUE - JS UNIFIÉ ===== */

class SimpleApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.api = new SimpleAPI();
        console.log('🏠 333HOME initialisé');
    }

    async init() {
        console.log('🚀 Initialisation de l\'application...');
        
        // Attendre que le DOM soit prêt
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.start());
        } else {
            this.start();
        }
    }

    start() {
        console.log('▶️ Démarrage de l\'application');
        
        // Gestion navigation
        this.setupNavigation();
        
        // Charger la page par défaut
        this.loadPage('dashboard');
        
        console.log('✅ Application prête !');
    }

    setupNavigation() {
        const links = document.querySelectorAll('[data-nav]');
        links.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.dataset.nav;
                this.loadPage(page);
                
                // Mettre à jour navigation active
                links.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            });
        });
    }

    async loadPage(page) {
        console.log(`📄 Chargement page: ${page}`);
        this.currentPage = page;
        
        const content = document.getElementById('app-content');
        if (!content) return;

        // Afficher loader
        content.innerHTML = '<div class="loading-state"><div class="loading-spinner">🔄</div><p>Chargement...</p></div>';

        try {
            switch (page) {
                case 'dashboard':
                    await this.loadDashboard(content);
                    break;
                case 'devices':
                    await this.loadDevices(content);
                    break;
                case 'network':
                    await this.loadNetwork(content);
                    break;
                case 'monitoring':
                    await this.loadMonitoring(content);
                    break;
                default:
                    content.innerHTML = '<div class="empty-state"><h3>Page non trouvée</h3></div>';
            }
        } catch (error) {
            console.error(`❌ Erreur chargement ${page}:`, error);
            content.innerHTML = '<div class="empty-state"><h3>❌ Erreur de chargement</h3></div>';
        }
    }

    async loadDashboard(container) {
        console.log('📊 Chargement dashboard...');
        
        const dashboardData = await this.api.get('/api/dashboard/');
        
        container.innerHTML = `
            <div class="dashboard">
                <h1>📊 Dashboard</h1>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">${dashboardData.system?.uptime || '0'}</div>
                        <div class="stat-label">Uptime</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${dashboardData.system?.cpu || '0'}%</div>
                        <div class="stat-label">CPU</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${dashboardData.system?.memory || '0'}%</div>
                        <div class="stat-label">Mémoire</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${dashboardData.network?.devices || '0'}</div>
                        <div class="stat-label">Appareils</div>
                    </div>
                </div>

                <div class="grid grid--2">
                    <div class="card">
                        <div class="card__header">
                            <h3>🏠 Système</h3>
                        </div>
                        <p>Raspberry Pi fonctionnel</p>
                        <p>Température: ${dashboardData.system?.temperature || 'N/A'}</p>
                    </div>
                    
                    <div class="card">
                        <div class="card__header">
                            <h3>📡 Réseau</h3>
                            <button class="btn btn--primary" onclick="app.scanNetwork()">🔍 Scanner</button>
                        </div>
                        <p>${dashboardData.network?.devices || 0} appareils détectés</p>
                    </div>
                </div>
            </div>
        `;
    }

    async loadDevices(container) {
        console.log('💻 Chargement appareils...');
        
        const devices = await this.api.get('/api/devices/');
        
        container.innerHTML = `
            <div class="devices">
                <h1>💻 Appareils</h1>
                
                <div class="devices-grid">
                    ${devices.map(device => `
                        <div class="card device-card">
                            <div class="card__header">
                                <h3>${device.name || device.ip}</h3>
                                <span class="status-badge status-badge--${device.status}">${device.status}</span>
                            </div>
                            <div class="device-info">
                                <div class="info-item">
                                    <span class="label">IP:</span>
                                    <span class="value">${device.ip}</span>
                                </div>
                                ${device.mac ? `
                                    <div class="info-item">
                                        <span class="label">MAC:</span>
                                        <span class="value">${device.mac}</span>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    async loadNetwork(container) {
        console.log('📡 Chargement réseau...');
        
        const networkData = await this.api.get('/api/network/discover');
        const devices = networkData.devices || [];
        
        container.innerHTML = `
            <div class="network">
                <h1>📡 Scanner Réseau</h1>
                
                <div class="card">
                    <div class="card__header">
                        <h3>🔍 Scanner</h3>
                        <button class="btn btn--primary" onclick="app.scanNetwork()">Scanner maintenant</button>
                    </div>
                    <p>Cliquez pour découvrir les appareils sur le réseau</p>
                </div>

                <div class="devices-grid">
                    ${devices.length === 0 ? 
                        '<div class="empty-state"><h3>🔍 Aucun appareil trouvé</h3><p>Lancez un scan pour découvrir les appareils</p></div>' 
                        :
                        devices.map(device => `
                            <div class="card device-card">
                                <div class="card__header">
                                    <h3>${device.hostname || device.ip}</h3>
                                    <span class="status-badge status-badge--online">En ligne</span>
                                </div>
                                <div class="device-info">
                                    <div class="info-item">
                                        <span class="label">IP:</span>
                                        <span class="value">${device.ip}</span>
                                    </div>
                                    ${device.mac ? `
                                        <div class="info-item">
                                            <span class="label">MAC:</span>
                                            <span class="value">${device.mac}</span>
                                        </div>
                                    ` : ''}
                                    ${device.vendor ? `
                                        <div class="info-item">
                                            <span class="label">Vendeur:</span>
                                            <span class="value">${device.vendor}</span>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        `).join('')
                    }
                </div>
            </div>
        `;
    }

    async loadMonitoring(container) {
        console.log('📈 Chargement monitoring...');
        
        container.innerHTML = `
            <div class="monitoring">
                <h1>📈 Monitoring</h1>
                
                <div class="card">
                    <div class="card__header">
                        <h3>📊 Statistiques système</h3>
                    </div>
                    <p>Monitoring en cours de développement...</p>
                </div>
            </div>
        `;
    }

    async scanNetwork() {
        console.log('🔍 Lancement scan réseau...');
        
        try {
            const result = await this.api.post('/api/network/scan');
            console.log('✅ Scan terminé:', result);
            
            // Recharger la page réseau
            if (this.currentPage === 'network') {
                this.loadPage('network');
            }
            
        } catch (error) {
            console.error('❌ Erreur scan:', error);
        }
    }
}

class SimpleAPI {
    constructor() {
        this.baseURL = '';
    }

    async request(url, options = {}) {
        try {
            console.log(`📡 API: ${options.method || 'GET'} ${url}`);
            
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log(`✅ API réponse:`, data);
            return data;
            
        } catch (error) {
            console.error(`❌ API erreur ${url}:`, error);
            throw error;
        }
    }

    async get(url) {
        return this.request(url);
    }

    async post(url, data = null) {
        return this.request(url, {
            method: 'POST',
            body: data ? JSON.stringify(data) : null
        });
    }
}

// Initialisation globale
let app;

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🌟 Démarrage 333HOME');
    app = new SimpleApp();
    await app.init();
});