# 📦 src/ - Code Source 333HOME v3.0

Architecture moderne feature-based pour 333HOME.

---

## 📁 Structure

```
src/
├── core/           # Cœur de l'application
├── features/       # Features métier (domain-driven)
├── shared/         # Code partagé
└── api/            # Configuration API et routage
```

---

## 🔥 core/ - Cœur de l'Application

**Responsabilité**: Configuration, logging, lifecycle

### Modules

#### `config.py`
Configuration centralisée avec **Pydantic Settings**.

```python
from src.core import settings

# Accès aux paramètres
print(settings.app_name)      # "333HOME"
print(settings.port)          # 8000
print(settings.data_dir)      # Path("/home/pie333/333HOME/data")
```

**Features**:
- ✅ Variables d'environnement (`.env`)
- ✅ Validation automatique des types
- ✅ Valeurs par défaut
- ✅ Documentation intégrée

#### `logging_config.py`
Système de logging moderne avec couleurs.

```python
from src.core import setup_logging, get_logger

# Configuration
setup_logging(level="INFO", colorize=True)

# Utilisation
logger = get_logger(__name__)
logger.info("Message info")
logger.error("Message erreur")
```

**Features**:
- ✅ Couleurs dans le terminal
- ✅ Formatage configurable
- ✅ Sortie fichier optionnelle
- ✅ Context managers pour tracer les opérations

#### `lifespan.py`
Gestion moderne du cycle de vie FastAPI.

```python
from src.core import lifespan, on_startup, on_shutdown

# Dans app.py
app = FastAPI(lifespan=lifespan)

# Enregistrer des tâches
@on_startup("mon_service")
def init_service():
    print("Service initialisé")
```

**Features**:
- ✅ Remplace `@app.on_event` (déprécié)
- ✅ Gestion centralisée des services
- ✅ Logging automatique
- ✅ Gestion d'erreurs robuste

---

## 🎨 features/ - Features Métier

**Responsabilité**: Logique métier organisée par domaine

### Structure d'une Feature

Chaque feature suit ce pattern:

```
features/nom_feature/
├── __init__.py
├── manager.py      # Logique métier
├── router.py       # Routes API
├── schemas.py      # Modèles Pydantic
└── service.py      # Services (optionnel)
```

### Features Prévues

- **devices/** - Gestion des appareils
- **network/** - Scan et analyse réseau
- **tailscale/** - Intégration VPN
- **monitoring/** - Surveillance système
- **system/** - Administration système

---

## 🔧 shared/ - Code Partagé

**Responsabilité**: Utilitaires, exceptions, constantes

### Modules

#### `exceptions.py`
Hiérarchie d'exceptions personnalisées.

```python
from src.shared import DeviceError, NetworkError

# Utilisation
if not device:
    raise DeviceError("Appareil non trouvé", details={"id": device_id})
```

**Exceptions disponibles**:
- `HomeException` - Base
- `ConfigurationError`
- `ServiceError`
- `DeviceError`
- `NetworkError`
- `ScanError`
- `StorageError`
- `ValidationError`
- `IntegrationError`

#### `utils.py`
Fonctions utilitaires réutilisables.

```python
from src.shared import is_valid_ip, normalize_mac, format_bytes

# Validation
is_valid_ip("192.168.1.1")  # True

# Formatage
normalize_mac("aa:bb:cc:dd:ee:ff")  # "AA:BB:CC:DD:EE:FF"
format_bytes(1024)  # "1.00 KB"
time_ago(timestamp)  # "il y a 5min"
```

**Utilitaires disponibles**:
- Validation (IP, MAC)
- Formatage (bytes, durée, datetime)
- Génération d'IDs
- JSON safe
- Manipulation dictionnaires
- Et plus...

#### `constants.py`
Constantes et Enums.

```python
from src.shared import DeviceStatus, DeviceType, EMOJIS

# Enums
status = DeviceStatus.ONLINE
type_ = DeviceType.COMPUTER

# Constantes
print(EMOJIS["success"])  # "✅"
```

**Constantes disponibles**:
- Enums (Status, Types, Events)
- Timeouts
- Limites
- Paths API
- Messages d'erreur
- Emojis
- Patterns de détection

---

## 🌐 api/ - Configuration API

**Responsabilité**: Routage et configuration API globale

### Structure

```
api/
├── __init__.py
├── router.py       # Router principal qui combine tous les sous-routers
└── middleware.py   # Middlewares custom (optionnel)
```

### Usage

```python
from src.api import main_router

app.include_router(main_router)
```

---

## 🚀 Utilisation

### Import Simple

```python
# Core
from src.core import settings, get_logger, lifespan

# Shared
from src.shared import DeviceStatus, is_valid_ip, EMOJIS

# Features (après migration)
from src.features.devices import DeviceManager
from src.features.network import NetworkScanner
```

### Créer une Nouvelle Feature

1. **Créer la structure**:
```bash
mkdir -p src/features/ma_feature
touch src/features/ma_feature/{__init__.py,manager.py,router.py,schemas.py}
```

2. **Implémenter le manager** (`manager.py`):
```python
from src.core import get_logger
from src.shared import ServiceError

logger = get_logger(__name__)

class MaFeatureManager:
    def __init__(self):
        logger.info("Manager initialisé")
    
    def do_something(self):
        try:
            # Logique métier
            pass
        except Exception as e:
            raise ServiceError(f"Erreur: {e}")
```

3. **Créer les routes** (`router.py`):
```python
from fastapi import APIRouter, Depends
from src.shared import EMOJIS

router = APIRouter(prefix="/api/ma-feature", tags=["ma-feature"])

@router.get("/")
async def get_data():
    return {"message": f"{EMOJIS['success']} Ça fonctionne !"}
```

4. **Exporter** (`__init__.py`):
```python
from .manager import MaFeatureManager
from .router import router

__all__ = ["MaFeatureManager", "router"]
```

5. **Intégrer dans l'app**:
```python
from src.features.ma_feature import router as ma_feature_router

app.include_router(ma_feature_router)
```

---

## ✅ Avantages de cette Architecture

1. **Modulaire** - Chaque feature est isolée
2. **Testable** - Tests unitaires faciles
3. **Scalable** - Ajouter des features sans impact
4. **Maintenable** - Code organisé logiquement
5. **Type-safe** - Type hints partout
6. **Moderne** - Best practices Python 2025

---

## 📚 Documentation

- Configuration: `src/core/config.py`
- Logging: `src/core/logging_config.py`
- Exceptions: `src/shared/exceptions.py`
- Utils: `src/shared/utils.py`

---

**Version**: 3.0.0  
**Status**: 🚧 En construction active  
**Qualité**: ⭐⭐⭐⭐⭐
