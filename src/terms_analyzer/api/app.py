from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import asyncio
import os
from dotenv import load_dotenv

from ..services.openai_service import OpenAIService
from ..models.analysis import TCAnalysis

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize services
openai_service = OpenAIService()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/analyze', methods=['POST'])
async def analyze_terms():
    """
    Analyze terms and conditions for a given app.
    
    Request body should be JSON with:
    {
        "app_name": "App Name",
        "terms_text": "Full text of terms and conditions...",
        "app_version": "1.0.0"  # optional
    }
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or 'app_name' not in data or 'terms_text' not in data:
        return jsonify({"error": "Missing required fields: app_name and terms_text are required"}), 400
    
    try:
        # Call the OpenAI service
        analysis = await openai_service.analyze_terms(
            app_name=data['app_name'],
            terms_text=data['terms_text'],
            app_version=data.get('app_version')
        )
        
        # Convert the Pydantic model to dict for JSON response
        return jsonify(analysis.model_dump())
        
    except Exception as e:
        return jsonify({"error": f"Error analyzing terms: {str(e)}"}), 500

if __name__ == '__main__':
    # Create the Flask app
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
