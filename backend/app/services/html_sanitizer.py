import re
import bleach
from typing import Dict


def sanitize_html(html_content: str) -> str:
    """
    Sanitize HTML content by removing malicious scripts and source-site specific classes.
    """
    # Define allowed tags for WordPress content
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'b', 'i', 'u', 'strike', 's',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'a', 'img', 'blockquote', 'code', 'pre',
        'ul', 'ol', 'li',
        'div', 'span', 'figure', 'figcaption',
        'table', 'thead', 'tbody', 'tr', 'th', 'td'
    ]
    
    # Define allowed attributes
    allowed_attributes = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'blockquote': ['cite'],
        '*': ['class']  # Allow classes but we'll filter them below
    }
    
    # Clean HTML with bleach
    cleaned_html = bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
    
    # Remove source-site specific CSS classes
    # This regex removes class attributes that look like they're from specific themes
    cleaned_html = re.sub(
        r'class="[^"]*?(?:theme|template|widget|sidebar|header|footer|nav|menu)[^"]*?"',
        '',
        cleaned_html
    )
    
    return cleaned_html


def convert_to_gutenberg_blocks(html_content: str, image_url_map: Dict[str, str]) -> str:
    """
    Convert sanitized HTML to WordPress Gutenberg block format.
    """
    content = html_content
    
    # Replace image URLs with WordPress media URLs and wrap in Gutenberg blocks
    for old_url, new_url in image_url_map.items():
        # Match img tags with the old URL
        img_pattern = f'<img([^>]*?)src=["\']{re.escape(old_url)}["\']([^>]*?)>'
        
        # Extract alt text if present
        alt_match = re.search(r'alt=["\']([^"\']*)["\']', img_pattern)
        alt_text = alt_match.group(1) if alt_match else ""
        
        # Create Gutenberg image block
        gutenberg_block = f'''<!-- wp:image {{"sizeSlug":"large"}} -->
<figure class="wp-block-image size-large"><img src="{new_url}" alt="{alt_text}"/></figure>
<!-- /wp:image -->'''
        
        content = re.sub(img_pattern, gutenberg_block, content)
    
    return content
