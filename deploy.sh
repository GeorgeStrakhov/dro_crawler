#!/bin/bash

# Firecrawl Crawler - Fly.io Deployment Script

set -e  # Exit on error

echo "🚀 Starting deployment to Fly.io..."

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl is not installed. Please install it first:"
    echo "   curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Check if user is logged in
if ! flyctl auth whoami &> /dev/null; then
    echo "❌ Not logged in to Fly.io. Please run: flyctl auth login"
    exit 1
fi

# Check if .env file exists and has required variables
if [[ ! -f .env ]]; then
    echo "❌ .env file not found. Please create it with:"
    echo "   FIRECRAWL_API_KEY=fc-your-api-key-here"
    echo "   ADMIN_PASSWORD=your-admin-password"
    exit 1
fi

# Check for required environment variables
if ! grep -q "FIRECRAWL_API_KEY" .env; then
    echo "❌ FIRECRAWL_API_KEY not found in .env file"
    exit 1
fi

if ! grep -q "ADMIN_PASSWORD" .env; then
    echo "❌ ADMIN_PASSWORD not found in .env file"
    exit 1
fi

echo "✅ Environment variables check passed"

# Check if app exists, if not create it
if ! flyctl apps list | grep -q "dro-crawler"; then
    echo "📱 Creating new Fly.io app..."
    flyctl apps create dro-crawler --yes
else
    echo "📱 App already exists, proceeding with deployment..."
fi

# Set secrets from .env file
echo "🔐 Setting secrets..."
flyctl secrets set --app dro-crawler $(grep -v '^#' .env | grep -v '^$' | tr '\n' ' ')

# Deploy the application
echo "🚀 Deploying application..."
flyctl deploy --app dro-crawler

# Check deployment status
echo "🔍 Checking deployment status..."
flyctl status --app dro-crawler

# Get the app URL
APP_URL=$(flyctl info --app dro-crawler | grep "Hostname" | awk '{print $2}')
echo ""
echo "✅ Deployment completed!"
echo "🌐 Your app is available at: https://$APP_URL"
echo ""
echo "📋 Next steps:"
echo "   1. Visit https://$APP_URL to use your crawler"
echo "   2. Use your ADMIN_PASSWORD for authentication"
echo "   3. Monitor logs with: flyctl logs --app dro-crawler"
echo "" 