#!/usr/bin/env python3

import os
import sys
import logging
import asyncio
from contextlib import asynccontextmanager

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import asyncio
from typing import Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("fpl-mcp-web")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting FPL MCP Web Server")
    try:
        # Import the MCP server after path is set
        from fpl_mcp.__main__ import mcp
        app.state.mcp_server = mcp
        logger.info("MCP server initialized")
    except Exception as e:
        logger.error(f"Failed to initialize MCP server: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down FPL MCP Web Server")

# Create FastAPI app
app = FastAPI(
    title="Fantasy Premier League MCP Server",
    description="MCP server for Fantasy Premier League data and tools",
    version="0.1.6",
    lifespan=lifespan
)

# Add CORS middleware for n8n compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "fpl-mcp-server", "version": "0.1.6"}

@app.get("/health")
async def health():
    """Detailed health check"""
    try:
        # Check if MCP server is available
        mcp_server = getattr(app.state, 'mcp_server', None)
        if mcp_server is None:
            raise HTTPException(status_code=503, detail="MCP server not initialized")

        return {
            "status": "healthy",
            "service": "fpl-mcp-server",
            "mcp_initialized": True,
            "version": "0.1.6"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/mcp/info")
async def mcp_info():
    """Get MCP server information"""
    try:
        mcp_server = getattr(app.state, 'mcp_server', None)
        if mcp_server is None:
            raise HTTPException(status_code=503, detail="MCP server not initialized")

        return {
            "name": "Fantasy Premier League",
            "instructions": "Access Fantasy Premier League data and tools",
            "status": "running",
            "type": "mcp_server",
            "websocket_endpoint": "/mcp/ws",
            "http_endpoint": "/mcp/http",
            "sse_endpoint": "/mcp/sse",
            "connection_info": {
                "websocket_url": "wss://fantasyplmcp.onrender.com/mcp/ws",
                "http_url": "https://fantasyplmcp.onrender.com/mcp/http",
                "sse_url": "https://fantasyplmcp.onrender.com/mcp/sse",
                "protocol": "mcp"
            }
        }
    except Exception as e:
        logger.error(f"MCP info request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/mcp/ws")
async def mcp_websocket(websocket: WebSocket):
    """WebSocket endpoint for MCP protocol communication"""
    await websocket.accept()
    logger.info("MCP WebSocket connection established")

    try:
        mcp_server = getattr(app.state, 'mcp_server', None)
        if mcp_server is None:
            await websocket.send_text(json.dumps({
                "error": "MCP server not initialized",
                "code": -32603
            }))
            await websocket.close()
            return

        # Handle MCP protocol messages
        async for message in websocket.iter_text():
            try:
                # Parse JSON-RPC message
                request = json.loads(message)
                logger.debug(f"Received MCP request: {request}")

                # Handle different MCP methods
                if request.get("method") == "initialize":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "resources": {
                                    "subscribe": True,
                                    "listChanged": True
                                },
                                "tools": {
                                    "listChanged": True
                                },
                                "prompts": {
                                    "listChanged": True
                                }
                            },
                            "serverInfo": {
                                "name": "Fantasy Premier League MCP Server",
                                "version": "0.1.6"
                            }
                        }
                    }
                    await websocket.send_text(json.dumps(response))

                elif request.get("method") == "resources/list":
                    # List available resources
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "resources": [
                                {
                                    "uri": "fpl://static/players",
                                    "name": "All Players",
                                    "description": "Complete list of FPL players with stats",
                                    "mimeType": "application/json"
                                },
                                {
                                    "uri": "fpl://static/teams",
                                    "name": "All Teams",
                                    "description": "Premier League teams with ratings",
                                    "mimeType": "application/json"
                                },
                                {
                                    "uri": "fpl://gameweeks/current",
                                    "name": "Current Gameweek",
                                    "description": "Current gameweek information",
                                    "mimeType": "application/json"
                                },
                                {
                                    "uri": "fpl://fixtures",
                                    "name": "Fixtures",
                                    "description": "All Premier League fixtures",
                                    "mimeType": "application/json"
                                }
                            ]
                        }
                    }
                    await websocket.send_text(json.dumps(response))

                elif request.get("method") == "tools/list":
                    # List available tools
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "tools": [
                                {
                                    "name": "analyze_player_fixtures",
                                    "description": "Analyze upcoming fixtures for a player",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "player_name": {"type": "string"},
                                            "num_fixtures": {"type": "integer", "default": 5}
                                        },
                                        "required": ["player_name"]
                                    }
                                },
                                {
                                    "name": "compare_players",
                                    "description": "Compare multiple players across metrics",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "player_names": {
                                                "type": "array",
                                                "items": {"type": "string"}
                                            },
                                            "metrics": {
                                                "type": "array",
                                                "items": {"type": "string"}
                                            }
                                        },
                                        "required": ["player_names"]
                                    }
                                },
                                {
                                    "name": "analyze_players",
                                    "description": "Filter and analyze players by criteria",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "position": {"type": "string"},
                                            "team": {"type": "string"},
                                            "min_price": {"type": "number"},
                                            "max_price": {"type": "number"},
                                            "sort_by": {"type": "string"}
                                        }
                                    }
                                }
                            ]
                        }
                    }
                    await websocket.send_text(json.dumps(response))

                elif request.get("method") == "resources/read":
                    # Handle resource reading - delegate to MCP server
                    try:
                        uri = request.get("params", {}).get("uri")
                        if not uri:
                            raise ValueError("No URI provided")

                        # Map URI to MCP server resource
                        if uri == "fpl://static/players":
                            from fpl_mcp.__main__ import get_all_players
                            data = await get_all_players()
                        elif uri == "fpl://static/teams":
                            from fpl_mcp.__main__ import get_all_teams
                            data = await get_all_teams()
                        elif uri == "fpl://gameweeks/current":
                            from fpl_mcp.__main__ import get_current_gameweek
                            data = await get_current_gameweek()
                        elif uri == "fpl://fixtures":
                            from fpl_mcp.__main__ import get_all_fixtures
                            data = await get_all_fixtures()
                        else:
                            raise ValueError(f"Unknown resource: {uri}")

                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {
                                "contents": [
                                    {
                                        "uri": uri,
                                        "mimeType": "application/json",
                                        "text": json.dumps(data, indent=2)
                                    }
                                ]
                            }
                        }
                        await websocket.send_text(json.dumps(response))

                    except Exception as e:
                        error_response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "error": {
                                "code": -32603,
                                "message": f"Resource read failed: {str(e)}"
                            }
                        }
                        await websocket.send_text(json.dumps(error_response))

                elif request.get("method") == "tools/call":
                    # Handle tool calls - delegate to MCP server tools
                    try:
                        params = request.get("params", {})
                        tool_name = params.get("name")
                        arguments = params.get("arguments", {})

                        # Map tool calls to MCP server functions
                        if tool_name == "analyze_player_fixtures":
                            from fpl_mcp.__main__ import analyze_player_fixtures
                            result = await analyze_player_fixtures(**arguments)
                        elif tool_name == "compare_players":
                            from fpl_mcp.__main__ import compare_players
                            result = await compare_players(**arguments)
                        elif tool_name == "analyze_players":
                            from fpl_mcp.__main__ import analyze_players
                            result = await analyze_players(**arguments)
                        else:
                            raise ValueError(f"Unknown tool: {tool_name}")

                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": json.dumps(result, indent=2)
                                    }
                                ]
                            }
                        }
                        await websocket.send_text(json.dumps(response))

                    except Exception as e:
                        error_response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "error": {
                                "code": -32603,
                                "message": f"Tool call failed: {str(e)}"
                            }
                        }
                        await websocket.send_text(json.dumps(error_response))

                else:
                    # Unknown method
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {request.get('method')}"
                        }
                    }
                    await websocket.send_text(json.dumps(error_response))

            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                await websocket.send_text(json.dumps(error_response))

            except Exception as e:
                logger.error(f"Error processing MCP request: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                await websocket.send_text(json.dumps(error_response))

    except WebSocketDisconnect:
        logger.info("MCP WebSocket connection closed")
    except Exception as e:
        logger.error(f"MCP WebSocket error: {e}")
    finally:
        logger.info("MCP WebSocket connection terminated")

# HTTP MCP endpoint for n8n compatibility
@app.post("/mcp/http")
async def mcp_http(request: Request):
    """HTTP endpoint for MCP protocol communication (n8n compatible)"""
    try:
        mcp_server = getattr(app.state, 'mcp_server', None)
        if mcp_server is None:
            raise HTTPException(status_code=503, detail="MCP server not initialized")

        # Parse JSON-RPC request
        body = await request.json()
        logger.debug(f"Received HTTP MCP request: {body}")

        # Handle MCP methods (same logic as WebSocket)
        response = await process_mcp_request(body)
        return response

    except json.JSONDecodeError as e:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32700,
                "message": f"Parse error: {str(e)}"
            }
        }
    except Exception as e:
        logger.error(f"HTTP MCP request failed: {e}")
        return {
            "jsonrpc": "2.0",
            "id": body.get("id") if 'body' in locals() else None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }

# SSE endpoint for streaming responses
@app.get("/mcp/sse")
async def mcp_sse():
    """Server-Sent Events endpoint for MCP streaming responses"""

    async def event_stream():
        try:
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connection', 'status': 'connected'})}\n\n"

            # Keep connection alive
            while True:
                await asyncio.sleep(30)  # Send keepalive every 30 seconds
                yield f"data: {json.dumps({'type': 'keepalive', 'timestamp': asyncio.get_event_loop().time()})}\n\n"

        except Exception as e:
            logger.error(f"SSE stream error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

# Shared MCP request processing function
async def process_mcp_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Process MCP request and return response"""

    method = request.get("method")
    request_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "resources": {
                        "subscribe": True,
                        "listChanged": True
                    },
                    "tools": {
                        "listChanged": True
                    },
                    "prompts": {
                        "listChanged": True
                    }
                },
                "serverInfo": {
                    "name": "Fantasy Premier League MCP Server",
                    "version": "0.1.6"
                }
            }
        }

    elif method == "resources/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": [
                    {
                        "uri": "fpl://static/players",
                        "name": "All Players",
                        "description": "Complete list of FPL players with stats",
                        "mimeType": "application/json"
                    },
                    {
                        "uri": "fpl://static/teams",
                        "name": "All Teams",
                        "description": "Premier League teams with ratings",
                        "mimeType": "application/json"
                    },
                    {
                        "uri": "fpl://gameweeks/current",
                        "name": "Current Gameweek",
                        "description": "Current gameweek information",
                        "mimeType": "application/json"
                    },
                    {
                        "uri": "fpl://fixtures",
                        "name": "Fixtures",
                        "description": "All Premier League fixtures",
                        "mimeType": "application/json"
                    }
                ]
            }
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "analyze_player_fixtures",
                        "description": "Analyze upcoming fixtures for a player",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "player_name": {"type": "string"},
                                "num_fixtures": {"type": "integer", "default": 5}
                            },
                            "required": ["player_name"]
                        }
                    },
                    {
                        "name": "compare_players",
                        "description": "Compare multiple players across metrics",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "player_names": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "metrics": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            },
                            "required": ["player_names"]
                        }
                    },
                    {
                        "name": "analyze_players",
                        "description": "Filter and analyze players by criteria",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "position": {"type": "string"},
                                "team": {"type": "string"},
                                "min_price": {"type": "number"},
                                "max_price": {"type": "number"},
                                "sort_by": {"type": "string"}
                            }
                        }
                    }
                ]
            }
        }

    elif method == "resources/read":
        try:
            uri = request.get("params", {}).get("uri")
            if not uri:
                raise ValueError("No URI provided")

            # Map URI to MCP server resource
            if uri == "fpl://static/players":
                from fpl_mcp.__main__ import get_all_players
                data = await get_all_players()
            elif uri == "fpl://static/teams":
                from fpl_mcp.__main__ import get_all_teams
                data = await get_all_teams()
            elif uri == "fpl://gameweeks/current":
                from fpl_mcp.__main__ import get_current_gameweek
                data = await get_current_gameweek()
            elif uri == "fpl://fixtures":
                from fpl_mcp.__main__ import get_all_fixtures
                data = await get_all_fixtures()
            else:
                raise ValueError(f"Unknown resource: {uri}")

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(data, indent=2)
                        }
                    ]
                }
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Resource read failed: {str(e)}"
                }
            }

    elif method == "tools/call":
        try:
            params = request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            # Map tool calls to MCP server functions
            if tool_name == "analyze_player_fixtures":
                from fpl_mcp.__main__ import analyze_player_fixtures
                result = await analyze_player_fixtures(**arguments)
            elif tool_name == "compare_players":
                from fpl_mcp.__main__ import compare_players
                result = await compare_players(**arguments)
            elif tool_name == "analyze_players":
                from fpl_mcp.__main__ import analyze_players
                result = await analyze_players(**arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool call failed: {str(e)}"
                }
            }

    else:
        # Unknown method
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

def main():
    """Run the web server"""
    port = int(os.getenv("PORT", 10000))
    host = "0.0.0.0"

    logger.info(f"Starting FPL MCP Web Server on {host}:{port}")

    uvicorn.run(
        "web_server:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        reload=False
    )

if __name__ == "__main__":
    main()