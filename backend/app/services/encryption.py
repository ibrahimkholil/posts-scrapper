from cryptography.fernet import Fernet
from app.core.config import get_settings
import base64

settings = get_settings()


def get_or_create_fernet_key() -> bytes:
    """Get Fernet key from settings or generate a new one for development."""
    if settings.FERNET_KEY:
        return settings.FERNET_KEY.encode()
    
    # For development, generate a key (in production, this should be stored securely)
    key = Fernet.generate_key()
    return key


def encrypt_password(password: str) -> str:
    """Encrypt WordPress application password."""
    fernet = Fernet(get_or_create_fernet_key())
    encrypted = fernet.encrypt(password.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_password(encrypted_password: str) -> str:
    """Decrypt WordPress application password."""
    fernet = Fernet(get_or_create_fernet_key())
    decoded = base64.urlsafe_b64decode(encrypted_password.encode())
    decrypted = fernet.decrypt(decoded)
    return decrypted.decode()
