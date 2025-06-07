#!/usr/bin/env python3
"""
FastAPI Web Interface for Firecrawl Website Crawler
Simple web app with password protection and zip downloads.
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import secrets
from dotenv import load_dotenv

from main import crawl_website

# Load environment variables
load_dotenv()

app = FastAPI(title="Firecrawl Website Crawler", version="1.0.0")
security = HTTPBasic()
templates = Jinja2Templates(directory="templates")

# Create templates directory if it doesn't exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

def verify_password(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify the admin password."""
    admin_password = os.getenv('ADMIN_PASSWORD')
    if not admin_password:
        raise HTTPException(status_code=500, detail="Admin password not configured")
    
    is_correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"), admin_password.encode("utf8")
    )
    
    if not is_correct_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

def create_zip_from_directory(source_dir: Path, zip_path: Path):
    """Create a zip file from a directory."""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in source_dir.rglob('*'):
            if file_path.is_file():
                # Add file to zip with relative path
                arcname = file_path.relative_to(source_dir)
                zipf.write(file_path, arcname)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, username: str = Depends(verify_password)):
    """Main page with crawler form."""
    return templates.TemplateResponse("index.html", {"request": request, "username": username})

@app.post("/crawl")
async def start_crawl(
    url: str = Form(...),
    depth: int = Form(2),
    max_pages: int = Form(50),
    username: str = Depends(verify_password)
):
    """Start the crawl process and return the ZIP file immediately."""
    
    # Validate inputs
    if depth < 0 or depth > 10:
        raise HTTPException(status_code=400, detail="Depth must be between 0 and 10")
    
    if max_pages < 1 or max_pages > 1000:
        raise HTTPException(status_code=400, detail="Max pages must be between 1 and 1000")
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # Perform the crawl
        crawl_result, output_dir = crawl_website(url, depth, max_pages)
        
        # Create zip file in memory/temp location
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = urlparse(url).netloc.replace('.', '_').replace(':', '_')
        zip_filename = f"{domain}_{timestamp}.zip"
        
        # Create a temporary zip file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
            temp_zip_path = Path(temp_zip.name)
        
        # Create the zip file
        create_zip_from_directory(output_dir, temp_zip_path)
        
        # Clean up the original directory immediately
        shutil.rmtree(output_dir)
        
        # Return the ZIP file as a download
        return FileResponse(
            path=temp_zip_path,
            filename=zip_filename,
            media_type='application/zip',
            background=lambda: os.unlink(temp_zip_path)  # Clean up temp file after sending
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawl failed: {str(e)}")

# Download endpoint removed - files are now returned immediately

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 