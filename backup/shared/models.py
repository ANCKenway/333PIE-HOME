"""
Modèles partagés pour 333HOME
"""

class DeviceStatus:
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"

class Computer:
    def __init__(self, name="", ip="", mac="", description=""):
        self.name = name
        self.ip = ip
        self.mac = mac
        self.description = description
        self.status = DeviceStatus.UNKNOWN

class APIResponse:
    def __init__(self, success=True, data=None, message="", error=None):
        self.success = success
        self.data = data or {}
        self.message = message
        self.error = error