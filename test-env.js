require('dotenv').config();

console.log('Testing environment variables:');
console.log('TAVILY_API_KEY exists:', !!process.env.TAVILY_API_KEY);
console.log('First 8 chars of key:', process.env.TAVILY_API_KEY ? 
  process.env.TAVILY_API_KEY.substring(0, 8) + '...' : 'undefined');

// Try to load the .env file directly
const fs = require('fs');
try {
  const envContent = fs.readFileSync('.env', 'utf8');
  console.log('\nContents of .env file:');
  console.log(envContent);
} catch (err) {
  console.error('Error reading .env file:', err.message);
}
