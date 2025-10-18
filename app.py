"""
🏠 Home Automation v3.0 - Application principale
Version propre et organisée
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

# Import des modules d'API
from src.api.devices import router as devices_router
from src.api.network import router as network_router

# Application FastAPI
app = FastAPI(
    title="Home Automation",
    description="Système de domotique pour Raspberry Pi",
    version="3.0.0"
)

# Fichiers statiques
app.mount("/web/static", StaticFiles(directory="web/static"), name="static")
app.mount("/css", StaticFiles(directory="web/static/css"), name="css")
app.mount("/js", StaticFiles(directory="web/static/js"), name="js")

# Routeurs API
app.include_router(devices_router, prefix="/api/devices", tags=["devices"])
app.include_router(network_router, prefix="/api/network", tags=["network"])

@app.get("/")
async def dashboard():
    """Page d'accueil - Dashboard principal"""
    return FileResponse("web/templates/index.html")

@app.get("/favicon.ico")
async def favicon():
    """Favicon simple pour éviter les erreurs 404"""
    return {"message": "No favicon"}

if __name__ == "__main__":
    print("🏠 Home Automation v3.0")
    print("🌐 Dashboard: http://localhost:8000")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )