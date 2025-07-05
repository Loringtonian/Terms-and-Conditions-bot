#!/usr/bin/env python3
"""
Simple interface to analyze terms and conditions using GPT-4o-latest
"""
import asyncio
import sys
from dotenv import load_dotenv
from src.terms_analyzer.services.analysis_service import AnalysisService

load_dotenv()

async def analyze_single_app(app_name: str):
    """Analyze a single app's terms"""
    analysis_service = AnalysisService()
    
    print(f"🔍 Analyzing {app_name}...")
    result = await analysis_service.analyze_app(app_name, save_results=True)
    
    if result:
        print(f"\n📋 ANALYSIS RESULTS FOR {app_name.upper()}:")
        print(f"=" * 50)
        print(f"📊 Overall Score: {result.overall_score}/10")
        print(f"👥 User Friendliness: {result.user_friendliness_score}/10")
        print(f"🔒 Data Collection: {result.data_collection_score}/10")
        print(f"📝 Legal Complexity: {result.legal_complexity_score}/10")
        print(f"\n📄 Summary:")
        print(f"   {result.summary}")
        
        if result.red_flags:
            print(f"\n🚩 Red Flags ({len(result.red_flags)}):")
            for flag in result.red_flags:
                print(f"   • {flag}")
        
        if result.privacy_concerns:
            print(f"\n🔒 Privacy Concerns ({len(result.privacy_concerns)}):")
            for concern in result.privacy_concerns:
                print(f"   • {concern.severity.upper()}: {concern.clause}")
                print(f"     {concern.explanation}")
                if concern.quote:
                    print(f"     Quote: \"{concern.quote[:100]}...\"")
    else:
        print(f"❌ Failed to analyze {app_name}")

async def analyze_multiple_apps(app_names: list):
    """Analyze multiple apps"""
    analysis_service = AnalysisService()
    
    results = await analysis_service.analyze_multiple_apps(app_names, delay_seconds=3)
    
    # Show summary
    print(f"\n📊 BATCH ANALYSIS SUMMARY:")
    print(f"=" * 50)
    
    successful_results = [(name, result) for name, result in results.items() if result]
    
    if successful_results:
        # Sort by overall score (worst first)
        successful_results.sort(key=lambda x: x[1].overall_score)
        
        print(f"🏆 RANKINGS (worst to best):")
        for i, (name, result) in enumerate(successful_results, 1):
            print(f"   {i:2d}. {name}: {result.overall_score}/10 overall")
    
    failed = [name for name, result in results.items() if result is None]
    if failed:
        print(f"\n❌ Failed to analyze: {', '.join(failed)}")

def show_available_apps():
    """Show available apps for analysis"""
    analysis_service = AnalysisService()
    apps = analysis_service.get_available_apps()
    
    print(f"📱 AVAILABLE APPS FOR ANALYSIS ({len(apps)}):")
    print(f"=" * 50)
    
    for i, app in enumerate(apps, 1):
        print(f"{i:2d}. {app}")

def show_analysis_summary():
    """Show summary of completed analyses"""
    analysis_service = AnalysisService()
    summary = analysis_service.get_analysis_summary()
    
    print(f"📊 ANALYSIS SUMMARY:")
    print(f"=" * 50)
    print(f"Total analyses completed: {summary['total_analyses']}")
    
    if summary['worst_scoring']:
        print(f"\n🚩 WORST SCORING APPS:")
        for app in summary['worst_scoring']:
            print(f"   • {app['app_name']}: {app['overall_score']}/10")
    
    if summary['best_scoring']:
        print(f"\n🏆 BEST SCORING APPS:")
        for app in summary['best_scoring']:
            print(f"   • {app['app_name']}: {app['overall_score']}/10")

async def main():
    if len(sys.argv) < 2:
        print("📋 TERMS AND CONDITIONS ANALYZER")
        print("=" * 50)
        print("Usage:")
        print("  python analyze_terms.py list                    - Show available apps")
        print("  python analyze_terms.py summary                 - Show analysis summary")
        print("  python analyze_terms.py analyze <app_name>      - Analyze single app")
        print("  python analyze_terms.py batch <app1> <app2>...  - Analyze multiple apps")
        print("\nExamples:")
        print("  python analyze_terms.py analyze TikTok")
        print("  python analyze_terms.py batch TikTok Instagram Facebook")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        show_available_apps()
    elif command == "summary":
        show_analysis_summary()
    elif command == "analyze":
        if len(sys.argv) < 3:
            print("❌ Please specify an app name to analyze")
            return
        app_name = " ".join(sys.argv[2:])
        await analyze_single_app(app_name)
    elif command == "batch":
        if len(sys.argv) < 3:
            print("❌ Please specify app names to analyze")
            return
        app_names = sys.argv[2:]
        await analyze_multiple_apps(app_names)
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    asyncio.run(main())