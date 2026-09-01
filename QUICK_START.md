# Soil Health DSS - Quick Start Guide

## Project Overview

This is a full-stack web application for managing and analyzing soil health frameworks:
- **Frontend**: React application (port 3000)
- **Backend**: Python FastAPI (port 8000)
- **Database**: PostgreSQL

## Local Development Setup

### Prerequisites
- Node.js 16+ and npm
- Python 3.10+
- PostgreSQL 12+

### 1. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 2. Install Backend Dependencies
```bash
cd api
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Create database (Linux/Mac)
createdb soil_health

# Or with psql:
psql -U postgres -c "CREATE DATABASE soil_health;"

# Initialize schema
psql -U postgres -d soil_health < ../db/init.sql
```

### 4. Start Backend (Terminal 1)
```bash
cd api
python run.py
```
Backend will be available at: http://localhost:8000

### 5. Start Frontend (Terminal 2)
```bash
cd frontend
npm start
```
Frontend will be available at: http://localhost:3000

## Project Structure

```
soil-health-dss/
├── frontend/                 # React application
│   ├── src/
│   │   ├── App.js           # Main application component
│   │   └── App.css          # Styles
│   ├── public/              # Static assets
│   └── package.json         # Dependencies
│
├── api/                      # Python FastAPI backend
│   ├── logic.py             # Main API routes
│   ├── db_utils.py          # Database utilities
│   ├── ontology_utils.py    # Ontology operations
│   ├── agrovoc_utils.py     # AGROVOC integration
│   ├── run.py               # Entry point
│   └── requirements.txt     # Python dependencies
│
├── db/                       # Database
│   └── init.sql             # Schema initialization
│
├── Frameworks/              # PDF framework documents
├── data/                    # Data files
├── principles_indicators/   # Extracted indicators and principles
└── DEPLOYMENT_GUIDE.md      # Production deployment instructions
```

## Available Sections

### 1. **Process**
- Data processing pipeline
- Framework extraction and analysis

### 2. **Database**  
- Framework registry (64 frameworks)
- Principle-indicator matrix
- Searchable database

### 3. **Provider Input**
- Register new frameworks
- Submit suggestions
- Contribute data

### 4. **Analytics Engine**
- Text extraction analysis
- Clustering and hierarchical analysis
- Semantic mapping

### 5. **Results**
- Evaluation results
- Framework comparisons
- Visual analytics

### 6. **Strategic Summary**
- Global alignment analysis
- Evolution trends
- Design domain assessment

## API Endpoints

### Frameworks
- `GET /frameworks` - List all frameworks
- `GET /frameworks/{id}` - Get specific framework

### Database
- `GET /db/status` - Database status
- `POST /db/refresh` - Refresh database

### Ontology
- `GET /ontology/master` - Master ontology
- `GET /ontology/mponela-hierarchy` - Mponela hierarchy

### Analytics  
- `GET /analytics/mponela/terms-summary` - Terms summary
- `POST /analytics/suggest` - Submit suggestions

## Environment Variables

### Frontend (.env or .env.local)
```
REACT_APP_API_BASE_URL=http://localhost:8000
```

### Backend (.env or os environment)
```
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=soil_health
```

## Development Tips

### Hot Reload
Both frontend and backend support hot reload:
- **Frontend**: Automatically reloads on file changes
- **Backend**: Uvicorn auto-reloads with `reload=True`

### Debug Frontend
Open browser DevTools (F12) to inspect:
- Console for errors
- Network tab for API calls
- React DevTools extension

### Debug Backend
Check terminal output for:
- API request logs
- Database queries
- Error tracebacks

### Database Access
```bash
# Access database directly
psql -U postgres -d soil_health

# Common queries
SELECT * FROM frameworks;
SELECT * FROM documents;
SELECT * FROM registrations;
```

## Common Issues

**"Cannot connect to database"**
- Ensure PostgreSQL is running
- Check connection string in run.py
- Verify database exists: `psql -l`

**"API connection refused"**
- Check if backend is running: http://localhost:8000/docs
- Verify REACT_APP_API_BASE_URL is correct
- Check firewall settings

**"Port already in use"**
- Check what's using the port: `lsof -i :3000` (frontend) or `:8000` (backend)
- Kill process or use different port

**Dependencies installation fails**
- Clear cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- For Python: Create fresh virtual environment

## Deployment

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for production deployment instructions to:
- Vercel (frontend)
- Railway/Render (backend)
- Docker & Kubernetes

## Contributing

1. Create a branch: `git checkout -b feature/your-feature`
2. Make changes
3. Commit: `git commit -am 'Add feature'`
4. Push: `git push origin feature/your-feature`
5. Create Pull Request

## Support

For issues or questions:
1. Check existing GitHub issues
2. Create new issue with details
3. Include error messages and steps to reproduce

## License

[Your License Here]

## Authors

Powell Mponela, Vimbayi Grace Petrova Chimonyo, and team

---

**Last Updated**: 2026-09-01
