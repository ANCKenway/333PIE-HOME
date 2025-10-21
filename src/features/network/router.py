"""
🌐 333HOME - Network Router (Main Aggregator)
Agrège tous les sous-routers modulaires

🔧 Architecture modulaire (RULES.md compliant):
- routers/scan_router.py : Scans ON-DEMAND
- routers/device_router.py : Devices & timeline
- routers/latency_router.py : Latence/qualité
- routers/bandwidth_router.py : Bande passante
- dhcp_router.py : DHCP tracking
"""

import logging
from fastapi import APIRouter

from .routers import (
    scan_router,
    device_router,
    latency_router,
    bandwidth_router,
)
from .dhcp_router import router as dhcp_router


logger = logging.getLogger(__name__)

# Router principal
router = APIRouter(prefix="/api/network", tags=["network"])

# Inclure tous les sous-routers
router.include_router(scan_router)
router.include_router(device_router)
router.include_router(latency_router)
router.include_router(bandwidth_router)
router.include_router(dhcp_router)


logger.info("✅ Network router aggregated (modular architecture)")
logger.info("📂 Sub-routers: scan, device, latency, bandwidth, dhcp")
