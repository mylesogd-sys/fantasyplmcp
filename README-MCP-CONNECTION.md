# MCP Protocol Connection Guide

Your FPL MCP server now supports **direct MCP protocol connections** via WebSocket for tools like n8n.

## 🔌 **Connection Details**

### **WebSocket Endpoint**
```
wss://fantasyplmcp.onrender.com/mcp/ws
```

### **Protocol**
- **Transport**: WebSocket
- **Protocol**: JSON-RPC 2.0
- **MCP Version**: 2024-11-05

## 🛠️ **n8n MCP Tool Configuration**

### **Connection Settings**
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

### **3. Manual WebSocket Test**
```javascript
const ws = new WebSocket('wss://fantasyplmcp.onrender.com/mcp/ws');

ws.onopen = () => {
    // Send initialize request
    ws.send(JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "initialize",
        params: {
            protocolVersion: "2024-11-05",
            capabilities: { resources: {}, tools: {}, prompts: {} },
            clientInfo: { name: "Test Client", version: "1.0.0" }
        }
    }));
};

ws.onmessage = (event) => {
    console.log('Response:', JSON.parse(event.data));
};
```

## 🎯 **Usage Examples**

### **Read Current Gameweek**
```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "resources/read",
    "params": {
        "uri": "fpl://gameweeks/current"
    }
}
```

### **Analyze Player Fixtures**
```json
{
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
}
```

### **Compare Players**
```json
{
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