import os
import re
from pathlib import Path
from typing import Optional
from datetime import datetime

class StorageManager:
    """Manages storage of terms and conditions as markdown files."""
    
    def __init__(self, base_dir: str = "data/terms"):
        """Initialize the storage manager.
        
        Args:
            base_dir: Base directory to store markdown files
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize app name to create a valid filename."""
        # Remove invalid characters
        name = re.sub(r'[^\w\s-]', '', name).strip().lower()
        # Replace spaces with underscores
        name = re.sub(r'[\s]+', '_', name)
        return name
    
    def get_terms_path(self, app_name: str, version: Optional[str] = None) -> Path:
        """Get the file path for an app's terms and conditions.
        
        Args:
            app_name: Name of the application
            version: Optional version string
            
        Returns:
            Path to the markdown file
        """
        safe_name = self._sanitize_filename(app_name)
        if version:
            safe_version = self._sanitize_filename(version)
            filename = f"{safe_name}_{safe_version}.md"
        else:
            filename = f"{safe_name}.md"
        return self.base_dir / filename
    
    def save_terms(
        self, 
        app_name: str, 
        content: str, 
        source_url: Optional[str] = None,
        version: Optional[str] = None
    ) -> Path:
        """Save terms and conditions as a markdown file.
        
        Args:
            app_name: Name of the application
            content: Content of the terms and conditions
            source_url: URL where the terms were fetched from
            version: Optional version string
            
        Returns:
            Path to the saved file
        """
        file_path = self.get_terms_path(app_name, version)
        
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare markdown content
        timestamp = datetime.utcnow().isoformat()
        markdown = f"""# {app_name} - Terms and Conditions

- **Version**: {version or 'N/A'}
- **Source URL**: {source_url or 'N/A'}
- **Retrieved At**: {timestamp}

---

{content}
"""
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
            
        return file_path
    
    def load_terms(self, app_name: str, version: Optional[str] = None) -> Optional[str]:
        """Load terms and conditions from a markdown file.
        
        Args:
            app_name: Name of the application
            version: Optional version string
            
        Returns:
            Content of the terms and conditions, or None if not found
        """
        file_path = self.get_terms_path(app_name, version)
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    def get_latest_version(self, app_name: str) -> Optional[str]:
        """Get the latest version of terms for an app.
        
        Args:
            app_name: Name of the application
            
        Returns:
            Latest version string, or None if no versions found
        """
        safe_name = self._sanitize_filename(app_name)
        pattern = f"{safe_name}_*.md"
        versions = []
        
        for file in self.base_dir.glob(pattern):
            # Extract version from filename
            version = file.stem.replace(f"{safe_name}_", "", 1)
            if version and version != safe_name:  # Skip if no version found
                versions.append(version)
        
        if not versions:
            # Check for unversioned file
            unversioned = self.base_dir / f"{safe_name}.md"
            if unversioned.exists():
                return None
            return None
            
        # Simple version comparison (can be enhanced)
        return max(versions)
