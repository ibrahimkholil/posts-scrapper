import httpx
from typing import Dict, Optional
from app.services.encryption import decrypt_password


class WordPressClient:
    """Client for interacting with WordPress REST API."""
    
    def __init__(self, site_url: str, username: str, app_password: str):
        self.site_url = site_url.rstrip('/')
        self.username = username
        self.app_password = app_password
        self.base_url = f"{self.site_url}/wp-json/wp/v2"
        
        # Create authenticated client
        self.client = httpx.Client(
            auth=(self.username, self.app_password),
            timeout=30.0
        )
    
    def test_connection(self) -> bool:
        """Test if the WordPress connection is valid."""
        try:
            response = self.client.get(f"{self.base_url}/users/me")
            return response.status_code == 200
        except Exception:
            return False
    
    def upload_media(self, image_data: bytes, filename: str, content_type: str) -> Optional[str]:
        """
        Upload media to WordPress and return the media URL.
        """
        headers = {
            'Content-Disposition': f'attachment; filename={filename}',
            'Content-Type': content_type
        }
        
        try:
            response = self.client.post(
                f"{self.base_url}/media",
                files={'file': (filename, image_data, content_type)},
                headers=headers
            )
            
            if response.status_code == 201:
                data = response.json()
                return data.get('source_url')
            return None
        except Exception:
            return None
    
    def create_post(self, title: str, content: str, status: str = 'draft') -> Optional[Dict]:
        """
        Create a post in WordPress.
        """
        post_data = {
            'title': title,
            'content': content,
            'status': status
        }
        
        try:
            response = self.client.post(
                f"{self.base_url}/posts",
                json=post_data
            )
            
            if response.status_code == 201:
                return response.json()
            return None
        except Exception:
            return None
