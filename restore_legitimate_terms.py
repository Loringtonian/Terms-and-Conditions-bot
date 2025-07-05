#!/usr/bin/env python3
"""
Restore legitimate terms files that were incorrectly archived.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def analyze_archived_file(file_path: Path) -> dict:
    """Analyze an archived file to determine if it's actually legitimate."""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"is_legitimate": False, "reason": f"Could not read file: {e}"}
    
    if len(content) < 500:
        return {"is_legitimate": False, "reason": "Content too short"}
    
    content_lower = content.lower()
    
    # Strong indicators this is NOT legitimate terms (news, government docs)
    strong_false_indicators = [
        'dear ms.', 'dear mr.', 'government of canada', 'we welcome this opportunity',
        'bbc.com', 'cnn.com', 'reuters.com', 'associated press',
        'breaking news', 'photo illustration', 'getty images',
        'parliament passed', 'the bill forces', 'senate on thursday',
        'our story', 'meet the team', 'company history',
        'press release', 'media kit', 'investor relations',
        'careers at', 'job opportunities', 'work with us'
    ]
    
    for indicator in strong_false_indicators:
        if indicator in content_lower:
            return {"is_legitimate": False, "reason": f"Contains clear non-terms indicator: {indicator}"}
    
    # Check if it's just navigation/headers without actual content
    lines = content.split('\n')
    content_lines = [line.strip() for line in lines if line.strip() and not line.startswith('#') and not line.startswith('*') and not line.startswith('-')]
    
    if len(content_lines) < 10:
        return {"is_legitimate": False, "reason": "Mostly navigation/headers, no substantial content"}
    
    # Strong indicators this IS legitimate terms
    strong_terms_indicators = [
        'terms of service', 'terms of use', 'privacy policy', 'user agreement',
        'service agreement', 'acceptable use', 'end user license',
        'these terms', 'this policy', 'our services', 'by using',
        'you agree', 'legally binding', 'effective date'
    ]
    
    strong_matches = sum(1 for indicator in strong_terms_indicators if indicator in content_lower)
    
    # Legal structure indicators
    legal_structure_indicators = [
        'personal information', 'data collection', 'intellectual property',
        'limitation of liability', 'governing law', 'arbitration',
        'termination', 'prohibited conduct', 'disclaimers'
    ]
    
    legal_matches = sum(1 for indicator in legal_structure_indicators if indicator in content_lower)
    
    # Check for section numbering
    has_numbered_sections = bool(re.search(r'\d+\.\s+[A-Z]', content))
    
    total_score = (strong_matches * 2) + legal_matches + (1 if has_numbered_sections else 0)
    
    if strong_matches >= 2 and total_score >= 6:
        return {
            "is_legitimate": True, 
            "reason": f"Legitimate terms document (strong: {strong_matches}, legal: {legal_matches}, score: {total_score})",
            "confidence": "high" if total_score >= 10 else "medium"
        }
    elif strong_matches >= 1 and total_score >= 4:
        return {
            "is_legitimate": True,
            "reason": f"Likely legitimate terms (strong: {strong_matches}, legal: {legal_matches}, score: {total_score})",
            "confidence": "medium"
        }
    else:
        return {
            "is_legitimate": False,
            "reason": f"Insufficient terms content (strong: {strong_matches}, legal: {legal_matches}, score: {total_score})"
        }

def restore_legitimate_files():
    """Restore files that were incorrectly archived."""
    
    project_root = Path(__file__).parent
    archive_dir = project_root / 'archived_invalid_terms'
    
    if not archive_dir.exists():
        print("❌ No archive directory found")
        return
    
    print("🔍 Analyzing archived files to identify legitimate terms...")
    
    # Check archived terms files
    archived_terms = archive_dir / 'terms_storage'
    legitimate_files = []
    
    if archived_terms.exists():
        for terms_file in archived_terms.glob('*.md'):
            service_name = terms_file.stem
            print(f"📋 Analyzing: {service_name}")
            
            analysis = analyze_archived_file(terms_file)
            
            if analysis['is_legitimate']:
                legitimate_files.append({
                    'service_name': service_name,
                    'terms_file': terms_file,
                    'analysis': analysis
                })
                print(f"✅ LEGITIMATE: {analysis['reason']}")
            else:
                print(f"❌ Invalid: {analysis['reason']}")
    
    if not legitimate_files:
        print("\n😞 No legitimate files found to restore")
        return
    
    print(f"\n📦 Found {len(legitimate_files)} legitimate files to restore")
    print("\nFiles to restore:")
    for file_info in legitimate_files:
        print(f"  ✓ {file_info['service_name']} ({file_info['analysis']['confidence']} confidence)")
    
    print(f"\n❓ Restore these {len(legitimate_files)} files? (y/N): ", end="")
    try:
        response = input().strip().lower()
    except EOFError:
        response = 'y'  # Auto-approve for non-interactive environments
    
    if response in ['y', 'yes']:
        restored_count = 0
        
        for file_info in legitimate_files:
            service_name = file_info['service_name']
            print(f"📦 Restoring: {service_name}")
            
            # Restore terms file
            source_terms = file_info['terms_file']
            dest_terms = project_root / 'terms_storage' / f'{service_name}.md'
            shutil.move(str(source_terms), str(dest_terms))
            
            # Restore analysis files if they exist
            analysis_file = archive_dir / 'terms_analysis' / f'{service_name}_analysis.json'
            if analysis_file.exists():
                dest_analysis = project_root / 'terms_analysis' / f'{service_name}_analysis.json'
                shutil.move(str(analysis_file), str(dest_analysis))
            
            deep_analysis_file = archive_dir / 'deep_analysis' / f'{service_name}_deep_analysis.json'
            if deep_analysis_file.exists():
                dest_deep = project_root / 'terms_analysis' / 'deep_analysis' / f'{service_name}_deep_analysis.json'
                dest_deep.parent.mkdir(exist_ok=True)
                shutil.move(str(deep_analysis_file), str(dest_deep))
            
            restored_count += 1
        
        print(f"\n✅ Successfully restored {restored_count} legitimate services!")
        print(f"📁 Files restored to terms_storage and terms_analysis directories")
        
        # Generate summary
        summary_file = project_root / f'restoration_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(summary_file, 'w') as f:
            f.write(f"# Restoration Summary\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Restored {restored_count} legitimate terms files\n\n")
            
            for file_info in legitimate_files:
                f.write(f"{file_info['service_name']}: {file_info['analysis']['reason']}\n")
        
        print(f"📄 Restoration summary saved to: {summary_file}")
        
    else:
        print("❌ Restoration cancelled")

if __name__ == "__main__":
    import re
    restore_legitimate_files()