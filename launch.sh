#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the frontend directory
cd "$SCRIPT_DIR/frontend" || { echo "❌ Error: Could not change to frontend directory"; exit 1; }

echo "🚀 Starting development server..."
echo "📂 Running from: $(pwd)"
echo "🌐 The app will be available at: http://localhost:3000"
echo ""
echo "🔄 Starting Next.js development server..."

exec npm run dev
