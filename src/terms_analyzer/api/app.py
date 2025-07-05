from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import asyncio
import os
import json
from dotenv import load_dotenv

# from ..services.openai_service import OpenAIService, TCAnalysis
# from ..services.tavily_service import TavilyService

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, 
     origins=["http://localhost:3000", "http://localhost:3001"], 
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True)

# Initialize services
# openai_service = OpenAIService()
# tavily_service = TavilyService()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/test-cors', methods=['GET'])
def test_cors():
    return jsonify({"message": "CORS is working!", "timestamp": "2025-07-05"}), 200

# Commented out for now - focus on serving existing analysis data
# @app.route('/analyze', methods=['POST'])
# async def analyze_terms():
#     """
#     Analyze terms and conditions for a given app.
#     """
#     return jsonify({"error": "Analysis endpoint not implemented yet"}), 501

# @app.route('/search', methods=['GET'])
# async def search_terms():
#     """
#     Search for terms and conditions for an app.
#     """
#     return jsonify({"error": "Search endpoint not implemented yet"}), 501

# @app.route('/api/analyze/text', methods=['POST'])
# async def analyze_text():
#     """
#     Analyze pasted terms and conditions text.
#     
#     Request body should be JSON with the following fields:
#     - text: The terms and conditions text to analyze
#     - app_name: Optional name of the app/service
#     
#     Returns:
#         JSON with analysis results in the same format as the service analysis
#     """
#     try:
#         data = request.get_json()
#         if not data or 'text' not in data:
#             return jsonify({"error": "Missing required field: text"}), 400
#             
#         text = data['text']
#         app_name = data.get('app_name', 'Pasted Terms')
#         
#         # Analyze the text using OpenAIService
#         analysis = openai_service.analyze_terms(
#             app_name=app_name,
#             terms_text=text
#         )
#         
#         # Convert the Pydantic model to dict for JSON serialization
#         return jsonify(analysis.dict())
#         
#     except Exception as e:
#         return jsonify({"error": f"Error analyzing text: {str(e)}"}), 500

@app.route('/services', methods=['GET'])
def get_services():
    """
    Get list of available services with analysis data.
    """
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.parent.parent.parent
        analysis_dir = project_root / 'terms_analysis'
        storage_dir = project_root / 'terms_storage'
        
        services = []
        
        # Get all analysis files
        if analysis_dir.exists():
            for analysis_file in analysis_dir.glob('*.json'):
                # Skip only deep analysis files
                if analysis_file.name.endswith('_deep_analysis.json'):
                    continue
                    
                service_name = analysis_file.stem.replace('_analysis', '')
                
                # Special handling for Netflix in your neighbourhood
                if service_name == 'netflix_in_your_neighbourhood':
                    display_name = 'Netflix'
                    service_id = 'netflix_in_your_neighbourhood'
                else:
                    display_name = service_name.replace('_', ' ').title()
                    service_id = service_name
                
                # Check if we have the markdown file for this service
                markdown_file = storage_dir / f"{service_name}.md"
                has_terms = markdown_file.exists()
                
                # Determine category and icon based on service name
                category, icon = get_service_category_and_icon(service_name)
                
                # Load analysis to get actual score for risk level
                try:
                    with open(analysis_file, 'r') as f:
                        analysis_data = json.load(f)
                        overall_score = analysis_data.get('overall_score', 5)
                        
                        # Determine risk level based on score
                        if overall_score >= 7:
                            risk_level = 'low'
                        elif overall_score >= 5:
                            risk_level = 'medium'
                        else:
                            risk_level = 'high'
                            
                except Exception:
                    risk_level = 'medium'
                
                services.append({
                    'id': service_id,
                    'name': display_name,
                    'displayName': display_name,
                    'category': category,
                    'icon': icon,
                    'riskLevel': risk_level,
                    'lastAnalyzed': '2025-07-05T00:00:00Z',
                    'hasAnalysis': True,
                    'hasTerms': has_terms
                })
        
        return jsonify({"services": services})
    except Exception as e:
        return jsonify({"error": f"Error getting services: {str(e)}"}), 500

@app.route('/analysis/<service_id>', methods=['GET'])
def get_analysis(service_id):
    """
    Get analysis data for a specific service.
    """
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.parent.parent.parent
        analysis_dir = project_root / 'terms_analysis'
        
        # Try to find the analysis file
        analysis_file = analysis_dir / f'{service_id}_analysis.json'
        deep_analysis_file = analysis_dir / 'deep_analysis' / f'{service_id}_deep_analysis.json'
        
        analysis_data = None
        
        # Check for deep analysis first
        if deep_analysis_file.exists():
            with open(deep_analysis_file, 'r') as f:
                raw_data = json.load(f)
                analysis_data = transform_deep_analysis_data(raw_data)
        elif analysis_file.exists():
            with open(analysis_file, 'r') as f:
                raw_data = json.load(f)
                analysis_data = transform_analysis_data(raw_data)
        else:
            return jsonify({"error": "Analysis not found"}), 404
        
        return jsonify(analysis_data)
    except Exception as e:
        return jsonify({"error": f"Error getting analysis: {str(e)}"}), 500

def get_service_category_and_icon(service_name):
    """
    Determine category and icon for a service based on its name.
    """
    service_name_lower = service_name.lower()
    
    if service_name_lower in ['netflix', 'netflix_in_your_neighbourhood', 'youtube', 'disney', 'hulu', 'prime_video', 'max', 'paramount', 'peacock_tv', 'crunchyroll']:
        return 'Entertainment', '🎬'
    elif service_name_lower in ['facebook', 'instagram', 'tiktok', 'snapchat', 'x', 'threads', 'linkedin', 'messenger']:
        return 'Social', '💬'
    elif service_name_lower in ['google_docs', 'google_sheets', 'google_slides', 'microsoft_word', 'microsoft_excel', 'microsoft_powerpoint', 'microsoft_teams', 'zoom']:
        return 'Productivity', '📊'
    elif service_name_lower in ['paypal', 'google_pay']:
        return 'Finance', '💰'
    elif service_name_lower in ['amazon_shopping', 'ebay', 'shein']:
        return 'Shopping', '🛒'
    else:
        return 'Other', '📱'

def transform_deep_analysis_data(raw_data):
    """
    Transform deep analysis data to match our frontend format.
    """
    concerns = []
    
    # Extract concerns from the deep analysis format
    if 'concerns_analyzed' in raw_data:
        for concern_data in raw_data['concerns_analyzed']:
            original_concern = concern_data.get('original_concern', {})
            concerns.append({
                'clause': original_concern.get('clause', ''),
                'severity': original_concern.get('severity', 'medium'),
                'explanation': original_concern.get('explanation', ''),
                'quote': original_concern.get('quote', ''),
                'clarity_analysis': concern_data.get('clarity_analysis')
            })
    
    # Calculate overall score based on severity
    high_severity_count = raw_data.get('total_high_severity_concerns', 0)
    overall_score = max(1, 10 - (high_severity_count * 2))  # Rough calculation
    
    return {
        'id': f"analysis-{raw_data.get('app_name', '').lower()}",
        'serviceName': raw_data.get('app_name', ''),
        'score': overall_score,
        'summary': f"Analysis reveals {high_severity_count} high-severity concerns that require attention.",
        'total_high_severity_concerns': high_severity_count,
        'user_friendliness_score': None,
        'data_collection_score': None,
        'legal_complexity_score': None,
        'concerns': concerns,
        'recommendations': [
            'Review privacy settings carefully',
            'Consider the implications of data sharing',
            'Read terms thoroughly before accepting',
            'Contact the service provider with questions about unclear terms'
        ],
        'red_flags': [concern['clause'] for concern in concerns if concern['severity'] == 'high']
    }

def transform_analysis_data(raw_data):
    """
    Transform regular analysis data to match our frontend format.
    """
    concerns = []
    
    # Extract concerns from the regular analysis format
    if 'privacy_concerns' in raw_data:
        for concern_data in raw_data['privacy_concerns']:
            concerns.append({
                'clause': concern_data.get('clause', ''),
                'severity': concern_data.get('severity', 'medium'),
                'explanation': concern_data.get('explanation', ''),
                'quote': concern_data.get('quote', '')
            })
    
    return {
        'id': f"analysis-{raw_data.get('app_name', '').lower()}",
        'serviceName': raw_data.get('app_name', ''),
        'score': raw_data.get('overall_score', 5),
        'summary': raw_data.get('summary', 'Analysis completed.'),
        'total_high_severity_concerns': len([c for c in concerns if c['severity'] == 'high']),
        'user_friendliness_score': raw_data.get('user_friendliness_score'),
        'data_collection_score': raw_data.get('data_collection_score'),
        'legal_complexity_score': raw_data.get('legal_complexity_score'),
        'concerns': concerns,
        'recommendations': [
            'Review privacy settings',
            'Consider data sharing implications',
            'Read terms carefully'
        ],
        'red_flags': raw_data.get('red_flags', [])
    }

if __name__ == '__main__':
    # Create the Flask app
    port = int(os.getenv('PORT', 5001))  # Changed from 5000 to 5001 due to macOS AirPlay conflict
    app.run(host='0.0.0.0', port=port, debug=True)
