# 🔥 Firecrawl Website Crawler

A web-based interface for crawling websites and converting them to clean markdown files using [Firecrawl](https://firecrawl.dev). Built with FastAPI and deployed on Fly.io.

## Features

- 🌐 **Web Interface**: Clean, modern UI for easy website crawling
- 🔒 **Password Protection**: Basic authentication using environment variables
- 📁 **ZIP Downloads**: Automatically packages crawled content into downloadable ZIP files
- ⚡ **Fast Deployment**: One-command deployment to Fly.io
- 🎛️ **Configurable**: Adjustable crawl depth and page limits
- 📱 **Responsive**: Works on desktop and mobile devices

## Quick Start

### 1. Prerequisites

- Python 3.12+
- [Firecrawl API key](https://firecrawl.dev)
- [Fly.io account](https://fly.io) (for deployment)
- Docker & Docker Compose (for containerized development)

### 2. Setup

```bash
# Clone or download the project
cd dro_crawler

# Install dependencies (using uv)
uv add fastapi uvicorn jinja2 python-multipart python-dotenv firecrawl-py

# Create environment file
cp .env.example .env
# Edit .env with your credentials:
# FIRECRAWL_API_KEY=fc-your-api-key-here
# ADMIN_PASSWORD=your-secure-password
```

### 3. Local Development

```bash
# Run locally
python app.py

# Or with uvicorn
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000` and use your `ADMIN_PASSWORD` to authenticate.

### 4. Docker Development (Alternative)

For containerized development with auto-reload and production testing:

```bash
# Start development environment with auto-reload
./docker-dev.sh dev

# Test production-like environment
./docker-dev.sh prod

# Test both environments simultaneously
./docker-dev.sh test

# View all available Docker commands
./docker-dev.sh help
```

**Docker URLs:**
- Development: `http://localhost:8000` (with auto-reload)
- Production test: `http://localhost:8001` (production-like)

### 5. Deploy to Fly.io

```bash
# Install flyctl (if not already installed)
curl -L https://fly.io/install.sh | sh

# Login to Fly.io
flyctl auth login

# Make deployment script executable
chmod +x deploy.sh

# Deploy!
./deploy.sh
```

## Usage

1. **Access the app**: Visit your deployed URL or `http://localhost:8000`
2. **Authenticate**: Use any username and your `ADMIN_PASSWORD`
3. **Enter URL**: Input the website you want to crawl
4. **Configure**: Set crawl depth (0-10) and max pages (1-1000)
5. **Crawl**: Click "Start Crawling" and wait for completion
6. **Download**: Download the ZIP file containing all markdown files

## Configuration

### Environment Variables

- `FIRECRAWL_API_KEY`: Your Firecrawl API key (required)
- `ADMIN_PASSWORD`: Password for web interface access (required)

### Crawl Settings

- **Depth**: How many levels deep to crawl (0 = only the main page)
- **Max Pages**: Maximum number of pages to crawl (prevents runaway crawls)

## File Structure

```
dro_crawler/
├── app.py              # FastAPI application
├── main.py             # Core crawler logic
├── templates/
│   └── index.html      # Web interface
├── Dockerfile          # Production container configuration
├── Dockerfile.dev      # Development container configuration
├── docker-compose.yml  # Multi-environment Docker setup
├── docker-dev.sh       # Docker development helper script
├── fly.toml           # Fly.io deployment config
├── deploy.sh          # Fly.io deployment script
├── requirements.txt   # Python dependencies (for Docker)
├── pyproject.toml     # UV project configuration
├── .env               # Environment variables (create this)
└── README.md          # This file
```

## API Endpoints

- `GET /` - Web interface
- `POST /crawl` - Start crawling process
- `GET /download/{filename}` - Download ZIP file
- `GET /health` - Health check

## Docker Development Commands

```bash
# Development workflow
./docker-dev.sh dev         # Start dev environment with auto-reload
./docker-dev.sh prod        # Test production-like environment
./docker-dev.sh test        # Test both environments
./docker-dev.sh shell       # Open shell in dev container
./docker-dev.sh logs        # View container logs
./docker-dev.sh stop        # Stop all containers
./docker-dev.sh clean       # Clean up containers and images
```

## Deployment Commands

```bash
# Deploy updates
flyctl deploy --app dro-crawler

# View logs
flyctl logs --app dro-crawler

# Check status
flyctl status --app dro-crawler

# Scale app
flyctl scale count 1 --app dro-crawler

# SSH into container
flyctl ssh console --app dro-crawler
```

## Troubleshooting

### Common Issues

1. **"Admin password not configured"**
   - Ensure `ADMIN_PASSWORD` is set in your `.env` file
   - For Fly.io, run: `flyctl secrets set ADMIN_PASSWORD=your-password --app dro-crawler`

2. **"FIRECRAWL_API_KEY not found"**
   - Get an API key from [firecrawl.dev](https://firecrawl.dev)
   - Add it to your `.env` file or Fly.io secrets

3. **Crawl fails**
   - Check your Firecrawl API credits
   - Verify the URL is accessible
   - Try reducing max pages or depth

4. **Memory issues**
   - Increase VM memory in `fly.toml`
   - Reduce max pages per crawl

5. **Docker build fails**
   - Ensure `requirements.txt` exists
   - Check Docker daemon is running
   - Try `./docker-dev.sh rebuild` for clean build

### Logs

```bash
# View application logs
flyctl logs --app dro-crawler

# Follow logs in real-time
flyctl logs --app dro-crawler -f
```

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## Support

- 📖 [Firecrawl Documentation](https://docs.firecrawl.dev)
- 🐛 [Report Issues](https://github.com/your-repo/issues)
- 💬 [Discussions](https://github.com/your-repo/discussions)
