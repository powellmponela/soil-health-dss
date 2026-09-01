# Vercel Deployment Checklist

## ✅ Pre-Deployment Status

- [x] Frontend build completed (`/frontend/build/` contains index.html + static/)
- [x] Backend running on port 8000 with all 64 frameworks loaded
- [x] Database initialized with schema and data
- [x] Environment configuration files created
- [x] Vercel config file created (`vercel.json`)

## 🚀 Deploy to Vercel (5 Steps)

### Step 1: Initialize Git
```bash
cd d:\dss\SOIL HEALTH

# Check if git is already initialized
git status

# If not initialized, run:
git init
git add .
git commit -m "Initial commit: Soil Health DSS - Production ready"
```

### Step 2: Create GitHub Repository

**Option A: Using Web Browser**
1. Go to [GitHub New Repository](https://github.com/new)
2. Name: `soil-health-dss`
3. Description: "Soil Health Decision Support System - Web Application"
4. Visibility: Public or Private
5. Click "Create repository"

**Option B: Using GitHub CLI**
```bash
# Install GitHub CLI from https://cli.github.com
# Then:
gh repo create soil-health-dss --public --source=. --remote=origin --push
```

### Step 3: Connect to GitHub
```bash
# Add remote and push
git remote add origin https://github.com/YOUR-USERNAME/soil-health-dss.git
git branch -M main
git push -u origin main

# Or if already exists:
git remote set-url origin https://github.com/YOUR-USERNAME/soil-health-dss.git
git push -u origin main
```

### Step 4: Deploy Frontend to Vercel

**Option A: Using Vercel Dashboard (Easiest)**
1. Visit [vercel.com/new](https://vercel.com/new)
2. Sign up/login with GitHub
3. Click "Import Git Repository"
4. Select `soil-health-dss` repository
5. Click "Import"
6. In "Build and Output settings", verify:
   - Framework Preset: `React`
   - Build Command: `cd frontend && npm run build`
   - Output Directory: `frontend/build`
7. Click "Environment Variables"
8. Add variable:
   - Name: `REACT_APP_API_BASE_URL`
   - Value: `http://localhost:8000` (temporary - update after backend deployed)
9. Click "Deploy"

**Option B: Using Vercel CLI**
```bash
npm install -g vercel
vercel --prod --name soil-health-dss --env REACT_APP_API_BASE_URL=http://localhost:8000
```

### Step 5: Deploy Backend to Railway (Recommended)

1. Visit [railway.app](https://railway.app)
2. Click "New Project"
3. Click "Deploy from GitHub"
4. Connect your GitHub account
5. Select `soil-health-dss` repository
6. Railway auto-detects FastAPI project
7. Configure environment variables:
   - `DB_HOST`: your-postgres-host
   - `DB_USER`: postgres
   - `DB_PASSWORD`: your-password
   - `DB_NAME`: soil_health
8. Click "Deploy"
9. Note the Railway URL (e.g., `https://api-prod.railway.app`)

## 📝 Post-Deployment Setup

### Update Frontend API URL
1. Go to Vercel Dashboard
2. Select your project
3. Settings → Environment Variables
4. Update `REACT_APP_API_BASE_URL` to your Railway URL
5. Vercel auto-redeploys with new environment

### Test Live Deployment
```bash
# Frontend should be live at: https://soil-health-dss.vercel.app
# (actual URL shown in Vercel dashboard)

# Test database section:
# Should display 64 frameworks in table
# All data should load from Railway backend
```

### Enable CORS on Backend
If frontend domain is `soil-health-dss.vercel.app`:

In `api/logic.py`, add:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://soil-health-dss.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy backend.

## 🔧 Alternative Backend Hosting Options

### Render.com
1. Visit [render.com](https://render.com)
2. New → Web Service
3. Connect GitHub
4. Select repository
5. Configure:
   - Build Command: `pip install -r api/requirements.txt`
   - Start Command: `cd api && python run.py`
6. Add environment variables
7. Deploy

### Heroku (Note: Paid tier required)
```bash
# Install Heroku CLI
npm install -g heroku

# Login and create app
heroku login
heroku create soil-health-dss-api

# Set environment variables
heroku config:set DB_HOST=xxx DB_USER=postgres DB_PASSWORD=xxx DB_NAME=soil_health

# Deploy
git push heroku main
```

## 🗄️ Database Setup on Cloud Platform

### Option 1: Railway PostgreSQL (Easiest)
- Create new PostgreSQL service in Railway
- Get connection string from Railway
- Use in `DB_HOST`, `DB_USER`, `DB_PASSWORD` variables

### Option 2: Self-Hosted PostgreSQL
1. Rent VPS (Linode, DigitalOcean, AWS)
2. Install PostgreSQL
3. Create database: `createdb soil_health`
4. Load schema: `psql -d soil_health < db/init.sql`
5. Configure firewall to allow backend only

## 📊 Monitoring & Troubleshooting

### Vercel Monitoring
- Dashboard: https://vercel.com/dashboard
- View logs: Click project → Deployments → View Logs
- Check build output and runtime errors

### Railway Monitoring
- Dashboard: https://railway.app/dashboard
- View logs: Click project → Logs tab
- Monitor resource usage

### Common Issues

**"Cannot connect to API"**
- Check `REACT_APP_API_BASE_URL` is correct
- Verify backend is running on Railway
- Check CORS configuration on backend

**"Database connection failed"**
- Verify `DB_HOST`, `DB_USER`, `DB_PASSWORD` are correct
- Check PostgreSQL is running on hosting platform
- Test connection manually: `psql -h host -U user -d soil_health`

**"Build fails on Vercel"**
- Check build logs for errors
- Verify `package.json` has all dependencies
- Ensure build command is correct

## 🔐 Security Checklist

- [ ] GitHub repository is private or has branch protection
- [ ] Database password is strong and stored in environment variables
- [ ] CORS is configured to allow only your frontend domain
- [ ] API authentication is implemented (if needed)
- [ ] Secrets are NOT committed to git
- [ ] .env files are in .gitignore

## 📱 Next Steps

### Phase 1: Basic Deployment (Current)
- [x] Build frontend
- [ ] Deploy to Vercel
- [ ] Deploy backend to Railway
- [ ] Test live application

### Phase 2: Production Hardening
- [ ] Set up SSL certificates
- [ ] Configure CDN for static assets
- [ ] Set up monitoring and alerts
- [ ] Configure automated backups
- [ ] Set up CI/CD pipeline

### Phase 3: Features & Scaling
- [ ] Add authentication (JWT tokens)
- [ ] Rate limiting on API
- [ ] Caching layer (Redis)
- [ ] Load balancing for backend
- [ ] Database replication

## 🆘 Support

- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app
- FastAPI Docs: https://fastapi.tiangolo.com
- React Docs: https://react.dev

---

**Total Deployment Time**: ~30 minutes  
**Cost**: Free tier available on Vercel + Railway  
**Complexity**: Beginner-friendly with step-by-step UI

Good luck! 🚀
