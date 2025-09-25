# FPL MCP Server - Render Deployment Guide

This guide explains how to deploy the Fantasy Premier League MCP Server to Render as a web service.

## Files Created for Deployment

### 1. `render.yaml` - Render Configuration
- Defines the web service configuration
- Sets environment variables
- Configures health check endpoint
- Uses Python runtime with starter plan

### 2. `web_server.py` - Web Server Wrapper
- FastAPI wrapper around the MCP server
- Provides HTTP endpoints for health checks
- Exposes MCP server information via REST API
- Handles graceful startup and shutdown

### 3. `requirements.txt` - Python Dependencies
- Lists all required Python packages
- Includes FastAPI and Uvicorn for web serving
- Compatible with Python 3.11+

### 4. `Dockerfile` - Container Configuration
- Multi-stage build for efficient deployment
- Health check using web endpoint
- Proper logging and error handling

### 5. `start.sh` - Startup Script
- Environment variable configuration
- Production/development mode handling
- Graceful server startup

### 6. `.env.example` - Environment Variables Template
- Example configuration for local development
- Optional FPL authentication settings
- Cache configuration options

## Deployment Steps

### Method 1: Using render.yaml (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`
   - Click "Create Web Service"

### Method 2: Manual Configuration

1. **Create New Web Service**
   - Go to Render Dashboard
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service Settings**
   - **Name**: `fpl-mcp-server`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python web_server.py`
   - **Plan**: `Starter` (or higher)

3. **Set Environment Variables**
   ```
   PORT=10000
   PYTHONPATH=src
   PYTHONUNBUFFERED=1
   LOG_LEVEL=INFO
   ENVIRONMENT=production
   ```

4. **Configure Health Check**
   - **Health Check Path**: `/health`

## Testing the Deployment

After deployment, test these endpoints:

- **Health Check**: `https://your-service.onrender.com/health`
- **Service Info**: `https://your-service.onrender.com/`
- **MCP Info**: `https://your-service.onrender.com/mcp/info`

## Environment Variables

### Required
- `PORT`: Server port (default: 10000)
- `PYTHONPATH`: Path to source code (default: src)

### Optional
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)
- `ENVIRONMENT`: Runtime environment (development, production)
- `FPL_EMAIL`: Fantasy PL email for authenticated features
- `FPL_PASSWORD`: Fantasy PL password for authenticated features
- `FPL_TEAM_ID`: Your FPL team ID
- `CACHE_TTL`: Cache time-to-live in seconds
- `CACHE_SIZE_LIMIT`: Maximum cache size

## Monitoring and Debugging

### Health Check Endpoints
- `GET /health` - Detailed health status
- `GET /` - Basic service status
- `GET /mcp/info` - MCP server information

### Logs
Monitor deployment logs in the Render dashboard to troubleshoot issues:
- Build logs for dependency installation issues
- Runtime logs for server startup and API errors
- Health check logs for service availability

### Common Issues

1. **Build Failures**
   - Check `requirements.txt` for correct package versions
   - Verify Python version compatibility

2. **Startup Issues**
   - Check environment variable configuration
   - Verify `PYTHONPATH` includes source directory

3. **Health Check Failures**
   - Ensure server starts on correct port
   - Verify health check endpoint responds correctly

## Local Testing

Test the deployment configuration locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export PYTHONPATH=src
export PORT=10000

# Start the server
python web_server.py
```

Visit `http://localhost:10000/health` to verify the service is running.

## Production Considerations

- **Scaling**: Render starter plan supports moderate traffic
- **Authentication**: FPL credentials should be set as environment variables
- **Monitoring**: Use Render's built-in monitoring or external services
- **Updates**: Automatic deploys on git push (if configured)

## Security Notes

- Never commit FPL credentials to version control
- Use Render's environment variable management
- Enable HTTPS (automatic on Render)
- Consider rate limiting for production use