"""
🔧 333HOME - Module Shared
Code partagé: exceptions, utilitaires, constantes
"""

from .exceptions import (
    HomeException,
    ConfigurationError,
    ServiceError,
    DeviceError,
    NetworkError,
    ScanError,
    StorageError,
    ValidationError,
    IntegrationError,
    DeviceNotFoundError,
    UnauthorizedError,
    RateLimitError
)

from .utils import (
    is_valid_ip,
    is_valid_mac,
    normalize_mac,
    get_hostname,
    get_local_ip,
    format_bytes,
    format_duration,
    time_ago,
    generate_id,
    safe_json_loads,
    safe_json_dumps
)

from .constants import (
    DeviceStatus,
    DeviceType,
    NetworkEventType,
    ScanType,
    EMOJIS,
    ERROR_MESSAGES
)

__all__ = [
    # Exceptions
    "HomeException",
    "ConfigurationError",
    "ServiceError",
    "DeviceError",
    "NetworkError",
    "ScanError",
    "StorageError",
    "ValidationError",
    "IntegrationError",
    "DeviceNotFoundError",
    "UnauthorizedError",
    "RateLimitError",
    # Utils
    "is_valid_ip",
    "is_valid_mac",
    "normalize_mac",
    "get_hostname",
    "get_local_ip",
    "format_bytes",
    "format_duration",
    "time_ago",
    "generate_id",
    "safe_json_loads",
    "safe_json_dumps",
    # Constants
    "DeviceStatus",
    "DeviceType",
    "NetworkEventType",
    "ScanType",
    "EMOJIS",
    "ERROR_MESSAGES"
]
