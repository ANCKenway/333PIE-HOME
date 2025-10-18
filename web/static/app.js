/**
 * 🏠 333HOME - Application JavaScript v4.0.0
 * Interface moderne pour gestion de parc informatique
 */

class HomeApp {
    constructor() {
        this.currentTab = 'status';
        this.apiBase = '';
        this.dataCache = new Map(); // Cache des données
        this.loadingStates = new Set(); // États de chargement
        console.log('🏠 333HOME v4.0.0 initialisé');
    }

    /**
     * Initialisation de l'application
     */
    init() {
        console.log('🚀 Démarrage de l\'application');
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.start());
        } else {
            this.start();
        }
    }

    /**
     * Démarrage de l'application
     */
    start() {
        this.setupNavigation();
        this.setupMobileMenu();
        this.setupInteractions();
        this.switchTab('status');
        this.updateConnectionStatus();
        console.log('✅ Application prête');
    }

    /**
     * Configuration de la navigation
     */
    setupNavigation() {
        const navButtons = document.querySelectorAll('.nav-btn');
        
        navButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const tab = e.currentTarget.dataset.tab;
                if (tab && tab !== this.currentTab) {
                    this.switchTab(tab);
                }
            });
        });
    }

    /**
     * Configuration du menu mobile
     */
    setupMobileMenu() {
        const menuBtn = document.getElementById('mobile-menu-btn');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobile-overlay');
        
        if (!menuBtn || !sidebar || !overlay) return;
        
        // Toggle du menu
        const toggleMenu = () => {
            const isOpen = sidebar.classList.contains('open');
            
            if (isOpen) {
                this.closeMobileMenu();
            } else {
                this.openMobileMenu();
            }
        };
        
        // Events
        menuBtn.addEventListener('click', toggleMenu);
        overlay.addEventListener('click', () => this.closeMobileMenu());
        
        // Fermer le menu lors du changement d'onglet sur mobile
        const originalSwitchTab = this.switchTab.bind(this);
        this.switchTab = (tabName) => {
            originalSwitchTab(tabName);
            if (window.innerWidth <= 768) {
                this.closeMobileMenu();
            }
        };
        
        // Gérer le redimensionnement
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                this.closeMobileMenu();
            }
        });
    }

    /**
     * Ouvrir le menu mobile
     */
    openMobileMenu() {
        const menuBtn = document.getElementById('mobile-menu-btn');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobile-overlay');
        
        if (menuBtn) menuBtn.classList.add('active');
        if (sidebar) sidebar.classList.add('open');
        if (overlay) {
            overlay.classList.add('active');
            overlay.style.display = 'block';
        }
        
        // Empêcher le scroll du body
        document.body.style.overflow = 'hidden';
    }

    /**
     * Fermer le menu mobile
     */
    closeMobileMenu() {
        const menuBtn = document.getElementById('mobile-menu-btn');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobile-overlay');
        
        if (menuBtn) menuBtn.classList.remove('active');
        if (sidebar) sidebar.classList.remove('open');
        if (overlay) {
            overlay.classList.remove('active');
            setTimeout(() => {
                overlay.style.display = 'none';
            }, 300);
        }
        
        // Rétablir le scroll du body
        document.body.style.overflow = '';
    }

    /**
     * Configuration des interactions
     */
    setupInteractions() {
        // Boutons de rafraîchissement
        this.setupButton('refresh-devices', () => this.refreshDevices());
        this.setupButton('add-device', () => this.showAddDevice());
        
        // Boutons de scan réseau
        this.setupButton('start-scan', () => this.startNetworkScan());
        this.setupButton('stop-scan', () => this.stopNetworkScan());
        
        // Boutons de test
        this.setupButton('test-get', () => this.testApiGet());
        this.setupButton('test-post', () => this.testApiPost());
    }

    /**
     * Utilitaire pour configurer un bouton
     */
    setupButton(id, handler) {
        const btn = document.getElementById(id);
        if (btn) {
            btn.addEventListener('click', handler);
        }
    }

    /**
     * Changer d'onglet avec optimisation
     */
    switchTab(tabName) {
        if (this.currentTab === tabName) return;
        
        console.log(`📂 Changement vers l'onglet: ${tabName}`);
        
        // Animation de sortie
        const currentTabElement = document.getElementById(`tab-${this.currentTab}`);
        if (currentTabElement) {
            currentTabElement.style.opacity = '0';
        }
        
        // Mise à jour immédiate de l'interface
        this.updateActiveStates(tabName);
        
        // Animation d'entrée après un délai court
        setTimeout(() => {
            this.showTab(tabName);
            this.loadTabData(tabName);
            this.currentTab = tabName;
        }, 150);
    }

    /**
     * Mettre à jour les états actifs
     */
    updateActiveStates(tabName) {
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });
        
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.toggle('active', tab.id === `tab-${tabName}`);
        });
    }

    /**
     * Afficher l'onglet avec animation
     */
    showTab(tabName) {
        const tabElement = document.getElementById(`tab-${tabName}`);
        if (tabElement) {
            tabElement.style.opacity = '1';
        }
    }

    /**
     * Charger les données d'un onglet
     */
    loadTabData(tabName) {
        // Éviter les chargements multiples
        if (this.loadingStates.has(tabName)) return;
        
        switch(tabName) {
            case 'status':
                this.loadStatus();
                break;
            case 'devices':
                this.loadDevices();
                break;
            case 'network':
                this.loadNetworkInterface();
                break;
            case 'test':
                this.loadTestInterface();
                break;
        }
    }

    /**
     * Charger le statut système
     */
    async loadStatus() {
        if (this.dataCache.has('status') && Date.now() - this.dataCache.get('status').timestamp < 30000) {
            return; // Cache valide de 30s
        }

        console.log('📊 Chargement du statut système');
        this.loadingStates.add('status');
        
        try {
            const response = await fetch(`${this.apiBase}/api/status`);
            const data = await response.json();
            
            if (data.success) {
                this.updateStatusDisplay(data.data);
                this.dataCache.set('status', { data: data.data, timestamp: Date.now() });
            }
        } catch (error) {
            console.error('❌ Erreur statut:', error);
            this.showError('app-status', 'Erreur de connexion');
        } finally {
            this.loadingStates.delete('status');
        }
    }

    /**
     * Mettre à jour l'affichage du statut
     */
    updateStatusDisplay(data) {
        this.setElementContent('app-status', `
            <div class="status-item">
                <span class="status-label">✅ ${data.app_name}</span>
                <div class="status-details">
                    <p>📋 Version: ${data.version}</p>
                    <p>🌐 Serveur: ${data.server}</p>
                    <p>🔧 Debug: ${data.debug ? 'Activé' : 'Désactivé'}</p>
                </div>
            </div>
        `);
        
        this.setElementContent('db-status', `
            <div class="status-item">
                <span class="status-label">✅ Base de données JSON</span>
                <div class="status-details">
                    <p>💾 Stockage: Fichiers locaux</p>
                    <p>🔄 Statut: Opérationnel</p>
                </div>
            </div>
        `);
    }

    /**
     * Charger les appareils
     */
    async loadDevices() {
        console.log('📱 Chargement des appareils');
        this.loadingStates.add('devices');
        
        const container = document.getElementById('devices-list');
        if (container) {
            container.innerHTML = '<div class="loading">🔄 Chargement des appareils...</div>';
        }
        
        try {
            const response = await fetch(`${this.apiBase}/api/devices`);
            const data = await response.json();
            
            if (data.success && data.data && data.data.length > 0) {
                this.displayDevices(data.data);
            } else {
                this.showEmptyDevices();
            }
        } catch (error) {
            console.error('❌ Erreur appareils:', error);
            this.showError('devices-list', 'Erreur lors du chargement des appareils');
        } finally {
            this.loadingStates.delete('devices');
        }
    }

    /**
     * Afficher les appareils
     */
    displayDevices(devices) {
        const container = document.getElementById('devices-list');
        if (!container) return;
        
        container.innerHTML = devices.map(device => `
            <div class="device-item">
                <div class="device-info">
                    <h4>${device.name || device.ip}</h4>
                    <p>IP: ${device.ip} | MAC: ${device.mac || 'N/A'}</p>
                    <p>Type: ${device.type || 'Inconnu'} | Statut: <span class="status-${device.status}">${device.status || 'Inconnu'}</span></p>
                </div>
                <div class="device-actions">
                    ${device.type === 'computer' ? '<button class="btn btn-success btn-sm">💻 Wake-on-LAN</button>' : ''}
                    <button class="btn btn-primary btn-sm">⚙️ Config</button>
                    <button class="btn btn-danger btn-sm">🗑️</button>
                </div>
            </div>
        `).join('');
    }

    /**
     * Affichage vide pour les appareils
     */
    showEmptyDevices() {
        const container = document.getElementById('devices-list');
        if (container) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📱</div>
                    <h3>Aucun appareil géré</h3>
                    <p>Utilisez le scan réseau pour découvrir et ajouter des appareils à votre parc informatique.</p>
                    <button class="btn btn-primary" onclick="app.switchTab('network')">🌐 Scanner le réseau</button>
                </div>
            `;
        }
    }

    /**
     * Interface de scan réseau
     */
    loadNetworkInterface() {
        console.log('🌐 Interface scan réseau prête');
        const container = document.getElementById('network-devices');
        if (container && !container.querySelector('.scan-ready')) {
            container.innerHTML = `
                <div class="scan-ready">
                    <div class="scan-info">
                        <h3>🎯 Découverte réseau</h3>
                        <p>Scannez votre réseau local pour découvrir les appareils connectés.</p>
                    </div>
                </div>
            `;
        }
    }

    /**
     * Démarrer le scan réseau
     */
    async startNetworkScan() {
        console.log('🔍 Démarrage du scan réseau professionnel');
        
        const startBtn = document.getElementById('start-scan');
        const stopBtn = document.getElementById('stop-scan');
        const progressDiv = document.getElementById('scan-progress');
        const statusSpan = document.getElementById('scan-status');
        const resultsDiv = document.getElementById('network-devices');
        
        try {
            // Interface
            if (startBtn) startBtn.disabled = true;
            if (stopBtn) stopBtn.disabled = false;
            if (progressDiv) progressDiv.style.display = 'flex';
            if (statusSpan) statusSpan.textContent = 'Scan en cours...';
            
            // Résultats immédiat
            if (resultsDiv) {
                resultsDiv.innerHTML = '<div class="loading">🔍 Scan réseau professionnel en cours...</div>';
            }
            
            // Animation de progression (sans auto-complétion)
            this.startProgressAnimation();
            
            // VRAI SCAN API
            console.log('📡 Lancement du scan API professionnel...');
            const response = await fetch(`${this.apiBase}/api/network/scan`);
            const data = await response.json();
            
            if (data.success) {
                console.log('✅ Scan API réussi:', data.scan_results.statistics);
                this.scanResults = data.scan_results;
                // Terminer l'animation et afficher les résultats
                this.completeScan();
            } else {
                throw new Error(data.message || 'Scan échoué');
            }
            
        } catch (error) {
            console.error('❌ Erreur scan:', error);
            if (resultsDiv) {
                resultsDiv.innerHTML = `
                    <div class="error-state">
                        <h3>❌ Erreur de scan</h3>
                        <p>${error.message}</p>
                        <button class="btn btn-primary" onclick="app.startNetworkScan()">🔄 Réessayer</button>
                    </div>
                `;
            }
            this.resetScanInterface();
        }
    }

    /**
     * Animation de progression (sans auto-complétion)
     */
    startProgressAnimation() {
        const progressFill = document.getElementById('progress-fill');
        const statusSpan = document.getElementById('scan-status');
        let progress = 0;
        
        // Animation lente qui ne dépasse jamais 90%
        this.progressInterval = setInterval(() => {
            progress += Math.random() * 5 + 2; // Plus lent
            if (progress > 90) progress = 90; // Plafonné à 90%
            
            if (progressFill) progressFill.style.width = `${progress}%`;
            if (statusSpan) statusSpan.textContent = `Scan réseau professionnel... ${Math.round(progress)}%`;
        }, 500); // Plus lent
    }
    
    /**
     * Animation de scan (ancienne - obsolète)
     */
    runScanAnimation() {
        console.log('⚠️ runScanAnimation() obsolète - utiliser startProgressAnimation()');
        this.startProgressAnimation();
    }

    /**
     * Terminer le scan
     */
    completeScan() {
        console.log('✅ Scan terminé');
        
        // Arrêter l'animation de progression
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        
        const startBtn = document.getElementById('start-scan');
        const stopBtn = document.getElementById('stop-scan');
        const progressDiv = document.getElementById('scan-progress');
        const progressFill = document.getElementById('progress-fill');
        const statusSpan = document.getElementById('scan-status');
        
        // Finaliser la barre à 100%
        if (progressFill) progressFill.style.width = '100%';
        if (statusSpan) statusSpan.textContent = 'Scan terminé !';
        
        // Interface
        if (startBtn) startBtn.disabled = false;
        if (stopBtn) stopBtn.disabled = true;
        
        // Résultats RÉELS
        this.displayScanResults();
        
        // Masquer la progress bar
        setTimeout(() => {
            if (progressDiv) progressDiv.style.display = 'none';
        }, 2000);
    }

    /**
     * Afficher les résultats du scan
     */
    displayScanResults() {
        const resultsDiv = document.getElementById('network-devices');
        if (!resultsDiv || !this.scanResults) return;
        
        const devices = this.scanResults.devices || [];
        const stats = this.scanResults.statistics || {};
        
        console.log(`🎯 Affichage de ${devices.length} appareils découverts`);
        
        // Grouper par catégorie pour un affichage organisé
        const categories = {
            'computers': { emoji: '💻', label: 'Ordinateurs & Serveurs', devices: [] },
            'mobile': { emoji: '📱', label: 'Mobiles & Tablettes', devices: [] },
            'iot': { emoji: '🏠', label: 'IoT & Smart Home', devices: [] },
            'network': { emoji: '🌐', label: 'Équipements Réseau', devices: [] },
            'unknown': { emoji: '❓', label: 'Appareils Inconnus', devices: [] }
        };
        
        // Catégorisation intelligente
        devices.forEach(device => {
            const deviceType = device.device_type?.toLowerCase() || '';
            const vendor = device.vendor?.toLowerCase() || '';
            const os = device.os_detected?.toLowerCase() || '';
            
            if (deviceType.includes('pc') || deviceType.includes('linux') || deviceType.includes('serveur') || os.includes('linux') || os.includes('windows')) {
                categories.computers.devices.push(device);
            } else if (deviceType.includes('iphone') || deviceType.includes('mobile') || vendor.includes('apple') || vendor.includes('samsung') || os.includes('ios') || os.includes('android')) {
                categories.mobile.devices.push(device);
            } else if (vendor.includes('dyson') || vendor.includes('esp') || deviceType.includes('iot') || deviceType.includes('smart')) {
                categories.iot.devices.push(device);
            } else if (vendor.includes('freebox') || deviceType.includes('routeur') || deviceType.includes('router')) {
                categories.network.devices.push(device);
            } else {
                categories.unknown.devices.push(device);
            }
        });
        
        resultsDiv.innerHTML = `
            <div class="scan-results">
                <div class="scan-header">
                    <h3>🎯 ${devices.length} appareils détectés</h3>
                </div>
                
                ${Object.entries(categories)
                    .filter(([key, cat]) => cat.devices.length > 0)
                    .map(([key, cat]) => `
                        <div class="device-category">
                            <h4 class="category-header">${cat.emoji} ${cat.label} (${cat.devices.length})</h4>
                            <div class="devices-grid">
                                ${cat.devices.map(device => this.renderDeviceCard(device)).join('')}
                            </div>
                        </div>
                    `).join('')}
                    
                ${devices.length === 0 ? '<div class="empty-state">❌ Aucun appareil découvert</div>' : ''}
            </div>
        `;
    }
    
    /**
     * Rendu d'une carte d'appareil
     */
    renderDeviceCard(device) {
        const hostname = device.hostname || '';
        const vendor = device.vendor || '';
        const os = device.os_detected || 'Inconnu';
        const deviceType = device.device_type || 'Inconnu';
        const confidence = device.os_confidence || 'Inconnue';
        
        // Titre intelligent : Hostname > Vendor > IP
        let deviceTitle = '';
        if (hostname && hostname !== 'N/A') {
            deviceTitle = hostname;
        } else if (vendor && vendor !== 'Inconnu') {
            deviceTitle = vendor;
        } else {
            deviceTitle = device.ip;
        }
        
        return `
            <div class="device-card">
                <div class="device-header">
                    <span class="device-title">${deviceTitle}</span>
                    <span class="device-status online">●</span>
                </div>
                <div class="device-details">
                    <div class="device-info">
                        <p><strong>📍 IP:</strong> ${device.ip}</p>
                        <p><strong>🏷️ Nom:</strong> ${hostname || 'N/A'}</p>
                        <p><strong>🏭 Fabricant:</strong> ${vendor || 'Inconnu'}</p>
                        <p><strong>💻 OS:</strong> ${os}</p>
                        <p><strong>📱 Type:</strong> ${deviceType}</p>
                        <p><strong>📊 Confiance:</strong> ${confidence}</p>
                    </div>
                </div>
                <div class="device-actions">
                    <button class="btn btn-primary btn-sm" onclick="app.addDeviceToMonitoring('${device.ip}')">
                        ➕ Surveiller
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="app.showDeviceDetails('${device.ip}')">
                        🔍 Détails
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Interface de test
     */
    loadTestInterface() {
        console.log('🔧 Interface de test prête');
    }

    /**
     * Tests API
     */
    async testApiGet() {
        const resultsDiv = document.getElementById('test-results');
        if (resultsDiv) {
            resultsDiv.innerHTML = '<div class="loading">🔄 Test GET...</div>';
        }
        
        try {
            const response = await fetch(`${this.apiBase}/api/status`);
            const data = await response.json();
            
            if (resultsDiv) {
                resultsDiv.innerHTML = `
                    <div class="test-result success">
                        <h4>✅ Test GET réussi</h4>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </div>
                `;
            }
        } catch (error) {
            if (resultsDiv) {
                resultsDiv.innerHTML = `
                    <div class="test-result error">
                        <h4>❌ Test GET échoué</h4>
                        <p>${error.message}</p>
                    </div>
                `;
            }
        }
    }

    /**
     * Réinitialiser l'interface de scan
     */
    resetScanInterface() {
        const startBtn = document.getElementById('start-scan');
        const stopBtn = document.getElementById('stop-scan');
        const progressDiv = document.getElementById('scan-progress');
        
        if (startBtn) startBtn.disabled = false;
        if (stopBtn) stopBtn.disabled = true;
        if (progressDiv) progressDiv.style.display = 'none';
    }
    
    /**
     * Arrêter le scan réseau
     */
    stopNetworkScan() {
        console.log('⏹️ Arrêt du scan demandé');
        
        // Arrêter l'animation de progression
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        
        this.resetScanInterface();
        
        const resultsDiv = document.getElementById('network-devices');
        if (resultsDiv) {
            resultsDiv.innerHTML = `
                <div class="card">
                    <p class="info-state">⏹️ Scan interrompu</p>
                    <button class="btn btn-primary" onclick="app.startNetworkScan()">🔄 Relancer</button>
                </div>
            `;
        }
    }
    
    /**
     * Ajouter un appareil au monitoring
     */
    async addDeviceToMonitoring(ip) {
        console.log(`➕ Ajout de ${ip} au monitoring`);
        
        try {
            const response = await fetch(`${this.apiBase}/api/devices`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    ip: ip,
                    name: `Appareil ${ip}`,
                    type: 'discovered'
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert(`✅ ${ip} ajouté au monitoring !`);
                // Rafraîchir l'onglet appareils si on y est
                if (this.currentTab === 'devices') {
                    this.loadDevices();
                }
            } else {
                alert(`❌ Erreur: ${data.message}`);
            }
            
        } catch (error) {
            console.error('❌ Erreur ajout monitoring:', error);
            alert(`❌ Erreur: ${error.message}`);
        }
    }
    
    /**
     * Afficher les détails d'un appareil
     */
    showDeviceDetails(ip) {
        if (!this.scanResults || !this.scanResults.devices) return;
        
        const device = this.scanResults.devices.find(d => d.ip === ip);
        if (!device) return;
        
        const detailsHtml = `
            <div class="device-details-modal">
                <h3>🔍 Détails - ${device.ip}</h3>
                <div class="details-grid">
                    <div><strong>🏷️ Hostname:</strong> ${device.hostname || 'N/A'}</div>
                    <div><strong>📶 MAC:</strong> ${device.mac_address || 'N/A'}</div>
                    <div><strong>🏭 Vendor:</strong> ${device.vendor || 'Inconnu'}</div>
                    <div><strong>💻 OS:</strong> ${device.os_detected || 'Inconnu'}</div>
                    <div><strong>📊 Confiance OS:</strong> ${device.os_confidence || 'Inconnue'}</div>
                    <div><strong>📱 Type:</strong> ${device.device_type || 'Inconnu'}</div>
                    <div><strong>🔌 Ports:</strong> ${(device.open_ports || []).join(', ') || 'Aucun'}</div>
                    <div><strong>⏱️ Ping:</strong> ${device.ping_ms || 'N/A'}ms</div>
                    <div><strong>🔍 Méthode:</strong> ${device.detection_method || 'Standard'}</div>
                </div>
                <div class="modal-actions">
                    <button class="btn btn-primary" onclick="app.addDeviceToMonitoring('${device.ip}')">➕ Surveiller</button>
                    <button class="btn btn-secondary" onclick="this.parentElement.parentElement.remove()">❌ Fermer</button>
                </div>
            </div>
        `;
        
        // Créer et afficher la modal
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = detailsHtml;
        modal.onclick = (e) => {
            if (e.target === modal) modal.remove();
        };
        
        document.body.appendChild(modal);
    }

    /**
     * Rafraîchir les appareils
     */
    refreshDevices() {
        this.dataCache.delete('devices');
        this.loadDevices();
    }

    /**
     * Mettre à jour le statut de connexion
     */
    updateConnectionStatus() {
        const indicator = document.getElementById('connection-status');
        if (indicator) {
            indicator.textContent = '🟢 Connecté';
        }
    }

    /**
     * Utilitaires
     */
    setElementContent(id, content) {
        const element = document.getElementById(id);
        if (element) element.innerHTML = content;
    }

    showError(containerId, message) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `<div class="error">❌ ${message}</div>`;
        }
    }
}

// Initialisation globale
const app = new HomeApp();
app.init();