from app.workers.celery_app import celery_app
from app.workers.base import DatabaseTask
from app.models.database import ImportJob, JobStatus, WPConnection
from app.services import (
    scrape_url,
    download_and_process_image,
    sanitize_html,
    convert_to_gutenberg_blocks,
    WordPressClient,
    decrypt_password
)
from datetime import datetime
import uuid


@celery_app.task(base=DatabaseTask, bind=True)
def process_import_job(self, job_id: str):
    """
    Background task to process a blog import job.
    """
    db = self.db
    
    try:
        # Get the job
        job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
        if not job:
            raise Exception(f"Job {job_id} not found")
        
        # Update status to processing
        job.status = JobStatus.processing
        db.commit()
        
        # Get WP connection details
        wp_connection = db.query(WPConnection).filter(
            WPConnection.id == job.target_wp_connection_id
        ).first()
        
        if not wp_connection:
            raise Exception("WordPress connection not found")
        
        # Decrypt the password
        wp_password = decrypt_password(wp_connection.wp_app_password_encrypted)
        
        # Step 1: Scrape the source URL
        scraped_data = scrape_url(job.source_url)
        
        # Step 2: Process images and upload to WordPress
        wp_client = WordPressClient(
            wp_connection.site_url,
            wp_connection.wp_username,
            wp_password
        )
        
        image_url_map = {}
        for img_url in scraped_data['images']:
            try:
                image_data, content_type = download_and_process_image(img_url)
                filename = f"{uuid.uuid4()}.webp"
                
                wp_media_url = wp_client.upload_media(
                    image_data,
                    filename,
                    content_type
                )
                
                if wp_media_url:
                    image_url_map[img_url] = wp_media_url
            except Exception as e:
                # Log error but continue with other images
                print(f"Failed to process image {img_url}: {str(e)}")
        
        # Step 3: Sanitize HTML
        sanitized_html = sanitize_html(scraped_data['content'])
        
        # Step 4: Convert to Gutenberg blocks
        gutenberg_content = convert_to_gutenberg_blocks(sanitized_html, image_url_map)
        
        # Step 5: Create WordPress post
        wp_post = wp_client.create_post(
            title=scraped_data['title'],
            content=gutenberg_content,
            status='draft'
        )
        
        if wp_post:
            job.status = JobStatus.completed
            job.wp_post_id = wp_post['id']
            job.wp_draft_url = f"{wp_connection.site_url}/wp-admin/post.php?post={wp_post['id']}&action=edit"
            job.completed_at = datetime.utcnow()
        else:
            raise Exception("Failed to create WordPress post")
        
        db.commit()
        
    except Exception as e:
        # Update job status to failed
        job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
        if job:
            job.status = JobStatus.failed
            job.error_log = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
        
        # Re-raise to mark task as failed
        raise
