# Universal Blog Cloner & WordPress Importer

A secure, web-based internal tool for scraping blog posts from any external website and importing them into WordPress sites as drafts.

## Features

- **Web Scraping**: Handles JavaScript-heavy sites using Playwright
- **Image Processing**: Downloads, optimizes (WebP), and uploads images to WordPress media library
- **HTML Sanitization**: Strips malicious scripts and source-site specific CSS classes
- **Gutenberg Formatting**: Converts content to native WordPress Gutenberg blocks
- **Async Processing**: Background workers handle long-running tasks without blocking the UI
- **Secure Credential Storage**: WordPress credentials encrypted at rest

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Frontend   │────▶│  Backend API │────▶│   Redis     │
│  (Next.js)  │     │  (FastAPI)   │     │  (Broker)   │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                                                ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ PostgreSQL  │◀────│  Celery       │◀────│   Worker    │
│ (Database)  │     │  Worker       │     │  (Python)   │
└─────────────┘     └──────────────┘     └─────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js + TailwindCSS |
| Backend API | FastAPI (Python) |
| Background Worker | Celery + Python |
| Web Scraping | Playwright |
| Content Extraction | readability-lxml |
| Image Processing | Pillow |
| HTML Sanitization | bleach/nh3 |
| Database | PostgreSQL |
| Message Broker | Redis |

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core utilities (config, security)
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── workers/      # Celery workers
│   └── tests/
├── frontend/
│   └── src/
│       ├── app/          # Next.js pages
│       ├── components/   # React components
│       ├── lib/          # Utilities
│       └── types/        # TypeScript types
├── docker/               # Docker configurations
└── README.md
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.9+ (for local development)

## Quick Start with Docker (Recommended)

The easiest way to run the entire stack is using Docker Compose, which will start:
- **PostgreSQL** (Database)
- **Redis** (Message Broker)
- **Backend API** (FastAPI)
- **Celery Worker** (Background tasks)
- **Frontend** (Next.js)

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd universal-blog-cloner
```

### Step 2: Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Database
POSTGRES_USER=blogcloner
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=blogcloner
DATABASE_URL=postgresql://blogcloner:your_secure_password@db:5432/blogcloner

# Redis
REDIS_URL=redis://redis:6379/0

# Security (Generate with: openssl rand -hex 32)
SECRET_KEY=your_super_secret_key_here
ENCRYPTION_KEY=your_32_byte_encryption_key_here

# WordPress (Optional - can be added via UI later)
WP_SITE_URL=
WP_USERNAME=
WP_APP_PASSWORD=
```

### Step 3: Run Docker Compose

```bash
docker-compose up --build
```

Wait for all services to start (may take 2-3 minutes on first run).

### Step 4: Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Worker Logs**: Check terminal output from `docker-compose up`

## Local Development Setup

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql://blogcloner:password@localhost:5432/blogcloner
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your_secret_key
ENCRYPTION_KEY=your_32_byte_encryption_key
```

Run backend:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

In a separate terminal, run the Celery worker:

```bash
celery -A app.workers.celery_app worker --loglevel=info
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Start Infrastructure Services

You still need PostgreSQL and Redis running locally:

```bash
docker-compose up db redis
```

## Testing the Application

### 1. Add a WordPress Connection

1. Navigate to http://localhost:3000
2. Go to **Settings > WordPress Connections**
3. Click **Add New Connection**
4. Enter:
   - **Site Name**: e.g., "My Marketing Blog"
   - **Site URL**: e.g., `https://your-wp-site.com`
   - **Username**: Your WordPress username
   - **Application Password**: Generate from WP Admin → Users → Profile → Application Passwords
5. Click **Test Connection** to verify
6. Click **Save**

### 2. Import a Blog Post

1. Go to **Import** page
2. Enter a blog post URL (e.g., `https://example.com/blog/post-title`)
3. Select your WordPress connection from dropdown
4. Click **Start Import**
5. Monitor the job status in real-time

### 3. Check Job History

1. Go to **History** page
2. View all import jobs with status (Pending, Processing, Completed, Failed)
3. Click on any job to see details and error logs

### 4. Verify in WordPress

1. Log into your WordPress admin
2. Go to **Posts → All Posts**
3. Find the imported post (saved as **Draft**)
4. Review content, images, and Gutenberg blocks

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login

### WordPress Connections
- `GET /api/wp-connections` - List connections
- `POST /api/wp-connections` - Add new connection
- `POST /api/wp-connections/test` - Test connection

### Import Jobs
- `POST /api/jobs` - Submit new URL for scraping
- `GET /api/jobs/{job_id}` - Check job status
- `GET /api/jobs` - List all jobs
- `POST /api/jobs/bulk` - Batch import from CSV

Full API docs available at: http://localhost:8000/docs

## Troubleshooting

### Common Issues

**Playwright browser not found:**
```bash
playwright install
```

**Database connection errors:**
Ensure PostgreSQL is running and `DATABASE_URL` is correct.

**Celery worker not processing jobs:**
Check Redis is running and `REDIS_URL` is correct.

**Images not importing:**
Verify WordPress Application Password has media upload permissions.

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f worker
docker-compose logs -f frontend
```

## Security Notes

- All WordPress credentials are encrypted at rest using Fernet encryption
- Application uses secure HTTP-only cookies for authentication
- Never commit `.env` files to version control
- Use strong, unique passwords for production deployments

## License

Internal use only.
