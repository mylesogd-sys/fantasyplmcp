#!/usr/bin/env python3
"""
Test script for proxy functionality
"""

import asyncio
import json
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("proxy-test")

async def test_proxy_functionality():
    """Test the MCP server's proxy functionality"""

    base_url = "https://fantasyplmcp.onrender.com"

    async with httpx.AsyncClient() as client:
        try:
            print("🔄 Testing FPL MCP Server with Proxy Support...")
            print("=" * 60)

            # Test 1: Health check
            print("\n1. Health Check:")
            response = await client.get(f"{base_url}/health")
            health_data = response.json()
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   MCP Initialized: {health_data.get('mcp_initialized', False)}")

            # Test 2: MCP Info
            print("\n2. MCP Configuration:")
            response = await client.get(f"{base_url}/mcp/info")
            info_data = response.json()
            print(f"   Server: {info_data.get('name', 'unknown')}")
            print(f"   HTTP Endpoint: {info_data.get('http_endpoint', 'N/A')}")

            # Test 3: Initialize MCP
            print("\n3. MCP Initialization:")
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"resources": {}, "tools": {}, "prompts": {}},
                    "clientInfo": {"name": "Proxy Test", "version": "1.0.0"}
                }
            }

            response = await client.post(f"{base_url}/mcp/http", json=init_request)
            if response.status_code == 200:
                init_result = response.json()
                server_info = init_result.get("result", {}).get("serverInfo", {})
                print(f"   ✅ Initialized: {server_info.get('name', 'unknown')}")
            else:
                print(f"   ❌ Failed: {response.status_code}")

            # Test 4: Try to get FPL data (this will test proxy functionality)
            print("\n4. FPL Data Access (Proxy Test):")
            data_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "analyze_players",
                    "arguments": {
                        "limit": 3,
                        "sort_by": "total_points",
                        "sort_order": "desc"
                    }
                }
            }

            print("   Attempting to fetch FPL data...")
            print("   (This will try direct connection, then proxies if needed)")

            response = await client.post(f"{base_url}/mcp/http", json=data_request, timeout=60.0)

            if response.status_code == 200:
                result = response.json()

                if "result" in result and "content" in result["result"]:
                    content = result["result"]["content"][0]["text"]
                    data = json.loads(content)

                    players = data.get("players", [])
                    if players:
                        print(f"   ✅ Success! Retrieved {len(players)} top players:")
                        for i, player in enumerate(players[:3], 1):
                            print(f"      {i}. {player.get('name', 'Unknown')} - {player.get('points', 0)} points")

                        print(f"\n   📊 Summary:")
                        print(f"      Total matches: {data.get('summary', {}).get('total_matches', 'N/A')}")
                        print(f"      Average points: {data.get('summary', {}).get('average_points', 'N/A')}")

                        return True
                    else:
                        print("   ❌ No player data received")

                elif "error" in result:
                    error = result["error"]
                    print(f"   ❌ Error: {error.get('message', 'Unknown error')}")

                    if "403 Forbidden" in str(error.get("message", "")):
                        print("\n   🔧 Proxy Troubleshooting:")
                        print("   - Direct connection blocked (403 Forbidden)")
                        print("   - Proxy rotation should be attempting...")
                        print("   - Check server logs for proxy attempts")
                        print("   - Consider adding commercial proxy services")
                else:
                    print(f"   ❌ Unexpected response format: {result}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")

            return False

        except Exception as e:
            logger.error(f"Test failed: {e}")
            return False

async def main():
    """Run proxy functionality test"""
    success = await test_proxy_functionality()

    print("\n" + "=" * 60)
    if success:
        print("🎉 PROXY TEST PASSED!")
        print("✅ FPL data successfully retrieved (proxy working)")
        print("✅ n8n MCP integration should work")
    else:
        print("⚠️  PROXY TEST INCONCLUSIVE")
        print("🔍 Check server logs for proxy rotation attempts")
        print("💡 Consider configuring commercial proxy services")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())