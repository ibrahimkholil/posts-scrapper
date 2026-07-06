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

- Node.js 18+
- Python 3.9+
- PostgreSQL
- Redis

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Running with Docker

```bash
docker-compose up --build
```

## License

Internal use only.
