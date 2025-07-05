from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import asyncio
import os
import json
import threading
import time
from dotenv import load_dotenv

try:
    from ..services.openai_service import OpenAIService
    from ..services.tavily_service import TavilyService
    from ..services.analysis_service import AnalysisService
except ImportError:
    # Fallback if relative import fails
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from services.openai_service import OpenAIService
    from services.tavily_service import TavilyService
    from services.analysis_service import AnalysisService

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, 
     origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"], 
     methods=['GET', 'POST', 'OPTIONS', 'PUT', 'DELETE'],
     allow_headers=['Content-Type', 'Authorization', 'Accept'],
     supports_credentials=True)

# Initialize services
try:
    openai_service = OpenAIService()
    tavily_service = TavilyService()
    analysis_service = AnalysisService()
except Exception as e:
    print(f"Warning: Could not initialize services: {e}")
    openai_service = None
    tavily_service = None
    analysis_service = None

# Request tracking for on-demand scraping
scraping_requests = {}  # {request_id: {status, progress, result, error}}

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

@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    """
    Analyze pasted terms and conditions text.
    
    Request body should be JSON with the following fields:
    - text: The terms and conditions text to analyze
    - app_name: Optional name of the app/service
    
    Returns:
        JSON with analysis results in the same format as the service analysis
    """
    try:
        if not openai_service:
            return jsonify({"error": "Analysis service not available"}), 503
            
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Missing required field: text"}), 400
            
        text = data['text']
        app_name = data.get('app_name', 'Pasted Terms')
        
        # Analyze the text using OpenAIService
        analysis = openai_service.analyze_terms(
            app_name=app_name,
            terms_text=text
        )
        
        # Convert the Pydantic model to dict for JSON serialization
        raw_data = analysis.dict()
        
        # Transform to match frontend format
        transformed_data = transform_analysis_data(raw_data)
        
        return jsonify(transformed_data)
        
    except Exception as e:
        return jsonify({"error": f"Error analyzing text: {str(e)}"}), 500

@app.route('/api/request-analysis', methods=['POST'])
def request_new_analysis():
    """
    Request analysis for a new service not in our database.
    
    Request body: {"service_name": "ServiceName", "known_url": "optional_url"}
    Returns: {"request_id": str, "status": "queued", "estimated_time": int}
    """
    try:
        if not tavily_service or not analysis_service:
            return jsonify({"error": "Scraping services not available"}), 503
            
        data = request.get_json()
        if not data or 'service_name' not in data:
            return jsonify({"error": "Missing required field: service_name"}), 400
            
        service_name = data['service_name'].strip()
        known_url = data.get('known_url', '').strip()
        
        if not service_name:
            return jsonify({"error": "Service name cannot be empty"}), 400
        
        # Generate unique request ID
        import uuid
        request_id = str(uuid.uuid4())
        
        # Initialize request tracking
        scraping_requests[request_id] = {
            'status': 'queued',
            'progress': 0,
            'service_name': service_name,
            'known_url': known_url,
            'created_at': time.time(),
            'result': None,
            'error': None
        }
        
        # Start scraping in background thread
        thread = threading.Thread(
            target=scrape_and_analyze_service,
            args=(request_id, service_name, known_url)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "request_id": request_id,
            "status": "queued",
            "estimated_time": 60,  # 1 minute estimate with Tavily
            "message": f"Analysis request for '{service_name}' has been queued"
        })
        
    except Exception as e:
        return jsonify({"error": f"Error creating analysis request: {str(e)}"}), 500

@app.route('/api/request-status/<request_id>', methods=['GET'])
def get_request_status(request_id):
    """
    Get the status of a scraping request.
    
    Returns: {"status": str, "progress": int, "result": dict, "error": str}
    """
    try:
        if request_id not in scraping_requests:
            return jsonify({"error": "Request not found"}), 404
            
        request_info = scraping_requests[request_id]
        
        # Clean up old completed requests (older than 10 minutes)
        if request_info['status'] in ['completed', 'failed']:
            if time.time() - request_info.get('completed_at', 0) > 600:
                del scraping_requests[request_id]
                return jsonify({"error": "Request expired"}), 410
        
        response = {
            "request_id": request_id,
            "status": request_info['status'],
            "progress": request_info['progress'],
            "service_name": request_info['service_name']
        }
        
        if request_info['status'] == 'completed':
            response['result'] = request_info['result']
        elif request_info['status'] == 'failed':
            response['error'] = request_info['error']
            
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": f"Error getting request status: {str(e)}"}), 500

def scrape_and_analyze_service(request_id, service_name, known_url=None):
    """
    Background function to scrape and analyze a service using Tavily.
    Updates the request status throughout the process.
    """
    try:
        # Update status to processing
        scraping_requests[request_id]['status'] = 'processing'
        scraping_requests[request_id]['progress'] = 10
        
        # Step 1: Scrape terms using Tavily
        scraping_requests[request_id]['progress'] = 20
        print(f"Starting Tavily scrape for {service_name}")
        
        # Use Tavily for faster scraping
        result = None
        try:
            if known_url:
                # If URL is provided, try to extract directly
                import asyncio
                content = asyncio.run(tavily_service.extract_terms_text(known_url))
                if content and len(content) > 500:
                    # Save to storage manually
                    saved_path = tavily_service.storage.save_terms(
                        app_name=service_name,
                        content=content,
                        source_url=known_url
                    )
                    result = {
                        'success': True,
                        'app_name': service_name,
                        'terms_url': known_url,
                        'terms_text': content,
                        'saved_path': str(saved_path)
                    }
                else:
                    result = {'success': False}
            else:
                # Use Tavily's search and extract functionality
                import asyncio
                terms_data = asyncio.run(tavily_service.find_terms_for_app(service_name, save_to_storage=True))
                if terms_data:
                    result = {
                        'success': True,
                        **terms_data
                    }
                else:
                    result = {'success': False}
        except Exception as tavily_error:
            print(f"Tavily error: {tavily_error}")
            result = {'success': False}
        
        if not result or not result.get('success'):
            scraping_requests[request_id]['status'] = 'failed'
            if known_url:
                scraping_requests[request_id]['error'] = f'Failed to extract terms from the provided URL: {known_url}. The URL may be incorrect or the content may not be accessible.'
            else:
                scraping_requests[request_id]['error'] = f'Could not find terms and conditions for "{service_name}". The service may not have publicly accessible terms, or try providing a specific URL to the terms page.'
            scraping_requests[request_id]['completed_at'] = time.time()
            return
        
        scraping_requests[request_id]['progress'] = 70
        
        # Step 2: Analyze the scraped terms
        print(f"Starting analysis for {service_name}")
        try:
            import asyncio
            analysis_result = asyncio.run(analysis_service.analyze_app(service_name, save_results=True))
            
            if not analysis_result:
                scraping_requests[request_id]['status'] = 'failed'
                scraping_requests[request_id]['error'] = 'Failed to analyze terms'
                scraping_requests[request_id]['completed_at'] = time.time()
                return
            
            scraping_requests[request_id]['progress'] = 95
            
            # Step 3: Transform for frontend
            transformed_result = transform_analysis_data(analysis_result.dict())
            
            scraping_requests[request_id]['status'] = 'completed'
            scraping_requests[request_id]['progress'] = 100
            scraping_requests[request_id]['result'] = transformed_result
            scraping_requests[request_id]['completed_at'] = time.time()
            
            print(f"Completed analysis for {service_name}")
            
        except Exception as e:
            print(f"Analysis error for {service_name}: {e}")
            scraping_requests[request_id]['status'] = 'failed'
            scraping_requests[request_id]['error'] = f'Analysis failed: {str(e)}'
            scraping_requests[request_id]['completed_at'] = time.time()
            
    except Exception as e:
        print(f"Scraping error for {service_name}: {e}")
        scraping_requests[request_id]['status'] = 'failed'
        scraping_requests[request_id]['error'] = f'Scraping failed: {str(e)}'
        scraping_requests[request_id]['completed_at'] = time.time()

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
                
                # Check if we have a valid terms file for this service
                markdown_file = storage_dir / f"{service_name}.md"
                has_terms = False
                
                if markdown_file.exists() and markdown_file.stat().st_size > 100:
                    try:
                        with open(markdown_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        validation_result = validate_terms_content(content, service_name)
                        has_terms = validation_result['is_valid']
                    except Exception:
                        has_terms = False
                
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
        
        # Also try alternative naming patterns for deep analysis
        alt_deep_analysis_patterns = []
        if service_id == 'netflix_in_your_neighbourhood':
            alt_deep_analysis_patterns.append(analysis_dir / 'deep_analysis' / 'netflix_deep_analysis.json')
        
        # Try the base service name if the full ID doesn't work
        if '_' in service_id:
            base_name = service_id.split('_')[0]  # e.g., 'netflix' from 'netflix_in_your_neighbourhood'
            alt_deep_analysis_patterns.append(analysis_dir / 'deep_analysis' / f'{base_name}_deep_analysis.json')
        
        analysis_data = None
        
        # Check for deep analysis first
        deep_analysis_data = None
        regular_analysis_data = None
        
        if deep_analysis_file.exists():
            with open(deep_analysis_file, 'r') as f:
                deep_raw_data = json.load(f)
                deep_analysis_data = transform_deep_analysis_data(deep_raw_data)
        else:
            # Try alternative patterns
            for alt_file in alt_deep_analysis_patterns:
                if alt_file.exists():
                    with open(alt_file, 'r') as f:
                        deep_raw_data = json.load(f)
                        deep_analysis_data = transform_deep_analysis_data(deep_raw_data)
                    break
        
        # Also load regular analysis for scores if deep analysis exists
        if analysis_file.exists():
            with open(analysis_file, 'r') as f:
                regular_raw_data = json.load(f)
                regular_analysis_data = transform_analysis_data(regular_raw_data)
        
        # Combine deep analysis with regular analysis scores
        if deep_analysis_data and regular_analysis_data:
            analysis_data = deep_analysis_data.copy()
            # Override scores from regular analysis
            analysis_data['user_friendliness_score'] = regular_analysis_data['user_friendliness_score']
            analysis_data['data_collection_score'] = regular_analysis_data['data_collection_score']
            analysis_data['legal_complexity_score'] = regular_analysis_data['legal_complexity_score']
            # Also use the regular analysis score and summary
            analysis_data['score'] = regular_analysis_data['score']
            analysis_data['summary'] = regular_analysis_data['summary']
        elif deep_analysis_data:
            analysis_data = deep_analysis_data
        elif regular_analysis_data:
            analysis_data = regular_analysis_data
        else:
            analysis_data = None
        
        if analysis_data is None:
            return jsonify({"error": "Analysis not found"}), 404
        
        return jsonify(analysis_data)
    except Exception as e:
        return jsonify({"error": f"Error getting analysis: {str(e)}"}), 500

@app.route('/terms/<service_id>', methods=['GET'])
def get_terms(service_id):
    """
    Get the original terms and conditions text for a specific service.
    """
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.parent.parent.parent
        storage_dir = project_root / 'terms_storage'
        
        # Try to find the terms file
        terms_file = storage_dir / f'{service_id}.md'
        
        if not terms_file.exists():
            return jsonify({"error": f"Original terms document not available for this service. This service has analysis but the source terms document was not saved."}), 404
        
        with open(terms_file, 'r', encoding='utf-8') as f:
            terms_text = f.read()
        
        return jsonify({
            "service_id": service_id,
            "terms_text": terms_text
        })
    except Exception as e:
        return jsonify({"error": f"Error getting terms: {str(e)}"}), 500

@app.route('/api/top-bottom-services', methods=['GET'])
def get_top_bottom_services():
    """
    Get the top 3 and bottom 3 rated services based on overall scores.
    
    Returns: {"top_services": [...], "bottom_services": [...]}
    """
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.parent.parent.parent
        analysis_dir = project_root / 'terms_analysis'
        
        if not analysis_dir.exists():
            return jsonify({"error": "Analysis directory not found"}), 404
        
        services_with_scores = []
        
        # Get storage directory to check for terms files
        storage_dir = project_root / 'terms_storage'
        
        # Get all analysis files
        for analysis_file in analysis_dir.glob('*.json'):
            # Skip deep analysis files
            if analysis_file.name.endswith('_deep_analysis.json'):
                continue
                
            try:
                with open(analysis_file, 'r') as f:
                    analysis_data = json.load(f)
                
                service_name = analysis_file.stem.replace('_analysis', '')
                
                # Only include services that have valid terms files with actual terms content
                markdown_file = storage_dir / f"{service_name}.md"
                has_valid_terms = False
                
                if markdown_file.exists() and markdown_file.stat().st_size > 100:
                    try:
                        with open(markdown_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        validation_result = validate_terms_content(content, service_name)
                        has_valid_terms = validation_result['is_valid']
                        if not has_valid_terms:
                            print(f"Skipping {service_name} - invalid terms content: {validation_result['reason']}")
                    except Exception as e:
                        print(f"Skipping {service_name} - error reading terms file: {e}")
                
                # Skip services without valid terms (these are stale/deleted services or invalid content)
                if not has_valid_terms:
                    continue
                
                overall_score = analysis_data.get('overall_score', 0)
                app_name = analysis_data.get('app_name', service_name.replace('_', ' ').title())
                
                # Get category and icon
                category, icon = get_service_category_and_icon(service_name)
                
                # Determine risk level based on score
                if overall_score >= 7:
                    risk_level = 'low'
                    risk_color = 'text-green-600'
                elif overall_score >= 5:
                    risk_level = 'medium'
                    risk_color = 'text-yellow-600'
                else:
                    risk_level = 'high'
                    risk_color = 'text-red-600'
                
                services_with_scores.append({
                    'id': service_name,
                    'displayName': app_name,
                    'category': category,
                    'icon': icon,
                    'overall_score': overall_score,
                    'risk_level': risk_level,
                    'risk_color': risk_color,
                    'user_friendliness_score': analysis_data.get('user_friendliness_score'),
                    'data_collection_score': analysis_data.get('data_collection_score'),
                    'legal_complexity_score': analysis_data.get('legal_complexity_score'),
                    'red_flags_count': len(analysis_data.get('red_flags', []))
                })
                
            except Exception as e:
                print(f"Error processing {analysis_file}: {e}")
                continue
        
        # Sort by overall score
        services_with_scores.sort(key=lambda x: x['overall_score'])
        
        # Get bottom 5 (worst) and top 5 (best)
        bottom_services = services_with_scores[:5]
        top_services = services_with_scores[-5:][::-1]  # Reverse to show highest first
        
        return jsonify({
            "top_services": top_services,
            "bottom_services": bottom_services,
            "total_analyzed": len(services_with_scores)
        })
        
    except Exception as e:
        return jsonify({"error": f"Error getting top/bottom services: {str(e)}"}), 500

@app.route('/validate-all-terms', methods=['GET'])
def validate_all_terms():
    """
    Validate all terms files and return a report of which are valid/invalid.
    """
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.parent.parent.parent
        storage_dir = project_root / 'terms_storage'
        
        if not storage_dir.exists():
            return jsonify({"error": "Terms storage directory not found"}), 404
        
        validation_results = {
            "valid": [],
            "invalid": [],
            "summary": {
                "total_files": 0,
                "valid_count": 0,
                "invalid_count": 0
            }
        }
        
        # Check all .md files in storage
        for terms_file in storage_dir.glob('*.md'):
            service_name = terms_file.stem
            validation_results["summary"]["total_files"] += 1
            
            try:
                with open(terms_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                validation_result = validate_terms_content(content, service_name)
                
                result_entry = {
                    "service_name": service_name,
                    "file_name": terms_file.name,
                    "reason": validation_result['reason'],
                    "content_length": len(content)
                }
                
                if validation_result['is_valid']:
                    validation_results["valid"].append(result_entry)
                    validation_results["summary"]["valid_count"] += 1
                else:
                    validation_results["invalid"].append(result_entry)
                    validation_results["summary"]["invalid_count"] += 1
                    
            except Exception as e:
                validation_results["invalid"].append({
                    "service_name": service_name,
                    "file_name": terms_file.name,
                    "reason": f"Error reading file: {str(e)}",
                    "content_length": 0
                })
                validation_results["summary"]["invalid_count"] += 1
        
        return jsonify(validation_results)
    except Exception as e:
        return jsonify({"error": f"Error validating terms: {str(e)}"}), 500

def validate_terms_content(content: str, service_name: str) -> dict:
    """
    Validate if content is actually terms of service/privacy policy.
    Returns dict with 'is_valid' boolean and 'reason' string.
    """
    if not content or len(content) < 100:
        return {'is_valid': False, 'reason': 'Content too short'}
    
    content_lower = content.lower()
    
    # Check for news website indicators (strong signals it's NOT terms)
    news_indicators = [
        'bbc.com', 'cnn.com', 'reuters.com', 'ap.org', 'bloomberg.com',
        'techcrunch.com', 'theverge.com', 'engadget.com', 'ars-technica.com',
        'news article', 'breaking news', 'reuters', 'associated press',
        'photo illustration', 'getty images', 'in this photo',
        'parliament passed', 'bill forces'
    ]
    
    for indicator in news_indicators:
        if indicator in content_lower:
            return {'is_valid': False, 'reason': f'Contains news content indicator: {indicator}'}
    
    # Check for terms/privacy policy indicators (positive signals)
    terms_indicators = [
        'terms of service', 'terms of use', 'user agreement', 'privacy policy',
        'data collection', 'cookies', 'we collect', 'personal information',
        'your data', 'user content', 'intellectual property', 'license',
        'prohibited conduct', 'termination', 'disclaimers', 'limitation of liability',
        'governing law', 'arbitration', 'acceptable use'
    ]
    
    terms_matches = sum(1 for indicator in terms_indicators if indicator in content_lower)
    
    # Require at least 2 terms-related indicators (reduced from 3)
    if terms_matches < 2:
        return {'is_valid': False, 'reason': f'Only {terms_matches} terms indicators found, need at least 2'}
    
    # Check content length - terms should be substantial
    if len(content) < 1000:
        return {'is_valid': False, 'reason': 'Content too short for terms of service'}
    
    # Additional check: if it looks like a news article structure
    if any(phrase in content_lower for phrase in ['facebook and instagram to', 'meta has said', 'the bill forces']):
        return {'is_valid': False, 'reason': 'Content appears to be a news article about the service, not terms of service'}
    
    return {'is_valid': True, 'reason': f'Valid terms content with {terms_matches} indicators'}

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
        'user_friendliness_score': raw_data.get('user_friendliness_score'),
        'data_collection_score': raw_data.get('data_collection_score'),
        'legal_complexity_score': raw_data.get('legal_complexity_score'),
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
