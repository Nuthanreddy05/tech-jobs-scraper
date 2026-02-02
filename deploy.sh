#!/bin/bash
# GitHub Actions Career Page Scraper - Auto Deployment Script
# Run this on your actual computer (not in VM)

set -e

echo "======================================================================"
echo "🚀 GITHUB ACTIONS CAREER PAGE SCRAPER - DEPLOYMENT"
echo "======================================================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Get GitHub username
read -p "Enter your GitHub username: " github_user

# Get repository name
read -p "Enter repository name (default: tech-jobs-scraper): " repo_name
repo_name=${repo_name:-tech-jobs-scraper}

# Get Groq API key
read -p "Enter your Groq API key (or press Enter to skip): " groq_key

echo ""
echo "📋 Configuration:"
echo "   GitHub User: $github_user"
echo "   Repository:  $repo_name"
echo "   Groq API:    $([ -n "$groq_key" ] && echo "✓ Provided" || echo "✗ Skipped")"
echo ""

read -p "Continue? (y/n): " confirm
if [[ $confirm != [yY] ]]; then
    echo "❌ Deployment cancelled"
    exit 0
fi

# Create directory
deployment_dir="$HOME/Desktop/$repo_name"
echo ""
echo "📁 Creating directory: $deployment_dir"
mkdir -p "$deployment_dir"

# Copy files
echo "📄 Copying files..."
cp -r .github "$deployment_dir/"
cp scraper.py "$deployment_dir/"
cp requirements.txt "$deployment_dir/"
cp README.md "$deployment_dir/"
cp .gitignore "$deployment_dir/"

cd "$deployment_dir"

# Initialize git
echo "🔧 Initializing git repository..."
git init
git add .
git commit -m "Initial commit: Hourly career page scraper"

# Create GitHub repo (requires gh CLI)
if command -v gh &> /dev/null; then
    echo "🌐 Creating GitHub repository..."
    gh repo create "$repo_name" --public --source=. --push
else
    echo ""
    echo "⚠️  GitHub CLI (gh) not found. Manual steps required:"
    echo ""
    echo "1. Go to https://github.com/new"
    echo "2. Create repository: $repo_name"
    echo "3. Run these commands:"
    echo ""
    echo "   cd $deployment_dir"
    echo "   git remote add origin https://github.com/$github_user/$repo_name.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo ""
fi

# Add Groq API key as secret (if provided)
if [ -n "$groq_key" ] && command -v gh &> /dev/null; then
    echo "🔑 Adding Groq API key as secret..."
    echo "$groq_key" | gh secret set GROQ_API_KEY
fi

echo ""
echo "======================================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "======================================================================"
echo ""
echo "📍 Repository location: $deployment_dir"
echo "🌐 GitHub URL: https://github.com/$github_user/$repo_name"
echo ""
echo "🎯 Next steps:"
echo "   1. Go to https://github.com/$github_user/$repo_name/actions"
echo "   2. Enable GitHub Actions if prompted"
echo "   3. Click 'Run workflow' to start scraping"
echo "   4. Scraper will run automatically every hour"
echo ""
echo "📊 Results will be in the 'jobs/' folder"
echo "======================================================================"
