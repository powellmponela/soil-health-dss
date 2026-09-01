#!/bin/bash

# Soil Health DSS - Vercel Deployment Script
# This script automates the deployment to Vercel

set -e

echo "======================================"
echo "Soil Health DSS - Vercel Deployment"
echo "======================================"
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Vercel CLI is not installed."
    echo "Install it with: npm install -g vercel"
    exit 1
fi

# Check if Git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: Soil Health DSS"
    echo ""
fi

# Get API URL from user
echo "Enter your backend API URL (e.g., https://api.example.com):"
read API_URL

if [ -z "$API_URL" ]; then
    echo "Error: API URL is required"
    exit 1
fi

# Update environment file
echo "Updating frontend environment variables..."
echo "REACT_APP_API_BASE_URL=$API_URL" > frontend/.env.production.local

# Build frontend
echo ""
echo "Building frontend..."
cd frontend
npm run build
cd ..

# Deploy to Vercel
echo ""
echo "Deploying to Vercel..."
vercel --prod --env REACT_APP_API_BASE_URL=$API_URL

echo ""
echo "======================================"
echo "Deployment Complete!"
echo "======================================"
echo ""
echo "Your application is now live!"
echo "Check your Vercel dashboard for more details."
