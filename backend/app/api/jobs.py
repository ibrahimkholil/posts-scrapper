from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db, ImportJob, JobStatus, WPConnection
from app.schemas import ImportJobCreate, ImportJobResponse, ImportJobBulk
from app.workers.tasks import process_import_job
from app.core.security import decode_access_token
from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/jobs", tags=["Import Jobs"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user."""
    from app.models.database import User
    
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


@router.post("/", response_model=ImportJobResponse)
async def create_import_job(
    job_data: ImportJobCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit a new URL for scraping."""
    import uuid
    
    # Check if URL already exists
    existing_job = db.query(ImportJob).filter(
        ImportJob.source_url == str(job_data.source_url)
    ).first()
    
    if existing_job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This URL has already been imported"
        )
    
    # Verify WP connection exists
    wp_connection = db.query(WPConnection).filter(
        WPConnection.id == job_data.target_wp_connection_id
    ).first()
    
    if not wp_connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WordPress connection not found"
        )
    
    # Create the job
    db_job = ImportJob(
        id=str(uuid.uuid4()),
        source_url=str(job_data.source_url),
        target_wp_connection_id=job_data.target_wp_connection_id,
        status=JobStatus.pending
    )
    
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    # Queue the background task
    process_import_job.delay(db_job.id)
    
    return db_job


@router.get("/{job_id}", response_model=ImportJobResponse)
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Check the real-time status of a specific job."""
    job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job


@router.get("/", response_model=List[ImportJobResponse])
async def list_jobs(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    status_filter: JobStatus = None,
    limit: int = 50,
    offset: int = 0
):
    """List all import history with filters."""
    query = db.query(ImportJob)
    
    if status_filter:
        query = query.filter(ImportJob.status == status_filter)
    
    jobs = query.order_by(ImportJob.created_at.desc()).offset(offset).limit(limit).all()
    
    return jobs


@router.post("/bulk", response_model=List[ImportJobResponse])
async def bulk_import_jobs(
    job_data: ImportJobBulk,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Accept a CSV of URLs for batch processing."""
    import uuid
    
    # Verify WP connection exists
    wp_connection = db.query(WPConnection).filter(
        WPConnection.id == job_data.target_wp_connection_id
    ).first()
    
    if not wp_connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WordPress connection not found"
        )
    
    created_jobs = []
    
    for url in job_data.urls:
        # Check if URL already exists
        existing_job = db.query(ImportJob).filter(
            ImportJob.source_url == str(url)
        ).first()
        
        if existing_job:
            continue  # Skip duplicates
        
        # Create the job
        db_job = ImportJob(
            id=str(uuid.uuid4()),
            source_url=str(url),
            target_wp_connection_id=job_data.target_wp_connection_id,
            status=JobStatus.pending
        )
        
        db.add(db_job)
        created_jobs.append(db_job)
        
        # Queue the background task
        process_import_job.delay(db_job.id)
    
    db.commit()
    
    for job in created_jobs:
        db.refresh(job)
    
    return created_jobs
