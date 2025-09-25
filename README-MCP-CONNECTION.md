# MCP Protocol Connection Guide

Your FPL MCP server now supports **multiple transport methods** for MCP protocol connections, including HTTP and SSE for n8n compatibility.

## 🔌 **Connection Details**

### **HTTP Endpoint (Recommended for n8n)**
```
POST https://fantasyplmcp.onrender.com/mcp/http
```

### **Server-Sent Events (SSE) Endpoint**
```
GET https://fantasyplmcp.onrender.com/mcp/sse
```

### **WebSocket Endpoint**
```
wss://fantasyplmcp.onrender.com/mcp/ws
```

### **Protocol**
- **Transport**: HTTP POST + SSE or WebSocket
- **Protocol**: JSON-RPC 2.0
- **MCP Version**: 2024-11-05

## 🛠️ **n8n MCP Tool Configuration**

### **Recommended HTTP Configuration**
- **Server URL**: `https://fantasyplmcp.onrender.com/mcp/http`
- **Transport Type**: `http`
- **Protocol**: `mcp`
- **Method**: `POST`

### **Alternative SSE Configuration**
- **SSE URL**: `https://fantasyplmcp.onrender.com/mcp/sse`
- **Transport Type**: `sse`
- **Protocol**: `mcp`

### **WebSocket Configuration (if supported)**
- **Server URL**: `wss://fantasyplmcp.onrender.com/mcp/ws`
- **Transport Type**: `websocket`
- **Protocol**: `mcp`

### **Alternative Local Connection**
For development/testing, you can also run locally:
```bash
# Run local MCP server
python -m fpl_mcp

# n8n connection (stdio)
Command: python
Args: ["-m", "fpl_mcp"]
Working Directory: /path/to/your/project
```

## 📊 **Available Resources**

Your MCP server provides these resources:

| URI | Description |
|-----|-------------|
| `fpl://static/players` | All FPL players with stats |
| `fpl://static/teams` | Premier League teams with ratings |
| `fpl://gameweeks/current` | Current gameweek information |
| `fpl://fixtures` | All Premier League fixtures |

## 🔧 **Available Tools**

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `analyze_player_fixtures` | Analyze upcoming fixtures for a player | `player_name` (string), `num_fixtures` (int) |
| `compare_players` | Compare multiple players across metrics | `player_names` (array), `metrics` (array) |
| `analyze_players` | Filter and analyze players by criteria | `position`, `team`, `min_price`, `max_price`, `sort_by` |

## 🧪 **Testing the Connection**

### **1. HTTP Endpoints (Health Check)**
```bash
curl https://fantasyplmcp.onrender.com/mcp/info
```

### **2. WebSocket Test Script**
```bash
python test_mcp_connection.py
```

### **3. Manual HTTP Test**
```bash
curl -X POST https://fantasyplmcp.onrender.com/mcp/http \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": { "resources": {}, "tools": {}, "prompts": {} },
      "clientInfo": { "name": "Test Client", "version": "1.0.0" }
    }
  }'
```

### **4. JavaScript HTTP Test**
```javascript
fetch('https://fantasyplmcp.onrender.com/mcp/http', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "initialize",
        params: {
            protocolVersion: "2024-11-05",
            capabilities: { resources: {}, tools: {}, prompts: {} },
            clientInfo: { name: "Test Client", version: "1.0.0" }
        }
    })
})
.then(response => response.json())
.then(data => console.log('Response:', data));
```

## 🎯 **Usage Examples**

### **Read Current Gameweek (HTTP)**
```bash
curl -X POST https://fantasyplmcp.onrender.com/mcp/http \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "resources/read",
    "params": {
        "uri": "fpl://gameweeks/current"
    }
  }'
```

### **Analyze Player Fixtures (HTTP)**
```bash
curl -X POST https://fantasyplmcp.onrender.com/mcp/http \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "analyze_player_fixtures",
        "arguments": {
            "player_name": "Salah",
            "num_fixtures": 5
        }
    }
  }'
```

### **Compare Players (HTTP)**
```bash
curl -X POST https://fantasyplmcp.onrender.com/mcp/http \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "compare_players",
        "arguments": {
            "player_names": ["Salah", "Haaland", "Kane"],
            "metrics": ["total_points", "goals_scored", "assists"]
        }
    }
  }'
```

## 📝 **n8n Integration Steps**

### **Step 1: Add MCP Node**
1. In n8n workflow editor, add an **MCP** node
2. Click on the node to configure

### **Step 2: Configure Connection**
- **Server URL**: `https://fantasyplmcp.onrender.com/mcp/http`
- **Transport**: `HTTP`
- **Content-Type**: `application/json`

### **Step 3: Initialize Connection**
First request should be initialization:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "resources": {},
      "tools": {},
      "prompts": {}
    },
    "clientInfo": {
      "name": "n8n",
      "version": "1.0.0"
    }
  }
}
```

### **Step 4: Use FPL Tools**
After initialization, call any available tool:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "analyze_player_fixtures",
    "arguments": {
      "player_name": "{{$json.player_name}}",
      "num_fixtures": 5
    }
  }
}
```

## 🔍 **Troubleshooting**

### **Connection Issues**
1. **Check server status**: `https://fantasyplmcp.onrender.com/health`
2. **Verify WebSocket endpoint**: `https://fantasyplmcp.onrender.com/mcp/info`
3. **Test with script**: `python test_mcp_connection.py`

### **Common Errors**
- **Connection refused**: Server may be starting up (Render cold start)
- **Protocol mismatch**: Ensure using MCP protocol version 2024-11-05
- **Invalid JSON**: Check request format matches JSON-RPC 2.0

### **Error Codes**
- `-32700`: Parse error (invalid JSON)
- `-32601`: Method not found
- `-32603`: Internal error
- `-32600`: Invalid request

## 📈 **Performance Notes**

- **Cold starts**: First connection may take 10-30 seconds (Render free tier)
- **Concurrent connections**: Supports multiple simultaneous MCP clients
- **Rate limiting**: Respects FPL API rate limits automatically
- **Caching**: Responses cached for optimal performance

## 🚀 **Next Steps**

1. **Test the connection** with the provided script
2. **Configure n8n** with the WebSocket endpoint
3. **Build workflows** using the available tools and resources
4. **Monitor performance** via Render dashboard

Your FPL MCP server is now ready for n8n integration! 🎉