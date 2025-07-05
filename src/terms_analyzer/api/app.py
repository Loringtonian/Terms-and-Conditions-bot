from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import asyncio
import os
from dotenv import load_dotenv

from ..services.openai_service import OpenAIService
from ..services.tavily_service import TavilyService
from ..models.analysis import TCAnalysis

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize services
openai_service = OpenAIService()
tavily_service = TavilyService()

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
        "terms_text": "Full text of terms and conditions...",  # optional if auto_fetch is True
        "app_version": "1.0.0",  # optional
        "auto_fetch": true  # optional, default false
    }
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or 'app_name' not in data:
        return jsonify({"error": "Missing required field: app_name"}), 400
    
    auto_fetch = data.get('auto_fetch', False)
    
    try:
        terms_text = data.get('terms_text')
        
        # If no terms text provided and auto_fetch is True, try to find it
        if not terms_text and auto_fetch:
            terms_data = await tavily_service.find_terms_for_app(data['app_name'])
            if terms_data:
                terms_text = terms_data['terms_text']
                source_url = terms_data.get('terms_url')
            else:
                return jsonify({"error": "Could not automatically find terms and conditions"}), 404
        
        if not terms_text:
            return jsonify({"error": "No terms text provided and auto_fetch is false"}), 400
        
        # Call the OpenAI service
        analysis = await openai_service.analyze_terms(
            app_name=data['app_name'],
            terms_text=terms_text,
            app_version=data.get('app_version')
        )
        
        # Add source URL if available
        result = analysis.model_dump()
        if 'source_url' in locals():
            result['source_url'] = source_url
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Error analyzing terms: {str(e)}"}), 500

@app.route('/search', methods=['GET'])
async def search_terms():
    """
    Search for terms and conditions for an app.
    
    Query parameters:
    - q: App name to search for
    - limit: Maximum number of results (default: 5)
    """
    app_name = request.args.get('q')
    if not app_name:
        return jsonify({"error": "Missing query parameter: q"}), 400
    
    try:
        results = await tavily_service.search_terms_and_conditions(app_name)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": f"Error searching for terms: {str(e)}"}), 500

if __name__ == '__main__':
    # Create the Flask app
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
