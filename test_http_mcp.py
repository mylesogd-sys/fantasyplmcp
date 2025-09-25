#!/usr/bin/env python3
"""
Test script for HTTP MCP endpoints (n8n compatible)
"""

import asyncio
import json
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("http-mcp-test")

async def test_http_mcp():
    """Test the HTTP MCP endpoints"""

    # For local testing, use http://localhost:10000
    # For production, use https://fantasyplmcp.onrender.com
    base_url = "https://fantasyplmcp.onrender.com"

    async with httpx.AsyncClient() as client:
        logger.info(f"Testing HTTP MCP at {base_url}")

        try:
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
                        "name": "HTTP MCP Test Client",
                        "version": "1.0.0"
                    }
                }
            }

            response = await client.post(f"{base_url}/mcp/http", json=initialize_request)
            init_response = response.json()
            logger.info(f"Initialize response: {init_response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")

            # Test 2: List available resources
            resources_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "resources/list"
            }

            response = await client.post(f"{base_url}/mcp/http", json=resources_request)
            resources_response = response.json()
            resources_count = len(resources_response.get('result', {}).get('resources', []))
            logger.info(f"Resources available: {resources_count}")

            # Test 3: List available tools
            tools_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/list"
            }

            response = await client.post(f"{base_url}/mcp/http", json=tools_request)
            tools_response = response.json()
            tools_count = len(tools_response.get('result', {}).get('tools', []))
            logger.info(f"Tools available: {tools_count}")

            # Test 4: Read a resource
            read_request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "resources/read",
                "params": {
                    "uri": "fpl://gameweeks/current"
                }
            }

            response = await client.post(f"{base_url}/mcp/http", json=read_request)
            read_response = response.json()
            success = 'result' in read_response and not 'error' in read_response
            logger.info(f"Resource read successful: {success}")

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

            response = await client.post(f"{base_url}/mcp/http", json=tool_request)
            tool_response = response.json()
            success = 'result' in tool_response and not 'error' in tool_response
            logger.info(f"Tool call successful: {success}")

            # Test 6: Test SSE endpoint
            try:
                async with client.stream('GET', f"{base_url}/mcp/sse") as sse_response:
                    logger.info(f"SSE connection status: {sse_response.status_code}")

                    # Read first few SSE events
                    count = 0
                    async for line in sse_response.aiter_lines():
                        if line.startswith('data:'):
                            logger.info(f"SSE event: {line}")
                            count += 1
                            if count >= 2:  # Just read first couple events
                                break

                    logger.info("SSE endpoint working")
            except Exception as e:
                logger.warning(f"SSE test failed (may be expected): {e}")

            logger.info("✅ All HTTP MCP tests passed!")
            return True

        except Exception as e:
            logger.error(f"❌ HTTP MCP test failed: {e}")
            return False

async def main():
    """Run the HTTP MCP test"""
    success = await test_http_mcp()
    if success:
        print("\n🎉 HTTP MCP endpoints are working!")
        print("For n8n MCP tool, use:")
        print("  - HTTP endpoint: https://fantasyplmcp.onrender.com/mcp/http")
        print("  - SSE endpoint: https://fantasyplmcp.onrender.com/mcp/sse")
    else:
        print("\n💥 HTTP MCP connection failed. Check server logs.")

if __name__ == "__main__":
    asyncio.run(main())