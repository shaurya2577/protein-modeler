# Setup Instructions

Complete setup guide for the AI-Powered Protein-Disease-Therapy Map.

## Prerequisites

- **Python 3.10+**: Backend API and data generation
- **Node.js 18+**: Frontend application
- **LLM API Key**: Anthropic (Claude) or OpenAI (GPT-4)
  - Get Anthropic key: https://console.anthropic.com/
  - Get OpenAI key: https://platform.openai.com/api-keys

## Step 1: Clone and Navigate

```bash
cd /Users/shaurya/dev/protein-modeler
```

## Step 2: Backend Setup

### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Or use a virtual environment (recommended):

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file:

```env
# Required: Add your API key
ANTHROPIC_API_KEY=sk-ant-xxxxx
# OR
OPENAI_API_KEY=sk-xxxxx

# LLM Settings
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022

# Data Settings
MAX_DISEASES=150
MIN_ASSOCIATION_STRENGTH=0.3

# API Settings (defaults are fine)
API_HOST=0.0.0.0
API_PORT=8000
```

### Generate Data

This is the most important step - it uses AI to create your dataset:

```bash
python scripts/generate_data.py
```

**What it does:**
- Uses Claude/GPT-4 to generate 150 diseases across all categories
- Extracts 5-10 proteins per disease
- Builds evidence-based associations
- Collects approved therapies and clinical trials
- Computes therapeutic opportunity scores
- Creates SQLite database and JSON export

**Time required:** 30-60 minutes (depends on API rate limits)

**Cost estimate:** $5-15 in API credits (150 diseases with comprehensive data)

**Watch for:**
- Progress messages showing each disease being processed
- Any rate limit warnings (script has retry logic)
- Final summary showing total diseases, proteins, associations

When prompted "Clear existing data? (y/N):", type `y` if regenerating.

### Start Backend Server

```bash
python main.py
```

Or with uvicorn for development:

```bash
uvicorn main:app --reload
```

**Verify it's working:**
- Visit: http://localhost:8000
- API docs: http://localhost:8000/docs
- Test endpoint: http://localhost:8000/api/graph

## Step 3: Frontend Setup

### Install Dependencies

```bash
cd ../protein-modeler-app
npm install
```

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Backend API URL
VITE_API_URL=http://localhost:8000

# Data mode: 'api' fetches from backend, 'local' uses JSON file
VITE_DATA_MODE=api
```

### Start Development Server

```bash
npm run dev
```

**Verify it's working:**
- Visit: http://localhost:5173
- You should see the Disease-Protein-Therapy Map
- The Opportunities Panel should load with real data

## Step 4: Verify Everything Works

### Backend Health Check

```bash
# Test API endpoints
curl http://localhost:8000/api/graph | jq

# Check opportunities
curl http://localhost:8000/api/opportunities?limit=5 | jq

# Search diseases
curl http://localhost:8000/api/search?q=alzheimer | jq
```

### Frontend Check

1. Open http://localhost:5173
2. Look for the Therapeutic Opportunities panel on the right
3. You should see diseases, proteins, scores, and maturity levels
4. Try filtering by disease category
5. Click on a disease or protein to see details

## Troubleshooting

### "No LLM API key found!"

**Problem:** Missing or invalid API key

**Solution:**
```bash
cd backend
cat .env  # Check if key is present
# Make sure it starts with sk-ant- (Anthropic) or sk- (OpenAI)
# No quotes needed in .env file
```

### "Failed to load seed data"

**Problem:** Data generation didn't complete or JSON file is missing

**Solution:**
```bash
cd backend
# Check if database exists
ls -la protein_disease.db

# Check if JSON was exported
ls -la ../protein-modeler-app/src/data/generated_seed.json

# If missing, regenerate
python scripts/generate_data.py
```

### "Connection refused" or "Network error"

**Problem:** Backend not running or wrong URL

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000

# If not, start it
cd backend
python main.py

# Check frontend .env
cd ../protein-modeler-app
cat .env  # Should have VITE_API_URL=http://localhost:8000
```

### Rate limiting errors during data generation

**Problem:** Too many API requests to LLM

**Solution:**
```bash
# Edit backend/.env and reduce diseases
MAX_DISEASES=50  # Start smaller

# Or wait a few minutes and the script will retry automatically
```

### Empty opportunities panel

**Problem:** No data loaded or all associations have approved therapies

**Solution:**
```bash
# Check if data exists in database
cd backend
sqlite3 protein_disease.db
SELECT COUNT(*) FROM associations WHERE maturity = 'none';
.quit

# If 0 results, regenerate with more diseases
```

## Production Deployment

### Backend

```bash
cd backend

# Set production environment
cp .env.example .env.prod
# Edit .env.prod with production settings

# Run with production server
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend

```bash
cd protein-modeler-app

# Build for production
npm run build

# Serve with any static file server
npx serve -s dist

# Or deploy to Vercel, Netlify, etc.
```

### Database

For production, consider migrating to PostgreSQL:

```env
# backend/.env.prod
DATABASE_URL=postgresql://user:password@localhost/protein_disease
```

## Next Steps

Once everything is running:

1. **Explore the Data**: Use filters to find interesting patterns
2. **Analyze Opportunities**: Look at high-scoring therapeutic gaps
3. **Discover Hubs**: Find proteins involved in many diseases
4. **Export Data**: Use API to export specific analyses
5. **Customize**: Modify disease list or scoring algorithms

## Development Workflow

### Adding New Diseases

```bash
cd backend

# Edit the disease list in data_collection/disease_collector.py
# Or adjust MAX_DISEASES in .env

# Regenerate
python scripts/generate_data.py  # Choose 'y' to clear old data
```

### Adjusting Scoring

Edit `backend/scoring/opportunity_scorer.py`:
- Modify `calculate_gap_score()` function
- Adjust maturity penalties
- Add new scoring factors

### Frontend Customization

- **Styling**: Edit `protein-modeler-app/src/index.css`
- **Components**: Modify files in `protein-modeler-app/src/components/`
- **Scoring Display**: Update `OpportunitiesPanel.tsx`

## Common Tasks

### Clear and regenerate all data

```bash
cd backend
python scripts/generate_data.py
# Type 'y' when prompted
```

### Query the database directly

```bash
cd backend
sqlite3 protein_disease.db

.tables
SELECT * FROM diseases LIMIT 5;
SELECT * FROM proteins WHERE id LIKE '%TNF%';
SELECT * FROM associations WHERE maturity = 'none' ORDER BY association_strength DESC LIMIT 10;
.quit
```

### Export data for analysis

```bash
# Get all opportunities
curl http://localhost:8000/api/opportunities?limit=100 > opportunities.json

# Get specific protein
curl http://localhost:8000/api/protein/TNF > tnf_data.json

# Get graph data
curl http://localhost:8000/api/graph > network.json
```

## Support

- **Backend Issues**: Check `backend/README.md`
- **API Documentation**: http://localhost:8000/docs
- **Frontend Issues**: Check React DevTools console for errors

## Summary Checklist

- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] API key obtained (Anthropic or OpenAI)
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Backend `.env` configured with API key
- [ ] Data generated (`python scripts/generate_data.py`)
- [ ] Backend running (`python main.py`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Frontend `.env` configured
- [ ] Frontend running (`npm run dev`)
- [ ] Can access http://localhost:8000/docs
- [ ] Can access http://localhost:5173
- [ ] Opportunities panel shows data

**You're all set! 🎉**

