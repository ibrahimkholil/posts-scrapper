# Project Blueprint: Universal Blog Cloner & WordPress Importer

**Document Version:** 1.0  
**Date:** July 6, 2026  
**Status:** Planning / Architecture Phase  

---

## 1. Executive Summary
This project aims to build a secure, web-based internal tool that allows team members to scrape blog posts (including text and images) from **any external website** and seamlessly import them into one or more **target WordPress sites** as drafts. 

The tool will handle complex tasks like JavaScript rendering, image downloading/optimization, HTML sanitization, and WordPress REST API authentication (via Application Passwords) in the background, ensuring a smooth UI experience and perfect content conversion.

---

## 2. System Architecture
The application uses an **asynchronous, decoupled architecture** to prevent the web interface from freezing during heavy scraping and image-processing tasks.

### High-Level Flow
1. **Frontend (Next.js):** User submits a URL and selects a target WP site.
2. **Backend API (FastAPI):** Validates the request, checks for duplicates, encrypts credentials, and pushes a job to the queue.
3. **Message Broker (Redis):** Holds the queue of pending scraping tasks.
4. **Background Worker (Python/Celery):** Picks up the task, scrapes the site, processes images, formats HTML, and uploads to WordPress.
5. **Database (PostgreSQL):** Stores user data, encrypted WP credentials, and job history.

---

## 3. Technology Stack

| Component | Technology | Reason for Choice |
| :--- | :--- | :--- |
| **Frontend** | Next.js (React) + TailwindCSS | Fast, modern UI, easy team authentication (NextAuth). |
| **Backend API** | Python (FastAPI) | High performance, async support, auto-generates API docs. |
| **Background Worker** | Python + Celery (or ARQ) | Handles long-running scraping/image tasks without blocking the API. |
| **Web Scraping** | Playwright (Python) | Handles JavaScript-heavy sites and bypasses basic anti-bot protections. |
| **Content Extraction**| `readability-lxml` + LLM API | Strips headers/footers to isolate the main article content cleanly. |
| **Image Processing** | Pillow (PIL) | Downloads, resizes (max 1920px), and converts images to WebP. |
| **HTML Sanitization**| `bleach` or `nh3` | Strips malicious scripts and source-site specific CSS classes. |
| **Database** | PostgreSQL | Reliable relational database for users, credentials, and logs. |
| **Message Broker** | Redis | Fast, in-memory queue for background tasks. |
| **Hosting / CI/CD** | Docker + Render/Railway + GitHub Actions | Easy deployment directly from Git, auto-scaling, managed SSL. |

---

## 4. Database Schema (PostgreSQL)

### Table: `users`
- `id` (UUID, PK)
- `email` (String, Unique)
- `role` (Enum: `admin`, `editor`)
- `created_at` (Timestamp)

### Table: `wp_connections`
- `id` (UUID, PK)
- `site_name` (String, e.g., "Main Marketing Blog")
- `site_url` (String, e.g., "https://targetsite.com")
- `wp_username` (String)
- `wp_app_password_encrypted` (Text) *(Encrypted at rest using Fernet)*
- `created_by` (UUID, FK -> users)

### Table: `import_jobs`
- `id` (UUID, PK)
- `source_url` (String, Unique Index to prevent duplicates)
- `target_wp_connection_id` (UUID, FK -> wp_connections)
- `status` (Enum: `pending`, `processing`, `completed`, `failed`)
- `wp_post_id` (Integer, Nullable)
- `wp_draft_url` (String, Nullable)
- `error_log` (Text, Nullable)
- `created_at` (Timestamp)
- `completed_at` (Timestamp, Nullable)

---

## 5. API Specifications (FastAPI)

### Authentication & WP Management
- `POST /api/auth/login` - Team member login.
- `GET /api/wp-connections` - List connected WP sites (Admin only).
- `POST /api/wp-connections` - Add new WP site & App Password (Admin only).
- `POST /api/wp-connections/test` - Test connection to WP before saving.

### Import Jobs
- `POST /api/jobs` - Submit a new URL for scraping. Returns `job_id`.
- `GET /api/jobs/{job_id}` - Check the real-time status of a specific job.
- `GET /api/jobs` - List all import history with filters (status, date).
- `POST /api/jobs/bulk` - Accept a CSV of URLs for batch processing.

---

## 6. Core Workflows & "Perfect Conversion" Logic

To ensure the imported blogs look native to the WordPress theme and do not break the site, the Background Worker must execute the following pipeline:

### Step 1: Scraping & Extraction
1. Load the `source_url` using **Playwright** (headless browser).
2. Extract raw HTML.
3. Pass HTML through `readability-lxml` to isolate the main article body (removing navbars, footers, sidebars).

### Step 2: The Image Pipeline (Crucial)
*Never hotlink images. This causes broken images and copyright issues.*
1. Parse the extracted HTML for all `<img>` tags.
2. Download each image into server memory.
3. **Process:** Resize to max width 1920px, convert format to **WebP** (for fast WP loading).
4. **Upload:** Send binary data to WP REST API (`POST /wp-json/wp/v2/media`) with correct headers (`Content-Disposition`, `Content-Type`).
5. **Replace:** Map the old source image URL to the new WP Media URL.

### Step 3: HTML Sanitization & Formatting
1. Run the HTML through `bleach` to strip `<script>`, `<iframe>`, and inline `style` attributes.
2. Remove source-site specific CSS classes (e.g., `class="theme-dark-header"`) so the WP theme's CSS takes over.
3. **Gutenberg Formatting:** Wrap images in native WP Gutenberg block comments so they are perfectly editable in the WP editor:
   ```html
   <!-- wp:image {"sizeSlug":"large"} -->
   <figure class="wp-block-image size-large"><img src="NEW_WP_URL" alt=""/></figure>
   <!-- /wp:image -->
