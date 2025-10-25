# Disease-Protein-Therapy Map

A production-ready React + Vite + TypeScript application for visualizing disease-protein-therapy networks with AI-assisted search, filtering, and therapeutic opportunity analysis.

## Features

- **Interactive Network Visualization**: Cytoscape.js-powered graph with disease-protein associations
- **AI-Assisted Search**: Fuzzy search with Fuse.js, BM25 ranking with MiniSearch, and optional semantic embeddings
- **Smart Filtering**: Filter by disease category, therapy maturity, and hub protein degree
- **Therapeutic Opportunities**: Ranked analysis of gaps in therapeutic coverage
- **Explainable AI**: Template-based explanations for proteins and diseases
- **CSV Import**: Upload your own data via CSV files
- **Type-Safe**: Full TypeScript implementation with Zod validation

## Quick Start

### Installation

```bash
# Install dependencies
npm install
# or
pnpm install
```

### Development

```bash
# Start development server
npm run dev
# or
pnpm dev
```

The app will be available at `http://localhost:5173`

### Build

```bash
# Build for production
npm run build
# or
pnpm build

# Preview production build
npm run preview
# or
pnpm preview
```

### Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run typecheck` - Run TypeScript type checking

## Demo Script

1. **Open the full map**: Navigate to `http://localhost:5173`
2. **Filter hub proteins**: Set "Hub Proteins (Min Degree)" slider to 5 or higher
3. **Click TNF**: The hub protein TNF should be highlighted (green = approved therapies)
4. **View Details**: Click TNF to open the details panel
5. **Explain**: Click the "AI Explanation" tab to see the generated summary
6. **Related**: Check the "Related" tab for semantic neighbors
7. **Opportunities**: View the opportunities panel on the right
8. **Export**: Click the download icon to export opportunities as CSV
9. **Search**: Try searching for "TNF" or "arthritis" in the search box
10. **Filters**: Experiment with different disease categories and maturity filters

## Data Replacement

To use your own data, replace `src/data/seed.json` with your data following this schema:

```json
{
  "diseases": [
    {
      "id": "unique_id",
      "name": "Disease Name",
      "category": "Category",
      "burden_score": 0.8,
      "sources": ["url1", "url2"]
    }
  ],
  "proteins": [
    {
      "id": "unique_id",
      "uniprot_id": "P12345",
      "symbol": "GENE",
      "name": "Protein Name",
      "family": "Family",
      "pathways": ["pathway1", "pathway2"],
      "sources": ["url1", "url2"]
    }
  ],
  "associations": [
    {
      "id": "unique_id",
      "disease_id": "disease_id",
      "protein_id": "protein_id",
      "association_strength": 0.9,
      "evidence_text": "Evidence description",
      "citations": ["pubmed_url"],
      "sources": ["source_url"],
      "maturity": "approved|trial|none",
      "last_updated": "2024-01-01"
    }
  ],
  "therapies": [
    {
      "id": "unique_id",
      "name": "Therapy Name",
      "target_protein_id": "protein_id",
      "status": "approved|trial|none",
      "drugbank_id": "DB12345",
      "chembl_id": "CHEMBL123",
      "indications": ["indication1", "indication2"],
      "sources": ["url1", "url2"]
    }
  ],
  "trials": [
    {
      "id": "unique_id",
      "nct_id": "NCT12345678",
      "phase": "Phase II",
      "status": "Recruiting",
      "condition": "Disease Name",
      "target_protein_id": "protein_id",
      "start_date": "2024-01-01",
      "link": "https://clinicaltrials.gov/study/NCT12345678",
      "sources": ["url1", "url2"]
    }
  ]
}
```

### CSV Import

Alternatively, you can import data via CSV files:

1. **diseases.csv**: `id,name,category,burden_score,sources`
2. **proteins.csv**: `id,uniprot_id,symbol,name,family,pathways,sources`
3. **associations.csv**: `id,disease_id,protein_id,association_strength,evidence_text,citations,sources,maturity,last_updated`

## Architecture

### Core Components

- **GraphView**: Cytoscape.js visualization with interactive nodes and edges
- **FiltersBar**: Multi-criteria filtering interface
- **SearchBox**: AI-powered search with fuzzy matching and semantic search
- **DetailsPanel**: Comprehensive node information with tabs
- **OpportunitiesPanel**: Ranked therapeutic opportunities with export

### Data Layer

- **dataClient.ts**: Zod-validated data access with in-memory caching
- **scoring.ts**: Gap score calculation and opportunity ranking
- **search.ts**: Multi-strategy search (Fuse.js + MiniSearch + embeddings)
- **explain.ts**: Template-based AI explanations

### State Management

- **useStore.ts**: Zustand store with typed selectors
- **Filters**: Category, maturity, hub degree
- **Selection**: Current node and type
- **Search**: Query, results, loading state
- **Graph**: Nodes, edges, loading, errors

### Type Safety

All data is validated with Zod schemas:
- `Disease`, `Protein`, `Association`, `Therapy`, `ClinicalTrial`
- `GraphNode`, `GraphEdge` for visualization
- `SearchResult`, `Opportunity` for UI state

## Performance

- **Initial graph**: ≤ 800 elements for smooth rendering
- **Lazy loading**: Embeddings load asynchronously without blocking
- **Memoization**: Graph transformations cached in dataClient
- **Debouncing**: Search queries debounced to 300ms
- **Virtualization**: Large lists virtualized for performance

## AI Features

### Search
- **Fuzzy Search**: Fuse.js for approximate string matching
- **BM25 Ranking**: MiniSearch for term frequency-based relevance
- **Semantic Search**: Universal Sentence Encoder embeddings (optional)
- **Fallback**: Graceful degradation when embeddings unavailable

### Scoring
- **Gap Score**: `association_strength × burden × maturity_penalty`
- **Maturity Penalty**: 1.0 (none), 0.5 (trial), 0.1 (approved)
- **Opportunity Ranking**: Sorted by therapeutic potential

### Explainability
- **Template-based**: Deterministic, fast explanations
- **Context-aware**: Incorporates associations, therapies, trials
- **Citation-aware**: Includes source references
- **Extensible**: Easy to add LLM integration later

## Development

### TypeScript Configuration

- **Strict mode**: All strict TypeScript settings enabled
- **Path mapping**: Clean import paths
- **Type checking**: `npm run typecheck` validates all types

### Linting

- **ESLint**: Configured for React + TypeScript
- **Prettier**: Code formatting (if configured)
- **Hooks**: React hooks linting enabled

### Testing

```bash
# Type checking
npm run typecheck

# Linting
npm run lint

# Build verification
npm run build
```

## Browser Support

- **Modern browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **WebGL**: Required for Cytoscape.js rendering
- **ES2020**: Modern JavaScript features used

## Troubleshooting

### Common Issues

1. **Graph not rendering**: Check browser console for WebGL errors
2. **Search not working**: Verify Fuse.js and MiniSearch are loaded
3. **Embeddings failing**: Check network connection, falls back to BM25
4. **Type errors**: Run `npm run typecheck` to identify issues

### Performance Issues

1. **Slow rendering**: Reduce initial graph size in seed data
2. **Search lag**: Increase debounce delay in SearchBox
3. **Memory usage**: Clear search cache periodically

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with proper TypeScript types
4. Run `npm run typecheck` and `npm run lint`
5. Test thoroughly
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- **Cytoscape.js**: Network visualization
- **Material-UI**: React component library
- **Zustand**: State management
- **Fuse.js**: Fuzzy search
- **MiniSearch**: BM25 search
- **TensorFlow.js**: Universal Sentence Encoder
- **PapaParse**: CSV parsing
