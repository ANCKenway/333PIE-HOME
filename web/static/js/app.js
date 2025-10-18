/**
 * Application principale - Gestion de l'interface et des interactions
 */
class HomeAutomationApp {
    constructor() {
        this.currentSection = 'dashboard';
        this.devices = [];
        this.networkDevices = [];
        this.refreshInterval = null;
        this.performanceMode = true; // Mode performance par défaut
        
        this.init();
    }
    
    // Plus besoin de Lucide - Émojis natifs ultra-rapides !
    safeCreateIcons() {
        // Fonction vide - plus d'icônes à créer
    }

    async init() {
        this.setupNavigation();
        this.setupEventListeners();
        this.setupModals();
        
        // Mode ultra-performance : pas d'animations
        document.body.style.setProperty('--transition-duration', '0s');
        document.documentElement.style.setProperty('--animation-duration', '0s');
        
        // Précharger Lucide pour un affichage instantané
        this.safeCreateIcons();
        
        // Chargement initial
        await this.loadDashboard();
        // Pas de refresh automatique - tout sera manuel
    }

    // === NAVIGATION ===

    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item[data-section]');
        
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                this.switchSection(section);
            });
        });
    }

    switchSection(sectionName) {
        // Mise à jour navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

        // Mise à jour contenu
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`${sectionName}-section`).classList.add('active');

        // Mise à jour titre
        const titles = {
            'dashboard': 'Dashboard',
            'devices': 'Mes Appareils',
            'network': 'Scanner Réseau',
            'monitoring': 'Monitoring Pi',
            'settings': 'Paramètres'
        };
        document.getElementById('page-title').textContent = titles[sectionName];

        this.currentSection = sectionName;

        // Fermer le menu mobile si ouvert
        this.closeMobileMenu();

        // Chargement des données spécifiques à la section
        this.loadSectionData(sectionName);
    }



    // === DASHBOARD ===

    async loadDashboard(force = false) {
        try {
            // CHARGEMENT INSTANTANÉ - Affichage immédiat du squelette
            this.showDashboardSkeleton();
            
            // Chargement en arrière-plan (non-bloquant)
            Promise.all([
                this.loadSystemStats(force),
                this.loadFavoriteDevices(force)
            ]).catch(error => {
                console.error('Erreur chargement dashboard:', error);
            });
            
        } catch (error) {
            console.error('Erreur chargement dashboard:', error);
        }
    }
    
    showDashboardSkeleton() {
        // Affichage instantané des valeurs par défaut
        document.getElementById('cpu-usage').textContent = '...';
        document.getElementById('temperature').textContent = '...';
        
        // Skeleton pour les appareils favoris
        const favoritesContainer = document.getElementById('favorite-devices');
        if (favoritesContainer) {
            favoritesContainer.innerHTML = `
                <div class="loading-skeleton">
                    <div class="animate-pulse flex space-x-4">
                        <div class="rounded bg-gray-300 h-12 w-12"></div>
                        <div class="flex-1 space-y-2 py-1">
                            <div class="h-4 bg-gray-300 rounded w-3/4"></div>
                            <div class="h-4 bg-gray-300 rounded w-1/2"></div>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    async loadSystemStats(force = false) {
        try {
            const data = await api.getSystemInfo(!force);
            
            document.getElementById('cpu-usage').textContent = 
                Components.formatNumber(data.cpu.usage_percent) + '%';
            document.getElementById('temperature').textContent = 
                Components.formatNumber(data.temperature) + '°C';
                
        } catch (error) {
            document.getElementById('cpu-usage').textContent = '--';
            document.getElementById('temperature').textContent = '--';
        }
    }

    async loadFavoriteDevices() {
        const container = document.getElementById('favorite-devices');
        container.innerHTML = Components.createLoading('Chargement des favoris...');
        
        try {
            const data = await api.getComputers();
            this.devices = data.computers || [];
            
            if (this.devices.length === 0) {
                container.innerHTML = Components.createEmpty(
                    'Aucun appareil configuré', 
                    'monitor'
                );
                return;
            }

            // Afficher seulement les 3 premiers
            const favoriteDevices = this.devices.slice(0, 3);
            container.innerHTML = favoriteDevices.map(device => 
                Components.createDeviceCard(device, { compact: true })
            ).join('');
            
            this.setupDeviceActions();
            
        } catch (error) {
            container.innerHTML = Components.createError('Erreur de chargement');
        }
    }

    // === GESTION DES APPAREILS ===

    async loadDevices(force = false) {
        const container = document.getElementById('devices-list');
        container.innerHTML = Components.createLoading('Chargement des appareils...');
        
        try {
            const data = await api.getComputers(!force);
            this.devices = data.computers || [];
            
            if (this.devices.length === 0) {
                container.innerHTML = Components.createEmpty(
                    'Aucun appareil configuré. Cliquez sur "Ajouter" pour commencer.',
                    'monitor'
                );
                return;
            }

            container.innerHTML = this.devices.map(device => 
                Components.createDeviceCard(device, { showActions: true })
            ).join('');
            
            this.setupDeviceActions();
            
        } catch (error) {
            container.innerHTML = Components.createError('Erreur de chargement');
        }
    }

    setupDeviceActions() {
        // Wake-on-LAN
        document.querySelectorAll('.wake-device-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const mac = btn.dataset.mac;
                await this.wakeDevice(mac, btn);
            });
        });

        // Infos détaillées
        document.querySelectorAll('.device-info-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const ip = btn.dataset.ip;
                await this.showDeviceInfo(ip);
            });
        });

        // Ajouter aux favoris
        document.querySelectorAll('.add-to-favorites-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const device = JSON.parse(btn.dataset.device);
                this.addToFavorites(device);
            });
        });

        // Supprimer appareil
        document.querySelectorAll('.remove-device-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const deviceId = btn.dataset.deviceId;
                this.removeDevice(deviceId);
            });
        });
    }

    async wakeDevice(mac, button) {
        // Feedback INSTANTANÉ - Réaction immédiate
        const originalText = button.innerHTML;
        const originalClass = button.className;
        
        // Animation immédiate sans attendre l'API
        button.innerHTML = '<i data-lucide="zap" class="w-4 h-4 animate-pulse"></i> Réveil...';
        button.className = originalClass + ' bg-yellow-500 text-white';
        button.disabled = true;
        
        // Notification immédiate de démarrage
        this.showNotification('⚡ Envoi du signal Wake-on-LAN...', 'info');
        
        try {
            // API en arrière-plan
            const result = await api.wakeOnLan(mac);
            
            // Succès instantané
            button.innerHTML = '<i data-lucide="check" class="w-4 h-4"></i> Envoyé';
            button.className = originalClass + ' bg-green-500 text-white';
            this.showNotification('✅ ' + result.message, 'success');
            
            // Pas d'attente de 3 sec - refresh immédiat en arrière-plan
            setTimeout(() => {
                this.loadSectionData(this.currentSection, false); // Soft refresh
            }, 1000);
            
        } catch (error) {
            button.innerHTML = '<i data-lucide="x" class="w-4 h-4"></i> Erreur';
            button.className = originalClass + ' bg-red-500 text-white';
            this.showNotification('❌ Erreur: ' + error.message, 'error');
        }
        
        // Restauration après 2 sec (plus court)
        setTimeout(() => {
            button.innerHTML = originalText;
            button.className = originalClass;
            button.disabled = false;
            this.safeCreateIcons(); // Recréer les icônes
        }, 2000);
    }

    async showDeviceInfo(ip) {
        try {
            const device = await api.getDeviceInfo(ip);
            
            const details = `
                <div class="space-y-3">
                    <div><strong>Nom:</strong> ${device.hostname}</div>
                    <div><strong>IP:</strong> ${device.ip}</div>
                    <div><strong>MAC:</strong> ${device.mac || 'Inconnu'}</div>
                    <div><strong>Type:</strong> ${Components.getDeviceTypeLabel(device.type)}</div>
                    <div><strong>Statut:</strong> ${Components.getStatusLabel(device.status)}</div>
                </div>
            `;
            
            this.showModal('Informations de l\'appareil', details);
            
        } catch (error) {
            this.showNotification('❌ Impossible de récupérer les informations', 'error');
        }
    }

    // === SCANNER RÉSEAU ===

    setupNetworkSection() {
        const scanBtn = document.getElementById('network-scan-btn');
        const quickScanBtn = document.getElementById('quick-scan-btn');
        
        if (scanBtn) {
            scanBtn.addEventListener('click', () => this.scanNetwork());
        }
        
        if (quickScanBtn) {
            quickScanBtn.addEventListener('click', () => this.quickScan());
        }

        // Filtres
        const typeFilter = document.getElementById('device-type-filter');
        const searchInput = document.getElementById('device-search');
        
        if (typeFilter) {
            typeFilter.addEventListener('change', () => this.filterNetworkDevices());
        }
        
        if (searchInput) {
            searchInput.addEventListener('input', () => this.filterNetworkDevices());
        }
    }

    async scanNetwork() {
        const container = document.getElementById('network-devices');
        const button = document.getElementById('network-scan-btn');
        const countElement = document.getElementById('devices-count');
        
        button.innerHTML = '<div class="spinner w-4 h-4 mr-2"></div>Scan en cours...';
        button.disabled = true;
        container.innerHTML = Components.createLoading('Scan du réseau en cours...');
        
        try {
            const data = await api.scanNetwork();
            this.networkDevices = data.devices || [];
            
            countElement.textContent = `${this.networkDevices.length} appareil${this.networkDevices.length > 1 ? 's' : ''}`;
            
            this.displayNetworkDevices();
            
        } catch (error) {
            container.innerHTML = Components.createError('Erreur lors du scan réseau');
            countElement.textContent = '0 appareil';
        } finally {
            button.innerHTML = '<i data-lucide="wifi" width="20" height="20"></i>Scanner le réseau';
            button.disabled = false;
            this.safeCreateIcons(); // Re-créer les icônes
        }
    }

    async quickScan() {
        const container = document.getElementById('quick-scan-results');
        
        container.innerHTML = Components.createLoading('Scan rapide...');
        
        try {
            const data = await api.discoverNetwork(true); // Force le scan complet
            const devices = data.devices || [];
            
            if (devices.length === 0) {
                container.innerHTML = '<p class="text-gray-600 text-sm">Aucun appareil détecté</p>';
                return;
            }
            
            container.innerHTML = devices.slice(0, 3).map(device => 
                `<div class="text-sm mb-2">
                    <span class="font-medium">${device.hostname}</span>
                    <span class="text-gray-600">- ${device.ip}</span>
                </div>`
            ).join('');
            
        } catch (error) {
            container.innerHTML = '<p class="text-error-600 text-sm">Erreur de scan</p>';
        }
    }

    displayNetworkDevices() {
        const container = document.getElementById('network-devices');
        
        if (this.networkDevices.length === 0) {
            container.innerHTML = Components.createEmpty(
                'Aucun appareil détecté sur le réseau',
                'wifi-off'
            );
            return;
        }

        container.innerHTML = this.networkDevices.map(device => 
            Components.createDeviceCard(device, { showActions: true })
        ).join('');
        
        this.setupDeviceActions();
        this.safeCreateIcons();
    }

    filterNetworkDevices() {
        const typeFilter = document.getElementById('device-type-filter')?.value;
        const searchTerm = document.getElementById('device-search')?.value.toLowerCase();
        
        let filteredDevices = [...this.networkDevices];
        
        if (typeFilter) {
            filteredDevices = filteredDevices.filter(device => 
                device.type === typeFilter
            );
        }
        
        if (searchTerm) {
            filteredDevices = filteredDevices.filter(device => 
                device.hostname.toLowerCase().includes(searchTerm) ||
                device.ip.includes(searchTerm)
            );
        }
        
        const container = document.getElementById('network-devices');
        
        if (filteredDevices.length === 0) {
            container.innerHTML = Components.createEmpty(
                'Aucun appareil ne correspond aux critères',
                'search'
            );
            return;
        }
        
        container.innerHTML = filteredDevices.map(device => 
            Components.createDeviceCard(device, { showActions: true })
        ).join('');
        
        this.setupDeviceActions();
        this.safeCreateIcons();
    }

    // === MONITORING ===

    async loadMonitoring() {
        try {
            // Stats détaillées
            await this.loadDetailedStats();
            
            // Services système
            await this.loadSystemServices();
            
        } catch (error) {
            console.error('Erreur monitoring:', error);
        }
    }

    async loadDetailedStats() {
        const container = document.getElementById('detailed-stats');
        container.innerHTML = Components.createLoading('Chargement...');
        
        try {
            const data = await api.getSystemInfo();
            
            container.innerHTML = `
                <div class="grid grid-cols-2 gap-4">
                    ${Components.createStatCard('CPU', data.cpu.usage_percent + '%', 'cpu')}
                    ${Components.createStatCard('Température', data.temperature + '°C', 'thermometer')}
                    ${Components.createStatCard('RAM', data.memory.usage_percent + '%', 'hard-drive')}
                    ${Components.createStatCard('Utilisé', Components.formatBytes(data.memory.used_gb * 1024 * 1024 * 1024), 'database')}
                </div>
            `;
            
            this.safeCreateIcons();
            
        } catch (error) {
            container.innerHTML = Components.createError('Erreur de chargement');
        }
    }

    async loadSystemServices() {
        const container = document.getElementById('system-services');
        container.innerHTML = Components.createLoading('Chargement des services...');
        
        try {
            const data = await api.getPiServices();
            const services = data.services || [];
            
            container.innerHTML = Components.createServicesList(services);
            this.safeCreateIcons();
            
        } catch (error) {
            container.innerHTML = Components.createError('Erreur de chargement');
        }
    }

    // === MODALS ET ÉVÉNEMENTS ===

    setupEventListeners() {
        // Bouton actualiser - force le refresh
        document.getElementById('refresh-btn')?.addEventListener('click', () => {
            this.loadSectionData(this.currentSection, true); // Force refresh
        });

        // Bouton ajouter appareil
        document.getElementById('add-device-btn')?.addEventListener('click', () => {
            this.showDeviceModal();
        });

        // Navigation par boutons
        document.querySelectorAll('button[data-section]').forEach(btn => {
            btn.addEventListener('click', () => {
                const section = btn.dataset.section;
                this.switchSection(section);
            });
        });

        // Menu mobile
        document.getElementById('mobile-menu-btn')?.addEventListener('click', () => {
            this.toggleMobileMenu();
        });
    }

    toggleMobileMenu() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.getElementById('mobile-overlay');
        
        if (sidebar.classList.contains('mobile-open')) {
            this.closeMobileMenu();
        } else {
            this.openMobileMenu();
        }
    }

    openMobileMenu() {
        const sidebar = document.querySelector('.sidebar');
        
        // Créer overlay si il n'existe pas
        let overlay = document.getElementById('mobile-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'mobile-overlay';
            overlay.className = 'mobile-menu-overlay';
            document.body.appendChild(overlay);
            
            overlay.addEventListener('click', () => {
                this.closeMobileMenu();
            });
        }
        
        sidebar.classList.add('mobile-open');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden'; // Empêcher le scroll
    }

    closeMobileMenu() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.getElementById('mobile-overlay');
        
        sidebar.classList.remove('mobile-open');
        if (overlay) {
            overlay.classList.remove('active');
        }
        document.body.style.overflow = ''; // Restaurer le scroll
    }

    setupModals() {
        // Fermeture des modals
        document.querySelectorAll('.modal-close, .modal-overlay').forEach(element => {
            element.addEventListener('click', () => {
                this.closeModal();
            });
        });

        // Formulaire d'ajout d'appareil
        document.getElementById('device-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.addDevice();
        });
    }

    showDeviceModal() {
        document.getElementById('device-modal').classList.remove('hidden');
    }

    closeModal() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.add('hidden');
        });
    }

    showModal(title, content) {
        // Modal générique pour affichage d'informations
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-overlay"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="modal-title">${title}</h3>
                    <button class="modal-close">
                        <i data-lucide="x" width="20" height="20"></i>
                    </button>
                </div>
                <div class="modal-body">${content}</div>
                <div class="modal-footer">
                    <button class="btn btn-secondary modal-close">Fermer</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        this.safeCreateIcons();
        
        // Event listeners
        modal.querySelectorAll('.modal-close, .modal-overlay').forEach(element => {
            element.addEventListener('click', () => {
                document.body.removeChild(modal);
            });
        });
    }

    async addDevice() {
        const form = document.getElementById('device-form');
        const formData = new FormData(form);
        
        const device = {
            name: document.getElementById('device-name').value,
            ip: document.getElementById('device-ip').value,
            mac: document.getElementById('device-mac').value,
            type: document.getElementById('device-type').value
        };

        try {
            await api.addDevice(device);
            this.showNotification('✅ Appareil ajouté avec succès', 'success');
            this.closeModal();
            form.reset();
            
            // Recharger la liste
            await this.loadDevices();
            
        } catch (error) {
            this.showNotification('❌ Erreur lors de l\'ajout: ' + error.message, 'error');
        }
    }

    async addToFavorites(device) {
        try {
            await api.addDevice(device);
            this.showNotification('✅ Appareil ajouté aux favoris', 'success');
            await this.loadFavoriteDevices();
        } catch (error) {
            this.showNotification('❌ Erreur: ' + error.message, 'error');
        }
    }

    async removeDevice(deviceId) {
        if (!confirm('Êtes-vous sûr de vouloir supprimer cet appareil ?')) {
            return;
        }

        try {
            await api.removeDevice(deviceId);
            this.showNotification('✅ Appareil supprimé', 'success');
            
            if (this.currentSection === 'devices') {
                await this.loadDevices();
            } else {
                await this.loadFavoriteDevices();
            }
        } catch (error) {
            this.showNotification('❌ Erreur: ' + error.message, 'error');
        }
    }

    showNotification(message, type = 'info') {
        // Toast notification simple
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
            type === 'success' ? 'bg-success-500 text-white' : 
            type === 'error' ? 'bg-error-500 text-white' : 
            'bg-primary-500 text-white'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 5000);
    }

    // === REFRESH MANUEL ===

    async loadSectionData(section, force = false) {
        // Lazy loading - ne charge que si pas déjà chargé ou si forcé
        const sectionElement = document.getElementById(`${section}-section`);
        const isLoaded = sectionElement?.dataset.loaded === 'true';
        
        if (!force && isLoaded) {
            return; // Section déjà chargée
        }
        
        // Animation du bouton refresh
        const refreshBtn = document.getElementById('refresh-btn');
        const refreshIcon = refreshBtn?.querySelector('[data-lucide="refresh-cw"]');
        if (refreshIcon) {
            refreshIcon.classList.add('animate-spin');
        }

        try {
            switch(section) {
                case 'dashboard':
                    await this.loadDashboard(force);
                    break;
                case 'devices':
                    await this.loadDevices(force);
                    break;
                case 'network':
                    this.setupNetworkSection();
                    break;
                case 'monitoring':
                    await this.loadMonitoring(force);
                    break;
            }
            
            // Marquer comme chargé
            if (sectionElement) {
                sectionElement.dataset.loaded = 'true';
            }
        } finally {
            // Arrêter l'animation
            if (refreshIcon) {
                setTimeout(() => {
                    refreshIcon.classList.remove('animate-spin');
                }, 200); // Animation plus courte
            }
        }
    }
    
    showCacheIndicator(container, isCached = false) {
        // Supprimer l'ancien indicateur
        const existingIndicator = container.querySelector('.cache-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }
        
        // Ajouter le nouvel indicateur
        const indicator = document.createElement('div');
        indicator.className = `cache-indicator ${isCached ? 'cached' : ''}`;
        indicator.innerHTML = `
            <i data-lucide="${isCached ? 'zap' : 'refresh-cw'}" width="12" height="12"></i>
            <span>${isCached ? 'Données en cache' : 'Données actualisées'}</span>
        `;
        
        container.appendChild(indicator);
        this.safeCreateIcons();
        
        // Supprimer après 3 secondes
        setTimeout(() => {
            if (indicator.parentNode) {
                indicator.remove();
            }
        }, 3000);
    }
}

// Initialisation de l'application
document.addEventListener('DOMContentLoaded', () => {
    window.app = new HomeAutomationApp();
});