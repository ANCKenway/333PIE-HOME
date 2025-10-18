/**
 * Components - Composants UI réutilisables
 */

class Components {
    /**
     * Crée une carte d'appareil
     */
    static createDeviceCard(device, options = {}) {
        const { showActions = true, compact = false } = options;
        
        return `
            <div class="device-card" data-device-id="${device.id || device.ip}">
                <div class="device-info">
                    <div class="device-name">
                        ${device.name || device.hostname}
                        ${device.vendor ? `<span class="text-sm text-gray-500 ml-2">(${device.vendor})</span>` : ''}
                    </div>
                    <div class="device-details">
                        <span>IP: ${device.ip}</span>
                        ${device.mac && device.mac !== 'unknown' ? `<span>MAC: ${device.mac}</span>` : ''}
                        ${device.device_type ? `<span>Type: ${this.getDeviceTypeLabel(device.device_type)}</span>` : ''}
                        ${device.description ? `<span class="text-blue-600">${device.description}</span>` : ''}
                    </div>
                </div>
                
                <div class="flex items-center gap-3">
                    <span class="status-badge status-${device.status || 'unknown'}">
                        <div class="w-2 h-2 rounded-full ${device.status === 'online' ? 'bg-success-500' : device.status === 'offline' ? 'bg-error-500' : 'bg-gray-400'}"></div>
                        ${this.getStatusLabel(device.status)}
                    </span>
                    
                    ${showActions ? `
                        <div class="device-actions">
                            ${device.status === 'offline' && device.mac ? `
                                <button class="btn btn-success btn-sm wake-device-btn" data-mac="${device.mac}">
                                    ⚡ Wake
                                </button>
                            ` : ''}
                            
                            <button class="btn btn-secondary btn-sm device-info-btn" data-ip="${device.ip}" title="Informations">
                                ℹ️
                            </button>
                            
                            ${!compact ? `
                                <button class="btn btn-primary btn-sm add-to-favorites-btn" data-device='${JSON.stringify(device)}' title="Ajouter aux favoris">
                                    ⭐
                                </button>
                                
                                <button class="btn btn-danger btn-sm remove-device-btn" data-device-id="${device.id || device.ip}" title="Supprimer">
                                    🗑️
                                </button>
                            ` : ''}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    /**
     * Crée une carte de statistique
     */
    static createStatCard(label, value, icon, color = 'primary') {
        return `
            <div class="text-center p-4 bg-gray-50 rounded-lg">
                <div class="flex items-center justify-center mb-2">
                    <span class="text-2xl">${this.getEmojiForStat(icon)}</span>
                </div>
                <div class="text-2xl font-bold text-${color}-600">${value}</div>
                <div class="text-sm text-gray-600">${label}</div>
            </div>
        `;
    }

    /**
     * Crée une liste de services
     */
    static createServicesList(services) {
        if (!services || services.length === 0) {
            return '<p class="text-gray-600 text-sm">Aucun service détecté</p>';
        }

        return services.map(service => `
            <div class="flex items-center justify-between p-3 border border-gray-200 rounded-lg mb-2">
                <div class="flex items-center gap-3">
                    <span class="text-lg">${this.getEmojiForService(service.type)}</span>
                    <div>
                        <div class="font-medium">${service.name}</div>
                        ${service.port ? `<div class="text-sm text-gray-600">Port ${service.port}</div>` : ''}
                    </div>
                </div>
                <span class="status-badge status-${service.status}">
                    ${this.getStatusLabel(service.status)}
                </span>
            </div>
        `).join('');
    }

    /**
     * État de chargement
     */
    static createLoading(message = 'Chargement...') {
        return `
            <div class="loading">
                <div class="spinner mr-3"></div>
                <span>${message}</span>
            </div>
        `;
    }

    /**
     * Message d'erreur
     */
    static createError(message) {
        return `
            <div class="flex items-center justify-center p-6 text-error-600">
                ⚠️
                <span>${message}</span>
            </div>
        `;
    }

    /**
     * Message vide
     */
    static createEmpty(message, icon = 'inbox') {
        return `
            <div class="text-center py-12">
                <span class="text-4xl mb-4 block">${this.getEmojiForEmpty(icon)}</span>
                <p class="text-gray-600">${message}</p>
            </div>
        `;
    }

    /**
     * Filtre de recherche et tri
     */
    static createFilters() {
        return `
            <div class="flex gap-4 items-center mb-6">
                <div class="flex-1">
                    <input type="text" id="search-input" class="form-input" placeholder="Rechercher un appareil...">
                </div>
                <select id="type-filter" class="form-select">
                    <option value="">Tous les types</option>
                    <option value="windows">Windows</option>
                    <option value="linux">Linux</option>
                    <option value="desktop">PC Bureau</option>
                    <option value="laptop">Portable</option>
                    <option value="server">Serveur</option>
                </select>
                <select id="status-filter" class="form-select">
                    <option value="">Tous les états</option>
                    <option value="online">En ligne</option>
                    <option value="offline">Hors ligne</option>
                </select>
            </div>
        `;
    }

    // === HELPERS ===

    static getDeviceTypeLabel(type) {
        const labels = {
            'desktop': 'PC Bureau',
            'laptop': 'Portable', 
            'server': 'Serveur',
            'windows': 'Windows',
            'linux': 'Linux',
            'mac': 'Mac',
            'ios': 'iOS',
            'android': 'Android',
            'router': 'Routeur',
            'printer': 'Imprimante',
            'raspberry-pi': 'Raspberry Pi',
            'unknown': 'Inconnu'
        };
        return labels[type] || type;
    }

    static getStatusLabel(status) {
        const labels = {
            'online': 'En ligne',
            'offline': 'Hors ligne',
            'unknown': 'Inconnu'
        };
        return labels[status] || status;
    }

    static getServiceIcon(type) {
        const icons = {
            'system': 'terminal',
            'web': 'globe',
            'container': 'package',
            'database': 'database',
            'media': 'play'
        };
        return icons[type] || 'server';
    }

    /**
     * Formate les nombres
     */
    static formatNumber(num, decimals = 1) {
        return Number(num).toFixed(decimals);
    }

    /**
     * Formate la taille de fichier
     */
    static formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    /**
     * Validation d'adresse IP
     */
    static validateIP(ip) {
        const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        return ipRegex.test(ip);
    }

    /**
     * Validation d'adresse MAC
     */
    static validateMAC(mac) {
        const macRegex = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/;
        return macRegex.test(mac);
    }
    
    /**
     * Émojis pour statistiques - ULTRA RAPIDE
     */
    static getEmojiForStat(icon) {
        const emojiMap = {
            'cpu': '🖥️',
            'thermometer': '🌡️',
            'hard-drive': '💽',
            'database': '💾',
            'memory': '🧠',
            'activity': '📊',
            'wifi': '📡',
            'network': '🌐'
        };
        return emojiMap[icon] || '📊';
    }
    
    /**
     * Émojis pour services - ULTRA RAPIDE  
     */
    static getEmojiForService(type) {
        const emojiMap = {
            'web': '🌐',
            'database': '💾',
            'mail': '📧',
            'ssh': '🔒',
            'ftp': '📁',
            'dns': '🔍',
            'dhcp': '🏠',
            'media': '🎥',
            'plex': '🎬'
        };
        return emojiMap[type] || '⚙️';
    }
    
    /**
     * Émojis pour empty state - ULTRA RAPIDE
     */
    static getEmojiForEmpty(icon) {
        const emojiMap = {
            'inbox': '📮',
            'search': '🔍',
            'wifi-off': '📵',
            'server': '🖥️'
        };
        return emojiMap[icon] || '📭';
    }
}

// Export global
window.Components = Components;