"""
🤖 333HOME Universal Agent
===========================

Agent de contrôle à distance universel cross-platform.
Se connecte au Hub 333HOME via WebSocket persistent.

Fonctionnalités:
- Auto-détection OS (Windows, Linux, macOS)
- Chargement dynamique plugins compatibles
- Communication WebSocket bidirectionnelle
- Heartbeat automatique (30s)
- Reconnexion auto en cas de perte connexion

Usage:
    # Agent Windows (TITO)
    python agent.py --agent-id TITO --hub-url wss://333pie.local:8000/ws/agents
    
    # Agent Linux (333srv)
    python agent.py --agent-id 333srv --hub-url wss://333pie.local:8000/ws/agents
"""

import asyncio
import logging
import platform
import sys
import argparse
import json
from typing import Optional, Dict, Any
from datetime import datetime
import websockets
from websockets.exceptions import ConnectionClosed

from config import AgentConfig, get_default_config
from plugins import PluginManager
from plugins.base import PluginResult
from remote_logging import setup_remote_logging


# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('agent.log')
    ]
)
logger = logging.getLogger(__name__)


class UniversalAgent:
    """
    Agent universel de contrôle à distance.
    
    Se connecte au Hub 333HOME et exécute les tâches via plugins.
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialise l'agent.
        
        Args:
            config: Configuration agent
        """
        self.config = config
        self.plugin_manager = PluginManager(config.os_platform)
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        self.connected = False
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._reconnect_attempts = 0
        self._remote_log_handler = None  # Handler logs remote
    
    async def start(self):
        """Démarre l'agent."""
        logger.info("=" * 70)
        logger.info(f"🤖 333HOME Universal Agent v1.0.0")
        logger.info(f"Agent ID: {self.config.agent_id}")
        logger.info(f"Hostname: {self.config.hostname}")
        logger.info(f"OS Platform: {self.config.os_platform}")
        logger.info(f"Hub URL: {self.config.hub_url}")
        logger.info("=" * 70)
        
        # Charger les plugins
        logger.info("Loading plugins...")
        plugins_count = await self.plugin_manager.load_plugins()
        logger.info(f"✓ {plugins_count} plugins loaded")
        
        if plugins_count == 0:
            logger.warning("⚠️  No plugins loaded - agent will be idle")
        
        # Liste des plugins
        for plugin in self.plugin_manager.list_plugins():
            logger.info(f"  • {plugin['name']} v{plugin['version']} [{plugin['os_platform']}]")
        
        # Setup remote logging
        logger.info("Setting up remote logging...")
        self._remote_log_handler = setup_remote_logging(self, level=logging.DEBUG)
        logger.info("✓ Remote logging enabled - logs will stream to Hub")
        
        self.running = True
        
        # Boucle principale avec reconnexion
        while self.running:
            try:
                await self._connect_and_run()
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                
                if self.running:
                    await self._handle_reconnect()
                else:
                    break
        
        await self.stop()
    
    async def _connect_and_run(self):
        """Se connecte au Hub et écoute les messages."""
        url = self._get_connection_url()
        logger.info(f"Connecting to Hub: {url}")
        
        try:
            async with websockets.connect(
                url,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=5
            ) as websocket:
                self.websocket = websocket
                self.connected = True
                self._reconnect_attempts = 0
                
                logger.info("✓ Connected to Hub")
                
                # Envoyer handshake
                await self._send_handshake()
                
                # Démarrer heartbeat
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                
                # Écouter les messages
                await self._listen_loop()
                
        except ConnectionClosed as e:
            logger.warning(f"Connection closed: {e}")
            self.connected = False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.connected = False
            raise
    
    async def _send_handshake(self):
        """Envoie le message de handshake au Hub."""
        handshake = {
            "type": "handshake",
            "agent_id": self.config.agent_id,
            "hostname": self.config.hostname,
            "os_platform": self.config.os_platform,
            "version": "1.0.0",
            "plugins": [p["name"] for p in self.plugin_manager.list_plugins()],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._send_message(handshake)
        logger.info("✓ Handshake sent")
    
    async def _heartbeat_loop(self):
        """Boucle d'envoi heartbeat."""
        try:
            while self.connected and self.running:
                await asyncio.sleep(self.config.heartbeat_interval)
                
                if self.connected:
                    heartbeat = {
                        "type": "heartbeat",
                        "timestamp": datetime.utcnow().isoformat(),
                        "plugins_loaded": [p["name"] for p in self.plugin_manager.list_plugins()]
                    }
                    await self._send_message(heartbeat)
                    logger.debug("💓 Heartbeat sent")
        except asyncio.CancelledError:
            logger.debug("Heartbeat task cancelled")
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
    
    async def _listen_loop(self):
        """Écoute les messages du Hub."""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}", exc_info=True)
        except ConnectionClosed:
            logger.info("Connection closed by Hub")
    
    async def _handle_message(self, data: Dict[str, Any]):
        """
        Traite un message reçu du Hub.
        
        Args:
            data: Données du message
        """
        msg_type = data.get("type")
        
        if msg_type == "task":
            await self._handle_task(data)
        elif msg_type == "ping":
            await self._send_message({"type": "pong"})
        elif msg_type == "shutdown":
            logger.info("Shutdown requested by Hub")
            self.running = False
        else:
            logger.warning(f"Unknown message type: {msg_type}")
    
    async def _handle_task(self, data: Dict[str, Any]):
        """
        Exécute une tâche plugin.
        
        Args:
            data: Données de la tâche
        """
        task_id = data.get("task_id")
        plugin_name = data.get("plugin")
        params = data.get("params", {})
        
        logger.info(f"📋 Task received: {task_id} (plugin: {plugin_name})")
        
        # Acquitter la tâche
        await self._send_message({
            "type": "task_ack",
            "task_id": task_id
        })
        
        # Récupérer le plugin
        plugin = self.plugin_manager.get_plugin(plugin_name)
        if not plugin:
            logger.error(f"Plugin not found: {plugin_name}")
            await self._send_task_result(task_id, PluginResult(
                status="error",
                error=f"Plugin not found: {plugin_name}"
            ))
            return
        
        if not plugin.enabled:
            logger.error(f"Plugin disabled: {plugin_name}")
            await self._send_task_result(task_id, PluginResult(
                status="error",
                error=f"Plugin disabled: {plugin_name}"
            ))
            return
        
        # Valider les paramètres
        if not plugin.validate_params(params):
            logger.error(f"Invalid params for plugin {plugin_name}")
            await self._send_task_result(task_id, PluginResult(
                status="error",
                error="Invalid parameters"
            ))
            return
        
        # Exécuter le plugin
        try:
            logger.info(f"🚀 Executing plugin: {plugin_name}")
            result = await plugin.execute(plugin.get_schema()["properties"].__class__(**params))
            logger.info(f"✓ Plugin execution completed: {result.status}")
            await self._send_task_result(task_id, result)
        except Exception as e:
            logger.error(f"Plugin execution failed: {e}", exc_info=True)
            await self._send_task_result(task_id, PluginResult(
                status="error",
                error=str(e)
            ))
    
    async def _send_task_result(self, task_id: str, result: PluginResult):
        """Envoie le résultat d'une tâche au Hub."""
        message = {
            "type": "task_result",
            "task_id": task_id,
            **result.dict()
        }
        await self._send_message(message)
    
    async def _send_message(self, data: Dict[str, Any]):
        """Envoie un message au Hub."""
        if self.websocket and self.connected:
            try:
                await self.websocket.send(json.dumps(data))
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                self.connected = False
    
    def _get_connection_url(self) -> str:
        """Construit l'URL de connexion."""
        base_url = self.config.hub_url
        
        # Ajouter agent_id à l'URL
        if "?" in base_url:
            url = f"{base_url}&agent_id={self.config.agent_id}"
        else:
            url = f"{base_url}?agent_id={self.config.agent_id}"
        
        # Ajouter token si disponible
        if self.config.jwt_token:
            url += f"&token={self.config.jwt_token}"
        
        return url
    
    async def _handle_reconnect(self):
        """Gère la reconnexion avec délai exponentiel."""
        self._reconnect_attempts += 1
        
        if self._reconnect_attempts > self.config.max_reconnect_attempts:
            logger.error(f"Max reconnect attempts reached ({self.config.max_reconnect_attempts})")
            self.running = False
            return
        
        delay = min(self.config.reconnect_delay * (2 ** (self._reconnect_attempts - 1)), 60)
        logger.info(f"Reconnecting in {delay}s (attempt {self._reconnect_attempts}/{self.config.max_reconnect_attempts})...")
        await asyncio.sleep(delay)
    
    async def stop(self):
        """Arrête l'agent."""
        logger.info("Stopping agent...")
        self.running = False
        self.connected = False
        
        # Annuler heartbeat
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Fermer WebSocket
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.error(f"Error closing websocket: {e}")
        
        # Décharger plugins
        await self.plugin_manager.unload_plugins()
        
        logger.info("✓ Agent stopped")


async def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(description="333HOME Universal Agent")
    parser.add_argument("--agent-id", help="Agent ID (ex: TITO, 333srv)")
    parser.add_argument("--hub-url", help="Hub WebSocket URL")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Load config
    if args.config:
        # TODO: Load from file
        config = get_default_config()
    else:
        config = get_default_config()
    
    # Override with CLI args
    if args.agent_id:
        config.agent_id = args.agent_id
    if args.hub_url:
        config.hub_url = args.hub_url
    
    # Start agent
    agent = UniversalAgent(config)
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        await agent.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Exiting...")
        sys.exit(0)
