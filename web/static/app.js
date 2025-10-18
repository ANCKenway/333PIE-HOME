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
        
        // Charger les informations de scan
        this.loadScanInfo();
        
        // Charger les appareils déconnectés
        this.loadDisconnectedDevices();
        
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
        
        // Recharger les informations de scan
        this.loadScanInfo();
        this.loadDisconnectedDevices();
        
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
            // 1. Récupérer les données du dernier scan pour cet appareil
            const scanResponse = await fetch(`${this.apiBase}/api/network/last-scan`);
            const scanData = await scanResponse.json();
            
            if (!scanData.success || !scanData.last_scan.devices) {
                alert('❌ Aucun scan récent trouvé. Lancez d\'abord un scan.');
                return;
            }
            
            // 2. Trouver l'appareil dans le scan
            const device = scanData.last_scan.devices.find(d => d.ip === ip);
            if (!device) {
                alert(`❌ Appareil ${ip} non trouvé dans le dernier scan.`);
                return;
            }
            
            // 3. Préparer les données complètes pour l'ajout
            const deviceData = {
                ip: device.ip,
                mac: device.mac,
                name: device.hostname || device.vendor || `Appareil-${device.ip.split('.').pop()}`,
                hostname: device.hostname,
                vendor: device.vendor,
                type: this.mapDeviceType(device.device_type),
                description: `${device.vendor || 'Inconnu'} - ${device.os_detected || 'OS inconnu'}`,
                wake_on_lan: false,
                os_detected: device.os_detected,
                device_type: device.device_type,
                added_from_scan: true,
                scan_timestamp: scanData.last_scan.timestamp
            };
            
            // 4. Envoyer à l'API
            const response = await fetch(`${this.apiBase}/api/devices`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(deviceData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert(`✅ ${deviceData.name} ajouté au monitoring !`);
                // Rafraîchir l'onglet appareils si on y est
                if (this.currentTab === 'devices') {
                    this.loadDevices();
                }
            } else {
                alert(`❌ Erreur: ${result.message}`);
            }
            
        } catch (error) {
            console.error('❌ Erreur ajout monitoring:', error);
            alert(`❌ Erreur: ${error.message}`);
        }
    }
    
    /**
     * Mapper le type d'appareil pour la BDD
     */
    mapDeviceType(deviceType) {
        if (!deviceType) return 'Inconnu';
        
        const mapping = {
            'PC/Desktop': 'PC',
            'Laptop': 'PC',
            'Server': 'Serveur',
            'Router': 'Réseau',
            'Switch': 'Réseau',
            'Access Point': 'Réseau',
            'Smartphone': 'Mobile',
            'Tablet': 'Mobile',
            'IoT Device': 'IoT',
            'Smart TV': 'Multimedia',
            'Game Console': 'Gaming'
        };
        
        return mapping[deviceType] || 'Appareil';
    }
    
    /**
     * Afficher les détails d'un appareil depuis l'historique
     */
    async showDeviceDetails(identifier) {
        // Identifier peut être une IP (ancienne méthode) ou une MAC (nouvelle méthode)
        const isMac = identifier.includes(':') || identifier.startsWith('no_mac_');
        
        if (isMac) {
            // Nouvelle méthode avec MAC depuis l'historique
            await this.showDeviceHistoryDetails(identifier);
        } else {
            // Ancienne méthode avec IP depuis le scan en cours
            this.showCurrentDeviceDetails(identifier);
        }
    }
    
    /**
     * Afficher les détails d'un appareil depuis l'historique (via MAC)
     */
    async showDeviceHistoryDetails(mac) {
        try {
            const response = await fetch(`${this.apiBase}/api/network/device-history/${encodeURIComponent(mac)}`);
            const data = await response.json();
            
            if (!data.success || !data.device) {
                alert('❌ Impossible de charger les détails de cet appareil');
                return;
            }
            
            const device = data.device;
            const current = device.current_data || {};
            const stats = device.stats || {};
            const changes = device.changes || {};
            
            const detailsHtml = `
                <div class="device-details-modal">
                    <h3>🔍 Détails Historique - ${current.hostname || 'Appareil inconnu'}</h3>
                    <div class="details-grid">
                        <div><strong>🏷️ Nom:</strong> ${current.hostname || 'N/A'}</div>
                        <div><strong>📶 MAC:</strong> ${mac.startsWith('no_mac_') ? 'Non disponible' : mac}</div>
                        <div><strong>🌐 Dernière IP:</strong> ${current.ip || 'IP inconnue'}</div>
                        <div><strong>🏭 Constructeur:</strong> ${current.vendor || 'Inconnu'}</div>
                        <div><strong>💻 Type:</strong> ${current.device_type || 'Non déterminé'}</div>
                        <div><strong>📊 Scans:</strong> ${stats.scan_count || 0}</div>
                        <div><strong>📅 Premier scan:</strong> ${stats.first_seen ? new Date(stats.first_seen * 1000).toLocaleString('fr-FR') : 'N/A'}</div>
                        <div><strong>⏱️ Dernier scan:</strong> ${current.last_seen ? new Date(current.last_seen * 1000).toLocaleString('fr-FR') : 'N/A'}</div>
                        <div><strong>📝 Toutes les IPs:</strong> ${device.ip_history ? device.ip_history.join(', ') : current.ip || 'Aucune'}</div>
                    </div>
                    
                    ${this.renderDeviceChangeHistory(changes)}
                    
                    <div class="modal-actions">
                        ${current.ip ? `<button class="btn btn-primary" onclick="app.addDeviceToMonitoring('${current.ip}')">➕ Surveiller</button>` : ''}
                        <button class="btn btn-secondary" onclick="closeDeviceModal()">❌ Fermer</button>
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
        
        // Ajouter une fonction globale pour fermer la modal
        window.closeDeviceModal = () => {
            modal.remove();
            document.removeEventListener('keydown', escapeHandler);
        };
        
        // Fermer avec la touche Escape
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                window.closeDeviceModal();
            }
        };
        document.addEventListener('keydown', escapeHandler);
        
        document.body.appendChild(modal);        } catch (error) {
            console.error('❌ Erreur détails appareil:', error);
            alert('❌ Erreur lors du chargement des détails');
        }
    }
    
    /**
     * Rendre l'historique des changements d'un appareil
     */
    renderDeviceChangeHistory(changes) {
        let html = '';
        
        if (changes.ip_changes?.length > 0 || changes.hostname_changes?.length > 0 || changes.vendor_changes?.length > 0) {
            html += '<div class="device-change-history"><h4>🔄 Historique des changements</h4>';
            
            if (changes.ip_changes?.length > 0) {
                html += '<div class="change-section"><strong>📍 Adresses IP:</strong><ul>';
                changes.ip_changes.forEach(change => {
                    html += `<li>${change.old_value} → ${change.new_value} <small>(${new Date(change.timestamp * 1000).toLocaleString('fr-FR')})</small></li>`;
                });
                html += '</ul></div>';
            }
            
            if (changes.hostname_changes?.length > 0) {
                html += '<div class="change-section"><strong>🏷️ Noms d\'hôte:</strong><ul>';
                changes.hostname_changes.forEach(change => {
                    html += `<li>${change.old_value || 'N/A'} → ${change.new_value} <small>(${new Date(change.timestamp * 1000).toLocaleString('fr-FR')})</small></li>`;
                });
                html += '</ul></div>';
            }
            
            if (changes.vendor_changes?.length > 0) {
                html += '<div class="change-section"><strong>🏭 Constructeurs:</strong><ul>';
                changes.vendor_changes.forEach(change => {
                    html += `<li>${change.old_value || 'N/A'} → ${change.new_value} <small>(${new Date(change.timestamp * 1000).toLocaleString('fr-FR')})</small></li>`;
                });
                html += '</ul></div>';
            }
            
            html += '</div>';
        }
        
        return html;
    }
    
    /**
     * Afficher les détails d'un appareil actuel (via IP)
     */
    showCurrentDeviceDetails(ip) {
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
                    <button class="btn btn-secondary" onclick="closeDeviceModal()">❌ Fermer</button>
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
        
        // Ajouter une fonction globale pour fermer la modal
        window.closeDeviceModal = () => {
            modal.remove();
            document.removeEventListener('keydown', escapeHandler);
        };
        
        // Fermer avec la touche Escape
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                window.closeDeviceModal();
            }
        };
        document.addEventListener('keydown', escapeHandler);
        
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
     * Charger les informations de scan
     */
    async loadScanInfo() {
        console.log('📊 Chargement des informations de scan');
        
        try {
            const response = await fetch(`${this.apiBase}/api/network/scan-stats`);
            const data = await response.json();
            
            const container = document.getElementById('scan-info-content');
            if (!container) return;
            
            if (data.success && data.stats.has_scan_data) {
                const lastScanDate = new Date(data.stats.last_scan_time);
                const timeAgo = this.getTimeAgo(lastScanDate);
                
                container.innerHTML = `
                    <div class="scan-stats">
                        <div class="stat-item">
                            <span class="stat-label">📅 Dernier scan:</span>
                            <span class="stat-value">${lastScanDate.toLocaleDateString('fr-FR')} à ${lastScanDate.toLocaleTimeString('fr-FR', {hour: '2-digit', minute: '2-digit'})}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">⏱️ Il y a:</span>
                            <span class="stat-value">${timeAgo}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">🔍 Appareils trouvés:</span>
                            <span class="stat-value">${data.stats.last_scan_devices}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">📊 Scans archivés:</span>
                            <span class="stat-value">${data.stats.scan_history_count}</span>
                        </div>
                    </div>
                `;
            } else {
                container.innerHTML = `
                    <div class="no-scan-data">
                        <p>🎯 Aucun scan effectué. Lancez votre premier scan pour commencer !</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('❌ Erreur chargement scan info:', error);
            this.showError('scan-info-content', 'Erreur lors du chargement des informations');
        }
    }
    
    /**
     * Charger les appareils déconnectés
     */
    async loadDisconnectedDevices() {
        console.log('📵 Chargement des appareils déconnectés');
        
        try {
            const response = await fetch(`${this.apiBase}/api/network/disconnected-devices?limit=10`);
            const data = await response.json();
            
            const section = document.getElementById('disconnected-section');
            const container = document.getElementById('disconnected-devices');
            
            if (!section || !container) return;
            
            if (data.success && data.disconnected_devices.length > 0) {
                section.style.display = 'block';
                
                container.innerHTML = data.disconnected_devices.map(device => `
                    <div class="disconnected-device">
                        <div class="device-info">
                            <div class="device-title">
                                <strong>${device.hostname || device.vendor || device.ip}</strong>
                                <span class="device-ip">${device.ip}</span>
                            </div>
                            <div class="device-details">
                                <span class="vendor">${device.vendor}</span>
                                <span class="separator">•</span>
                                <span class="os">${device.os_detected}</span>
                                <span class="separator">•</span>
                                <span class="time-ago">${device.time_ago}</span>
                            </div>
                        </div>
                        <div class="device-actions">
                            <button class="btn btn-sm btn-outline" onclick="app.pingDevice('${device.ip}')">
                                📡 Ping
                            </button>
                        </div>
                    </div>
                `).join('');
            } else {
                section.style.display = 'none';
            }
        } catch (error) {
            console.error('❌ Erreur chargement déconnectés:', error);
        }
    }
    
    /**
     * Ping d'un appareil spécifique
     */
    async pingDevice(ip) {
        console.log(`📡 Ping de ${ip}`);
        
        try {
            // Pour l'instant, on affiche juste un message
            // Plus tard on pourra ajouter un endpoint de ping rapide
            alert(`📡 Ping de ${ip} en cours...`);
            
        } catch (error) {
            console.error('❌ Erreur ping:', error);
            alert(`❌ Erreur lors du ping de ${ip}`);
        }
    }
    
    /**
     * Toggle de l'historique réseau
     */
    toggleNetworkHistory() {
        const section = document.getElementById('network-history-section');
        const btn = document.getElementById('show-history');
        
        if (!section || !btn) return;
        
        if (section.style.display === 'none' || !section.style.display) {
            section.style.display = 'block';
            btn.textContent = '❌ Fermer Historique';
            this.loadNetworkHistory();
        } else {
            section.style.display = 'none';
            btn.textContent = '📋 Historique Réseau';
        }
    }
    
    /**
     * Afficher un onglet de l'historique
     */
    showHistoryTab(tabName) {
        // Mettre à jour les boutons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
        
        // Mettre à jour les contenus
        document.querySelectorAll('.history-tab-content').forEach(content => {
            content.classList.remove('active');
            content.style.display = 'none';
        });
        
        const targetContent = document.getElementById(`history-${tabName}`);
        if (targetContent) {
            targetContent.classList.add('active');
            targetContent.style.display = 'block';
            
            // Charger le contenu si nécessaire
            if (tabName === 'devices') {
                this.loadDevicesHistory();
            } else if (tabName === 'events') {
                this.loadNetworkEvents();
            }
        }
    }
    
    /**
     * Charger l'historique réseau
     */
    async loadNetworkHistory() {
        // Charger par défaut l'onglet appareils
        this.loadDevicesHistory();
    }
    
    /**
     * Charger l'historique des appareils
     */
    async loadDevicesHistory() {
        console.log('📋 Chargement historique des appareils');
        
        const container = document.getElementById('history-devices');
        if (!container) return;
        
        container.innerHTML = '<div class="loading">🔄 Chargement de l\'historique...</div>';
        
        try {
            const response = await fetch(`${this.apiBase}/api/network/devices-history`);
            const data = await response.json();
            
            if (data.success && data.history && data.history.devices_by_mac) {
                const devices = Object.entries(data.history.devices_by_mac);
                
                if (devices.length > 0) {
                    // Trier par dernière vue (plus récent en premier)
                    devices.sort((a, b) => {
                        const aLastSeen = new Date(a[1].current_data?.last_seen || 0);
                        const bLastSeen = new Date(b[1].current_data?.last_seen || 0);
                        return bLastSeen - aLastSeen;
                    });
                    
                    container.innerHTML = `
                        <table class="history-devices-table">
                            <thead>
                                <tr>
                                    <th>📍 Nom</th>
                                    <th>🔧 Adresse MAC</th>
                                    <th>🌐 Dernière IP</th>
                                    <th>🏭 Constructeur</th>
                                    <th>💻 Type</th>
                                    <th>📊 Scans</th>
                                    <th>🔄 Changements</th>
                                    <th>⏱️ Dernière Vue</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${devices.map(([mac, device]) => this.renderDeviceHistoryRow(mac, device)).join('')}
                            </tbody>
                        </table>
                    `;
                } else {
                    container.innerHTML = '<div class="empty-state">📋 Aucun appareil dans l\'historique.</div>';
                }
            } else {
                container.innerHTML = '<div class="empty-state">📋 Aucun historique disponible.</div>';
            }
        } catch (error) {
            console.error('❌ Erreur historique appareils:', error);
            container.innerHTML = '<div class="error">❌ Erreur lors du chargement de l\'historique</div>';
        }
    }
    
    /**
     * Rendre une ligne de l'historique d'appareil
     */
    renderDeviceHistoryRow(mac, device) {
        const current = device.current_data || {};
        const stats = device.stats || {};
        const changes = device.changes || {};
        
        const hostname = current.hostname || 'Appareil inconnu';
        const displayMac = mac.startsWith('no_mac_') ? 
            '<span class="mac-unknown">Non disponible</span>' : 
            `<code class="mac-address">${mac}</code>`;
        
        // Afficher la dernière IP connue (pas le statut de connexion)
        const lastKnownIp = current.ip || 'IP inconnue';
        const isCurrentlyConnected = current.last_seen && 
            (new Date() - new Date(current.last_seen * 1000)) < (5 * 60 * 1000); // 5min = connecté
        
        const ipDisplay = isCurrentlyConnected ? 
            `<code class="ip-connected">${lastKnownIp}</code>` : 
            `<code class="ip-disconnected">${lastKnownIp}</code>`;
        const vendor = current.vendor || 'Inconnu';
        const deviceType = current.device_type || 'Non déterminé';
        const scanCount = stats.scan_count || 0;
        
        // Calculer le nombre total de changements
        const totalChanges = (changes.ip_changes?.length || 0) + 
                           (changes.hostname_changes?.length || 0) + 
                           (changes.vendor_changes?.length || 0);
        
        const lastSeen = current.last_seen ? 
            new Date(current.last_seen * 1000).toLocaleString('fr-FR') : 'Jamais';
        
        // Badges de changements
        const changeBadges = [];
        if (changes.ip_changes?.length > 0) {
            changeBadges.push(`<span class="change-badge ip" title="${changes.ip_changes.length} changements IP">IP (${changes.ip_changes.length})</span>`);
        }
        if (changes.hostname_changes?.length > 0) {
            changeBadges.push(`<span class="change-badge hostname" title="${changes.hostname_changes.length} changements de nom">Nom (${changes.hostname_changes.length})</span>`);
        }
        if (changes.vendor_changes?.length > 0) {
            changeBadges.push(`<span class="change-badge vendor" title="${changes.vendor_changes.length} changements de constructeur">Vendeur (${changes.vendor_changes.length})</span>`);
        }
        
        return `
            <tr onclick="app.showDeviceDetails('${mac}')">
                <td>
                    <strong>${hostname}</strong>
                </td>
                <td>${displayMac}</td>
                <td>${ipDisplay}</td>
                <td>${vendor}</td>
                <td>${deviceType}</td>
                <td class="text-center">${scanCount}</td>
                <td>
                    <div class="device-changes">
                        ${changeBadges.length > 0 ? changeBadges.join('') : '<span class="no-changes">-</span>'}
                    </div>
                </td>
                <td>${lastSeen}</td>
            </tr>
        `;
    }
    
    /**
     * Charger les événements réseau
     */
    async loadNetworkEvents() {
        console.log('📅 Chargement événements réseau');
        
        const container = document.getElementById('history-events');
        if (!container) return;
        
        container.innerHTML = '<div class="loading">🔄 Chargement des événements...</div>';
        
        try {
            const response = await fetch(`${this.apiBase}/api/network/recent-events?limit=30`);
            const data = await response.json();
            
            if (data.success) {
                const allEvents = [
                    ...data.events.connection_events.map(e => ({...e, category: 'connection'})),
                    ...data.events.ip_changes.map(e => ({...e, category: 'ip_change'})),
                    ...data.events.mac_changes.map(e => ({...e, category: 'mac_change'}))
                ].sort((a, b) => b.timestamp - a.timestamp);
                
                if (allEvents.length > 0) {
                    container.innerHTML = `
                        <div class="network-events">
                            ${allEvents.map(event => this.renderNetworkEvent(event)).join('')}
                        </div>
                    `;
                } else {
                    container.innerHTML = '<div class="empty-state">📅 Aucun événement récent.</div>';
                }
            }
        } catch (error) {
            console.error('❌ Erreur événements réseau:', error);
            container.innerHTML = '<div class="error">❌ Erreur lors du chargement des événements</div>';
        }
    }
    
    /**
     * Rendre un événement réseau
     */
    renderNetworkEvent(event) {
        let icon, title, description;
        
        if (event.category === 'connection') {
            if (event.type === 'new_device') {
                icon = '🆕';
                title = 'Nouvel appareil détecté';
                description = `${event.hostname || event.ip} (${event.vendor || 'Inconnu'}) s'est connecté`;
            } else if (event.type === 'reconnection') {
                icon = '🔄';
                title = 'Reconnexion détectée';
                description = `${event.hostname || event.ip} s'est reconnecté après ${Math.round(event.time_offline / 3600)}h`;
            } else if (event.type === 'disconnection') {
                icon = '📴';
                title = 'Déconnexion détectée';
                description = `${event.hostname || event.ip} (${event.vendor || 'Inconnu'}) s'est déconnecté`;
            }
        } else if (event.category === 'ip_change') {
            icon = '🌐';
            title = 'Changement d\'IP';
            description = `Appareil ${event.ip}: ${event.old_ip} → ${event.new_ip}`;
        } else if (event.category === 'mac_change') {
            icon = '🔄';
            title = 'Changement de MAC';
            description = `Appareil ${event.ip}: ${event.old_mac} → ${event.new_mac}`;
        }
        
        const eventTime = new Date(event.datetime).toLocaleString('fr-FR');
        
        return `
            <div class="network-event">
                <div class="event-icon ${event.type || event.category}">${icon}</div>
                <div class="event-details">
                    <div class="event-title">${title}</div>
                    <div class="event-description">${description}</div>
                </div>
                <div class="event-time">${eventTime}</div>
            </div>
        `;
    }

    /**
     * Calculer le temps écoulé
     */
    getTimeAgo(date) {
        const now = new Date();
        const diff = now - date;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) return `${days}j`;
        if (hours > 0) return `${hours}h`;
        if (minutes > 0) return `${minutes}min`;
        return `${seconds}s`;
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