"""
🔄 333HOME - Gestion du cycle de vie de l'application
Lifespan events moderne pour FastAPI (remplace @app.on_event)
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI

logger = logging.getLogger(__name__)


class AppLifespan:
    """Gestionnaire du cycle de vie de l'application"""
    
    def __init__(self):
        self.services = []
        self.startup_tasks = []
        self.shutdown_tasks = []
    
    def register_service(self, service, name: str):
        """Enregistrer un service à gérer"""
        self.services.append((service, name))
    
    def add_startup_task(self, task, name: str):
        """Ajouter une tâche de démarrage"""
        self.startup_tasks.append((task, name))
    
    def add_shutdown_task(self, task, name: str):
        """Ajouter une tâche d'arrêt"""
        self.shutdown_tasks.append((task, name))
    
    async def startup(self):
        """Exécuter les tâches de démarrage"""
        logger.info("🚀 333HOME - Démarrage de l'application")
        logger.info("=" * 60)
        
        # 🔧 Charger le NetworkRegistry au démarrage (singleton)
        try:
            from src.features.network.registry import get_network_registry
            registry = get_network_registry()
            logger.info(f"✅ NetworkRegistry chargé: {len(registry.devices)} devices")
        except Exception as e:
            logger.error(f"❌ Erreur chargement NetworkRegistry: {e}")
        
        # Exécuter les tâches de démarrage personnalisées
        for task, name in self.startup_tasks:
            try:
                logger.info(f"▶️ Démarrage: {name}")
                if callable(task):
                    await task() if hasattr(task, '__await__') else task()
                logger.info(f"✅ {name} - OK")
            except Exception as e:
                logger.error(f"❌ Erreur démarrage {name}: {e}")
        
        # Initialiser les services
        for service, name in self.services:
            try:
                if hasattr(service, 'initialize'):
                    logger.info(f"🔧 Initialisation service: {name}")
                    await service.initialize() if hasattr(service.initialize, '__await__') else service.initialize()
                    logger.info(f"✅ Service {name} initialisé")
            except Exception as e:
                logger.error(f"❌ Erreur initialisation {name}: {e}")
        
        logger.info("=" * 60)
        logger.info("✅ Application 333HOME prête !")
        logger.info(f"🌐 Interface web: http://0.0.0.0:8000")
        logger.info(f"📚 Documentation API: http://0.0.0.0:8000/docs")
        logger.info("=" * 60)
    
    async def shutdown(self):
        """Exécuter les tâches d'arrêt"""
        logger.info("🔴 333HOME - Arrêt de l'application")
        logger.info("=" * 60)
        
        # Arrêter les services dans l'ordre inverse
        for service, name in reversed(self.services):
            try:
                if hasattr(service, 'shutdown'):
                    logger.info(f"⏹️ Arrêt service: {name}")
                    await service.shutdown() if hasattr(service.shutdown, '__await__') else service.shutdown()
                    logger.info(f"✅ Service {name} arrêté")
            except Exception as e:
                logger.error(f"❌ Erreur arrêt {name}: {e}")
        
        # Exécuter les tâches d'arrêt personnalisées
        for task, name in self.shutdown_tasks:
            try:
                logger.info(f"⏹️ Exécution tâche d'arrêt: {name}")
                if callable(task):
                    await task() if hasattr(task, '__await__') else task()
                logger.info(f"✅ {name} - OK")
            except Exception as e:
                logger.error(f"❌ Erreur tâche d'arrêt {name}: {e}")
        
        logger.info("=" * 60)
        logger.info("✅ Arrêt propre de l'application")


# Instance globale du gestionnaire de lifecycle
app_lifespan = AppLifespan()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Context manager pour le cycle de vie de FastAPI
    
    Usage dans app.py:
        app = FastAPI(lifespan=lifespan)
    """
    # Startup
    await app_lifespan.startup()
    
    yield
    
    # Shutdown
    await app_lifespan.shutdown()


def get_lifespan():
    """Obtenir l'instance du gestionnaire de lifecycle"""
    return app_lifespan


# Décorateurs pour enregistrer facilement des tâches
def on_startup(name: str):
    """Décorateur pour enregistrer une tâche de démarrage"""
    def decorator(func):
        app_lifespan.add_startup_task(func, name)
        return func
    return decorator


def on_shutdown(name: str):
    """Décorateur pour enregistrer une tâche d'arrêt"""
    def decorator(func):
        app_lifespan.add_shutdown_task(func, name)
        return func
    return decorator
