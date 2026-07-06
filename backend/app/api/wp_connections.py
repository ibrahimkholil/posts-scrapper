from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db, WPConnection, User, UserRole
from app.schemas import WPConnectionCreate, WPConnectionResponse, WPConnectionTest
from app.services import WordPressClient, encrypt_password, decrypt_password
from app.core.security import decode_access_token
from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/wp-connections", tags=["WordPress Connections"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.get("/", response_model=List[WPConnectionResponse])
async def list_wp_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all WordPress connections (Admin only)."""
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    connections = db.query(WPConnection).all()
    return connections


@router.post("/", response_model=WPConnectionResponse)
async def create_wp_connection(
    connection_data: WPConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a new WordPress connection (Admin only)."""
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Encrypt the password before storing
    encrypted_password = encrypt_password(connection_data.wp_app_password)
    
    import uuid
    db_connection = WPConnection(
        id=str(uuid.uuid4()),
        site_name=connection_data.site_name,
        site_url=str(connection_data.site_url),
        wp_username=connection_data.wp_username,
        wp_app_password_encrypted=encrypted_password,
        created_by=current_user.id
    )
    
    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)
    
    return db_connection


@router.post("/test")
async def test_wp_connection(
    connection_data: WPConnectionTest,
    current_user: User = Depends(get_current_user)
):
    """Test WordPress connection before saving."""
    wp_client = WordPressClient(
        str(connection_data.site_url),
        connection_data.wp_username,
        connection_data.wp_app_password
    )
    
    is_valid = wp_client.test_connection()
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to connect to WordPress. Please check credentials."
        )
    
    return {"success": True, "message": "Connection successful"}
