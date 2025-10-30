"""
333HOME - Application FastAPI Moderne
Application de domotique pour Raspberry Pi
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.core import settings, setup_logging, get_logger
from src.features.devices import router as devices_router
from src.features.network import network_router
from src.core.unified import router as hub_router  # ✅ Renommé: hub → unified
from src.features.agents import router as agents_router, ws_router as agents_ws_router  # 🤖 Agents management
# ❌ unified_router supprimé (Phase 4 - redondant avec network_router modulaire)

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("🚀 333HOME - Démarrage")
    logger.info(f"📦 Version: 3.0.0")
    logger.info(f"🌐 Host: {settings.host}:{settings.port}")
    logger.info("=" * 60)
    
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    logger.info("✅ Répertoires OK")
    
    # 🔧 Charger le NetworkRegistry au démarrage (singleton - Phase 6)
    try:
        from src.features.network.registry import get_network_registry, DeviceRegistryEntry
        from src.features.network.routers.registry_router import get_local_mac_address
        from datetime import datetime, UTC
        
        registry = get_network_registry()
        logger.info(f"✅ NetworkRegistry chargé: {len(registry.devices)} devices")
        
        # ✅ Auto-détection du device local (robuste aux changements réseau)
        local_mac = get_local_mac_address()
        if local_mac:
            if local_mac not in registry.devices:
                logger.info(f"🔧 Auto-ajout du device local ({local_mac})")
                now_str = datetime.now(UTC).isoformat()
                registry.devices[local_mac] = DeviceRegistryEntry(
                    mac=local_mac,
                    current_ip="192.168.1.150",  # Sera mis à jour au premier scan
                    current_hostname="333PIE",
                    vendor="Raspberry Pi",
                    os_detected="Linux",
                    device_type="Server",
                    is_online=True,
                    first_seen=now_str,
                    last_seen=now_str,
                    last_seen_online=now_str,
                    total_detections=1,
                    notes="Self-device (auto-detected)",
                    is_managed=True
                )
                registry._save()
                logger.info(f"✅ Device local ajouté au registry (VPN sera enrichi au premier refresh)")
            else:
                logger.info(f"ℹ️  Device local présent ({local_mac})")
        else:
            logger.warning("⚠️  Impossible de détecter MAC locale")
            
    except Exception as e:
        logger.error(f"❌ Erreur chargement NetworkRegistry: {e}")
    
    # ⚠️ MONITORING DÉSACTIVÉ : Scans ON-DEMAND uniquement via API
    # Raison : Éviter perturbations réseau et détection antivirus
    # Utiliser : POST /api/network/scan ou POST /api/network/v2/scan
    logger.info("ℹ️  Network monitoring: ON-DEMAND mode (no auto-scan)")
    
    yield
    
    logger.info("👋 Shutdown gracefully")
    
    logger.info("🛑 333HOME - Arrêt")


def create_app() -> FastAPI:
    app = FastAPI(
        title="333HOME API",
        description="API de domotique",
        version="3.0.0",
        lifespan=lifespan,
        docs_url="/api/docs"
    )
    
    # CORS - Permet WebSocket cross-origin
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Routes API
    app.include_router(devices_router, prefix="/api")
    logger.info("✅ Router devices monté")
    
    app.include_router(network_router)
    logger.info("✅ Router network monté (modulaire: scan, device, latency, bandwidth, dhcp)")
    
    # ❌ unified_router retiré (Phase 4 - redondant)
    
    app.include_router(hub_router, prefix="/api")
    logger.info("✅ Router hub monté")
    
    # Router agents REST (avec /api/agents)
    app.include_router(agents_router)
    logger.info("✅ Router agents REST monté")
    
    # Router agents WebSocket (SANS prefix pour compatibilité)
    app.include_router(agents_ws_router)
    logger.info("✅ Router agents WebSocket monté (/api/ws/agents)")
    
    # Routes spécifiques AVANT StaticFiles
    @app.get("/")
    async def root():
        """Serve the original working interface (index.html)"""
        web_dir = Path(__file__).parent / "web"
        index_file = web_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"error": "Index page not found"}
    
    @app.get("/hub")
    async def hub_page():
        """Serve the HUB unified interface"""
        web_dir = Path(__file__).parent / "web"
        hub_file = web_dir / "hub.html"
        if hub_file.exists():
            return FileResponse(hub_file)
        return {"error": "Hub page not found"}
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": "3.0.0"}
    
    @app.get("/api/info")
    async def app_info():
        return {
            "name": "333HOME",
            "version": "3.0.0",
            "features": ["devices", "network"]
        }
    
    # StaticFiles pour packages agents (AVANT /static pour priorité)
    agents_dir = Path(__file__).parent / "static" / "agents"
    if agents_dir.exists():
        app.mount("/static/agents", StaticFiles(directory=str(agents_dir)), name="agents")
        logger.info(f"✅ Packages agents: {agents_dir}")
    
    # StaticFiles pour assets web uniquement (pas html=True)
    web_dir = Path(__file__).parent / "web"
    if web_dir.exists():
        app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")
        logger.info(f"✅ Fichiers statiques: {web_dir}")
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
