from PIL import Image
import io
import httpx
from typing import Tuple


def download_and_process_image(image_url: str) -> Tuple[bytes, str]:
    """
    Download an image, process it (resize to max 1920px width, convert to WebP),
    and return the binary data and content type.
    """
    with httpx.Client() as client:
        response = client.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Open image with Pillow
        img = Image.open(io.BytesIO(response.content))
        
        # Convert to RGB if necessary (for PNG with transparency, etc.)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize if width exceeds 1920px
        max_width = 1920
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to WebP format
        output = io.BytesIO()
        img.save(output, format='WEBP', quality=85)
        
        return output.getvalue(), 'image/webp'
