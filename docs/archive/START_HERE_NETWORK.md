# 🚀 START HERE - Prochaine Session AI

**Date de création** : 19 octobre 2025  
**Version du projet** : 3.0  
**Phase actuelle** : Feature Network - Architecture définie ✅

---

## 📍 Où en sommes-nous ?

### ✅ Complété
1. **Architecture Core** : config, logging, lifecycle moderne
2. **Shared Utilities** : exceptions, utils, constants
3. **Feature Devices** : 100% complète et fonctionnelle
4. **Documentation** : Architecture + APIs documentées
5. **Storage v3.0** : Format moderne avec migration auto

### 🎯 Prochaine étape : Feature Network

**Objectif** : Créer le hub de monitoring réseau complet

**Documentation** : [docs/NETWORK_ARCHITECTURE.md](docs/NETWORK_ARCHITECTURE.md)

---

## 🌐 Vision Feature Network

### Concept Principal
**Network** est le **hub central** qui :
- 🔍 Découvre TOUS les appareils sur le réseau
- 📊 Conserve l'historique complet (IP, connexions, changements)
- 📈 Affiche une timeline des événements
- 🔗 Permet de "promouvoir" des appareils vers Devices

### Différence clé
| 🌐 Network | 📱 Devices |
|-----------|-----------|
| Tous les appareils vus | Sélection manuelle |
| Historique complet | Config + monitoring avancé |
| Read-only (sauf scan) | CRUD complet |
| Base de données réseau | Liste de favoris |

### Workflow utilisateur
```
1. User lance scan réseau
2. Network découvre 15 appareils
3. User voit "PC-GAMER" jamais vu avant
4. User clique "Ajouter aux favoris"
5. Appareil créé dans Devices avec Wake-on-LAN activé
```

---

## 📋 TODO Immédiat

### 1. Créer `src/features/network/schemas.py`
Modèles Pydantic pour :
- `NetworkDevice` : Appareil découvert sur réseau
- `ScanResult` : Résultat d'un scan
- `IPHistoryEntry` : Entrée historique IP
- `NetworkEvent` : Événement réseau
- `NetworkTimeline` : Timeline pour frontend
- `NetworkStats` : Statistiques globales

### 2. Créer `src/features/network/scanner.py`
**NetworkScanner** avec :
```python
class NetworkScanner:
    async def scan_network(
        subnet: str = "192.168.1.0/24",
        scan_type: str = "full"
    ) -> ScanResult
    
    async def _scan_icmp() -> List[str]
    async def _scan_mdns() -> List[Dict]
    async def _scan_arp() -> List[Dict]
    
    async def detect_os(ip: str) -> Optional[str]
    async def detect_vendor(mac: str) -> Optional[str]
    async def identify_device(device_info: Dict) -> Dict
```

**À extraire de `_backup/modules/network/`** :
- `scanner.py` → logique scan nmap
- `mdns_scanner.py` → logique mDNS
- Refactorer en async/await moderne

### 3. Créer `src/features/network/storage.py`
Format v3.0 pour `network_scan_history.json` :
```json
{
  "version": "3.0",
  "updated_at": "2025-10-19T18:00:00Z",
  "scans": [...],
  "devices": {...},
  "events": [...]
}
```

Fonctions :
- `save_scan_result()`
- `load_scan_history()`
- `migrate_old_format()` (backup auto)

### 4. Créer `src/features/network/history.py`
**NetworkHistory** pour :
- Suivre apparitions/disparitions
- Détecter changements IP/MAC
- Générer timeline d'événements
- Calculer statistiques

### 5. Créer `src/features/network/detector.py`
**DeviceDetector** pour :
- Lookup vendor via MAC OUI
- Détection type appareil (PC, mobile, IoT)
- Détection OS (TTL, ports)

### 6. Créer `src/features/network/router.py`
Routes API :
- `POST /api/network/scan`
- `GET /api/network/devices`
- `GET /api/network/history/{mac}`
- `GET /api/network/timeline`
- `POST /api/network/devices/{mac}/promote`
- `GET /api/network/stats`

---

## 🗂️ Fichiers à consulter

### Documentation de référence
1. **[docs/NETWORK_ARCHITECTURE.md](docs/NETWORK_ARCHITECTURE.md)** - Architecture complète Network
2. **[docs/DEVICES_FEATURE.md](docs/DEVICES_FEATURE.md)** - Exemple de feature complète
3. **[RULES.md](RULES.md)** - Règles de développement
4. **[README_V3.md](README_V3.md)** - Vue d'ensemble du projet

### Code de référence
1. **[src/features/devices/](src/features/devices/)** - Exemple de feature bien structurée
2. **[src/core/](src/core/)** - Utiliser config, logging
3. **[src/shared/](src/shared/)** - Utiliser exceptions, utils

### Ancien code (référence uniquement)
1. **[_backup_old_structure/modules/network/](\_backup_old_structure/modules/network/)** - Ancien scanner
2. **Attention** : Ne pas copier-coller, refactorer selon RULES.md

---

## 🎨 Principes à respecter (RULES.md)

### ✅ À FAIRE
- **Type hints** partout
- **Pydantic** pour validation
- **Async/await** pour I/O
- **Logging structuré** avec emojis
- **Docstrings** complètes
- **Format v3.0** pour storage
- **Migration auto** de l'ancien format
- **Backup auto** avant migration
- **Tests** au fur et à mesure

### ❌ À ÉVITER
- Fichiers > 300 lignes
- Code dupliqué
- Magic numbers
- Imports circulaires
- Logique dans les routers (mettre dans services)
- Oublier la documentation

---

## 🔧 Commandes utiles

```bash
# Voir les anciens fichiers network
ls -la _backup_old_structure/modules/network/

# Tester les imports
python3 -c "from src.features.network import NetworkScanner"

# Lancer l'app
python3 app.py

# Tester l'API
curl http://localhost:8000/api/network/scan -X POST | jq .

# Voir les logs
tail -f /tmp/333home.log
```

---

## 🎯 Objectif de la session

**Créer une feature Network complète et fonctionnelle** qui :
1. ✅ Scanne le réseau efficacement
2. ✅ Stocke l'historique au format v3.0
3. ✅ Expose des APIs propres
4. ✅ S'intègre avec Devices
5. ✅ Est testée et validée
6. ✅ Est documentée

**Estimation** : 2-3h pour une implémentation complète

---

## 💡 Tips

1. **Commencer par schemas.py** : Définir les modèles d'abord
2. **Scanner en parallèle** : Utiliser asyncio.gather pour performance
3. **Réutiliser shared/utils.py** : normalize_mac(), is_valid_ip(), etc.
4. **Logger abondamment** : Avec emojis pour lisibilité
5. **Tester au fur et à mesure** : Ne pas attendre la fin
6. **Documenter inline** : Docstrings Python + commentaires

---

## 🚦 État du système

### Application
- ✅ app.py fonctionne
- ✅ Feature Devices opérationnelle
- ✅ API docs : http://localhost:8000/api/docs

### Données
- ✅ `data/devices.json` (format v3.0)
- ✅ Backup créé : `data/devices.json.backup`
- 🔄 `data/network_scan_history.json` (à créer)

### Backup
- ✅ Ancien code dans `_backup_old_structure/`
- ✅ Safe de supprimer après migration complète

---

**Bonne continuation ! 🚀**

*Remember: Quality over speed. Follow RULES.md. Document everything.*
