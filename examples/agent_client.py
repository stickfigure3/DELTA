"""
Example: AI Agent connecting to DELTA platform.

This shows how an AI agent connects to DELTA and communicates with users.
Run this alongside the DELTA API server.

Usage:
    # Terminal 1: Run the DELTA API
    poetry run uvicorn delta.api.main:app --reload --port 8000
    
    # Terminal 2: Run this agent client
    poetry run python examples/agent_client.py
    
    # Terminal 3: Connect as a user (use websocat or browser)
    websocat "ws://localhost:8000/v1/ws/user/agent-123?user_id=user-456"
"""

import asyncio
import json
from datetime import datetime

import websockets


DELTA_HOST = "localhost:8000"
AGENT_ID = "agent-123"
API_KEY = "test-api-key"


async def agent_main():
    """Main agent loop - connects to DELTA and communicates with users."""
    
    uri = f"ws://{DELTA_HOST}/v1/ws/agent/{AGENT_ID}?api_key={API_KEY}"
    
    print(f"🤖 Agent connecting to DELTA: {uri}")
    
    async with websockets.connect(uri) as ws:
        print("✅ Agent connected to DELTA!")
        
        # Send initial greeting
        await ws.send(json.dumps({
            "type": "message",
            "content": "Hello! I'm your DELTA agent. How can I help you today?",
            "msg_type": "agent_message",
        }))
        
        # Listen for messages from users
        async for message in ws:
            data = json.loads(message)
            print(f"📨 Received: {data}")
            
            if data.get("type") == "user_message":
                user_content = data.get("content", "")
                print(f"👤 User said: {user_content}")
                
                # Simulate agent thinking
                await ws.send(json.dumps({
                    "type": "status",
                    "content": "Thinking...",
                }))
                
                await asyncio.sleep(1)  # Simulate processing
                
                # Send response
                response = f"I received your message: '{user_content}'. This is a demo response!"
                
                await ws.send(json.dumps({
                    "type": "message",
                    "content": response,
                    "msg_type": "agent_message",
                    "metadata": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "tokens_used": 10,
                    }
                }))
                
                print(f"🤖 Agent replied: {response}")
            
            elif data.get("type") == "pong":
                print("🏓 Pong received")


async def demo_conversation():
    """Demo: Simulate both agent and user for testing."""
    
    print("=" * 60)
    print("DELTA Agent-to-User Communication Demo")
    print("=" * 60)
    
    # Connect agent
    agent_uri = f"ws://{DELTA_HOST}/v1/ws/agent/{AGENT_ID}?api_key={API_KEY}"
    user_uri = f"ws://{DELTA_HOST}/v1/ws/user/{AGENT_ID}?user_id=demo-user"
    
    async with websockets.connect(agent_uri) as agent_ws, \
               websockets.connect(user_uri) as user_ws:
        
        print("✅ Agent connected")
        print("✅ User connected")
        
        # Agent sends greeting
        await agent_ws.send(json.dumps({
            "type": "message",
            "content": "Hello! I'm your AI assistant. What would you like to do today?",
            "msg_type": "agent_message",
        }))
        print("🤖 Agent: Hello! I'm your AI assistant...")
        
        # Small delay to let message propagate
        await asyncio.sleep(0.5)
        
        # User receives and responds
        user_msg = await asyncio.wait_for(user_ws.recv(), timeout=5.0)
        print(f"👤 User received: {json.loads(user_msg)['content'][:50]}...")
        
        # User sends a message
        await user_ws.send(json.dumps({
            "type": "message",
            "content": "Can you help me write a Python script?",
        }))
        print("👤 User: Can you help me write a Python script?")
        
        await asyncio.sleep(0.5)
        
        # Agent receives user message
        agent_msg = await asyncio.wait_for(agent_ws.recv(), timeout=5.0)
        received = json.loads(agent_msg)
        print(f"🤖 Agent received: {received['content']}")
        
        # Agent responds
        await agent_ws.send(json.dumps({
            "type": "message",
            "content": "Of course! I'd be happy to help you write a Python script. What should it do?",
            "msg_type": "agent_message",
        }))
        print("🤖 Agent: Of course! I'd be happy to help...")
        
        await asyncio.sleep(0.5)
        
        # User receives response
        user_msg = await asyncio.wait_for(user_ws.recv(), timeout=5.0)
        print(f"👤 User received: {json.loads(user_msg)['content'][:50]}...")
        
        print("\n" + "=" * 60)
        print("✅ Demo complete! Agent-to-User communication working.")
        print("=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # Run full demo with simulated user
        asyncio.run(demo_conversation())
    else:
        # Run as standalone agent waiting for users
        asyncio.run(agent_main())
