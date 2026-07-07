# Universal Blog Cloner & WordPress Importer

A secure, web-based internal tool that allows team members to scrape blog posts (including text and images) from any external website and seamlessly import them into one or more target WordPress sites as drafts.

## Features

- **Web Scraping**: Uses Playwright to handle JavaScript-heavy sites
- **Image Processing**: Downloads, resizes (max 1920px), and converts images to WebP
- **HTML Sanitization**: Strips malicious scripts and source-site specific CSS classes
- **Gutenberg Formatting**: Wraps images in native WP Gutenberg block comments
- **Async Processing**: Background workers handle heavy tasks without blocking the UI
- **Secure Authentication**: JWT-based auth with encrypted WordPress credentials

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.10+ (for local backend development)

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/ibrahimkholil/posts-scrapper.git
   cd posts-scrapper
   ```

2. **Copy environment file**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` file** with your settings:
   - `SECRET_KEY`: Generate a random string for JWT signing
   - `FERNET_KEY`: Leave empty for auto-generation (dev only)
   - Database credentials if needed

4. **Start all services**
   ```bash
   docker-compose up --build
   ```

5. **Initialize the database** (in another terminal)
   ```bash
   docker-compose exec backend python init_db.py
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Local Development

1. **Start infrastructure (PostgreSQL & Redis)**
   ```bash
   docker-compose up db redis
   ```

2. **Initialize database**
   ```bash
   cd backend
   pip install -r requirements.txt
   python init_db.py
   ```

3. **Start backend**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Start frontend** (in another terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Start Celery worker** (in another terminal)
   ```bash
   cd backend
   celery -A app.workers.celery_app worker --loglevel=info
   ```

## Default Credentials

After running `init_db.py`, you can login with:

- **Admin**: admin@example.com / admin123
- **Editor**: editor@example.com / editor123

## Testing the Application

### Step 1: Add a WordPress Connection

1. Login at http://localhost:3000/login
2. Navigate to "Connections"
3. Click "Add Connection"
4. Enter your WordPress site details:
   - Site Name: e.g., "My Test Blog"
   - Site URL: e.g., "https://your-wp-site.com"
   - Username: Your WordPress username
   - Application Password: Generate from WP Admin → Users → Profile → Application Passwords

### Step 2: Import a Blog Post

1. Go to the homepage
2. Select your WordPress connection from the dropdown
3. Enter a blog post URL (e.g., https://techcrunch.com/some-article)
4. Click "Import Blog Post"
5. Monitor the job status in the table below

### Step 3: Check the Result

1. Once the job shows "completed", click "View Draft"
2. You'll be taken to your WordPress admin to edit the imported post
3. Verify that:
   - Text content is properly formatted
   - Images are uploaded to your media library
   - Gutenberg blocks are correctly structured

## API Endpoints

### Authentication
- `POST /api/auth/login?email=&password=` - Login and get JWT token

### WordPress Connections
- `GET /api/wp-connections/` - List all connections (requires auth)
- `POST /api/wp-connections/` - Add new connection (requires admin)
- `POST /api/wp-connections/test` - Test connection before saving

### Import Jobs
- `POST /api/jobs/` - Submit a new URL for scraping
- `GET /api/jobs/` - List all jobs with filters
- `GET /api/jobs/{job_id}` - Get specific job status
- `POST /api/jobs/bulk` - Batch process multiple URLs

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Frontend   │────▶│  FastAPI     │────▶│   Redis     │
│  (Next.js)  │     │  Backend     │     │   (Queue)   │
└─────────────┘     └──────────────┘     └─────────────┘
                           │                    │
                           ▼                    ▼
                    ┌──────────────┐     ┌─────────────┐
                    │  PostgreSQL  │     │   Celery    │
                    │  (Database)  │     │   Worker    │
                    └──────────────┘     └─────────────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │  WordPress  │
                                         │  REST API   │
                                         └─────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js + TypeScript + TailwindCSS |
| Backend API | Python + FastAPI |
| Background Worker | Python + Celery |
| Web Scraping | Playwright |
| Content Extraction | readability-lxml |
| Image Processing | Pillow (PIL) |
| HTML Sanitization | bleach |
| Database | PostgreSQL |
| Message Broker | Redis |

## Troubleshooting

### Playwright Installation Issues
If scraping fails, install Playwright browsers:
```bash
playwright install chromium
```

### Database Connection Errors
Ensure PostgreSQL is running:
```bash
docker-compose ps
```

### Worker Not Processing Jobs
Check Celery worker logs:
```bash
docker-compose logs worker
```

## License

MIT License
