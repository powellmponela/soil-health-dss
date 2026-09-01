# Quick Git Setup Guide

## Initialize and Push to GitHub

### 1. Verify Git is Installed
```bash
git --version
# Should show: git version X.X.X
```

### 2. Configure Git (First Time Only)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. Initialize Repository
```bash
cd d:\dss\SOIL HEALTH

# Check if git is already initialized
git status

# If you see "fatal: not a git repository", initialize:
git init
```

### 4. Add All Files
```bash
git add .
```

### 5. Create Initial Commit
```bash
git commit -m "Initial commit: Soil Health DSS - Production Ready

- Frontend: React SPA with all components
- Backend: Python FastAPI with 64 frameworks
- Database: PostgreSQL schema initialized
- Documentation: Complete deployment guides"
```

### 6. Create GitHub Repository

Go to [GitHub New Repository](https://github.com/new):
- **Repository name**: soil-health-dss
- **Description**: Soil Health Decision Support System
- **Visibility**: Public (for open science) or Private
- **Initialize**: Do NOT check any boxes (we already have commits)
- Click "Create repository"

### 7. Connect Local to GitHub
```bash
# Replace USERNAME and REPO with your values
git remote add origin https://github.com/YOUR-USERNAME/soil-health-dss.git
git branch -M main
git push -u origin main

# Example:
git remote add origin https://github.com/powell-mponela/soil-health-dss.git
git branch -M main
git push -u origin main
```

### 8. Verify Upload
Visit: https://github.com/YOUR-USERNAME/soil-health-dss

You should see all your files uploaded!

## Common Git Commands

```bash
# Check status
git status

# View recent commits
git log --oneline -10

# Update remote origin (if you change your mind)
git remote set-url origin https://github.com/NEW-USERNAME/soil-health-dss.git

# View remote configuration
git remote -v

# Pull latest changes (if pushing from another computer)
git pull origin main

# Create a new branch for features
git checkout -b feature/my-feature
git add .
git commit -m "Add my feature"
git push origin feature/my-feature

# Merge branch (on GitHub via Pull Request)
# Then switch back:
git checkout main
git pull origin main
```

## Next Step: Deploy to Vercel

After pushing to GitHub, follow [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md)

---

**Quick Reference**:
- Your GitHub: https://github.com/YOUR-USERNAME
- Your Repository: https://github.com/YOUR-USERNAME/soil-health-dss
- Vercel Import: https://vercel.com/new
