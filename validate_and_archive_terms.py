#!/usr/bin/env python3
"""
Comprehensive validation and archival script for terms and conditions files.
This script will:
1. Validate all terms files to identify which are legitimate terms vs other content
2. Archive invalid files (both .md and analysis) 
3. Generate a re-scraping list
4. Provide detailed reporting
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import re

class TermsValidator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.terms_storage = project_root / 'terms_storage'
        self.terms_analysis = project_root / 'terms_analysis'
        self.archive_dir = project_root / 'archived_invalid_terms'
        self.deep_analysis_dir = self.terms_analysis / 'deep_analysis'
        
        # Create archive directory structure
        self.archive_dir.mkdir(exist_ok=True)
        (self.archive_dir / 'terms_storage').mkdir(exist_ok=True)
        (self.archive_dir / 'terms_analysis').mkdir(exist_ok=True)
        (self.archive_dir / 'deep_analysis').mkdir(exist_ok=True)
        
        # Report file
        self.report_file = project_root / f'terms_validation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
    def validate_terms_content(self, content: str, service_name: str) -> Dict:
        """
        Enhanced validation for terms and conditions content.
        Returns detailed validation result with reasons.
        """
        if not content or len(content) < 200:
            return {
                'is_valid': False, 
                'reason': 'Content too short (less than 200 characters)',
                'confidence': 'high',
                'content_type': 'insufficient_content'
            }
        
        content_lower = content.lower()
        
        # Strong indicators this is NOT terms/privacy policy
        news_indicators = [
            # News sites and articles
            'bbc.com', 'cnn.com', 'reuters.com', 'ap.org', 'bloomberg.com',
            'techcrunch.com', 'theverge.com', 'engadget.com', 'ars-technica.com',
            'news article', 'breaking news', 'reuters', 'associated press',
            'getty images', 'photo illustration', 'shutterstock',
            
            # Legal/government content that's not terms
            'parliament passed', 'bill forces', 'legislation', 'regulatory framework',
            'government consultation', 'policy submission', 'regulatory impact',
            'committee report', 'senate', 'house of commons',
            
            # Generic website content
            'about us', 'contact us', 'our story', 'meet the team',
            'company history', 'press release', 'media kit',
            'investor relations', 'careers', 'job opportunities',
            
            # E-commerce/product pages
            'add to cart', 'buy now', 'product description', 'customer reviews',
            'shipping information', 'return policy' # Note: return policy could be legit
        ]
        
        for indicator in news_indicators:
            if indicator in content_lower:
                return {
                    'is_valid': False, 
                    'reason': f'Contains non-terms content indicator: {indicator}',
                    'confidence': 'high',
                    'content_type': 'news_or_general_content'
                }
        
        # Check for positive terms/privacy indicators
        strong_terms_indicators = [
            'terms of service', 'terms of use', 'user agreement', 'service agreement',
            'privacy policy', 'privacy notice', 'data policy',
            'acceptable use policy', 'code of conduct',
            'end user license agreement', 'eula',
            'terms and conditions', 'terms & conditions'
        ]
        
        moderate_terms_indicators = [
            'personal information', 'personal data', 'data collection', 'data processing',
            'cookies', 'tracking', 'analytics', 'advertising',
            'user content', 'intellectual property', 'copyright',
            'prohibited conduct', 'violations', 'termination',
            'disclaimers', 'limitation of liability', 'indemnification',
            'governing law', 'jurisdiction', 'arbitration', 'dispute resolution',
            'account', 'registration', 'subscription', 'payment'
        ]
        
        # Count matches
        strong_matches = sum(1 for indicator in strong_terms_indicators if indicator in content_lower)
        moderate_matches = sum(1 for indicator in moderate_terms_indicators if indicator in content_lower)
        
        # Calculate score
        terms_score = (strong_matches * 3) + moderate_matches
        
        # Check content structure
        has_sections = bool(re.search(r'\b(section|article|clause|paragraph)\s+\d+', content_lower))
        has_legal_structure = bool(re.search(r'\b\d+\.\s+[A-Z]', content))  # "1. TERMS"
        has_effective_date = bool(re.search(r'effective\s+date|last\s+updated|version|revised', content_lower))
        
        structure_score = sum([has_sections, has_legal_structure, has_effective_date])
        
        # Final validation logic
        if strong_matches >= 1 and terms_score >= 8:
            confidence = 'high' if terms_score >= 12 else 'medium'
            return {
                'is_valid': True,
                'reason': f'Valid terms content with {strong_matches} strong + {moderate_matches} moderate indicators',
                'confidence': confidence,
                'content_type': 'legitimate_terms',
                'scores': {
                    'strong_matches': strong_matches,
                    'moderate_matches': moderate_matches,
                    'structure_score': structure_score,
                    'total_score': terms_score
                }
            }
        elif terms_score >= 5 and structure_score >= 1:
            return {
                'is_valid': True,
                'reason': f'Likely valid terms with {terms_score} total indicators and legal structure',
                'confidence': 'medium',
                'content_type': 'likely_terms',
                'scores': {
                    'strong_matches': strong_matches,
                    'moderate_matches': moderate_matches,
                    'structure_score': structure_score,
                    'total_score': terms_score
                }
            }
        else:
            return {
                'is_valid': False,
                'reason': f'Insufficient terms indicators: {strong_matches} strong, {moderate_matches} moderate (score: {terms_score})',
                'confidence': 'high',
                'content_type': 'insufficient_terms_indicators',
                'scores': {
                    'strong_matches': strong_matches,
                    'moderate_matches': moderate_matches,
                    'structure_score': structure_score,
                    'total_score': terms_score
                }
            }
    
    def validate_all_terms(self) -> Dict:
        """Validate all terms files and return comprehensive report."""
        print("🔍 Starting comprehensive validation of all terms files...")
        
        report = {
            'validation_date': datetime.now().isoformat(),
            'total_files': 0,
            'valid_files': [],
            'invalid_files': [],
            'summary': {
                'valid_count': 0,
                'invalid_count': 0,
                'high_confidence_invalid': 0,
                'medium_confidence_invalid': 0,
                'content_types': {}
            }
        }
        
        if not self.terms_storage.exists():
            print("❌ Terms storage directory not found!")
            return report
        
        # Process all .md files
        for terms_file in self.terms_storage.glob('*.md'):
            service_name = terms_file.stem
            report['total_files'] += 1
            
            print(f"📋 Validating: {service_name}")
            
            try:
                with open(terms_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                validation_result = self.validate_terms_content(content, service_name)
                
                file_info = {
                    'service_name': service_name,
                    'file_name': terms_file.name,
                    'file_size': len(content),
                    'validation': validation_result,
                    'has_analysis': self.has_analysis_files(service_name)
                }
                
                if validation_result['is_valid']:
                    report['valid_files'].append(file_info)
                    report['summary']['valid_count'] += 1
                else:
                    report['invalid_files'].append(file_info)
                    report['summary']['invalid_count'] += 1
                    
                    if validation_result['confidence'] == 'high':
                        report['summary']['high_confidence_invalid'] += 1
                
                # Track content types
                content_type = validation_result['content_type']
                if content_type not in report['summary']['content_types']:
                    report['summary']['content_types'][content_type] = 0
                report['summary']['content_types'][content_type] += 1
                
            except Exception as e:
                print(f"❌ Error processing {terms_file}: {e}")
                report['invalid_files'].append({
                    'service_name': service_name,
                    'file_name': terms_file.name,
                    'validation': {
                        'is_valid': False,
                        'reason': f'Error reading file: {str(e)}',
                        'confidence': 'high',
                        'content_type': 'read_error'
                    },
                    'has_analysis': False
                })
                report['summary']['invalid_count'] += 1
                report['summary']['high_confidence_invalid'] += 1
        
        return report
    
    def has_analysis_files(self, service_name: str) -> Dict:
        """Check if service has analysis files."""
        analysis_file = self.terms_analysis / f'{service_name}_analysis.json'
        deep_analysis_file = self.deep_analysis_dir / f'{service_name}_deep_analysis.json'
        
        return {
            'has_standard_analysis': analysis_file.exists(),
            'has_deep_analysis': deep_analysis_file.exists(),
            'analysis_file': str(analysis_file) if analysis_file.exists() else None,
            'deep_analysis_file': str(deep_analysis_file) if deep_analysis_file.exists() else None
        }
    
    def archive_invalid_files(self, report: Dict, confidence_threshold: str = 'high') -> List[str]:
        """Archive invalid files and return list of services to re-scrape."""
        print(f"\n📦 Archiving invalid files with {confidence_threshold} confidence...")
        
        archived_services = []
        
        for file_info in report['invalid_files']:
            if file_info['validation']['confidence'] == confidence_threshold or confidence_threshold == 'all':
                service_name = file_info['service_name']
                print(f"📦 Archiving: {service_name}")
                
                # Archive terms file
                terms_file = self.terms_storage / f'{service_name}.md'
                if terms_file.exists():
                    shutil.move(str(terms_file), str(self.archive_dir / 'terms_storage' / f'{service_name}.md'))
                
                # Archive analysis files
                analysis_info = file_info['has_analysis']
                if analysis_info['has_standard_analysis']:
                    analysis_file = Path(analysis_info['analysis_file'])
                    shutil.move(str(analysis_file), str(self.archive_dir / 'terms_analysis' / analysis_file.name))
                
                if analysis_info['has_deep_analysis']:
                    deep_file = Path(analysis_info['deep_analysis_file'])
                    shutil.move(str(deep_file), str(self.archive_dir / 'deep_analysis' / deep_file.name))
                
                archived_services.append(service_name)
        
        return archived_services
    
    def generate_rescrape_list(self, archived_services: List[str]) -> None:
        """Generate a list of services that need to be re-scraped."""
        rescrape_file = self.project_root / f'rescrape_list_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        
        with open(rescrape_file, 'w') as f:
            f.write(f"# Services to Re-scrape\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Total services: {len(archived_services)}\n\n")
            
            for service in archived_services:
                f.write(f"{service}\n")
        
        print(f"📄 Re-scrape list saved to: {rescrape_file}")
    
    def run_full_validation(self, archive_confidence: str = 'high') -> None:
        """Run the complete validation and archival process."""
        print("🚀 Starting comprehensive terms validation and cleanup...")
        
        # Step 1: Validate all files
        report = self.validate_all_terms()
        
        # Step 2: Save report
        with open(self.report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 VALIDATION REPORT:")
        print(f"✅ Valid files: {report['summary']['valid_count']}")
        print(f"❌ Invalid files: {report['summary']['invalid_count']}")
        print(f"🔴 High confidence invalid: {report['summary']['high_confidence_invalid']}")
        print(f"📄 Full report saved to: {self.report_file}")
        
        # Step 3: Show content type breakdown
        print(f"\n📋 Content Type Breakdown:")
        for content_type, count in report['summary']['content_types'].items():
            print(f"   {content_type}: {count}")
        
        # Step 4: Archive invalid files
        if report['summary']['invalid_count'] > 0:
            print(f"\n❓ Archive invalid files with '{archive_confidence}' confidence? (y/N): ", end="")
            response = input().strip().lower()
            
            if response in ['y', 'yes']:
                archived_services = self.archive_invalid_files(report, archive_confidence)
                self.generate_rescrape_list(archived_services)
                
                print(f"\n✅ Archived {len(archived_services)} invalid services")
                print(f"📁 Files moved to: {self.archive_dir}")
            else:
                print("❌ Archival cancelled")
        
        print(f"\n🎉 Validation complete!")

def main():
    project_root = Path(__file__).parent
    validator = TermsValidator(project_root)
    
    print("🔍 Terms & Conditions Validator")
    print("=" * 50)
    
    # Run with high confidence archival by default
    validator.run_full_validation(archive_confidence='high')

if __name__ == "__main__":
    main()