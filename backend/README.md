# Protein-Disease-Therapy Backend API

AI-powered backend for therapeutic opportunity discovery using LLMs to extract and structure biomedical data.

## Features

- **AI Data Collection**: Uses Claude/GPT-4 to extract disease-protein relationships from biomedical knowledge
- **REST API**: FastAPI backend serving protein, disease, therapy, and trial data
- **Therapeutic Scoring**: Algorithms to identify drug discovery opportunities and repurposing candidates
- **Real-time Analysis**: Hub analysis, opportunity scoring, and gap identification

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```env
# Use either Anthropic or OpenAI
ANTHROPIC_API_KEY=your_key_here
# OR
OPENAI_API_KEY=your_key_here

LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
```

### 3. Generate Data

Run the AI-powered data generation pipeline:

```bash
python scripts/generate_data.py
```

This will:
- Generate 100-200 diseases across categories
- Extract associated proteins using AI
- Build disease-protein associations with evidence
- Collect therapies and clinical trials
- Compute therapeutic opportunity scores
- Export to database and JSON

**Note**: Data generation takes 30-60 minutes depending on the number of diseases and LLM rate limits.

### 4. Start the Server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## API Endpoints

### Graph Data
- `GET /api/graph` - Get disease-protein network graph
  - Query params: `category`, `maturity`, `hub_min_degree`

### Disease Details
- `GET /api/disease/{id}` - Get disease with associated proteins

### Protein Details
- `GET /api/protein/{id}` - Get protein with diseases, therapies, and trials

### Opportunities
- `GET /api/opportunities` - Get ranked therapeutic opportunities
  - Query params: `limit` (default 20)

### Search
- `GET /api/search?q={query}` - Search diseases and proteins
  - Query params: `q` (required), `limit` (default 10)

## Project Structure

```
backend/
├── main.py                 # FastAPI application
├── config.py              # Configuration and settings
├── models.py              # Pydantic models
├── database.py            # SQLAlchemy database models
├── requirements.txt       # Python dependencies
│
├── data_collection/       # AI-powered data extraction
│   ├── ai_extractor.py        # LLM interface
│   ├── disease_collector.py   # Disease data collection
│   ├── protein_collector.py   # Protein data collection
│   ├── association_builder.py # Association extraction
│   ├── therapy_collector.py   # Drug/therapy data
│   └── trial_collector.py     # Clinical trials data
│
├── scoring/               # Opportunity scoring algorithms
│   ├── opportunity_scorer.py  # Gap score calculation
│   ├── hub_analyzer.py        # Protein hub identification
│   └── repurposing_finder.py  # Drug repurposing finder
│
└── scripts/
    └── generate_data.py   # Main data generation script
```

## Data Sources

The AI extracts information from:
- **Diseases**: CDC, WHO, medical literature
- **Proteins**: UniProt, biomedical knowledge bases
- **Associations**: DisGeNET, OMIM, PubMed
- **Therapies**: DrugBank, ChEMBL (via AI knowledge)
- **Clinical Trials**: ClinicalTrials.gov API

## Development

### Running Tests

```bash
pytest
```

### Database Management

Clear and regenerate database:
```bash
python scripts/generate_data.py
# Choose 'y' when prompted to clear existing data
```

View database:
```bash
sqlite3 protein_disease.db
.tables
SELECT COUNT(*) FROM diseases;
```

## Performance

- Initial data generation: ~30-60 minutes for 150 diseases
- API response time: <100ms for most endpoints
- Database: SQLite (can scale to PostgreSQL for production)

## Troubleshooting

**Issue**: "No LLM API key found"
- Solution: Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in `.env`

**Issue**: Rate limit errors during data generation
- Solution: Reduce `MAX_DISEASES` in `.env` or wait between batches

**Issue**: Import errors
- Solution: Ensure you're in the `backend` directory when running scripts

## License

MIT

