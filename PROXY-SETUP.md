# Proxy Configuration for FPL API Access

This document explains how to configure proxies to bypass FPL API 403 Forbidden errors.

## 🚨 **Problem**

The Fantasy Premier League API sometimes returns **403 Forbidden** errors when accessed from:
- Cloud hosting providers (Render, Vercel, etc.)
- Certain geographic regions
- Datacenter IP ranges
- High-traffic server farms

## 🔧 **Solution: Proxy Rotation**

The MCP server now includes intelligent proxy rotation that:

1. **Tries direct connection first** (fastest when it works)
2. **Falls back to proxy rotation** on 403 errors
3. **Rotates through multiple proxies** for reliability
4. **Provides detailed logging** for troubleshooting

## ⚙️ **Configuration**

### **Environment Variables**

Set these in your Render environment:

```bash
# Enable/disable proxy usage
PROXY_ENABLED=true

# Comma-separated list of proxy URLs
PROXY_URLS="http://proxy1:port,http://proxy2:port,http://user:pass@proxy3:port"
```

### **Built-in Proxy List**

The server includes some free public proxies by default:
- `http://20.206.106.192:8123`
- `http://103.149.162.194:80`
- `http://47.74.152.29:8888`
- `http://103.167.109.69:80`
- `http://20.111.54.16:8123`

**⚠️ Warning**: Public proxies are unreliable and may be slow or offline.

## 🏆 **Recommended Proxy Services**

### **Commercial Proxy Services (Reliable)**

1. **ProxyMesh** - $10-50/month
   ```
   http://username:password@proxy.proxymesh.com:31280
   ```

2. **Bright Data** - $500+/month (enterprise)
   ```
   http://username:password@zproxy.lum-superproxy.io:22225
   ```

3. **SmartProxy** - $75+/month
   ```
   http://username:password@gate.smartproxy.com:10000
   ```

4. **ProxyRotator** - $30+/month
   ```
   http://username:password@rotating.proxies.com:8080
   ```

### **Free Alternatives**

1. **Cloudflare WARP** (limited)
2. **Public proxy lists** (unreliable)
3. **VPN with proxy** (manual setup)

## 🔨 **Setup Instructions**

### **Option 1: Use Built-in Proxies**
No configuration needed - proxies are automatically used when direct connection fails.

### **Option 2: Add Your Own Proxies**
1. Sign up for a proxy service (recommended: ProxyMesh)
2. Get your proxy URL with credentials
3. Set environment variable in Render:
   ```
   PROXY_URLS=http://user:pass@your-proxy.com:port
   ```

### **Option 3: Multiple Proxies for High Reliability**
```bash
PROXY_URLS=http://proxy1:port,http://proxy2:port,http://proxy3:port
```

## 📊 **How It Works**

```
1. Direct Request → FPL API
   ↓ (if 403)
2. Proxy 1 → FPL API
   ↓ (if fails)
3. Proxy 2 → FPL API
   ↓ (if fails)
4. Proxy 3 → FPL API
   ↓ (etc.)
5. Success or Final Error
```

## 🧪 **Testing**

### **Test Proxy Configuration**
```bash
# Check if proxies are configured
curl https://fantasyplmcp.onrender.com/mcp/info

# Test MCP tool with proxy fallback
curl -X POST https://fantasyplmcp.onrender.com/mcp/http \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"analyze_players","arguments":{"limit":1}}}'
```

### **Monitor Logs**
Check Render logs for proxy usage:
```
✅ Success via proxy http://proxy.example.com:8080
🔄 Direct request failed, trying proxy rotation
❌ All proxies failed - widespread blocking
```

## 🚨 **Troubleshooting**

### **Still Getting 403 Errors?**

1. **Check proxy status** - public proxies go offline frequently
2. **Try commercial proxies** - much more reliable
3. **Use residential proxies** - harder for APIs to detect
4. **Rotate proxy services** - spread requests across providers

### **Slow Responses?**

1. **Proxy latency** - choose proxies closer to UK
2. **Proxy quality** - free proxies are often slow
3. **Connection timeouts** - proxies may be overloaded

### **Logs Show Proxy Failures?**

```
Proxy http://proxy:port connection failed: ConnectTimeout
```

**Solutions:**
- Remove failed proxy from list
- Increase `PROXY_TIMEOUT` setting
- Use backup proxy service

## 🔐 **Security Notes**

- **Never use untrusted proxies** for sensitive data
- **Commercial proxies are safer** than free ones
- **HTTPS proxies preferred** for encrypted connections
- **Rotate credentials** regularly for commercial services

## 💡 **Pro Tips**

1. **Mix proxy types**: Combine datacenter + residential proxies
2. **Geographic spread**: Use proxies from different countries
3. **Load balancing**: Don't overload single proxy
4. **Monitor usage**: Track proxy performance and costs
5. **Backup plan**: Always have multiple proxy sources

## 📈 **Performance Impact**

- **Direct connection**: ~100-300ms
- **Datacenter proxy**: ~300-500ms
- **Residential proxy**: ~500-1000ms
- **Free proxy**: ~1000-5000ms (variable)

The system automatically uses the fastest available method.