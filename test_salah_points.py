#!/usr/bin/env python3
"""
Quick test to get Salah's current points from the MCP server
"""

import asyncio
import json
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("salah-test")

async def get_salah_points():
    """Get Salah's current points from the MCP server"""

    base_url = "https://fantasyplmcp.onrender.com"

    async with httpx.AsyncClient() as client:
        try:
            # First, let's find Salah using the player search
            search_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "analyze_players",
                    "arguments": {
                        "position": "MID",
                        "limit": 50,
                        "sort_by": "total_points",
                        "sort_order": "desc"
                    }
                }
            }

            logger.info("Searching for Liverpool midfielders...")
            response = await client.post(f"{base_url}/mcp/http", json=search_request)
            logger.info(f"Response status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()

                if "result" in result and "content" in result["result"]:
                    # Parse the JSON content
                    content = result["result"]["content"][0]["text"]
                    data = json.loads(content)

                    # Look for Salah in the players
                    salah_data = None
                    for player in data.get("players", []):
                        if "salah" in player.get("name", "").lower():
                            salah_data = player
                            break

                    if salah_data:
                        print(f"\n🔥 **Mohamed Salah Stats:**")
                        print(f"   Points: {salah_data.get('points', 'N/A')}")
                        print(f"   Price: £{salah_data.get('price', 'N/A')}m")
                        print(f"   Team: {salah_data.get('team', 'N/A')}")
                        print(f"   Form: {salah_data.get('form', 'N/A')}")
                        print(f"   Selected by: {salah_data.get('selected_by_percent', 'N/A')}%")
                        print(f"   Goals: {salah_data.get('goals_scored', 'N/A')}")
                        print(f"   Assists: {salah_data.get('assists', 'N/A')}")
                        return salah_data
                    else:
                        print("❌ Salah not found in top midfielders")
                        # Print top 5 for debugging
                        print("\nTop 5 midfielders found:")
                        for i, player in enumerate(data.get("players", [])[:5]):
                            print(f"{i+1}. {player.get('name', 'Unknown')} - {player.get('points', 0)} points")
                else:
                    print(f"❌ Unexpected response format: {result}")
            else:
                print(f"❌ HTTP error: {response.status_code}")
                print(f"Response: {response.text}")

        except Exception as e:
            logger.error(f"Error getting Salah's points: {e}")
            return None

async def main():
    """Main function"""
    print("🔍 Getting Salah's current FPL points...")
    await get_salah_points()

if __name__ == "__main__":
    asyncio.run(main())