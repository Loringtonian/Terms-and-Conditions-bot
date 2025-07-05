const fs = require('fs');

// Get the API key from the existing .env file if it exists
let apiKey = '';
try {
  const envContent = fs.readFileSync('.env', 'utf8');
  const match = envContent.match(/TAVILY_API_KEY=(.*)/);
  if (match && match[1]) {
    apiKey = match[1].trim();
    console.log('Found existing API key in .env file');
  }
} catch (err) {
  console.log('No existing .env file or error reading it');
}

// If no API key found, use the one from the backup file
if (!apiKey) {
  try {
    const backupContent = fs.readFileSync('.env.backup', 'utf8');
    const match = backupContent.match(/TAVILY_API_KEY=(.*)/);
    if (match && match[1]) {
      apiKey = match[1].trim();
      console.log('Found API key in .env.backup file');
    }
  } catch (err) {
    console.log('No backup file or error reading it');
  }
}

// If still no API key, prompt the user
if (!apiKey) {
  console.error('Error: Could not find TAVILY_API_KEY in any .env files');
  console.log('Please enter your Tavily API key (it should start with tvly-):');
  // The actual input will need to be provided by the user
  process.exit(1);
}

// Create the new .env file
const envContent = `# Tavily API Configuration
TAVILY_API_KEY=${apiKey}
`;

try {
  fs.writeFileSync('.env', envContent);
  console.log('Successfully created new .env file');
  console.log('File location:', require('path').resolve('.env'));
} catch (err) {
  console.error('Error writing .env file:', err.message);
  process.exit(1);
}
