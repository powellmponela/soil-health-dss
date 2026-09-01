# Railway Backend Deployment Guide

## Why Railway?

✅ **Easiest for FastAPI**: Auto-detects Python + FastAPI  
✅ **Free tier**: $5/month free credits (sufficient for testing)  
✅ **One-click PostgreSQL**: Database included in platform  
✅ **Auto-deploys**: Git push = automatic deployment  
✅ **Simple setup**: No configuration files needed  

---

## 🚀 Deploy in 5 Minutes

### Step 1: Go to Railway Dashboard
1. Visit **https://railway.app**
2. Sign up with GitHub (recommended) or email
3. Click **"New Project"**

### Step 2: Select Deployment Source
1. Click **"Deploy from GitHub"**
2. Connect your GitHub account when prompted
3. Select **"Approve & Install"** to allow Railway access
4. Choose repository: **`soil-health-dss`**
5. Click **"Deploy"**

### Step 3: Railway Auto-Detects & Builds

Railway will:
- ✅ Detect Python project
- ✅ Detect FastAPI in `api/` folder
- ✅ Install dependencies from `api/requirements.txt`
- ✅ Start backend with `python api/run.py`
- ✅ Create public URL like `https://api.railway.app`

**Build takes 2-5 minutes** - Watch the logs in Railway dashboard

### Step 4: Add PostgreSQL Database

**Option A: Railway-Hosted PostgreSQL (Easy)**
1. In Railway dashboard, click **"+ New Service"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway creates database automatically
4. Copy connection details (they auto-populate as env vars)

**Option B: Use External Database**
If you have existing PostgreSQL:
- Get connection string
- Set environment variables manually (Step 5)

### Step 5: Configure Environment Variables

In Railway dashboard → Variables:

**Required Variables:**
```
DB_HOST=localhost  (or your PostgreSQL host)
DB_USER=postgres   (default PostgreSQL user)
DB_PASSWORD=xyz    (your password)
DB_NAME=soil_health
DATABASE_URL=postgresql://user:pass@host:5432/soil_health
```

**Optional Variables:**
```
PYTHONUNBUFFERED=1
RAILWAY_ENVIRONMENT=production
```

**Auto-populated by Railway PostgreSQL:**
- If you added Railway PostgreSQL, these vars auto-populate
- No manual entry needed ✨

### Step 6: Database Schema

Railroad creates empty PostgreSQL. You need to initialize schema:

**Option A: Auto-run Migration (Recommended)**
- `api/run.py` has `migrate_data()` that runs on startup
- Loads schema + data automatically
- Already configured! ✅

**Option B: Manual Migration**
```bash
# Via Railway terminal:
psql $DATABASE_URL < db/init.sql
```

## ✅ Deployment Checklist

- [ ] GitHub account connected to Railway
- [ ] Repository imported (`soil-health-dss`)
- [ ] Build succeeds (check Railway logs)
- [ ] PostgreSQL database added
- [ ] Environment variables set
- [ ] Migration runs (check Railway logs for "Frameworks: 64, Documents: 64")
- [ ] Test API at `https://api.railway.app/docs` (should show Swagger UI)

---

## 🔍 How to Check Deployment

### View Logs
1. Railway dashboard → Your project
2. Click **"Logs"** tab
3. Look for:
   ```
   Creating tables...
   Importing frameworks...
   Frameworks: 64, Documents: 64
   Uvicorn running on 0.0.0.0:8000
   ```

### Test API Endpoints
```bash
# Replace with your Railway URL
https://api.railway.app/docs          # Swagger UI
https://api.railway.app/frameworks    # API endpoint
https://api.railway.app/db/status     # Database status
```

### Get Your Backend URL
1. Railway dashboard → Deployments
2. Click your deployment
3. Copy the "Service URL"
4. Example: `https://api-prod.railway.app`

---

## 📝 Update Frontend

After backend deploys, update frontend API URL:

### In Vercel Dashboard:
1. Go to your project settings
2. Environment Variables
3. Update `REACT_APP_API_BASE_URL`
   - **Old**: `http://localhost:8000`
   - **New**: `https://api-prod.railway.app` (use your Railway URL)
4. Click "Save"
5. Vercel auto-redeploys frontend

### Verify Connection:
- Visit your Vercel frontend URL
- Database section should load frameworks
- No "Cannot connect to API" error

---

## 🆘 Troubleshooting

### Build Fails
**Error**: `ModuleNotFoundError: No module named 'fastapi'`
- **Cause**: `api/requirements.txt` not found
- **Fix**: Ensure `api/requirements.txt` exists in root of repo

**Error**: `AttributeError: module 'uvicorn' has no attribute 'run'`
- **Cause**: Uvicorn version mismatch
- **Fix**: Check `requirements.txt` has `uvicorn>=0.50.0`

### Cannot Connect to Database
**Error**: `psycopg2.OperationalError: could not connect to server`
- **Cause**: `DB_HOST` or credentials wrong
- **Fix**: Copy exact connection string from Railway PostgreSQL service
- **Test**: 
  ```bash
  psql $DATABASE_URL  # Try connecting via Railway terminal
  ```

### API Returns 500 Error
1. Check Railway logs for error details
2. Verify database migration completed
3. Check environment variables are set
4. Restart service in Railway dashboard

### CORS Errors (Frontend → Backend)
**Error**: `Access to XMLHttpRequest has been blocked by CORS policy`
- **Fix**: Backend needs CORS enabled for frontend domain
- **In `api/logic.py`**, add:
  ```python
  from fastapi.middleware.cors import CORSMiddleware
  
  app.add_middleware(
      CORSMiddleware,
      allow_origins=[
          "https://soil-health-dss.vercel.app",  # Your Vercel domain
          "http://localhost:3000"  # Local dev
      ],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
- Commit and push → Auto-redeploys

---

## 📊 Railway Pricing & Usage

| Feature | Cost |
|---------|------|
| Compute (per hour) | $0.000925 |
| Storage (per GB/month) | $1 |
| PostgreSQL | Included |
| **Total Estimate** | ~$5-15/month (depending on usage) |

**Free Credits**: Railway gives $5/month free to start

---

## 🔐 Security Best Practices

- ✅ Don't commit `.env` files
- ✅ Use Railway environment variables for secrets
- ✅ Enable CORS only for your frontend domain
- ✅ Use HTTPS for all requests
- ✅ Rotate database password monthly
- ✅ Enable Railway monitoring & alerts

---

## ⚡ Advanced: Custom Deployment

### Use Railway CLI (Optional)
```bash
npm install -g @railway/cli
railway login                    # Authenticate with GitHub
railway service add postgres    # Add PostgreSQL
railway service add python      # Add Python service
railway up                       # Deploy
railway open                     # View dashboard
```

### Monitor Performance
- Railway Dashboard → Metrics tab
- View CPU, memory, network usage
- Set alerts for high usage

### Rollback Deployment
1. Railway → Deployments tab
2. Click previous deployment
3. Click "Deploy"
4. Done! (Instant rollback)

---

## 📞 Support

- Railway Docs: https://docs.railway.app
- Railway Pricing: https://railway.app/pricing
- FastAPI Docs: https://fastapi.tiangolo.com
- PostgreSQL Docs: https://www.postgresql.org/docs

---

## Next Steps

1. ✅ Deploy backend to Railway (5 min)
2. ✅ Note your Railway URL
3. ✅ Update frontend REACT_APP_API_BASE_URL
4. ✅ Test end-to-end on Vercel
5. 🎉 Celebrate! Your app is live! 🚀

---

**Estimated Total Time**: 10 minutes  
**Cost**: Free tier available  
**Difficulty**: Beginner-friendly ⭐⭐☆☆☆
