#!/usr/bin/env python3

import os
import sys
import logging
import asyncio
from contextlib import asynccontextmanager

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

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
            "type": "mcp_server"
        }
    except Exception as e:
        logger.error(f"MCP info request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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