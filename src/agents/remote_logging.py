"""
📡 Remote Logging - Streaming logs vers Hub
============================================

Handler logging custom qui envoie les logs via WebSocket au Hub en temps réel.

Fonctionnalités:
- Streaming logs temps réel vers Hub
- Buffer en cas de déconnexion
- Niveaux configurables (DEBUG, INFO, WARNING, ERROR)
- Formatage structuré (JSON)
"""

import logging
import json
import asyncio
from typing import Optional
from datetime import datetime
from collections import deque


class RemoteLogHandler(logging.Handler):
    """
    Handler logging qui envoie les logs au Hub via WebSocket.
    
    Usage:
        remote_handler = RemoteLogHandler(agent)
        logging.getLogger().addHandler(remote_handler)
    """
    
    def __init__(self, agent, buffer_size: int = 1000):
        """
        Initialise le handler.
        
        Args:
            agent: Instance UniversalAgent (pour accès WebSocket)
            buffer_size: Taille max buffer (logs en attente si déconnecté)
        """
        super().__init__()
        self.agent = agent
        self.buffer = deque(maxlen=buffer_size)
        self._send_task: Optional[asyncio.Task] = None
        self._running = False
    
    def emit(self, record: logging.LogRecord):
        """
        Appelé quand un log est émis.
        
        Args:
            record: Log record
        """
        try:
            # Formater le log
            log_entry = self._format_log(record)
            
            # Ajouter au buffer
            self.buffer.append(log_entry)
            
            # Envoyer si connecté
            if self.agent.connected and not self._send_task:
                self._send_task = asyncio.create_task(self._send_logs())
        
        except Exception as e:
            # Ne pas propager les erreurs du handler
            self.handleError(record)
    
    def _format_log(self, record: logging.LogRecord) -> dict:
        """
        Formate un log record en JSON.
        
        Args:
            record: Log record
        
        Returns:
            Log formaté en dict
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": self.format(record),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process
        }
    
    async def _send_logs(self):
        """Envoie les logs bufferisés au Hub."""
        try:
            while self.buffer and self.agent.connected:
                # Prendre batch de logs
                batch = []
                while self.buffer and len(batch) < 10:
                    batch.append(self.buffer.popleft())
                
                # Envoyer au Hub
                await self.agent._send_message({
                    "type": "logs",
                    "logs": batch
                })
                
                # Petit délai pour éviter spam
                await asyncio.sleep(0.1)
        
        except Exception as e:
            logging.error(f"Failed to send logs: {e}")
        
        finally:
            self._send_task = None
    
    def start(self):
        """Démarre le handler."""
        self._running = True
    
    def stop(self):
        """Arrête le handler."""
        self._running = False
        if self._send_task:
            self._send_task.cancel()


def setup_remote_logging(agent, level: int = logging.INFO) -> RemoteLogHandler:
    """
    Configure le logging remote pour un agent.
    
    Args:
        agent: Instance UniversalAgent
        level: Niveau de log (logging.DEBUG, INFO, etc.)
    
    Returns:
        Handler configuré
    """
    # Créer handler
    remote_handler = RemoteLogHandler(agent)
    remote_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    remote_handler.setFormatter(formatter)
    
    # Ajouter au logger root
    logging.getLogger().addHandler(remote_handler)
    
    remote_handler.start()
    return remote_handler
