# 🚀 Guide Développeur - Ajouter de Nouvelles Features

**333HOME - Architecture Modulaire**

Ce guide explique comment ajouter facilement de nouvelles features en suivant l'architecture établie.

---

## 📋 Table des Matières

1. [Architecture Overview](#architecture-overview)
2. [Créer une Nouvelle Feature Backend](#backend-feature)
3. [Créer un Nouveau Widget Frontend](#frontend-widget)
4. [Ajouter un Endpoint API](#api-endpoint)
5. [Best Practices](#best-practices)
6. [Exemples Complets](#exemples)

---

## 🏗️ Architecture Overview

### Structure Globale

```
333HOME/
├── src/features/          # Features backend
│   ├── network/          # ✅ Feature Network complète
│   ├── devices/          # ✅ Feature Devices
│   ├── system/           # 🔜 À créer
│   └── tailscale/        # 🔜 À créer
│
├── web/                  # Frontend
│   ├── *.html           # Pages
│   └── static/
│       ├── css/         # Styles
│       └── js/
│           ├── core/    # Core modules
│           └── modules/ # Feature widgets
│
├── docs/                # Documentation
└── tests/               # Tests
```

### Principes

✅ **Feature-based**: Chaque feature = 1 dossier  
✅ **Modularité**: Components indépendants  
✅ **Réutilisabilité**: Core modules partagés  
✅ **RULES.md**: <300 lines par fichier  

---

## 🎯 Backend Feature

### Étape 1: Créer la Structure

```bash
mkdir -p src/features/ma_feature
cd src/features/ma_feature
```

### Étape 2: Créer les Fichiers

#### `__init__.py` - Exports

```python
"""
🎯 333HOME - Ma Feature

Description de la feature
"""

from .schemas import MyModel, MyRequest, MyResponse
from .service import MyService
from .router import router as ma_feature_router

__all__ = [
    "MyModel",
    "MyRequest",
    "MyResponse",
    "MyService",
    "ma_feature_router",
]
```

#### `schemas.py` - Models Pydantic

```python
"""
🎯 333HOME - Ma Feature Schemas

Pydantic models pour validation et sérialisation
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MyModel(BaseModel):
    """Modèle principal"""
    
    id: str = Field(..., description="Unique ID")
    name: str = Field(..., description="Name")
    value: float = Field(..., description="Value")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123",
                "name": "Example",
                "value": 42.0,
            }
        }


class MyRequest(BaseModel):
    """Request model"""
    
    param1: str
    param2: Optional[int] = None


class MyResponse(BaseModel):
    """Response model"""
    
    success: bool
    data: MyModel
    message: str
```

#### `service.py` - Business Logic

```python
"""
🎯 333HOME - Ma Feature Service

Business logic et operations
"""

import logging
from typing import List, Optional
from .schemas import MyModel

logger = logging.getLogger(__name__)


class MyService:
    """
    Service pour gérer Ma Feature
    
    Responsabilités:
    - Business logic
    - Data processing
    - External APIs
    """
    
    def __init__(self):
        """Initialize service"""
        self._data: List[MyModel] = []
        logger.info("MyService initialized")
    
    async def get_all(self) -> List[MyModel]:
        """
        Récupère tous les items
        
        Returns:
            Liste des items
        """
        return self._data
    
    async def get_by_id(self, item_id: str) -> Optional[MyModel]:
        """
        Récupère un item par ID
        
        Args:
            item_id: ID de l'item
            
        Returns:
            Item ou None
        """
        return next((item for item in self._data if item.id == item_id), None)
    
    async def create(self, item: MyModel) -> MyModel:
        """
        Crée un nouvel item
        
        Args:
            item: Item à créer
            
        Returns:
            Item créé
        """
        self._data.append(item)
        logger.info(f"Item created: {item.id}")
        return item
    
    async def update(self, item_id: str, updates: dict) -> Optional[MyModel]:
        """
        Met à jour un item
        
        Args:
            item_id: ID de l'item
            updates: Mises à jour
            
        Returns:
            Item mis à jour ou None
        """
        item = await self.get_by_id(item_id)
        if item:
            for key, value in updates.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            logger.info(f"Item updated: {item_id}")
        return item
    
    async def delete(self, item_id: str) -> bool:
        """
        Supprime un item
        
        Args:
            item_id: ID de l'item
            
        Returns:
            True si supprimé
        """
        item = await self.get_by_id(item_id)
        if item:
            self._data.remove(item)
            logger.info(f"Item deleted: {item_id}")
            return True
        return False


# Singleton
_service: Optional[MyService] = None


def get_my_service() -> MyService:
    """Récupère l'instance singleton du service"""
    global _service
    if _service is None:
        _service = MyService()
    return _service
```

#### `router.py` - API Endpoints

```python
"""
🎯 333HOME - Ma Feature Router

API endpoints FastAPI
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, status

from .schemas import MyModel, MyRequest, MyResponse
from .service import get_my_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ma-feature", tags=["ma_feature"])


@router.get("/items", response_model=List[MyModel])
async def get_items() -> List[MyModel]:
    """
    Liste tous les items
    
    Returns:
        Liste des items
    """
    try:
        service = get_my_service()
        items = await service.get_all()
        return items
    except Exception as e:
        logger.error(f"Error getting items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/items/{item_id}", response_model=MyModel)
async def get_item(item_id: str) -> MyModel:
    """
    Récupère un item par ID
    
    Args:
        item_id: ID de l'item
        
    Returns:
        Item trouvé
    """
    try:
        service = get_my_service()
        item = await service.get_by_id(item_id)
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item not found: {item_id}"
            )
        
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/items", response_model=MyResponse, status_code=status.HTTP_201_CREATED)
async def create_item(request: MyRequest) -> MyResponse:
    """
    Crée un nouvel item
    
    Args:
        request: Données de création
        
    Returns:
        Response avec item créé
    """
    try:
        service = get_my_service()
        
        # Créer item
        item = MyModel(
            id=f"item-{len(await service.get_all()) + 1}",
            name=request.param1,
            value=request.param2 or 0.0,
        )
        
        created = await service.create(item)
        
        return MyResponse(
            success=True,
            data=created,
            message="Item created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: str):
    """
    Supprime un item
    
    Args:
        item_id: ID de l'item
    """
    try:
        service = get_my_service()
        deleted = await service.delete(item_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item not found: {item_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
```

### Étape 3: Intégrer dans `app.py`

```python
# app.py
from src.features.ma_feature import ma_feature_router

app.include_router(ma_feature_router)
logger.info("✅ Router ma_feature monté")
```

---

## 🎨 Frontend Widget

### Étape 1: Créer le Module

#### `web/static/js/modules/my-widget.js`

```javascript
/**
 * 🎯 My Widget
 * 
 * Description du widget
 */

import { Component } from '../core/component.js';
import { APIClient } from '../core/api-client.js';

// API Client pour Ma Feature
class MyFeatureAPI extends APIClient {
    constructor() {
        super();
        this.prefix = '/api/ma-feature';
    }
    
    async getItems() {
        return this.get(`${this.prefix}/items`);
    }
    
    async createItem(data) {
        return this.post(`${this.prefix}/items`, data);
    }
}

const myFeatureAPI = new MyFeatureAPI();


export class MyWidget extends Component {
    constructor(elementId) {
        super(elementId);
        
        this.state = {
            items: [],
            loading: true,
            error: null,
        };
        
        this.refreshInterval = null;
    }
    
    /**
     * Initialize widget
     */
    async init() {
        await this.loadData();
        this.startAutoRefresh();
    }
    
    /**
     * Load data from API
     */
    async loadData() {
        try {
            this.setState({ loading: true, error: null });
            
            const items = await myFeatureAPI.getItems();
            
            this.setState({
                items,
                loading: false,
            });
        } catch (error) {
            console.error('Error loading data:', error);
            this.setState({
                loading: false,
                error: error.message,
            });
        }
    }
    
    /**
     * Start auto-refresh
     */
    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            this.loadData();
        }, 30000); // 30s
    }
    
    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
    
    /**
     * Render widget
     */
    render() {
        if (!this.element) return;
        
        if (this.state.loading) {
            this.showLoading();
            return;
        }
        
        if (this.state.error) {
            this.showError(this.state.error);
            return;
        }
        
        const { items } = this.state;
        
        this.element.innerHTML = `
            <div class="my-widget">
                <h4>🎯 My Widget</h4>
                ${items.length > 0 ? `
                    <div class="items-list">
                        ${items.map(item => this.renderItem(item)).join('')}
                    </div>
                ` : '<p class="empty-state">No items yet</p>'}
            </div>
        `;
        
        this.attachEventHandlers();
    }
    
    /**
     * Render single item
     */
    renderItem(item) {
        return `
            <div class="item-card" data-id="${item.id}">
                <div class="item-name">${item.name}</div>
                <div class="item-value">${item.value}</div>
            </div>
        `;
    }
    
    /**
     * Attach event handlers
     */
    attachEventHandlers() {
        document.querySelectorAll('.item-card').forEach(card => {
            this.addEventListener(card, 'click', () => {
                const id = card.dataset.id;
                this.handleItemClick(id);
            });
        });
    }
    
    /**
     * Handle item click
     */
    handleItemClick(id) {
        console.log('Item clicked:', id);
        // Votre logique ici
    }
    
    /**
     * Cleanup
     */
    destroy() {
        this.stopAutoRefresh();
        super.destroy();
    }
}
```

### Étape 2: Ajouter les Styles

#### `web/static/css/modern.css`

```css
/* === MY WIDGET === */
.my-widget h4 {
    margin-bottom: var(--spacing-md);
    color: var(--text-secondary);
    font-size: 1rem;
}

.items-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.item-card {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: var(--spacing-md);
    cursor: pointer;
    transition: all var(--transition-base);
}

.item-card:hover {
    border-color: var(--accent-primary);
    transform: translateY(-2px);
}

.item-name {
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: var(--spacing-xs);
}

.item-value {
    font-size: 0.875rem;
    color: var(--text-secondary);
}
```

### Étape 3: Intégrer dans Dashboard

```javascript
// Dans votre dashboard principal
import { MyWidget } from './my-widget.js';

class MyDashboard extends Component {
    initWidgets() {
        this.myWidget = new MyWidget('my-widget-id');
        this.myWidget.init();
    }
    
    destroy() {
        if (this.myWidget) {
            this.myWidget.destroy();
        }
        super.destroy();
    }
}
```

```html
<!-- Dans votre HTML -->
<div class="card">
    <div id="my-widget-id"></div>
</div>
```

---

## 🎯 Best Practices

### Backend

✅ **Type Hints**: Toujours utiliser  
✅ **Docstrings**: Pour classes et méthodes  
✅ **Logging**: Logger actions importantes  
✅ **Error Handling**: Try/except avec HTTPException  
✅ **Async/Await**: Pour operations I/O  
✅ **Singleton**: Pour services stateful  
✅ **RULES.md**: <300 lines par fichier  

### Frontend

✅ **Modularité**: 1 widget = 1 fichier  
✅ **Component Base**: Extend Component class  
✅ **State Management**: Use setState()  
✅ **Event Cleanup**: addEventListener() helper  
✅ **Auto-refresh**: Avec cleanup  
✅ **Error Handling**: Try/catch partout  
✅ **JSDoc**: Type hints  

### Général

✅ **Naming**: Clear & consistent  
✅ **Comments**: Why, not what  
✅ **Documentation**: README pour chaque feature  
✅ **Tests**: Valider avant commit  
✅ **Git**: Commits atomic  

---

## 📚 Ressources

### Exemples Complets

- **Network Feature**: `src/features/network/` (référence complète)
- **Frontend**: `web/static/js/modules/network-dashboard.js`
- **Tests**: `test_network_pro.py`

### Documentation

- `docs/NETWORK_COMPLETE_SUMMARY.md` - Vue d'ensemble
- `docs/FRONTEND_ARCHITECTURE_SESSION4.md` - Frontend détaillé
- `RULES.md` - Règles du projet

### Core Modules

- `web/static/js/core/api-client.js` - HTTP client
- `web/static/js/core/component.js` - Base component
- `web/static/css/modern.css` - Design system

---

## 🚀 Quick Start

### Nouvelle Feature Backend

```bash
# 1. Créer structure
mkdir -p src/features/ma_feature
cd src/features/ma_feature

# 2. Créer fichiers (voir templates ci-dessus)
touch __init__.py schemas.py service.py router.py

# 3. Implémenter

# 4. Intégrer dans app.py

# 5. Tester
python3 -c "from src.features.ma_feature import ma_feature_router; print(router.routes)"
```

### Nouveau Widget Frontend

```bash
# 1. Créer module
touch web/static/js/modules/my-widget.js

# 2. Implémenter (voir template ci-dessus)

# 3. Ajouter styles dans modern.css

# 4. Intégrer dans dashboard

# 5. Tester dans browser
```

---

## 💡 Tips

1. **Copier Network Feature** comme template
2. **Réutiliser Core Modules** (api-client, component)
3. **Suivre Naming Conventions** existantes
4. **Documenter en cours** d'implémentation
5. **Tester régulièrement** pendant dev
6. **Demander review** avant merge

---

**Happy Coding! 🚀**

*Architecture modulaire = Features infinies*
