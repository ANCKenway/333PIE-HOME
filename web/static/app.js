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
        this.autoSyncVpn(); // Auto-sync VPN au démarrage
        
        // Pré-charger les appareils dès le démarrage
        setTimeout(() => this.loadDevices(), 1000);
        
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
        this.setupButton('sync-vpn-devices', () => this.syncVpnDevices());
        
        // Boutons de scan réseau
        this.setupButton('start-scan', () => this.startNetworkScan());
        this.setupButton('stop-scan', () => this.stopNetworkScan());
        
        // Boutons VPN Tailscale
        this.setupButton('refresh-tailscale', () => this.refreshTailscale());
        this.setupButton('tailscale-settings', () => this.toggleTailscaleSettings());
        
        // Formulaire de configuration Tailscale
        const tailscaleForm = document.getElementById('tailscale-config-form');
        if (tailscaleForm) {
            tailscaleForm.addEventListener('submit', (event) => this.saveTailscaleConfig(event));
        }
        
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
            case 'vpn':
                this.loadVpnInterface();
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
            
            if (data.devices && data.devices.length > 0) {
                this.displayDevices(data.devices);
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
        
        container.innerHTML = `
            <div class="devices-grid">
                ${devices.map(device => this.renderDeviceCard(device)).join('')}
            </div>
        `;
    }

    /**
     * Rendu d'une carte d'appareil
     */
    renderDeviceCard(device) {
        const statusClass = device.status === 'online' ? 'online' : 'offline';
        const statusIcon = device.status === 'online' ? '🟢' : '🔴';
        const deviceIcon = this.getDeviceIcon(device.type);
        
        return `
            <div class="device-card" data-device-id="${device.ip}">
                <div class="device-card-header">
                    <div class="device-icon">${deviceIcon}</div>
                    <div class="status-indicators">
                        <div class="device-status ${statusClass}">
                            <span class="status-indicator">${statusIcon}</span>
                            <span class="status-text">${device.status || 'Inconnu'}</span>
                        </div>
                        ${this.renderVpnIndicator(device)}
                    </div>
                </div>
                
                <div class="device-card-body">
                    <h3 class="device-name">${device.name || device.hostname || device.ip}</h3>
                    <div class="device-details">
                        <div class="detail-row">
                            <span class="detail-label">🌐 IP Principale:</span>
                            <span class="detail-value">${device.current_ip || device.ip}</span>
                        </div>
                        ${device.mac ? `
                            <div class="detail-row">
                                <span class="detail-label">🔧 MAC:</span>
                                <span class="detail-value mac-address">${device.mac}</span>
                            </div>
                        ` : ''}
                        <div class="detail-row">
                            <span class="detail-label">📱 Type:</span>
                            <span class="detail-value">${device.device_type || device.type || 'Inconnu'}</span>
                        </div>
                        ${device.vendor ? `
                            <div class="detail-row">
                                <span class="detail-label">🏭 Fabricant:</span>
                                <span class="detail-value">${device.vendor}</span>
                            </div>
                        ` : ''}
                        <div class="detail-row">
                            <span class="detail-label">⏱️ Dernière vérification:</span>
                            <span class="detail-value">${device.last_seen || 'Jamais'}</span>
                        </div>
                        ${device.vpn && device.vpn.connected ? `
                        <div class="detail-row vpn-info">
                            <span class="detail-label">🔒 Tailscale IP:</span>
                            <span class="detail-value">${device.vpn.tailscale_ip}</span>
                        </div>
                        <div class="detail-row vpn-info">
                            <span class="detail-label">🌐 VPN Status:</span>
                            <span class="detail-value">${device.vpn.online ? '🟢 En ligne' : '🔴 Hors ligne'}</span>
                        </div>
                        ${device.vpn.exit_node ? `
                        <div class="detail-row vpn-info">
                            <span class="detail-label">🚪 Exit Node:</span>
                            <span class="detail-value">✅ Activé</span>
                        </div>
                        ` : ''}
                        ` : ''}
                    </div>
                </div>
                
                <div class="device-card-actions">
                    ${device.wake_on_lan ? `
                        <button class="btn btn-success btn-wol" onclick="app.wakeDevice('${device.mac}')">
                            💻 Wake-on-LAN
                        </button>
                    ` : ''}
                    <button class="btn btn-primary btn-config" onclick="app.configureDevice('${device.ip}')">
                        ⚙️ Configurer
                    </button>
                    <button class="btn btn-danger btn-delete" onclick="app.confirmDeleteDevice('${device.ip}')">
                        🗑️ Supprimer
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Obtenir l'icône d'un appareil selon son type
     */
    getDeviceIcon(type) {
        const icons = {
            'PC': '🖥️',
            'Serveur': '🖲️', 
            'Réseau': '🌐',
            'Appareil': '📱',
            'discovered': '❓'
        };
        return icons[type] || '📟';
    }

    /**
     * Rendu de l'indicateur VPN
     */
    renderVpnIndicator(device) {
        // Nouveau système VPN Tailscale intégré
        if (device.vpn && device.vpn.connected) {
            const vpnClass = device.vpn.online ? 'vpn-online' : 'vpn-offline';
            const vpnTitle = `Tailscale: ${device.vpn.online ? 'En ligne' : 'Hors ligne'} (${device.vpn.tailscale_ip})`;
            
            return `
                <div class="vpn-indicator ${vpnClass}" title="${vpnTitle}">
                    <span class="vpn-label">🔒 VPN</span>
                </div>
            `;
        }
        
        // Ancien système VPN (fallback)
        if (!device.is_vpn || !device.ip_secondary) {
            return '';
        }
        
        // Déterminer le statut VPN depuis les données de monitoring
        let vpnStatus = 'unknown';
        let vpnClass = 'vpn-unknown';
        let vpnTitle = 'VPN: Statut inconnu';
        
        if (device.vpn_status) {
            if (device.vpn_status.status === 'online') {
                vpnStatus = 'online';
                vpnClass = 'vpn-online';
                vpnTitle = `VPN: En ligne (${device.vpn_status.ip})`;
            } else if (device.vpn_status.status === 'offline') {
                vpnStatus = 'offline';
                vpnClass = 'vpn-offline';
                vpnTitle = `VPN: Hors ligne (${device.vpn_status.ip})`;
            } else if (device.vpn_status.status === 'error') {
                vpnStatus = 'error';
                vpnClass = 'vpn-error';
                vpnTitle = `VPN: Erreur (${device.vpn_status.ip})`;
            }
        }
        
        return `
            <div class="vpn-indicator ${vpnClass}" title="${vpnTitle}">
                <span class="vpn-label">VPN</span>
            </div>
        `;
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
                                ${cat.devices.map(device => this.renderNetworkDeviceCard(device)).join('')}
                            </div>
                        </div>
                    `).join('')}
                    
                ${devices.length === 0 ? '<div class="empty-state">❌ Aucun appareil découvert</div>' : ''}
            </div>
        `;
    }
    
    /**
     * Rendu d'une carte d'appareil réseau (scan)
     */
    renderNetworkDeviceCard(device) {
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
            
            // DEBUG: Vérifier les données de l'appareil
            console.log('🔍 Données appareil du scan:', device);
            
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
     * Synchronisation VPN automatique au démarrage
     */
    async autoSyncVpn() {
        try {
            // Vérifier si Tailscale est configuré
            const configResponse = await fetch(`${this.apiBase}/api/tailscale/config`);
            const configData = await configResponse.json();
            
            if (configData.configured) {
                console.log('🔒 Auto-sync VPN activé');
                // Synchronisation silencieuse au démarrage
                const response = await fetch(`${this.apiBase}/api/sync/enable-auto-vpn`, {
                    method: 'POST'
                });
                
                const data = await response.json();
                if (data.success) {
                    console.log('✅ Sync VPN automatique réussie');
                } else {
                    console.warn('⚠️ Sync VPN automatique échouée:', data.error);
                }
            }
        } catch (error) {
            console.warn('⚠️ Auto-sync VPN non disponible:', error.message);
        }
    }

    /**
     * Synchronisation VPN intelligente
     */
    async syncVpnDevices() {
        this.showNotification('🔄 Synchronisation VPN en cours...', 'info');
        
        try {
            const response = await fetch(`${this.apiBase}/api/sync/enable-auto-vpn`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification(`✅ ${data.message}`, 'success');
                // Recharger les appareils pour voir les changements
                await this.refreshDevices();
            } else {
                this.showNotification(`❌ Erreur de synchronisation: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Erreur sync VPN:', error);
            this.showNotification('❌ Erreur de connexion lors de la synchronisation', 'error');
        }
    }

    /**
     * Rafraîchir les appareils
     */
    async refreshDevices() {
        console.log('🔄 Actualisation forcée des appareils');
        this.dataCache.delete('devices');
        
        const container = document.getElementById('devices-list');
        if (container) {
            container.innerHTML = '<div class="loading">🔄 Actualisation forcée des appareils...</div>';
        }

        try {
            const response = await fetch(`${this.apiBase}/api/devices/refresh`);
            const data = await response.json();

            if (data.success && data.devices && data.devices.length > 0) {
                this.displayDevices(data.devices);
                this.showNotification('✅ Appareils actualisés', 'success');
            } else {
                this.showEmptyDevices();
            }
        } catch (error) {
            console.error('❌ Erreur actualisation:', error);
            this.showError('devices-list', 'Erreur lors de l\'actualisation');
            this.showNotification('❌ Erreur lors de l\'actualisation', 'error');
        }
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

    /**
     * Confirmer la suppression d'un appareil
     */
    confirmDeleteDevice(deviceIp) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="device-config-modal">
                <div class="modal-header">
                    <h3>🗑️ Supprimer l'appareil</h3>
                    <button onclick="closeDeviceModal()" class="btn-close">×</button>
                </div>
                <div class="modal-body">
                    <p>⚠️ Êtes-vous sûr de vouloir supprimer cet appareil ?</p>
                    <p><strong>IP:</strong> ${deviceIp}</p>
                    <p>Cette action est irréversible.</p>
                </div>
                <div class="modal-actions">
                    <button onclick="closeDeviceModal()" class="btn btn-secondary">Annuler</button>
                    <button onclick="app.deleteDevice('${deviceIp}')" class="btn btn-danger">Supprimer</button>
                </div>
            </div>
        `;
        
        modal.onclick = (e) => {
            if (e.target === modal) modal.remove();
        };
        
        // Fonction globale pour fermer la modal
        window.closeDeviceModal = () => {
            modal.remove();
            document.removeEventListener('keydown', escapeHandler);
        };
        
        // Fermer avec Escape
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                window.closeDeviceModal();
            }
        };
        document.addEventListener('keydown', escapeHandler);
        
        document.body.appendChild(modal);
    }

    /**
     * Supprimer un appareil
     */
    async deleteDevice(deviceIp) {
        try {
            const response = await fetch(`${this.apiBase}/api/devices/${deviceIp}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                window.closeDeviceModal();
                this.loadDevices();
                this.showNotification('✅ Appareil supprimé avec succès', 'success');
            } else {
                this.showNotification('❌ Erreur lors de la suppression', 'error');
            }
        } catch (error) {
            console.error('❌ Erreur suppression:', error);
            this.showNotification('❌ Erreur lors de la suppression', 'error');
        }
    }

    /**
     * Configurer un appareil
     */
    configureDevice(deviceIp) {
        // Chercher l'appareil dans la liste
        const deviceElement = document.querySelector(`[data-device-id="${deviceIp}"]`);
        if (!deviceElement) return;
        
        // Récupérer les données depuis l'API
        fetch(`${this.apiBase}/api/devices`)
            .then(response => response.json())
            .then(data => {
                const device = data.devices.find(d => d.ip === deviceIp || d.current_ip === deviceIp);
                if (device) {
                    this.showDeviceConfigModal(device);
                }
            })
            .catch(error => {
                console.error('❌ Erreur chargement appareil:', error);
                this.showNotification('❌ Erreur lors du chargement', 'error');
            });
    }

    /**
     * Afficher la modal de configuration d'appareil
     */
    showDeviceConfigModal(device) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="device-config-modal">
                <div class="modal-header">
                    <h3>⚙️ Configuration - ${device.name || device.ip}</h3>
                    <button onclick="closeDeviceConfigModal()" class="btn-close">×</button>
                </div>
                <form class="device-config-form" onsubmit="app.saveDeviceConfig(event, '${device.ip}')">
                    <div class="modal-body">
                        <div class="form-group">
                            <label>📝 Nom personnalisé</label>
                            <input type="text" id="device-name" value="${device.name || ''}" 
                                   placeholder="Ex: PC Bureau, Serveur NAS..." class="form-control">
                        </div>
                        
                        <div class="form-group">
                            <label>🌐 IP Principale</label>
                            <input type="text" id="device-ip" value="${device.ip || ''}" 
                                   placeholder="192.168.1.100" class="form-control" readonly>
                        </div>
                        
                        <div class="form-group">
                            <label class="checkbox-label">
                                <input type="checkbox" id="device-vpn" ${device.is_vpn ? 'checked' : ''} onchange="app.toggleVpnFields()">
                                🔒 VPN (Tailscale)
                            </label>
                        </div>
                        
                        <div class="form-group vpn-fields" id="vpn-fields" style="display: ${device.is_vpn ? 'block' : 'none'}">
                            <label>🌐 IP Secondaire (Tailscale)</label>
                            <input type="text" id="device-ip2" value="${device.ip_secondary || ''}" 
                                   placeholder="100.64.0.10" class="form-control">
                        </div>
                        
                        <div class="form-group">
                            <label>🔧 Adresse MAC</label>
                            <input type="text" id="device-mac" value="${device.mac || ''}" 
                                   placeholder="AA:BB:CC:DD:EE:FF" class="form-control">
                        </div>
                        
                        <div class="form-group">
                            <label>📱 Type d'appareil</label>
                            <select id="device-type" class="form-control">
                                <option value="PC" ${device.type === 'PC' ? 'selected' : ''}>🖥️ PC/Ordinateur</option>
                                <option value="Serveur" ${device.type === 'Serveur' ? 'selected' : ''}>🖲️ Serveur</option>
                                <option value="Réseau" ${device.type === 'Réseau' ? 'selected' : ''}>🌐 Équipement réseau</option>
                                <option value="Mobile" ${device.type === 'Mobile' ? 'selected' : ''}>📱 Appareil mobile</option>
                                <option value="IoT" ${device.type === 'IoT' ? 'selected' : ''}>🏠 Objet connecté</option>
                                <option value="Autre" ${device.type === 'Autre' ? 'selected' : ''}>📟 Autre</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>📝 Description</label>
                            <textarea id="device-description" class="form-control" rows="2" 
                                      placeholder="Description optionnelle...">${device.description || ''}</textarea>
                        </div>
                        
                        <div class="form-group">
                            <label class="checkbox-label">
                                <input type="checkbox" id="device-wol" ${device.wake_on_lan ? 'checked' : ''}>
                                💻 Activer Wake-on-LAN
                            </label>
                        </div>
                    </div>
                    
                    <div class="modal-actions">
                        <button type="button" onclick="closeDeviceConfigModal()" class="btn btn-secondary">Annuler</button>
                        <button type="submit" class="btn btn-primary">💾 Sauvegarder</button>
                    </div>
                </form>
            </div>
        `;
        
        modal.onclick = (e) => {
            if (e.target === modal) modal.remove();
        };
        
        // Fonction globale pour fermer la modal
        window.closeDeviceConfigModal = () => {
            modal.remove();
            document.removeEventListener('keydown', escapeHandler);
        };
        
        // Fermer avec Escape
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                window.closeDeviceConfigModal();
            }
        };
        document.addEventListener('keydown', escapeHandler);
        
        document.body.appendChild(modal);
    }

    /**
     * Basculer l'affichage des champs VPN
     */
    toggleVpnFields() {
        const vpnCheckbox = document.getElementById('device-vpn');
        const vpnFields = document.getElementById('vpn-fields');
        const ip2Field = document.getElementById('device-ip2');
        
        if (vpnCheckbox.checked) {
            vpnFields.style.display = 'block';
            ip2Field.required = false; // Optionnel même avec VPN
        } else {
            vpnFields.style.display = 'none';
            ip2Field.value = ''; // Vider le champ si VPN désactivé
        }
    }

    /**
     * Sauvegarder la configuration d'un appareil
     */
    async saveDeviceConfig(event, deviceIp) {
        event.preventDefault();
        
        const formData = {
            name: document.getElementById('device-name').value,
            ip: document.getElementById('device-ip').value,
            ip_secondary: document.getElementById('device-ip2').value,
            mac: document.getElementById('device-mac').value,
            type: document.getElementById('device-type').value,
            description: document.getElementById('device-description').value,
            wake_on_lan: document.getElementById('device-wol').checked,
            is_vpn: document.getElementById('device-vpn').checked
        };
        
        try {
            const response = await fetch(`${this.apiBase}/api/devices/${deviceIp}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                window.closeDeviceConfigModal();
                this.loadDevices();
                this.showNotification('✅ Configuration sauvegardée', 'success');
            } else {
                this.showNotification('❌ Erreur lors de la sauvegarde', 'error');
            }
        } catch (error) {
            console.error('❌ Erreur sauvegarde:', error);
            this.showNotification('❌ Erreur lors de la sauvegarde', 'error');
        }
    }

    /**
     * Wake-on-LAN pour un appareil
     */
    async wakeDevice(mac) {
        if (!mac) {
            this.showNotification('❌ Adresse MAC requise pour Wake-on-LAN', 'error');
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBase}/api/wake/${mac}`, {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('✅ Signal Wake-on-LAN envoyé', 'success');
            } else {
                this.showNotification('❌ Erreur Wake-on-LAN', 'error');
            }
        } catch (error) {
            console.error('❌ Erreur Wake-on-LAN:', error);
            this.showNotification('❌ Erreur Wake-on-LAN', 'error');
        }
    }

    /**
     * Réparer les MACs manquantes en utilisant l'historique réseau
     */
    async repairMissingMacs() {
        try {
            // 1. Charger les appareils gérés
            const devicesResponse = await fetch(`${this.apiBase}/api/devices`);
            const devicesData = await devicesResponse.json();
            
            // 2. Charger l'historique réseau
            const historyResponse = await fetch(`${this.apiBase}/api/network/devices-history`);
            const historyData = await historyResponse.json();
            
            if (!devicesData.success || !historyData.success) {
                console.log('❌ Impossible de charger les données pour réparation');
                return;
            }
            
            const devices = devicesData.devices;
            const history = historyData.history.devices_by_mac;
            
            // 3. Pour chaque appareil sans MAC, chercher dans l'historique
            for (const device of devices) {
                if (!device.mac && device.ip) {
                    // Chercher dans l'historique par IP
                    for (const [mac, deviceHistory] of Object.entries(history)) {
                        const currentData = deviceHistory.current_data;
                        if (currentData && currentData.ip === device.ip && !mac.startsWith('no_mac_')) {
                            console.log(`🔧 MAC trouvée pour ${device.ip}: ${mac}`);
                            
                            // Mettre à jour l'appareil
                            const updateData = { ...device, mac: mac };
                            const updateResponse = await fetch(`${this.apiBase}/api/devices/${device.ip}`, {
                                method: 'PUT',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify(updateData)
                            });
                            
                            if (updateResponse.ok) {
                                console.log(`✅ MAC réparée pour ${device.name || device.ip}`);
                            }
                            break;
                        }
                    }
                }
            }
            
        } catch (error) {
            console.error('❌ Erreur réparation MACs:', error);
        }
    }

    /**
     * ===== SECTION VPN TAILSCALE =====
     */
    
    /**
     * Charger l'interface VPN Tailscale
     */
    loadVpnInterface() {
        console.log('🔒 Chargement interface VPN Tailscale');
        
        // Vérifier si la config existe
        this.checkTailscaleConfig();
        
        // Charger les appareils si configuré
        this.loadTailscaleDevices();
    }
    
    /**
     * Vérifier la configuration Tailscale
     */
    async checkTailscaleConfig() {
        try {
            const response = await fetch(`${this.apiBase}/api/tailscale/config`);
            const data = await response.json();
            
            // Ne pas afficher automatiquement la configuration
            // L'utilisateur doit cliquer sur "Paramètres" pour la voir
            if (!data.success || !data.config.api_key_configured) {
                console.log('ℹ️ Configuration Tailscale non trouvée');
                this.showTailscaleStats(null);
            }
        } catch (error) {
            console.log('ℹ️ Erreur lors de la vérification de la configuration Tailscale');
            this.showTailscaleStats(null);
        }
    }
    
    /**
     * Charger les appareils Tailscale
     */
    async loadTailscaleDevices() {
        console.log('🔄 Chargement appareils Tailscale');
        
        const container = document.getElementById('tailscale-devices');
        container.innerHTML = '<div class="loading">🔄 Connexion à Tailscale...</div>';
        
        try {
            const response = await fetch(`${this.apiBase}/api/tailscale/devices`);
            const data = await response.json();
            
            if (data.success && data.devices) {
                this.displayTailscaleDevices(data.devices);
                this.showTailscaleStats(data.devices);
            } else {
                // Gestion spécifique des erreurs API
                if (data.error_type === 'expired_api_key') {
                    container.innerHTML = `
                        <div class="api-error-panel">
                            <div class="error-icon">🔑⏰</div>
                            <h3>Clé API Expirée</h3>
                            <p>${data.error}</p>
                            <p class="help-text">${data.help_text}</p>
                            <div class="error-actions">
                                <a href="${data.help_url}" target="_blank" class="btn btn-primary">
                                    📝 Générer une nouvelle clé
                                </a>
                                <button onclick="app.showTailscaleSettings()" class="btn btn-secondary">
                                    ⚙️ Configurer
                                </button>
                            </div>
                        </div>
                    `;
                    this.showNotification('Clé API Tailscale expirée - Veuillez la renouveler', 'warning');
                } else if (data.error_type === 'missing_api_key') {
                    container.innerHTML = `
                        <div class="api-error-panel">
                            <div class="error-icon">🔑❌</div>
                            <h3>Configuration Requise</h3>
                            <p>Aucune clé API Tailscale configurée.</p>
                            <div class="error-actions">
                                <a href="${data.help_url}" target="_blank" class="btn btn-primary">
                                    📝 Obtenir une clé API
                                </a>
                                <button onclick="app.showTailscaleSettings()" class="btn btn-secondary">
                                    ⚙️ Configurer
                                </button>
                            </div>
                        </div>
                    `;
                } else {
                    container.innerHTML = `<div class="error">❌ ${data.error || 'Erreur lors du chargement'}</div>`;
                }
                this.showTailscaleStats(null);
            }
        } catch (error) {
            console.error('❌ Erreur Tailscale:', error);
            container.innerHTML = '<div class="error">❌ Erreur de connexion à l\'API Tailscale</div>';
            this.showTailscaleStats(null);
        }
    }
    
    /**
     * Afficher les appareils Tailscale
     */
    displayTailscaleDevices(devices) {
        const container = document.getElementById('tailscale-devices');
        
        if (!devices || devices.length === 0) {
            container.innerHTML = '<div class="empty-state">📱 Aucun appareil Tailscale trouvé</div>';
            return;
        }
        
        const devicesHtml = devices.map(device => this.renderTailscaleDevice(device)).join('');
        container.innerHTML = `
            <div class="tailscale-devices-grid">
                ${devicesHtml}
            </div>
        `;
    }
    
    /**
     * Vérifier si un appareil est récemment actif (moins de 5 minutes)
     */
    isRecentlyActive(lastSeenStr) {
        try {
            const lastSeen = new Date(lastSeenStr);
            const now = new Date();
            const diffMinutes = (now - lastSeen) / (1000 * 60);
            return diffMinutes < 5; // Considéré en ligne si vu dans les 5 dernières minutes
        } catch {
            return false;
        }
    }

    /**
     * Rendu d'un appareil Tailscale
     */
    renderTailscaleDevice(device) {
        // Tentative de détection du statut selon différents formats API
        const isOnline = device.online || 
                        device.connected || 
                        device.status === 'online' || 
                        device.status === 'active' ||
                        (device.lastSeen && this.isRecentlyActive(device.lastSeen));
        
        const statusClass = isOnline ? 'online' : 'offline';
        const statusIcon = isOnline ? '🟢' : '🔴';
        const lastSeen = device.lastSeen ? new Date(device.lastSeen).toLocaleString('fr-FR') : 'Jamais';
        
        return `
            <div class="tailscale-device-card ${statusClass}">
                <div class="device-header">
                    <h4>${device.hostname || device.name || 'Appareil inconnu'}</h4>
                    <span class="status-badge ${statusClass}">
                        ${statusIcon} ${isOnline ? 'En ligne' : 'Hors ligne'}
                    </span>
                </div>
                <div class="device-details">
                    <div class="detail-row">
                        <span>🔗 IP Tailscale:</span>
                        <code>${device.addresses?.[0] || 'N/A'}</code>
                    </div>
                    <div class="detail-row">
                        <span>💻 OS:</span>
                        <span>${device.os || 'Inconnu'}</span>
                    </div>
                    <div class="detail-row">
                        <span>👤 Utilisateur:</span>
                        <span>${device.user || 'N/A'}</span>
                    </div>
                    <div class="detail-row">
                        <span>⏱️ Dernière vue:</span>
                        <span>${lastSeen}</span>
                    </div>
                    ${device.id ? `
                    <div class="device-actions">
                        <button onclick="app.renameDevice('${device.id}', '${device.hostname || device.name}')" 
                                class="btn btn-sm btn-secondary" title="Renommer">
                            ✏️ Renommer
                        </button>
                        ${!device.authorized ? `
                        <button onclick="app.authorizeDevice('${device.id}')" 
                                class="btn btn-sm btn-success" title="Autoriser">
                            ✅ Autoriser
                        </button>
                        ` : ''}
                        <button onclick="app.deleteDevice('${device.id}', '${device.hostname || device.name}')" 
                                class="btn btn-sm btn-danger" title="Supprimer">
                            🗑️ Supprimer
                        </button>
                    </div>
                    ` : ''}
                </div>
                ${device.advertisesExitNode ? '<div class="exit-node-badge">🚪 Exit Node</div>' : ''}
                ${!device.authorized ? '<div class="auth-required-badge">⚠️ Autorisation requise</div>' : ''}
            </div>
        `;
    }
    
    /**
     * Afficher les statistiques Tailscale
     */
    showTailscaleStats(devices) {
        if (!devices) {
            document.getElementById('total-devices').textContent = '-';
            document.getElementById('online-devices').textContent = '-';
            document.getElementById('offline-devices').textContent = '-';
            document.getElementById('last-sync').textContent = '-';
            return;
        }
        
        const total = devices.length;
        
        // Utiliser la même logique de détection que renderTailscaleDevice
        const online = devices.filter(device => {
            return device.online || 
                   device.connected || 
                   device.status === 'online' || 
                   device.status === 'active' ||
                   (device.lastSeen && this.isRecentlyActive(device.lastSeen));
        }).length;
        
        const offline = total - online;
        
        document.getElementById('total-devices').textContent = total;
        document.getElementById('online-devices').textContent = online;
        document.getElementById('offline-devices').textContent = offline;
        document.getElementById('last-sync').textContent = new Date().toLocaleTimeString('fr-FR');
    }
    
    /**
     * Actualiser les données Tailscale
     */
    async refreshTailscale() {
        this.showNotification('🔄 Actualisation Tailscale...', 'info');
        await this.loadTailscaleDevices();
        
        // Recharger aussi les autres sections si elles sont visibles
        if (document.getElementById('vpn-tab-routes').classList.contains('active')) {
            await this.loadTailscaleRoutes();
        }
        if (document.getElementById('vpn-tab-acl').classList.contains('active')) {
            await this.loadTailscaleACL();
        }
        
        this.showNotification('✅ Tailscale actualisé', 'success');
    }

    /**
     * Afficher un sous-onglet VPN
     */
    showVpnTab(tabName) {
        // Masquer tous les onglets
        document.querySelectorAll('.vpn-tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.vpn-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Afficher l'onglet sélectionné
        const targetTab = document.getElementById(`vpn-tab-${tabName}`);
        const targetButton = document.querySelector(`.vpn-tab[onclick="app.showVpnTab('${tabName}')"]`);
        
        if (targetTab && targetButton) {
            targetTab.classList.add('active');
            targetButton.classList.add('active');
            
            // Charger les données seulement si l'onglet est vide
            if (tabName === 'routes') {
                const container = document.getElementById('tailscale-routes');
                if (container && container.querySelector('.loading')) {
                    this.loadTailscaleRoutes();
                }
            } else if (tabName === 'acl') {
                const container = document.getElementById('tailscale-acl');
                if (container && container.querySelector('.loading')) {
                    this.loadTailscaleACL();
                }
            }
        }
    }

    /**
     * Charger les routes Tailscale
     */
    async loadTailscaleRoutes() {
        const container = document.getElementById('tailscale-routes');
        container.innerHTML = '<div class="loading">🔄 Chargement des routes...</div>';
        
        try {
            const response = await fetch(`${this.apiBase}/api/tailscale/routes`);
            const data = await response.json();
            
            if (data.success) {
                this.displayTailscaleRoutes(data.routes);
            } else {
                container.innerHTML = `<div class="error">❌ ${data.error}</div>`;
            }
        } catch (error) {
            console.error('Erreur routes Tailscale:', error);
            container.innerHTML = '<div class="error">❌ Erreur de chargement des routes</div>';
        }
    }

    /**
     * Afficher les routes Tailscale
     */
    displayTailscaleRoutes(routes) {
        const container = document.getElementById('tailscale-routes');
        
        if (!routes || routes.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h4>🛣️ Aucune route subnet configurée</h4>
                    <p>Les routes subnet permettent d'accéder aux réseaux locaux via Tailscale.</p>
                    <p>💡 <strong>Pour configurer des routes :</strong></p>
                    <ol style="text-align: left; max-width: 500px; margin: 16px auto;">
                        <li>Installez Tailscale sur un appareil du réseau local</li>
                        <li>Lancez: <code>tailscale up --advertise-routes=192.168.1.0/24</code></li>
                        <li>Autorisez les routes dans l'admin Tailscale</li>
                    </ol>
                </div>
            `;
            return;
        }
        
        const routesHtml = routes.map(route => `
            <div class="route-item card">
                <div class="route-info">
                    <strong>🎯 ${route.destination}</strong>
                    <span class="route-via">via ${route.advertiser}</span>
                </div>
                <div class="route-status">
                    <span class="status ${route.enabled ? 'status-success' : 'status-warning'}">
                        ${route.enabled ? '✅ Activée' : '⏸️ Désactivée'}
                    </span>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = routesHtml;
    }

    /**
     * Charger les règles ACL Tailscale
     */
    async loadTailscaleACL() {
        const container = document.getElementById('tailscale-acl');
        container.innerHTML = '<div class="loading">🔄 Chargement des règles...</div>';
        
        try {
            const response = await fetch(`${this.apiBase}/api/tailscale/acl`);
            const data = await response.json();
            
            if (data.success) {
                this.displayTailscaleACL(data.acl);
            } else {
                const errorMessage = data.error === "Permissions insuffisantes pour accéder aux ACL" ?
                    `<div class="alert alert-warning">
                        <h4>🔒 Permissions Limitées</h4>
                        <p>Votre clé API n'a pas les permissions pour accéder aux règles ACL.</p>
                        <p>💡 <strong>Solution :</strong> Générez une nouvelle clé API avec les permissions "Access controls: Read"</p>
                        <a href="https://login.tailscale.com/admin/settings/keys" target="_blank" class="btn btn-primary btn-sm">
                            🔑 Gérer les clés API
                        </a>
                    </div>` :
                    `<div class="alert alert-error">❌ ${data.error}</div>`;
                
                container.innerHTML = errorMessage;
            }
        } catch (error) {
            console.error('Erreur ACL Tailscale:', error);
            container.innerHTML = `
                <div class="alert alert-error">
                    <h4>❌ Erreur de connexion</h4>
                    <p>Impossible de charger les règles ACL. Vérifiez votre configuration.</p>
                </div>
            `;
        }
    }

    /**
     * Afficher les règles ACL Tailscale
     */
    displayTailscaleACL(acl) {
        const container = document.getElementById('tailscale-acl');
        
        if (!acl) {
            container.innerHTML = '<div class="empty-state">🛡️ Aucune règle ACL configurée</div>';
            return;
        }
        
        // Afficher un résumé des règles ACL
        const groupsCount = Object.keys(acl.groups || {}).length;
        const rulesCount = (acl.acls || []).length;
        const testsCount = (acl.tests || []).length;
        
        const aclHtml = `
            <div class="card">
                <h4>📋 Résumé de la Politique de Sécurité</h4>
                
                <div class="stats-grid" style="margin: 20px 0;">
                    <div class="stat-card">
                        <h3>${groupsCount}</h3>
                        <p>Groupes</p>
                    </div>
                    <div class="stat-card">
                        <h3>${rulesCount}</h3>
                        <p>Règles ACL</p>
                    </div>
                    <div class="stat-card">
                        <h3>${testsCount}</h3>
                        <p>Tests</p>
                    </div>
                </div>
                
                ${Object.keys(acl.groups || {}).length > 0 ? `
                <div class="section">
                    <h5>👥 Groupes configurés</h5>
                    <div class="groups-list">
                        ${Object.keys(acl.groups).map(group => `
                            <span class="tag">${group}</span>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
                
                <div class="alert alert-info">
                    <p><strong>💡 Information :</strong> Les règles ACL contrôlent qui peut accéder à quoi dans votre réseau Tailscale.</p>
                    <p>Pour des modifications avancées, utilisez l'interface d'administration Tailscale.</p>
                    <p><a href="https://login.tailscale.com/admin/acls" target="_blank" class="btn btn-primary btn-sm">
                        🔗 Gérer les ACL
                    </a></p>
                </div>
            </div>
        `;
        
        container.innerHTML = aclHtml;
    }
    
    /**
     * Basculer l'affichage des paramètres
     */
    toggleTailscaleSettings() {
        const section = document.getElementById('vpn-config-section');
        section.style.display = section.style.display === 'none' ? 'block' : 'none';
    }

    /**
     * Afficher les paramètres Tailscale
     */
    showTailscaleSettings() {
        const section = document.getElementById('vpn-config-section');
        section.style.display = 'block';
        
        // Focus sur le champ API Key si vide
        const apiKeyField = document.getElementById('tailscale-api-key');
        if (!apiKeyField.value.trim()) {
            apiKeyField.focus();
        }
    }

    /**
     * Sauvegarder la configuration Tailscale
     */
    async saveTailscaleConfig(event) {
        event.preventDefault();
        
        const apiKey = document.getElementById('tailscale-api-key').value.trim();
        const tailnet = document.getElementById('tailscale-tailnet').value.trim();
        
        if (!apiKey) {
            this.showNotification('Veuillez saisir une clé API Tailscale', 'error');
            return;
        }
        
        if (!tailnet) {
            this.showNotification('Veuillez saisir le nom de votre Tailnet', 'error');
            return;
        }
        
        // Afficher l'indicateur de chargement
        const submitButton = event.target.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.textContent = '⏳ Test de la connexion...';
        submitButton.disabled = true;
        
        try {
            const response = await fetch(`${this.apiBase}/api/tailscale/config`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    api_key: apiKey,
                    tailnet: tailnet
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('✅ Configuration Tailscale sauvegardée avec succès !', 'success');
                
                // Cacher la section de configuration
                document.getElementById('vpn-config-section').style.display = 'none';
                
                // Recharger les appareils
                this.loadTailscaleDevices();
                this.checkTailscaleConfig();
                
            } else {
                // Gestion des erreurs spécifiques
                if (data.help_text && data.help_url) {
                    this.showNotification(`❌ ${data.error}`, 'error');
                    
                    // Afficher un message d'aide détaillé
                    setTimeout(() => {
                        const helpHtml = `
                            <div class="api-error-help">
                                <p><strong>💡 Aide :</strong> ${data.help_text}</p>
                                <a href="${data.help_url}" target="_blank" class="help-link">
                                    📝 Générer une nouvelle clé API
                                </a>
                            </div>
                        `;
                        
                        // Insérer l'aide sous le formulaire
                        const form = document.getElementById('tailscale-config-form');
                        const existingHelp = form.querySelector('.api-error-help');
                        if (existingHelp) existingHelp.remove();
                        
                        form.insertAdjacentHTML('afterend', helpHtml);
                    }, 1000);
                } else {
                    this.showNotification(`❌ ${data.error}`, 'error');
                }
            }
        } catch (error) {
            console.error('Erreur lors de la sauvegarde:', error);
            this.showNotification('❌ Erreur de connexion lors de la sauvegarde', 'error');
        } finally {
            // Restaurer le bouton
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }
    }

    /**
     * Renommer un appareil Tailscale
     */
    async renameDevice(deviceId, currentName) {
        const newName = prompt(`Nouveau nom pour "${currentName}":`, currentName);
        if (!newName || newName === currentName) return;
        
        try {
            const response = await fetch(`${this.apiBase}/api/tailscale/device/${deviceId}/rename`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: newName })
            });
            
            const data = await response.json();
            if (data.success) {
                this.showNotification(data.message, 'success');
                this.loadTailscaleDevices(); // Recharger la liste
            } else {
                this.showNotification(`Erreur: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showNotification('Erreur de connexion', 'error');
        }
    }

    /**
     * Autoriser un appareil Tailscale
     */
    async authorizeDevice(deviceId) {
        if (!confirm('Autoriser cet appareil sur le réseau ?')) return;
        
        try {
            const response = await fetch(`${this.apiBase}/api/tailscale/device/${deviceId}/authorize`, {
                method: 'POST'
            });
            
            const data = await response.json();
            if (data.success) {
                this.showNotification(data.message, 'success');
                this.loadTailscaleDevices(); // Recharger la liste
            } else {
                this.showNotification(`Erreur: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showNotification('Erreur de connexion', 'error');
        }
    }

    /**
     * Supprimer un appareil Tailscale
     */
    async deleteDevice(deviceId, deviceName) {
        if (!confirm(`⚠️ ATTENTION ⚠️\n\nSupprimer "${deviceName}" du réseau Tailscale ?\n\nCette action est irréversible !`)) return;
        
        try {
            const response = await fetch(`${this.apiBase}/api/tailscale/device/${deviceId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            if (data.success) {
                this.showNotification(data.message, 'success');
                this.loadTailscaleDevices(); // Recharger la liste
            } else {
                this.showNotification(`Erreur: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showNotification('Erreur de connexion', 'error');
        }
    }

    /**
     * Afficher une notification toast
     */
    showNotification(message, type = 'info', duration = 3000) {
        // Supprimer les anciennes notifications
        document.querySelectorAll('.toast-notification').forEach(toast => toast.remove());
        
        // Créer la nouvelle notification
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        
        const icon = {
            'success': '✅',
            'error': '❌', 
            'warning': '⚠️',
            'info': 'ℹ️'
        }[type] || 'ℹ️';
        
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-icon">${icon}</span>
                <span class="toast-message">${message}</span>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // Ajouter au DOM
        document.body.appendChild(toast);
        
        // Animation d'entrée
        requestAnimationFrame(() => {
            toast.classList.add('toast-show');
        });
        
        // Auto-suppression
        setTimeout(() => {
            if (toast.parentElement) {
                toast.classList.remove('toast-show');
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
    }
}

// Initialisation globale
const app = new HomeApp();
app.init();