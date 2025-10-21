"""
📱 333HOME - Devices Schemas
Modèles Pydantic pour validation des données appareils
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime


class DeviceBase(BaseModel):
    """Modèle de base pour un appareil"""
    name: str = Field(..., min_length=1, max_length=100, description="Nom de l'appareil")
    ip: str = Field(..., description="Adresse IP")
    mac: Optional[str] = Field(None, description="Adresse MAC")
    hostname: Optional[str] = Field(None, description="Hostname")
    type: Optional[str] = Field("other", description="Type d'appareil")
    description: Optional[str] = Field(None, max_length=500, description="Description")


class DeviceCreate(DeviceBase):
    """Modèle pour créer un appareil"""
    pass


class DeviceUpdate(BaseModel):
    """Modèle pour mettre à jour un appareil"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    ip: Optional[str] = None
    mac: Optional[str] = None
    hostname: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None


class DeviceResponse(DeviceBase):
    """Modèle de réponse pour un appareil"""
    id: str
    status: str = "unknown"
    online: bool = False
    last_seen: Optional[datetime] = None
    vendor: Optional[str] = None
    
    class Config:
        from_attributes = True


class WakeOnLanRequest(BaseModel):
    """Requête pour Wake-on-LAN"""
    mac: str = Field(..., description="Adresse MAC de l'appareil")
    broadcast: str = Field(default="255.255.255.255", description="Adresse broadcast")
    port: int = Field(default=9, ge=1, le=65535, description="Port WOL")


class DeviceStatusSummary(BaseModel):
    """Résumé du statut des appareils"""
    total: int
    online: int
    offline: int
    unknown: int
    last_update: datetime
