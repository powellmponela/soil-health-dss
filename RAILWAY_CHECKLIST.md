# 🚀 Backend Deployment Checklist - Railway

## Pre-Deployment

- [ ] Frontend already deployed to Vercel (URL noted)
- [ ] Code committed to GitHub
- [ ] `api/requirements.txt` contains all dependencies
- [ ] `api/run.py` exists and calls migrate_data()
- [ ] `db/init.sql` contains schema
- [ ] Procfile created ✅
- [ ] runtime.txt created ✅

## Deployment Steps

### 1. Go to Railway.app
- [ ] Visit https://railway.app
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub"

### 2. Authenticate & Select Repository
- [ ] Connect GitHub account
- [ ] Authorize Railway app access
- [ ] Select "powellmponela/soil-health-dss" repository
- [ ] Click "Deploy"

### 3. Wait for Build (2-5 minutes)
- [ ] Watch Railway dashboard
- [ ] Check logs for errors
- [ ] Look for "Uvicorn running" message
- [ ] Deployment should be marked "Success" ✅

### 4. Add PostgreSQL Database
- [ ] Click "+ New Service"
- [ ] Select "Database"
- [ ] Select "PostgreSQL"
- [ ] Railway creates database automatically

### 5. Check Environment Variables
In Railway → Variables tab:

```
DB_HOST=postgres.railway.internal  (auto-set)
DB_USER=postgres                    (auto-set)
DB_PASSWORD=xxxx                    (auto-set)
DB_NAME=railway                     (auto-set)
DATABASE_URL=postgresql://...       (auto-set)
```

- [ ] All variables appear automatically
- [ ] No manual entry needed ✅

### 6. Verify Database Schema Loaded
- [ ] Check Railway logs for: "Importing frameworks..."
- [ ] Look for: "Frameworks: 64, Documents: 64"
- [ ] Migration completed successfully ✅

### 7. Test Backend API
- [ ] Get your Railway URL from Deployments tab
- [ ] Visit: `https://your-api.railway.app/docs`
- [ ] Should show Swagger UI (interactive API docs)
- [ ] Click on `/frameworks` endpoint
- [ ] Execute: Should return list of frameworks
- [ ] API working! ✅

### 8. Note Your Backend URL
- [ ] Copy API URL (e.g., `https://api.railway.app`)
- [ ] Save for next step

## Post-Deployment

### 9. Update Frontend on Vercel
- [ ] Go to Vercel dashboard
- [ ] Select your "soil-health-dss" project
- [ ] Go to Settings → Environment Variables
- [ ] Update `REACT_APP_API_BASE_URL`:
  - Old: `http://localhost:8000`
  - New: `https://your-api.railway.app`
- [ ] Click "Save"
- [ ] Vercel auto-redeploys (2-3 min)

### 10. Test End-to-End
- [ ] Visit your Vercel frontend URL
- [ ] Navigate to "Database" section
- [ ] Should see 64 frameworks loaded
- [ ] No "Cannot connect to API" error
- [ ] Click on framework → should work
- [ ] All sections functional ✅

## Monitoring

### 11. Set Up Alerts (Optional)
- [ ] Railway dashboard → Metrics
- [ ] Set CPU/Memory alerts
- [ ] Set uptime alerts

### 12. Check Logs Daily
- [ ] Railway → Logs tab
- [ ] Look for errors
- [ ] Monitor performance
- [ ] Database health

## Troubleshooting

### Build Failed?
1. Check Railway logs for specific error
2. Common issues:
   - Missing `api/requirements.txt`
   - Wrong Python version in `runtime.txt`
   - Syntax error in `api/run.py`
3. Fix locally, push to GitHub, Railway auto-retries

### API Not Responding?
1. Check if Railway deployment succeeded
2. Verify PostgreSQL service is running
3. Check environment variables are set
4. Look at live logs for errors

### Cannot Connect Frontend to Backend?
1. Verify CORS is enabled in backend
2. Check `REACT_APP_API_BASE_URL` is correct
3. Make sure Railway backend URL is accessible
4. Test directly: `curl https://your-api.railway.app/docs`

### Database Migration Failed?
1. Check Railway logs
2. Verify `db/init.sql` exists and is valid
3. Manually run: `psql $DATABASE_URL < db/init.sql`
4. Check PostgreSQL service health

## Success Criteria ✅

- [ ] Railway deployment shows "Success"
- [ ] PostgreSQL database operational
- [ ] API docs accessible at `/docs`
- [ ] `GET /frameworks` returns 64 frameworks
- [ ] Frontend displays data without errors
- [ ] All sections load correctly
- [ ] No console errors in browser

## Next Steps (Optional)

- [ ] Set up CI/CD pipeline
- [ ] Configure monitoring alerts
- [ ] Set up automatic backups
- [ ] Configure custom domain
- [ ] Enable SSL certificate

---

**Total Time**: ~15-20 minutes  
**Cost**: Free tier available  
**Status**: Ready for production ✨

---

**Questions?** See [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) for detailed troubleshooting.
