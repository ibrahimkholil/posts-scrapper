"""
Database initialization script.
Creates an admin user if one doesn't exist.
"""
from sqlalchemy.orm import Session
from app.models.database import SessionLocal, User, UserRole
from app.core.security import get_password_hash
import uuid

def init_db():
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        
        if not admin:
            # Create admin user
            admin = User(
                id=str(uuid.uuid4()),
                email="admin@example.com",
                role=UserRole.admin,
                hashed_password=get_password_hash("admin123")
            )
            db.add(admin)
            db.commit()
            print("✓ Created admin user: admin@example.com / admin123")
        else:
            print("✓ Admin user already exists")
        
        # Create editor user for testing
        editor = db.query(User).filter(User.email == "editor@example.com").first()
        if not editor:
            editor = User(
                id=str(uuid.uuid4()),
                email="editor@example.com",
                role=UserRole.editor,
                hashed_password=get_password_hash("editor123")
            )
            db.add(editor)
            db.commit()
            print("✓ Created editor user: editor@example.com / editor123")
        else:
            print("✓ Editor user already exists")
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialization complete!")
