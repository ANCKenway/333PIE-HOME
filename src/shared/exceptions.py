"""
⚠️ 333HOME - Exceptions personnalisées
Hiérarchie d'exceptions pour une gestion d'erreurs propre
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class HomeException(Exception):
    """Exception de base pour 333HOME"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(HomeException):
    """Erreur de configuration"""
    pass


class ServiceError(HomeException):
    """Erreur générique de service"""
    pass


class DeviceError(HomeException):
    """Erreur liée aux appareils"""
    pass


class NetworkError(HomeException):
    """Erreur réseau"""
    pass


class ScanError(NetworkError):
    """Erreur lors d'un scan réseau"""
    pass


class StorageError(HomeException):
    """Erreur de stockage/persistence"""
    pass


class ValidationError(HomeException):
    """Erreur de validation de données"""
    pass


class IntegrationError(HomeException):
    """Erreur d'intégration avec service externe (Tailscale, 333srv)"""
    pass


# Conversions vers HTTPException FastAPI

def to_http_exception(error: HomeException, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR) -> HTTPException:
    """Convertir une HomeException en HTTPException FastAPI"""
    return HTTPException(
        status_code=status_code,
        detail={
            "error": error.__class__.__name__,
            "message": error.message,
            "details": error.details
        }
    )


class DeviceNotFoundError(DeviceError):
    """Appareil non trouvé"""
    
    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "DeviceNotFound", "message": self.message}
        )


class UnauthorizedError(HomeException):
    """Erreur d'authentification/autorisation"""
    
    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Unauthorized", "message": self.message}
        )


class RateLimitError(HomeException):
    """Trop de requêtes"""
    
    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "RateLimitExceeded", "message": self.message}
        )
