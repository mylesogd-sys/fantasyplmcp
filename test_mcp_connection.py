#!/usr/bin/env python3
"""
Test script for MCP WebSocket connection
"""

import asyncio
import json
import websockets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-test")

async def test_mcp_connection():
    """Test the MCP WebSocket connection"""

    # For local testing, use ws://localhost:10000/mcp/ws
    # For production, use wss://fantasyplmcp.onrender.com/mcp/ws
    url = "wss://fantasyplmcp.onrender.com/mcp/ws"

    try:
        logger.info(f"Connecting to {url}")

        async with websockets.connect(url) as websocket:
            logger.info("Connected to MCP WebSocket")

            # Test 1: Initialize MCP session
            initialize_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "resources": {"subscribe": True},
                        "tools": {},
                        "prompts": {}
                    },
                    "clientInfo": {
                        "name": "MCP Test Client",
                        "version": "1.0.0"
                    }
                }
            }

            await websocket.send(json.dumps(initialize_request))
            response = await websocket.recv()
            init_response = json.loads(response)
            logger.info(f"Initialize response: {init_response}")

            # Test 2: List available resources
            resources_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "resources/list"
            }

            await websocket.send(json.dumps(resources_request))
            response = await websocket.recv()
            resources_response = json.loads(response)
            logger.info(f"Resources available: {len(resources_response.get('result', {}).get('resources', []))}")

            # Test 3: List available tools
            tools_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/list"
            }

            await websocket.send(json.dumps(tools_request))
            response = await websocket.recv()
            tools_response = json.loads(response)
            logger.info(f"Tools available: {len(tools_response.get('result', {}).get('tools', []))}")

            # Test 4: Read a resource
            read_request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "resources/read",
                "params": {
                    "uri": "fpl://gameweeks/current"
                }
            }

            await websocket.send(json.dumps(read_request))
            response = await websocket.recv()
            read_response = json.loads(response)
            logger.info(f"Resource read successful: {'result' in read_response}")

            # Test 5: Call a tool
            tool_request = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "analyze_player_fixtures",
                    "arguments": {
                        "player_name": "Salah",
                        "num_fixtures": 3
                    }
                }
            }

            await websocket.send(json.dumps(tool_request))
            response = await websocket.recv()
            tool_response = json.loads(response)
            logger.info(f"Tool call successful: {'result' in tool_response}")

            logger.info("✅ All MCP tests passed!")
            return True

    except Exception as e:
        logger.error(f"❌ MCP connection test failed: {e}")
        return False

async def main():
    """Run the MCP connection test"""
    success = await test_mcp_connection()
    if success:
        print("\n🎉 MCP WebSocket connection is working!")
        print("Your n8n MCP tool can connect to: wss://fantasyplmcp.onrender.com/mcp/ws")
    else:
        print("\n💥 MCP connection failed. Check server logs.")

if __name__ == "__main__":
    asyncio.run(main())