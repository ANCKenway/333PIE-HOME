# 📱 Feature Devices - Documentation

## Vue d'ensemble

La feature **devices** gère l'ensemble du cycle de vie des appareils du réseau : création, modification, suppression, monitoring en temps réel, et Wake-on-LAN.

## Architecture

```
src/features/devices/
├── __init__.py         # Exports publics
├── schemas.py          # Modèles Pydantic (validation)
├── manager.py          # Gestionnaire CRUD + stockage
├── monitor.py          # Monitoring (ping, statut)
├── wol.py              # Service Wake-on-LAN
├── router.py           # Routes API FastAPI
└── storage.py          # Format de données + migration
```

## Format de données (v3.0)

### Structure du fichier `data/devices.json`

```json
{
  "version": "3.0",
  "updated_at": "2025-10-19T17:00:00Z",
  "devices": [
    {
      "id": "dev_rpi_d83add123456",
      "name": "Raspberry Pi 5",
      "ip": "192.168.1.150",
      "mac": "d8:3a:dd:12:34:56",
      "hostname": "raspberrypi.local",
      "type": "serveur",
      "description": "Serveur domotique principal",
      "tags": ["production", "linux", "arm64"],
      "metadata": {
        "os": "Raspberry Pi OS",
        "vendor": "Raspberry Pi Foundation",
        "wol_enabled": false
      },
      "created_at": "2025-10-19T10:00:00Z",
      "updated_at": "2025-10-19T17:00:00Z"
    }
  ]
}
```

### Champs obligatoires
- `id`: Identifiant unique (généré automatiquement)
- `name`: Nom de l'appareil
- `ip`: Adresse IP principale

### Champs optionnels
- `mac`: Adresse MAC (requis pour Wake-on-LAN)
- `hostname`: Nom d'hôte
- `type`: Type d'appareil (pc, serveur, iot, etc.)
- `description`: Description libre
- `tags`: Array de tags pour catégorisation
- `metadata`: Objet JSON extensible (OS, vendor, etc.)
- `created_at`: Date de création (ISO 8601)
- `updated_at`: Date de dernière modification (ISO 8601)

## Migration automatique

Le `DeviceManager` détecte automatiquement l'ancien format et migre vers v3.0 :

1. **Détection** : Vérification du champ `version`
2. **Backup** : Création automatique d'un fichier `.backup`
3. **Migration** : Conversion des données vers le nouveau format
4. **Enrichissement** : Génération automatique des tags

### Formats supportés pour migration
- Liste directe : `[{...}, {...}]`
- Ancien dict : `{"devices": [...]}`
- Format avec ancienne version

## API Endpoints

### GET `/api/devices/`
Liste tous les appareils.

**Query params:**
- `check_status` (bool): Si true, vérifie le statut online/offline

**Response:** `List[DeviceResponse]`

```json
[
  {
    "id": "dev_xxx",
    "name": "Mon PC",
    "ip": "192.168.1.100",
    "status": "online",
    "online": true,
    ...
  }
]
```

### GET `/api/devices/summary`
Résumé du statut de tous les appareils.

**Response:** `DeviceStatusSummary`

```json
{
  "total": 10,
  "online": 7,
  "offline": 2,
  "unknown": 1,
  "last_update": "2025-10-19T17:00:00Z"
}
```

### GET `/api/devices/{device_id}`
Récupère un appareil par son ID.

**Path params:**
- `device_id` (str): ID de l'appareil

**Query params:**
- `check_status` (bool): Si true, vérifie le statut

**Response:** `DeviceResponse`

### POST `/api/devices/`
Crée un nouvel appareil.

**Body:** `DeviceCreate`

```json
{
  "name": "Mon Nouveau PC",
  "ip": "192.168.1.200",
  "mac": "aa:bb:cc:dd:ee:ff",
  "type": "pc",
  "description": "PC de bureau"
}
```

**Response:** `DeviceResponse` (201 Created)

### PATCH `/api/devices/{device_id}`
Met à jour un appareil existant.

**Body:** `DeviceUpdate` (tous les champs optionnels)

```json
{
  "name": "Nouveau nom",
  "description": "Nouvelle description"
}
```

**Response:** `DeviceResponse`

### DELETE `/api/devices/{device_id}`
Supprime un appareil.

**Response:** 204 No Content

### POST `/api/devices/{device_id}/wake`
Réveille un appareil via Wake-on-LAN.

**Prérequis:** L'appareil doit avoir une adresse MAC configurée.

**Response:**
```json
{
  "message": "Magic packet envoyé avec succès",
  "device_id": "dev_xxx",
  "mac": "aa:bb:cc:dd:ee:ff"
}
```

### POST `/api/devices/wake`
Envoie un magic packet WOL personnalisé (sans avoir configuré l'appareil).

**Body:** `WakeOnLanRequest`

```json
{
  "mac": "aa:bb:cc:dd:ee:ff",
  "broadcast": "255.255.255.255",
  "port": 9
}
```

### POST `/api/devices/{device_id}/ping`
Ping un appareil pour vérifier sa connectivité.

**Response:**
```json
{
  "device_id": "dev_xxx",
  "ip": "192.168.1.100",
  "online": true,
  "status": "online"
}
```

## Utilisation programmatique

### Créer un appareil
```python
from src.features.devices import DeviceManager

manager = DeviceManager()
device = manager.create_device({
    "name": "Mon PC",
    "ip": "192.168.1.100",
    "mac": "aa:bb:cc:dd:ee:ff",
    "type": "pc"
})
```

### Vérifier le statut
```python
from src.features.devices import DeviceMonitor

monitor = DeviceMonitor()
online = await monitor.ping("192.168.1.100")
```

### Wake-on-LAN
```python
from src.features.devices import WakeOnLanService

wol = WakeOnLanService()
await wol.wake("aa:bb:cc:dd:ee:ff")
```

## Tests

```bash
# Tester la migration
python3 -c "from src.features.devices import DeviceManager; DeviceManager()"

# Tester l'API
curl http://localhost:8000/api/devices/

# Tester le summary
curl http://localhost:8000/api/devices/summary

# Créer un appareil
curl -X POST http://localhost:8000/api/devices/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","ip":"192.168.1.1"}'
```

## Évolutions futures

- [ ] Support de groupes d'appareils
- [ ] Historique des changements de statut
- [ ] Notifications sur changement d'état
- [ ] API GraphQL en complément
- [ ] Export/Import des configurations
- [ ] Templates d'appareils prédéfinis
