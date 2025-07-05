require('dotenv').config();
const { spawn } = require('child_process');

// Check if API key is loaded
if (!process.env.TAVILY_API_KEY) {
  console.error('Error: TAVILY_API_KEY not found in .env file');
  process.exit(1);
}

console.log('Starting Tavily MCP server with API key:', process.env.TAVILY_API_KEY.substring(0, 5) + '...');

// Start the Tavily MCP server
const tavily = spawn('npx', ['@mseep/tavily-mcp'], {
  env: {
    ...process.env,
    TAVILY_API_KEY: process.env.TAVILY_API_KEY
  },
  stdio: 'inherit'
});

tavily.on('error', (error) => {
  console.error('Failed to start Tavily MCP server:', error);
});

tavily.on('close', (code) => {
  console.log(`Tavily MCP server process exited with code ${code}`);
});
