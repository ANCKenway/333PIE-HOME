/**
 * API Client - Module de communication avec l'API FastAPI
 */

class API {
    constructor() {
        this.baseURL = '';
        this.cache = new Map();
        this.cacheTTL = 30000; // 30 secondes de cache côté client
    }
    
    _getCacheKey(url, options = {}) {
        return `${url}_${JSON.stringify(options)}`;
    }
    
    _isValidCache(cacheEntry) {
        return cacheEntry && (Date.now() - cacheEntry.timestamp < this.cacheTTL);
    }
    
    _setCache(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
    }
    
    _getCache(key) {
        const entry = this.cache.get(key);
        return this._isValidCache(entry) ? entry.data : null;
    }

    /**
     * Méthode générique pour les requêtes
     */
    async request(endpoint, options = {}) {
        const { useCache = false, ...fetchOptions } = options;
        const cacheKey = this._getCacheKey(endpoint, fetchOptions);
        
        // Vérifier le cache pour les requêtes GET
        if (useCache && (!fetchOptions.method || fetchOptions.method === 'GET')) {
            const cachedData = this._getCache(cacheKey);
            if (cachedData) {
                return cachedData;
            }
        }
        
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...fetchOptions.headers
                },
                ...fetchOptions
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            // Mettre en cache les réponses GET réussies
            if (useCache && (!fetchOptions.method || fetchOptions.method === 'GET')) {
                this._setCache(cacheKey, data);
            }
            
            return data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    // === APPAREILS ===
    
    /**
     * Récupère la liste des ordinateurs configurés
     */
    async getComputers(useCache = true) {
        return this.request('/api/devices/computers', { useCache });
    }

    /**
     * Ajoute un nouvel appareil
     */
    async addDevice(device) {
        return this.request('/api/devices/computers', {
            method: 'POST',
            body: JSON.stringify(device)
        });
    }

    /**
     * Supprime un appareil
     */
    async removeDevice(deviceId) {
        return this.request(`/api/devices/computers/${deviceId}`, {
            method: 'DELETE'
        });
    }

    /**
     * Wake-on-LAN pour un appareil
     */
    async wakeOnLan(mac) {
        return this.request(`/api/devices/wol/${mac}`, {
            method: 'POST'
        });
    }

    /**
     * Status du Raspberry Pi
     */
    async getPiStatus() {
        return this.request('/api/devices/pi/status');
    }

    /**
     * Services du Raspberry Pi
     */
    async getPiServices() {
        return this.request('/api/devices/pi/services');
    }

    /**
     * Informations système simplifiées
     */
    async getSystemInfo(useCache = true) {
        return this.request('/api/devices/system', { useCache });
    }

    // === RÉSEAU ===
    
    /**
     * Scan complet du réseau
     */
    async scanNetwork() {
        return this.request('/api/network/scan');
    }

    /**
     * Découverte rapide des appareils
     */
    async discoverNetwork(force = false) {
        const endpoint = force ? '/api/network/discover?force=true' : '/api/network/discover';
        return this.request(endpoint, { useCache: !force });
    }

    /**
     * Informations détaillées d'un appareil
     */
    async getDeviceInfo(ip) {
        return this.request(`/api/network/device/${ip}`);
    }
}

// Instance globale
window.api = new API();