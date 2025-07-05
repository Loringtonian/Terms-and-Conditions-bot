# Tavily MCP Server Documentation

## Overview

Tavily MCP Server allows you to use the Tavily API in your MCP (Model Context Protocol) clients. This documentation provides instructions for setting up and using the Tavily MCP server.

## Prerequisites

- Tavily API key (Get one at [app.tavily.com](https://app.tavily.com))
- Node.js (v20 or higher)
- MCP client (like Cursor or Claude Desktop)

## Installation

### Quick Start

```bash
npx -y tavily-mcp@0.1.3
```

### With Environment Variable

```bash
TAVILY_API_KEY=your_api_key_here npx -y tavily-mcp@0.1.3
```

## Configuration

### For Cursor (v0.45.6 or higher)

1. Open Cursor Settings
2. Navigate to Features > MCP Servers
3. Click on "+ Add New MCP Server"
4. Configure with these settings:
   - **Name**: tavily-mcp
   - **Type**: command
   - **Command**: 
     ```
     env TAVILY_API_KEY=your_api_key_here npx -y tavily-mcp@0.1.3
     ```

### For Claude Desktop

1. Create or edit the config file at:
   ```
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

2. Add this configuration (replace with your API key):
   ```json
   {
     "mcpServers": {
       "tavily-mcp": {
         "command": "npx",
         "args": ["-y", "tavily-mcp@0.1.2"],
         "env": {
           "TAVILY_API_KEY": "your_api_key_here"
         }
       }
     }
   }
   ```

## API Reference

### Base URL

```
https://api.tavily.com
```

### Authentication

All endpoints require an API key in the Authorization header:
```
Authorization: Bearer your_api_key_here
```

## Troubleshooting

### Common Issues

1. **API Key Not Recognized**
   - Ensure your API key is correctly set in the environment variables
   - Verify the API key is active at [app.tavily.com](https://app.tavily.com)

2. **Version Mismatch**
   - Make sure you're using a compatible version of the MCP server
   - Check for updates with `npm outdated -g tavily-mcp`

## Resources

- [Tavily Website](https://tavily.com)
- [API Documentation](https://docs.tavily.com)
- [GitHub Repository](https://github.com/tavily-ai/tavily-mcp)
- [MCP Documentation](https://modelcontextprotocol.io)
