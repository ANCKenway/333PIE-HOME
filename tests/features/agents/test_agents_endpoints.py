#!/usr/bin/env python3
"""
Script de test pour valider les endpoints /restart et /update
"""
import asyncio
import websockets
import json
import requests
from datetime import datetime

# Configuration
HUB_URL = "ws://localhost:8000/api/ws/agents"
API_URL = "http://localhost:8000/api/agents"
AGENT_ID = "test-agent-333pie"

async def mock_agent():
    """Simule un agent connecté avec plugins system_restart et self_update"""
    
    print(f"🔌 Connecting mock agent: {AGENT_ID}")
    
    async with websockets.connect(f"{HUB_URL}?agent_id={AGENT_ID}") as ws:
        # Handshake
        handshake = {
            "type": "handshake",
            "agent_id": AGENT_ID,
            "hostname": "test-machine",
            "os_platform": "Linux",
            "version": "1.0.17",
            "plugins": ["system_info", "self_update", "logmein_rescue", "system_restart"]
        }
        
        await ws.send(json.dumps(handshake))
        print(f"📤 Sent handshake")
        
        # Attendre ack
        ack = await ws.recv()
        ack_data = json.loads(ack)
        print(f"📥 Received: {ack_data}")
        
        if ack_data.get("type") != "handshake_ack":
            print("❌ Handshake failed")
            return
        
        print(f"✅ Agent {AGENT_ID} connected and registered")
        
        # Heartbeat loop
        heartbeat_task = asyncio.create_task(send_heartbeats(ws))
        
        # Attendre tâches du Hub
        print(f"👂 Listening for tasks...")
        
        try:
            while True:
                message = await asyncio.wait_for(ws.recv(), timeout=60)
                data = json.loads(message)
                
                msg_type = data.get("type")
                
                if msg_type == "task":
                    task_id = data.get("task_id")
                    plugin = data.get("plugin")
                    params = data.get("params", {})
                    
                    print(f"\n📨 Received task:")
                    print(f"   Task ID: {task_id}")
                    print(f"   Plugin: {plugin}")
                    print(f"   Params: {params}")
                    
                    # Envoyer ACK
                    await ws.send(json.dumps({
                        "type": "task_ack",
                        "task_id": task_id
                    }))
                    print(f"✅ Task acknowledged")
                    
                    # Simuler exécution
                    await asyncio.sleep(1)
                    
                    # Envoyer résultat
                    result = {
                        "type": "task_result",
                        "task_id": task_id,
                        "status": "success",
                        "message": f"Mock execution of {plugin} successful",
                        "data": {"mock": True, "params_received": params},
                        "duration_ms": 1000
                    }
                    
                    await ws.send(json.dumps(result))
                    print(f"✅ Task result sent")
                    
                    # Si restart, déconnecter après 2s
                    if plugin == "system_restart":
                        print(f"🔄 Mock restart in 2s...")
                        await asyncio.sleep(2)
                        print(f"🔌 Disconnecting (simulating restart)...")
                        break
        
        except asyncio.TimeoutError:
            print("⏱️ No tasks received in 60s")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            heartbeat_task.cancel()
            print(f"👋 Agent disconnected")


async def send_heartbeats(ws):
    """Envoie heartbeats toutes les 10s"""
    try:
        while True:
            await asyncio.sleep(10)
            await ws.send(json.dumps({"type": "heartbeat"}))
            print(f"💓 Heartbeat sent")
    except asyncio.CancelledError:
        pass


def test_restart_endpoint():
    """Test l'endpoint POST /api/agents/{id}/restart"""
    print(f"\n\n🧪 TEST 1: POST /api/agents/{AGENT_ID}/restart")
    print("=" * 60)
    
    response = requests.post(
        f"{API_URL}/{AGENT_ID}/restart",
        params={"delay": 5}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200


def test_update_endpoint():
    """Test l'endpoint POST /api/agents/{id}/update"""
    print(f"\n\n🧪 TEST 2: POST /api/agents/{AGENT_ID}/update (auto-detect version)")
    print("=" * 60)
    
    response = requests.post(f"{API_URL}/{AGENT_ID}/update")
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200


async def main():
    """Workflow de test complet"""
    
    print("\n" + "=" * 60)
    print("🚀 Tests endpoints /restart et /update")
    print("=" * 60)
    
    # Démarrer mock agent
    agent_task = asyncio.create_task(mock_agent())
    
    # Attendre connexion
    await asyncio.sleep(2)
    
    # Test 1: Restart
    success1 = test_restart_endpoint()
    
    # Attendre traitement
    await asyncio.sleep(3)
    
    # Attendre fin agent
    await agent_task
    
    # Redémarrer agent pour test 2
    print(f"\n🔄 Reconnecting agent for update test...")
    agent_task = asyncio.create_task(mock_agent())
    await asyncio.sleep(2)
    
    # Test 2: Update
    success2 = test_update_endpoint()
    
    # Attendre traitement
    await asyncio.sleep(3)
    
    # Cancel agent task
    agent_task.cancel()
    
    # Résumé
    print("\n\n" + "=" * 60)
    print("📊 RÉSUMÉ TESTS")
    print("=" * 60)
    print(f"✅ Test Restart: {'PASSED' if success1 else 'FAILED'}")
    print(f"✅ Test Update: {'PASSED' if success2 else 'FAILED'}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
