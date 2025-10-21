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
from src.features.hub import router as hub_router
from src.api.unified_router import router as unified_router

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
    logger.info("✅ Router network monté (legacy)")
    
    app.include_router(unified_router)
    logger.info("✅ Router network unified monté")
    
    app.include_router(hub_router, prefix="/api")
    logger.info("✅ Router hub monté")
    
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
    
    # StaticFiles pour assets uniquement (pas html=True)
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
