# Scanner Réseau - Documentation Technique

## 📋 Résumé des améliorations

### ✅ Réalisations accomplies

1. **Scanner réseau unifié exhaustif** 
   - Fichier: `src/services/network_unified.py`
   - Remplace l'ancien scanner complexe
   - Détection Windows, Android, iOS, IoT

2. **Détecteur MAC vendor avec API**
   - Fichier: `src/services/mac_detector.py` 
   - API macvendors.com en priorité
   - Base JSON locale en fallback
   - Cache pour éviter spam API

3. **Détecteur mobile avancé**
   - Fichier: `src/services/mobile_detector.py`
   - Techniques poussées: mDNS, UPnP, HTTP fingerprinting
   - Identification REDMI/iPhone spécifique

4. **Base MAC vendors complète**
   - Fichier: `src/data/mac_vendors.json`
   - Focus Android/iOS (Samsung, Xiaomi, Apple, Huawei)
   - Patterns MAC privées

5. **API FastAPI intégrée**
   - Fichier: `src/api/network.py` mis à jour
   - Endpoints: `/api/network/scan`, `/api/network/discover`
   - Utilise le scanner unifié

## 🔧 Architecture technique

### Scanner unifié (`network_unified.py`)
```python
class UnifiedNetworkScanner:
    def __init__(self):
        self.mac_detector = MacVendorDetector()      # API + base locale
        self.mobile_detector = AdvancedMobileDetector()  # Techniques avancées
    
    def scan_complete_network(self) -> List[Dict]:
        # 1. Découverte nmap des IPs actives
        # 2. Scan exhaustif de chaque IP
        # 3. Combinaison hostname + MAC + ports
```

### Détection MAC (`mac_detector.py`)
```python
def detect_vendor_and_type(self, mac: str) -> Tuple[str, str]:
    # 1. API macvendors.com (si internet)
    # 2. Base locale JSON 
    # 3. Détection MAC privées (iOS/Android)
    # 4. Patterns mobiles
```

### Détection mobile (`mobile_detector.py`)  
```python
def analyze_mobile_device(self, ip: str, mac: str, hostname: str) -> Dict:
    # 1. mDNS/Bonjour services
    # 2. HTTP fingerprinting
    # 3. UPnP détaillé
    # 4. Ports mobiles spécifiques
    # 5. Patterns hostname
```

## 📊 Résultats tests réseau

### Appareils détectés sur 192.168.1.x:

| IP | MAC | Vendor (API) | Type détecté | Description |
|----|-----|--------------|--------------|-------------|
| 192.168.1.174 | 34:5a:60:7f:12:c1 | Micro-Star INTL CO. | Windows PC | TITO (MSI PC) |
| 192.168.1.24 | 10:7c:61:78:72:8b | ASUSTek COMPUTER INC. | PC/Laptop | CLACLA (ASUS) |
| 192.168.1.186 | 14:a3:2f:7f:a5:0f | **Huawei Device Co.** | **Android Phone** | **Probablement REDMI 12** |
| 192.168.1.171 | a4:e5:7c:31:54:36 | Espressif Inc. | IoT Device | ESP32/Arduino |
| 192.168.1.254 | 8c:97:ea:31:c0:a2 | FREEBOX SAS | Network Equipment | Box internet |
| 192.168.1.23 | ca:08:c5:bf:00:13 | MAC Privée | Mobile (Privacy) | **iPhone/Android** |
| 192.168.1.99 | 9e:67:44:b4:b8:7d | MAC Privée | Mobile (Privacy) | **iPhone/Android** |

### 🎯 Cibles identifiées:
- **REDMI 12**: Probablement 192.168.1.186 (Huawei Device Co.)
- **iPhone 13 Pro**: Probablement 192.168.1.23 ou 192.168.1.99 (MAC privées)

## 🚀 Fonctionnalités

### Détection Windows
- NetBIOS (nmblookup, nbtscan)
- Ports SMB (139, 445)
- Hostname patterns

### Détection Android  
- Vendors: Samsung, Xiaomi, Huawei, OPPO, VIVO
- Services mDNS spécifiques
- Patterns UPnP

### Détection iOS
- MAC randomisées (bit locally administered)
- Services AirPlay, HomeKit
- Patterns Apple

### API macvendors.com
- Rate limit: 1 req/sec respecté
- Cache intégré
- Fallback base locale si pas d'internet

## 📁 Fichiers modifiés/créés

### Nouveaux fichiers:
- `src/services/network_unified.py` - Scanner principal
- `src/services/mac_detector.py` - Détection vendor avec API
- `src/services/mobile_detector.py` - Détection mobile avancée  
- `src/data/mac_vendors.json` - Base MAC locale

### Fichiers modifiés:
- `src/api/network.py` - API FastAPI mise à jour
- Interface web (emojis natifs au lieu de Lucide)

## 🔄 Points à reprendre plus tard

1. **Optimisation mobile detector**: Timeout et parallélisation
2. **Cache persistant**: Sauvegarder résultats API 
3. **Signature devices**: Fingerprints spécifiques REDMI/iPhone
4. **Interface web**: Affichage détections avancées
5. **Stats réseau**: Dashboard analytics des appareils

## 🛠️ Commandes pour reprendre

```bash
# Démarrer le serveur
cd /home/pie333/Desktop/333HOME
source venv/bin/activate
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Tester l'API
curl -s "http://localhost:8000/api/network/scan" | jq

# Test individuel
curl -s "http://localhost:8000/api/network/device/192.168.1.186" | jq
```

## 📋 Statut
- ✅ Scanner unifié fonctionnel
- ✅ API macvendors.com intégrée  
- ✅ Détection mobile avec MAC privées
- ✅ Identification Windows/Android/iOS
- ⏸️ **PAUSE** - Reprendre monitoring Pi température