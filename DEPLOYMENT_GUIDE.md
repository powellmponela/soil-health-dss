# Soil Health DSS - Vercel Deployment Guide

## Prerequisites
- Vercel account (free at https://vercel.com)
- Vercel CLI installed (`npm install -g vercel`)
- GitHub, GitLab, or Bitbucket account (optional but recommended)

## Frontend Deployment (React app)

### Option 1: Git-Based Deployment (Recommended)

1. **Push to Git Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/soil-health-dss.git
   git push -u origin main
   ```

2. **Connect to Vercel via Git**
   - Go to https://vercel.com/new
   - Select your Git provider (GitHub, GitLab, or Bitbucket)
   - Authorize Vercel to access your repositories
   - Select the `soil-health-dss` repository
   - Configure build settings:
     - **Framework Preset**: React
     - **Build Command**: `cd frontend && npm run build`
     - **Output Directory**: `frontend/build`
     - **Install Command**: `cd frontend && npm install`

3. **Set Environment Variables**
   - In Vercel Dashboard → Project Settings → Environment Variables
   - Add: `REACT_APP_API_BASE_URL` = `https://your-api-domain.com`

4. **Deploy**
   - Click "Deploy"
   - Vercel will automatically build and deploy your frontend

### Option 2: Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   cd frontend
   vercel --prod
   ```

4. **Set Environment Variables**
   ```bash
   vercel env add REACT_APP_API_BASE_URL
   # Enter: https://your-api-domain.com
   ```

## Backend Deployment (Python FastAPI)

The Python backend needs to be deployed separately. Here are options:

### Option A: Railway (Recommended)
1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Configure environment:
   - Add PostgreSQL service
   - Set `PYTHONUNBUFFERED=1`
5. Railway will auto-detect and deploy the FastAPI app

### Option B: Render
1. Go to https://render.com
2. Create a new "Web Service"
3. Connect GitHub repository
4. Configure:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r api/requirements.txt`
   - **Start Command**: `cd api && python run.py`
5. Add PostgreSQL database
6. Deploy

### Option C: Heroku (Legacy but still works)
1. Install Heroku CLI
2. `heroku login`
3. `heroku create soil-health-api`
4. `git push heroku main`
5. Add PostgreSQL: `heroku addons:create heroku-postgresql:hobby-dev`

## Update Frontend API URL

Once your backend is deployed:

1. Update `frontend/.env.production.local`:
   ```
   REACT_APP_API_BASE_URL=https://your-api-service.railway.app
   ```

2. Or set in Vercel Dashboard:
   - Project Settings → Environment Variables
   - Update `REACT_APP_API_BASE_URL` with your backend URL

3. Redeploy frontend (Vercel will auto-rebuild on git push)

## Database Configuration

Both Railway and Render provide PostgreSQL. Update your Python backend with:
- `DB_HOST`: Provided by hosting service
- `DB_USER`: Provided by hosting service  
- `DB_PASSWORD`: Provided by hosting service
- `DB_NAME`: soil_health

## Post-Deployment Checklist

- [ ] Frontend loads at `https://your-project.vercel.app`
- [ ] Backend API running at `https://your-api-domain.com`
- [ ] Environment variables set on both services
- [ ] Database connection working
- [ ] CORS configured on backend to accept requests from Vercel domain
- [ ] Test API endpoints from frontend

## Troubleshooting

**Frontend shows "Failed to connect to API"**
- Check `REACT_APP_API_BASE_URL` environment variable
- Verify backend is running and accessible
- Check browser console for CORS errors
- Backend must have CORS enabled for Vercel domain

**Build fails on Vercel**
- Check build logs in Vercel Dashboard
- Ensure all dependencies in `frontend/package.json`
- Run `npm install` locally to test

**Backend database connection fails**
- Verify PostgreSQL connection string
- Check firewall/security group settings
- Ensure database is running and accessible

## Monitoring

- Vercel Dashboard: https://vercel.com/dashboard
- Railway/Render: Check respective dashboards for logs and metrics
- Use browser DevTools to check API calls and CORS issues

## CI/CD Pipeline

Vercel automatically deploys on every git push to your connected branch. To control this:
1. Go to Project Settings → Git
2. Set Deploy on push: On/Off
3. Configure protected branches if needed

## Costs

- **Vercel**: Free tier includes generous limits for frontend
- **Railway**: Free credits ($5/month), then pay-as-you-go
- **Render**: Free tier available, but limited resources
- **Database**: PostgreSQL typically $5-15/month depending on usage

