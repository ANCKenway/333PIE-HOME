"""
333HOME API - Agents Management
================================

Endpoints pour gérer les agents de contrôle à distance.

Routes:
    WebSocket:
        - GET /ws/agents: Connexion WebSocket agents
    
    REST:
        - GET /api/agents: Liste agents connectés
        - POST /api/agents/{agent_id}/tasks: Envoyer tâche à un agent
        - GET /api/agents/{agent_id}/plugins: Liste plugins agent
        - GET /api/agents/{agent_id}/status: Statut agent
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any, Literal
from datetime import datetime, timezone
import logging
import json
import asyncio
import uuid
from pathlib import Path


logger = logging.getLogger(__name__)

# Router principal (REST endpoints avec /api/agents)
router = APIRouter(prefix="/api/agents", tags=["agents"])

# Router WebSocket séparé (SANS prefix pour compatibilité FastAPI)
ws_router = APIRouter(tags=["agents-websocket"])


# ============================================================================
# MODELS
# ============================================================================

class TaskRequest(BaseModel):
    """Requête de création de tâche."""
    plugin: str = Field(..., description="Nom du plugin à exécuter")
    params: Dict[str, Any] = Field(default_factory=dict, description="Paramètres plugin")
    timeout: int = Field(default=120, ge=10, le=600, description="Timeout (secondes)")


class TaskResponse(BaseModel):
    """Réponse création tâche."""
    task_id: str
    agent_id: str
    plugin: str
    status: Literal["pending", "acknowledged", "running", "completed", "error", "timeout"]
    created_at: str
    message: str


class AgentInfo(BaseModel):
    """Informations agent."""
    agent_id: str
    hostname: str
    os_platform: str
    version: str
    connected: bool
    plugins: List[str]
    last_heartbeat: Optional[str]
    connected_at: Optional[str]


# ============================================================================
# AGENT MANAGER (In-memory storage)
# ============================================================================

class AgentConnection:
    """Représente une connexion agent active."""
    
    def __init__(
        self,
        agent_id: str,
        websocket: WebSocket,
        metadata: Dict[str, Any]
    ):
        self.agent_id = agent_id
        self.websocket = websocket
        self.metadata = metadata
        self.connected_at = datetime.now(timezone.utc)
        self.last_heartbeat = datetime.now(timezone.utc)
        self.plugins: List[str] = metadata.get("plugins", [])
        self.pending_tasks: Dict[str, Dict] = {}
        self.logs: List[Dict] = []  # Buffer logs (max 100 derniers)
        self._max_logs = 100
    
    async def send(self, data: Dict[str, Any]):
        """Envoie un message à l'agent."""
        try:
            await self.websocket.send_text(json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to send message to {self.agent_id}: {e}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dict."""
        return {
            "agent_id": self.agent_id,
            "hostname": self.metadata.get("hostname", "unknown"),
            "os_platform": self.metadata.get("os_platform", "unknown"),
            "version": self.metadata.get("version", "unknown"),
            "connected": True,
            "plugins": self.plugins,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "connected_at": self.connected_at.isoformat(),
            "logs_count": len(self.logs)
        }
    
    def add_logs(self, logs: List[Dict]):
        """Ajoute des logs au buffer."""
        self.logs.extend(logs)
        # Garder seulement les N derniers
        if len(self.logs) > self._max_logs:
            self.logs = self.logs[-self._max_logs:]


class AgentManager:
    """Gestionnaire d'agents connectés."""
    
    def __init__(self):
        self.connections: Dict[str, AgentConnection] = {}
        self.tasks: Dict[str, Dict] = {}
    
    def register(self, agent_id: str, websocket: WebSocket, metadata: Dict) -> AgentConnection:
        """Enregistre un agent."""
        if agent_id in self.connections:
            logger.warning(f"Agent {agent_id} already connected, replacing connection")
        
        connection = AgentConnection(agent_id, websocket, metadata)
        self.connections[agent_id] = connection
        logger.info(f"✓ Agent registered: {agent_id} ({metadata.get('os_platform')})")
        return connection
    
    def unregister(self, agent_id: str):
        """Désenregistre un agent."""
        if agent_id in self.connections:
            del self.connections[agent_id]
            logger.info(f"Agent unregistered: {agent_id}")
    
    def get_connection(self, agent_id: str) -> Optional[AgentConnection]:
        """Récupère une connexion agent."""
        return self.connections.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """Liste tous les agents."""
        return [conn.to_dict() for conn in self.connections.values()]
    
    def update_heartbeat(self, agent_id: str):
        """Met à jour le heartbeat d'un agent."""
        conn = self.get_connection(agent_id)
        if conn:
            conn.last_heartbeat = datetime.now(timezone.utc)
    
    async def send_task(
        self,
        agent_id: str,
        plugin: str,
        params: Dict[str, Any],
        timeout: int = 120
    ) -> str:
        """
        Envoie une tâche à un agent.
        
        Returns:
            task_id
        """
        conn = self.get_connection(agent_id)
        if not conn:
            raise ValueError(f"Agent {agent_id} not connected")
        
        task_id = str(uuid.uuid4())
        
        task_data = {
            "task_id": task_id,
            "agent_id": agent_id,
            "plugin": plugin,
            "params": params,
            "timeout": timeout,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "result": None
        }
        
        self.tasks[task_id] = task_data
        conn.pending_tasks[task_id] = task_data
        
        # Envoyer au agent
        await conn.send({
            "type": "task",
            "task_id": task_id,
            "plugin": plugin,
            "params": params
        })
        
        logger.info(f"Task {task_id} sent to agent {agent_id} (plugin: {plugin})")
        return task_id
    
    def update_task_status(
        self,
        task_id: str,
        status: str,
        result: Optional[Dict] = None
    ):
        """Met à jour le statut d'une tâche."""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            if result:
                self.tasks[task_id]["result"] = result
            self.tasks[task_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Récupère une tâche."""
        return self.tasks.get(task_id)


# Instance globale
agent_manager = AgentManager()


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@ws_router.websocket("/api/ws/agents")
async def websocket_agent_endpoint(websocket: WebSocket):
    """
    Endpoint WebSocket pour connexion agents.
    
    Protocol:
        1. Handshake: Agent envoie {"type": "handshake", "agent_id": "...", ...}
        2. Heartbeat: Agent envoie {"type": "heartbeat"} toutes les 30s
        3. Tasks: Hub envoie {"type": "task", "task_id": "...", "plugin": "...", ...}
        4. Results: Agent envoie {"type": "task_result", "task_id": "...", "status": "...", ...}
    """
    # IMPORTANT: Accept FIRST, then validate
    await websocket.accept()
    logger.info(f"🔌 WebSocket connection accepted from {websocket.client}")
    
    # Extract agent_id from query params AFTER accept
    agent_id = websocket.query_params.get("agent_id")
    logger.info(f"🔍 Query params: {dict(websocket.query_params)}")
    
    if not agent_id:
        logger.error("❌ Missing agent_id in query params")
        await websocket.close(code=1008, reason="Missing agent_id query parameter")
        return
    
    logger.info(f"✅ Agent ID validated: {agent_id}")
    
    connection: Optional[AgentConnection] = None
    
    try:
        # Attendre handshake
        handshake_data = await asyncio.wait_for(websocket.receive_text(), timeout=10)
        handshake = json.loads(handshake_data)
        
        if handshake.get("type") != "handshake":
            await websocket.close(code=1008, reason="Expected handshake")
            return
        
        # Vérifier agent_id
        if handshake.get("agent_id") != agent_id:
            await websocket.close(code=1008, reason="agent_id mismatch")
            return
        
        # Enregistrer agent
        connection = agent_manager.register(agent_id, websocket, handshake)
        
        # Confirmer handshake
        await websocket.send_text(json.dumps({
            "type": "handshake_ack",
            "message": "Agent registered successfully"
        }))
        
        # Boucle de réception messages
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)
                
                msg_type = data.get("type")
                
                if msg_type == "heartbeat":
                    agent_manager.update_heartbeat(agent_id)
                    logger.debug(f"💓 Heartbeat from {agent_id}")
                
                elif msg_type == "task_ack":
                    task_id = data.get("task_id")
                    agent_manager.update_task_status(task_id, "acknowledged")
                    logger.info(f"Task {task_id} acknowledged by {agent_id}")
                
                elif msg_type == "task_result":
                    task_id = data.get("task_id")
                    status = data.get("status")
                    result_data = {
                        "status": status,
                        "message": data.get("message"),
                        "data": data.get("data"),
                        "error": data.get("error"),
                        "duration_ms": data.get("duration_ms")
                    }
                    agent_manager.update_task_status(task_id, status, result_data)
                    logger.info(f"✓ Task {task_id} completed: {status}")
                
                elif msg_type == "logs":
                    # Logs streaming depuis agent
                    logs = data.get("logs", [])
                    if connection:
                        connection.add_logs(logs)
                    logger.debug(f"📡 Received {len(logs)} logs from {agent_id}")
                
                else:
                    logger.warning(f"Unknown message type from {agent_id}: {msg_type}")
            
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from {agent_id}: {e}")
            except Exception as e:
                logger.error(f"Error handling message from {agent_id}: {e}", exc_info=True)
    
    except asyncio.TimeoutError:
        logger.error(f"Handshake timeout for {agent_id}")
        await websocket.close(code=1008, reason="Handshake timeout")
    
    except Exception as e:
        logger.error(f"WebSocket error for {agent_id}: {e}", exc_info=True)
    
    finally:
        if connection:
            agent_manager.unregister(agent_id)
        logger.info(f"WebSocket closed for agent: {agent_id}")


# ============================================================================
# REST ENDPOINTS
# ============================================================================

@router.get("", response_model=List[AgentInfo])
async def list_agents():
    """
    Liste tous les agents connectés.
    
    Returns:
        Liste des agents avec leurs métadonnées
    """
    return agent_manager.list_agents()


@router.get("/{agent_id}", response_model=AgentInfo)
async def get_agent_info(agent_id: str):
    """
    Récupère les infos d'un agent.
    
    Args:
        agent_id: ID de l'agent
    
    Returns:
        Informations de l'agent
    """
    conn = agent_manager.get_connection(agent_id)
    if not conn:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    return conn.to_dict()


@router.get("/{agent_id}/plugins")
async def get_agent_plugins(agent_id: str):
    """
    Liste les plugins disponibles sur un agent.
    
    Args:
        agent_id: ID de l'agent
    
    Returns:
        Liste des plugins
    """
    conn = agent_manager.get_connection(agent_id)
    if not conn:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    return {
        "agent_id": agent_id,
        "plugins": conn.plugins
    }


@router.post("/{agent_id}/tasks", response_model=TaskResponse)
async def create_task(agent_id: str, task_req: TaskRequest):
    """
    Envoie une tâche à un agent.
    
    Args:
        agent_id: ID de l'agent
        task_req: Détails de la tâche
    
    Returns:
        Informations de la tâche créée
    """
    try:
        task_id = await agent_manager.send_task(
            agent_id=agent_id,
            plugin=task_req.plugin,
            params=task_req.params,
            timeout=task_req.timeout
        )
        
        task = agent_manager.get_task(task_id)
        
        return TaskResponse(
            task_id=task_id,
            agent_id=agent_id,
            plugin=task_req.plugin,
            status="pending",
            created_at=task["created_at"],
            message="Task sent to agent"
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Récupère le statut d'une tâche.
    
    Args:
        task_id: ID de la tâche
    
    Returns:
        Statut de la tâche
    """
    task = agent_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return task


@router.get("/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """
    Vérifie le statut d'un agent (ping).
    
    Args:
        agent_id: ID de l'agent
    
    Returns:
        Statut de connexion
    """
    conn = agent_manager.get_connection(agent_id)
    
    if not conn:
        return {
            "agent_id": agent_id,
            "connected": False,
            "message": "Agent not connected"
        }
    
    # Calculer délai depuis dernier heartbeat
    last_heartbeat_delta = (datetime.now(timezone.utc) - conn.last_heartbeat).total_seconds()
    
    return {
        "agent_id": agent_id,
        "connected": True,
        "last_heartbeat_seconds_ago": last_heartbeat_delta,
        "healthy": last_heartbeat_delta < 60,
        "message": "Agent connected and healthy" if last_heartbeat_delta < 60 else "Agent may be stale"
    }


@router.get("/{agent_id}/logs")
async def get_agent_logs(
    agent_id: str,
    limit: int = Query(default=100, ge=1, le=1000, description="Nombre de logs max")
):
    """
    Récupère les logs d'un agent.
    
    Args:
        agent_id: ID de l'agent
        limit: Nombre de logs max
    
    Returns:
        Liste des logs
    """
    conn = agent_manager.get_connection(agent_id)
    if not conn:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found or not connected")
    
    # Retourner les N derniers logs
    logs = conn.logs[-limit:] if len(conn.logs) > limit else conn.logs
    
    return {
        "agent_id": agent_id,
        "logs": logs,
        "total_count": len(conn.logs),
        "returned_count": len(logs)
    }


@router.post("/{agent_id}/restart")
async def restart_agent(
    agent_id: str,
    target: str = Query(default="agent", description="Cible restart: 'agent' ou 'system'"),
    delay: int = Query(default=5, ge=0, le=300, description="Délai avant restart (secondes)")
):
    """
    Redémarre un agent ou sa machine hôte.
    
    Args:
        agent_id: ID de l'agent
        target: "agent" (redémarre l'agent) ou "system" (redémarre la machine)
        delay: Délai avant restart (0-300s)
    
    Returns:
        Tâche de restart créée
    """
    try:
        # Vérifier agent connecté
        conn = agent_manager.get_connection(agent_id)
        if not conn:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not connected")
        
        # Vérifier plugin disponible
        if "system_restart" not in conn.plugins:
            raise HTTPException(
                status_code=400, 
                detail=f"Plugin 'system_restart' not available on agent {agent_id}"
            )
        
        # Envoyer tâche
        task_id = await agent_manager.send_task(
            agent_id=agent_id,
            plugin="system_restart",
            params={
                "target": target,
                "delay": delay
            },
            timeout=60  # 1min timeout
        )
        
        task = agent_manager.get_task(task_id)
        
        action = "Agent restart" if target == "agent" else "System restart"
        
        return TaskResponse(
            task_id=task_id,
            agent_id=agent_id,
            plugin="system_restart",
            status="pending",
            created_at=task["created_at"],
            message=f"{action} scheduled in {delay}s"
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to restart agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to restart agent: {str(e)}")


@router.post("/{agent_id}/update")
async def trigger_agent_update(
    agent_id: str,
    version: Optional[str] = Query(default=None, description="Version cible (optionnel, défaut: latest)"),
    force: bool = Query(default=False, description="Forcer update même version")
):
    """
    Déclenche l'auto-update d'un agent.
    
    Si version non spécifiée, détecte automatiquement la dernière version depuis checksums.json.
    
    Args:
        agent_id: ID de l'agent
        version: Version cible (optionnel, par défaut: latest depuis checksums.json)
        force: Forcer update même si version identique
    
    Returns:
        Tâche d'update créée
    """
    try:
        # Vérifier agent connecté
        conn = agent_manager.get_connection(agent_id)
        if not conn:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not connected")
        
        # Vérifier plugin disponible
        if "self_update" not in conn.plugins:
            raise HTTPException(
                status_code=400, 
                detail=f"Plugin 'self_update' not available on agent {agent_id}"
            )
        
        # Lire checksums.json pour auto-détection version/checksum
        checksums_path = Path("/home/pie333/333HOME/static/agents/checksums.json")
        
        if not checksums_path.exists():
            raise HTTPException(
                status_code=500, 
                detail="checksums.json not found, cannot auto-detect version"
            )
        
        with open(checksums_path, "r") as f:
            checksums_data = json.load(f)
        
        versions = checksums_data.get("versions", {})
        
        if not versions:
            raise HTTPException(status_code=500, detail="No versions found in checksums.json")
        
        # Déterminer version cible
        if version:
            # Version spécifiée par user
            if version not in versions:
                available = ", ".join(versions.keys())
                raise HTTPException(
                    status_code=400, 
                    detail=f"Version {version} not found. Available: {available}"
                )
            target_version = version
        else:
            # Auto-détection: dernière version (tri sémantique)
            sorted_versions = sorted(
                versions.keys(), 
                key=lambda v: [int(x) for x in v.split(".")],
                reverse=True
            )
            target_version = sorted_versions[0]
        
        # Récupérer infos version cible
        version_info = versions[target_version]
        checksum = version_info.get("checksum")
        
        if not checksum:
            raise HTTPException(
                status_code=500, 
                detail=f"Checksum missing for version {target_version}"
            )
        
        # Générer URL download
        download_url = f"http://localhost:8000/static/agents/agent_v{target_version}.zip"
        
        # Version actuelle agent
        current_version = conn.metadata.get("version", "unknown")
        
        # Vérifier si update nécessaire
        if current_version == target_version and not force:
            raise HTTPException(
                status_code=400, 
                detail=f"Agent already on version {target_version}. Use force=true to reinstall."
            )
        
        # Envoyer tâche
        task_id = await agent_manager.send_task(
            agent_id=agent_id,
            plugin="self_update",
            params={
                "version": target_version,
                "download_url": download_url,
                "checksum": checksum,
                "force": force
            },
            timeout=300  # 5min pour update
        )
        
        task = agent_manager.get_task(task_id)
        
        return {
            "task_id": task_id,
            "agent_id": agent_id,
            "plugin": "self_update",
            "status": "pending",
            "current_version": current_version,
            "target_version": target_version,
            "created_at": task["created_at"],
            "message": f"Update from {current_version} to {target_version} initiated"
        }
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to trigger update: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to trigger update: {str(e)}")

