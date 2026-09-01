# Soil Health DSS - Decision Support System

A comprehensive web-based Decision Support System for soil health assessment and framework management, built with React and Python FastAPI.

## Features

✨ **Framework Management**
- Registry of 64 soil health frameworks
- Searchable, filterable database
- Document access and PDF support

📊 **Analytics Engine**
- Natural Language Processing for framework extraction
- Hierarchical clustering analysis
- Semantic mapping and ontology integration

🎯 **Decision Support**
- Provider input for framework contributions
- Strategic summary and evaluation tools
- Multi-principle indicator analysis

🌍 **Global Insights**
- Alignment analysis across frameworks
- Evolution trends visualization
- Design domain assessment

## Quick Start

### Local Development (5 minutes)

```bash
# 1. Install dependencies
cd frontend && npm install
cd ../api && pip install -r requirements.txt

# 2. Start backend (Terminal 1)
cd api && python run.py

# 3. Start frontend (Terminal 2)
cd frontend && npm start

# Open http://localhost:3000
```

See [QUICK_START.md](./QUICK_START.md) for detailed setup.

## Production Deployment

### Deploy to Vercel + Railway (Recommended)

**Step 1: Deploy Frontend to Vercel**
```bash
# Option A: Using CLI
npm install -g vercel
vercel --prod

# Option B: Git-based (recommended)
# - Push to GitHub
# - Visit https://vercel.com/new
# - Connect repository
# - Deploy (Vercel auto-detects React)
```

**Step 2: Deploy Backend to Railway**
```bash
# Visit https://railway.app
# New Project → Deploy from GitHub
# Select this repository
# Railway auto-detects and deploys FastAPI
```

**Step 3: Configure Environment**
- Update `REACT_APP_API_BASE_URL` in Vercel with Railway backend URL
- Vercel auto-redeploys on environment variable changes

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for alternatives (Render, Heroku, Docker).

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | React 18, Framer Motion, Lucide Icons |
| Backend | Python 3.10+, FastAPI, Uvicorn |
| Database | PostgreSQL 12+ |
| Hosting | Vercel (Frontend), Railway/Render (Backend) |
| API | RESTful with JSON |

## Project Structure

```
soil-health-dss/
├── frontend/               # React SPA
│   ├── public/            # Static assets
│   ├── src/
│   │   ├── App.js         # Main component
│   │   ├── App.css        # Styles
│   │   └── index.js       # Entry
│   └── package.json
│
├── api/                    # Python backend
│   ├── logic.py           # FastAPI routes
│   ├── db_utils.py        # Database layer
│   ├── ontology_utils.py  # Ontology operations
│   ├── run.py             # Startup script
│   └── requirements.txt
│
├── db/                     # Database
│   └── init.sql           # Schema
│
├── Frameworks/            # PDF documents (64)
├── data/                  # Datasets
├── principles_indicators/ # Extracted data
└── docs/                  # Documentation
```

## API Documentation

### Interactive Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints
```
GET  /frameworks              # List all frameworks
GET  /frameworks/{id}         # Get framework details
GET  /db/status               # Database status
GET  /ontology/master         # Master ontology
GET  /ontology/mponela-hierarchy
POST /analytics/suggest       # Submit suggestions
```

## Environment Variables

### Frontend
```
REACT_APP_API_BASE_URL=http://localhost:8000  # API endpoint
```

### Backend
```
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=soil_health
```

## Database

### Initialize
```bash
createdb soil_health
psql -d soil_health < db/init.sql
```

### Schema
- **frameworks**: 64 registered frameworks
- **documents**: PDF metadata and paths
- **registrations**: User contributions
- **suggestions**: Community feedback

## Development

### Frontend
```bash
cd frontend
npm start          # Development server (hot reload)
npm run build      # Production build
npm test           # Run tests
```

### Backend
```bash
cd api
python run.py      # Auto-reload dev server on file changes
pytest             # Run tests (if configured)
```

### Database
```bash
# Access directly
psql -d soil_health

# Run migrations
python migrate.py
```

## Deployment Options

| Platform | Frontend | Backend | Database | Cost |
|----------|----------|---------|----------|------|
| **Vercel + Railway** (Recommended) | Vercel | Railway | Railway | Free tier available |
| Vercel + Render | Vercel | Render | Render | Free tier available |
| Vercel + Heroku | Vercel | Heroku | Heroku | Paid (Heroku changed model) |
| Docker + Kubernetes | Docker | Docker | Docker | $5+/month |
| Self-hosted | nginx | gunicorn | PostgreSQL | $5+/month VPS |

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed instructions.

## Troubleshooting

### Frontend Issues
- **"Cannot connect to API"**: Check REACT_APP_API_BASE_URL
- **"Port 3000 in use"**: `lsof -i :3000` or use different port
- **Build fails**: Clear node_modules: `rm -rf node_modules && npm install`

### Backend Issues
- **"Database connection failed"**: Check PostgreSQL is running
- **"Port 8000 in use"**: `lsof -i :8000` or configure different port
- **Import errors**: Install all dependencies: `pip install -r requirements.txt`

### Deployment Issues
- **Vercel build fails**: Check build logs, ensure dependencies in package.json
- **CORS errors**: Backend must allow frontend domain in CORS configuration
- **API timeout**: Check Railway/Render service is running, not sleeping

See [QUICK_START.md](./QUICK_START.md#common-issues) for more solutions.

## Contributing

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** Pull Request

## Features Roadmap

- [ ] Real-time collaboration
- [ ] Advanced analytics dashboards
- [ ] Machine learning recommendations
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] Audit trail and versioning
- [ ] API rate limiting and authentication

## Citation

If you use this system in research, please cite:

```bibtex
@article{mponela2026soil,
  title={Soil-health frameworks in agri-food systems. A review},
  author={Mponela, Powell and Chimonyo, Vimbayi Grace Petrova and others},
  journal={Agronomy for Sustainable Development},
  volume={46},
  year={2026}
}
```

## License

[Add your license here]

## Support

- **Documentation**: See QUICK_START.md and DEPLOYMENT_GUIDE.md
- **Issues**: GitHub Issues tab
- **Discussions**: GitHub Discussions
- **Email**: [your-email@example.com]

## Authors

- **Powell Mponela** - Lead developer
- **Vimbayi Grace Petrova Chimonyo** - Research lead
- **Team Contributors** - See CONTRIBUTORS.md

## Acknowledgments

- Agricultural frameworks community
- Open-source libraries and tools
- Research funders and institutions

---

**Last Updated**: 2026-09-01  
**Version**: 1.0.0  
**Status**: Production Ready ✅

[Star us on GitHub ⭐](https://github.com/your-username/soil-health-dss)
