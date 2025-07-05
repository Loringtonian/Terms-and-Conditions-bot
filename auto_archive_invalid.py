#!/usr/bin/env python3
"""
Auto-archive invalid terms files based on validation report.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def auto_archive_invalid_terms():
    """Automatically archive invalid terms files based on validation report."""
    
    project_root = Path(__file__).parent
    
    # Read the validation report
    report_file = None
    for file in project_root.glob('terms_validation_report_*.json'):
        if report_file is None or file.stat().st_mtime > report_file.stat().st_mtime:
            report_file = file
    
    if not report_file:
        print("❌ No validation report found!")
        return
    
    print(f"📖 Reading validation report: {report_file.name}")
    
    with open(report_file, 'r') as f:
        report = json.load(f)
    
    # Create archive directories
    archive_dir = project_root / 'archived_invalid_terms'
    archive_dir.mkdir(exist_ok=True)
    (archive_dir / 'terms_storage').mkdir(exist_ok=True)
    (archive_dir / 'terms_analysis').mkdir(exist_ok=True)
    (archive_dir / 'deep_analysis').mkdir(exist_ok=True)
    
    archived_services = []
    
    print(f"\n📦 Archiving {len(report['invalid_files'])} invalid files...")
    
    for file_info in report['invalid_files']:
        service_name = file_info['service_name']
        reason = file_info['validation']['reason']
        
        print(f"📦 Archiving {service_name}: {reason}")
        
        # Archive terms file
        terms_file = project_root / 'terms_storage' / f'{service_name}.md'
        if terms_file.exists():
            shutil.move(str(terms_file), str(archive_dir / 'terms_storage' / f'{service_name}.md'))
        
        # Archive analysis files
        analysis_info = file_info['has_analysis']
        if analysis_info['has_standard_analysis'] and analysis_info['analysis_file']:
            analysis_file = Path(analysis_info['analysis_file'])
            if analysis_file.exists():
                shutil.move(str(analysis_file), str(archive_dir / 'terms_analysis' / analysis_file.name))
        
        if analysis_info['has_deep_analysis'] and analysis_info['deep_analysis_file']:
            deep_file = Path(analysis_info['deep_analysis_file'])
            if deep_file.exists():
                shutil.move(str(deep_file), str(archive_dir / 'deep_analysis' / deep_file.name))
        
        archived_services.append(service_name)
    
    # Generate re-scrape list
    rescrape_file = project_root / f'rescrape_list_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    
    with open(rescrape_file, 'w') as f:
        f.write(f"# Services to Re-scrape\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n")
        f.write(f"# Total services: {len(archived_services)}\n")
        f.write(f"# Reason: Invalid content found during validation\n\n")
        
        # Group by content type for easier review
        content_types = {}
        for file_info in report['invalid_files']:
            content_type = file_info['validation']['content_type']
            if content_type not in content_types:
                content_types[content_type] = []
            content_types[content_type].append(file_info['service_name'])
        
        for content_type, services in content_types.items():
            f.write(f"# {content_type.replace('_', ' ').title()} ({len(services)} services)\n")
            for service in services:
                f.write(f"{service}\n")
            f.write(f"\n")
    
    print(f"\n✅ Successfully archived {len(archived_services)} invalid services")
    print(f"📁 Archived files location: {archive_dir}")
    print(f"📄 Re-scrape list saved to: {rescrape_file}")
    
    # Show remaining valid services
    print(f"\n📊 SUMMARY:")
    print(f"✅ Valid services remaining: {len(report['valid_files'])}")
    print(f"📦 Invalid services archived: {len(archived_services)}")
    print(f"🔄 Services needing re-scraping: {len(archived_services)}")
    
    print(f"\n✅ Valid services that remain:")
    for valid_file in report['valid_files']:
        confidence = valid_file['validation']['confidence']
        content_type = valid_file['validation']['content_type']
        print(f"   ✓ {valid_file['service_name']} ({confidence} confidence, {content_type})")

if __name__ == "__main__":
    auto_archive_invalid_terms()