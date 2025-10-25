from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List
import json

from config import settings
from database import get_db, init_db, DiseaseDB, ProteinDB, AssociationDB, TherapyDB, ClinicalTrialDB
from models import (
    Disease, Protein, Association, Therapy, ClinicalTrial,
    GraphResponse, GraphNode, GraphEdge,
    DiseaseWithAssociations, ProteinWithContext, AssociationWithProtein, AssociationWithDisease,
    Opportunity, SearchResult, Maturity
)
from scoring.opportunity_scorer import calculate_opportunities

# Initialize FastAPI app
app = FastAPI(
    title="Protein-Disease-Therapy API",
    description="AI-powered therapeutic opportunity discovery platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/")
async def root():
    return {
        "message": "Protein-Disease-Therapy API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/graph", response_model=GraphResponse)
async def get_graph(
    category: Optional[str] = None,
    maturity: Optional[Maturity] = None,
    hub_min_degree: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get graph nodes and edges with optional filters"""
    
    # Get all diseases
    disease_query = db.query(DiseaseDB)
    if category:
        disease_query = disease_query.filter(DiseaseDB.category == category)
    diseases = disease_query.all()
    disease_ids = {d.id for d in diseases}
    
    # Get associations
    assoc_query = db.query(AssociationDB)
    if category:
        assoc_query = assoc_query.filter(AssociationDB.disease_id.in_(disease_ids))
    if maturity:
        assoc_query = assoc_query.filter(AssociationDB.maturity == maturity)
    associations = assoc_query.all()
    
    # Get protein IDs from associations
    protein_ids = {a.protein_id for a in associations}
    proteins = db.query(ProteinDB).filter(ProteinDB.id.in_(protein_ids)).all()
    
    # Calculate degrees
    protein_degrees = {}
    for protein_id in protein_ids:
        degree = len([a for a in associations if a.protein_id == protein_id])
        protein_degrees[protein_id] = degree
    
    # Filter by hub degree
    if hub_min_degree is not None:
        protein_ids = {pid for pid, deg in protein_degrees.items() if deg >= hub_min_degree}
        proteins = [p for p in proteins if p.id in protein_ids]
        associations = [a for a in associations if a.protein_id in protein_ids]
    
    # Build nodes
    nodes = []
    
    # Disease nodes
    for disease in diseases:
        if disease.id in disease_ids:
            nodes.append(GraphNode(
                id=disease.id,
                type="disease",
                label=disease.name,
                burden=disease.burden_score,
                degree=None,
                maturity=None
            ))
    
    # Protein nodes
    for protein in proteins:
        nodes.append(GraphNode(
            id=protein.id,
            type="protein",
            label=protein.symbol or protein.name or protein.id,
            burden=None,
            degree=protein_degrees.get(protein.id, 0),
            maturity=None
        ))
    
    # Build edges
    edges = []
    for assoc in associations:
        edges.append(GraphEdge(
            id=assoc.id,
            source=assoc.disease_id,
            target=assoc.protein_id,
            strength=assoc.association_strength
        ))
    
    return GraphResponse(nodes=nodes, edges=edges)


@app.get("/api/disease/{disease_id}", response_model=DiseaseWithAssociations)
async def get_disease(disease_id: str, db: Session = Depends(get_db)):
    """Get disease details with associated proteins"""
    
    disease = db.query(DiseaseDB).filter(DiseaseDB.id == disease_id).first()
    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")
    
    # Get associations
    associations = db.query(AssociationDB).filter(
        AssociationDB.disease_id == disease_id
    ).all()
    
    # Enrich with protein data
    associations_with_proteins = []
    for assoc in associations:
        protein = db.query(ProteinDB).filter(ProteinDB.id == assoc.protein_id).first()
        if protein:
            associations_with_proteins.append(
                AssociationWithProtein(
                    id=assoc.id,
                    disease_id=assoc.disease_id,
                    protein_id=assoc.protein_id,
                    association_strength=assoc.association_strength,
                    evidence_text=assoc.evidence_text,
                    citations=json.loads(assoc.citations) if assoc.citations else None,
                    sources=json.loads(assoc.sources) if assoc.sources else None,
                    maturity=assoc.maturity,
                    last_updated=assoc.last_updated,
                    protein=Protein(
                        id=protein.id,
                        uniprot_id=protein.uniprot_id,
                        symbol=protein.symbol,
                        name=protein.name,
                        family=protein.family,
                        pathways=json.loads(protein.pathways) if protein.pathways else None,
                        sources=json.loads(protein.sources) if protein.sources else None
                    )
                )
            )
    
    return DiseaseWithAssociations(
        disease=Disease(
            id=disease.id,
            name=disease.name,
            category=disease.category,
            burden_score=disease.burden_score,
            sources=json.loads(disease.sources) if disease.sources else None
        ),
        associations=associations_with_proteins
    )


@app.get("/api/protein/{protein_id}", response_model=ProteinWithContext)
async def get_protein(protein_id: str, db: Session = Depends(get_db)):
    """Get protein details with diseases, therapies, and trials"""
    
    protein = db.query(ProteinDB).filter(ProteinDB.id == protein_id).first()
    if not protein:
        raise HTTPException(status_code=404, detail="Protein not found")
    
    # Get associations
    associations = db.query(AssociationDB).filter(
        AssociationDB.protein_id == protein_id
    ).all()
    
    # Enrich with disease data
    diseases_with_assoc = []
    for assoc in associations:
        disease = db.query(DiseaseDB).filter(DiseaseDB.id == assoc.disease_id).first()
        if disease:
            diseases_with_assoc.append(
                AssociationWithDisease(
                    id=assoc.id,
                    disease_id=assoc.disease_id,
                    protein_id=assoc.protein_id,
                    association_strength=assoc.association_strength,
                    evidence_text=assoc.evidence_text,
                    citations=json.loads(assoc.citations) if assoc.citations else None,
                    sources=json.loads(assoc.sources) if assoc.sources else None,
                    maturity=assoc.maturity,
                    last_updated=assoc.last_updated,
                    disease=Disease(
                        id=disease.id,
                        name=disease.name,
                        category=disease.category,
                        burden_score=disease.burden_score,
                        sources=json.loads(disease.sources) if disease.sources else None
                    )
                )
            )
    
    # Get therapies
    therapies_db = db.query(TherapyDB).filter(TherapyDB.target_protein_id == protein_id).all()
    therapies = [
        Therapy(
            id=t.id,
            name=t.name,
            target_protein_id=t.target_protein_id,
            status=t.status,
            drugbank_id=t.drugbank_id,
            chembl_id=t.chembl_id,
            indications=json.loads(t.indications) if t.indications else None,
            sources=json.loads(t.sources) if t.sources else None
        )
        for t in therapies_db
    ]
    
    # Get trials
    trials_db = db.query(ClinicalTrialDB).filter(ClinicalTrialDB.target_protein_id == protein_id).all()
    trials = [
        ClinicalTrial(
            id=t.id,
            nct_id=t.nct_id,
            phase=t.phase,
            status=t.status,
            condition=t.condition,
            target_protein_id=t.target_protein_id,
            start_date=t.start_date,
            link=t.link,
            sources=json.loads(t.sources) if t.sources else None
        )
        for t in trials_db
    ]
    
    return ProteinWithContext(
        protein=Protein(
            id=protein.id,
            uniprot_id=protein.uniprot_id,
            symbol=protein.symbol,
            name=protein.name,
            family=protein.family,
            pathways=json.loads(protein.pathways) if protein.pathways else None,
            sources=json.loads(protein.sources) if protein.sources else None
        ),
        diseases=diseases_with_assoc,
        therapies=therapies,
        trials=trials
    )


@app.get("/api/opportunities", response_model=List[Opportunity])
async def get_opportunities(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get ranked therapeutic opportunities"""
    
    opportunities = calculate_opportunities(db, limit)
    return opportunities


@app.get("/api/search", response_model=List[SearchResult])
async def search(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Search diseases and proteins"""
    
    query_lower = q.lower()
    results = []
    
    # Search diseases
    diseases = db.query(DiseaseDB).all()
    for disease in diseases:
        if query_lower in disease.name.lower() or (disease.category and query_lower in disease.category.lower()):
            score = 1.0 if disease.name.lower().startswith(query_lower) else 0.5
            results.append(SearchResult(
                id=disease.id,
                type="disease",
                score=score,
                snippet=f"{disease.name} ({disease.category})"
            ))
    
    # Search proteins
    proteins = db.query(ProteinDB).all()
    for protein in proteins:
        match = False
        snippet = protein.symbol or protein.name or protein.id
        
        if protein.symbol and query_lower in protein.symbol.lower():
            match = True
        elif protein.name and query_lower in protein.name.lower():
            match = True
        elif protein.uniprot_id and query_lower in protein.uniprot_id.lower():
            match = True
        
        if match:
            score = 1.0 if (protein.symbol and protein.symbol.lower().startswith(query_lower)) else 0.5
            results.append(SearchResult(
                id=protein.id,
                type="protein",
                score=score,
                snippet=snippet
            ))
    
    # Sort by score and limit
    results.sort(key=lambda x: x.score, reverse=True)
    return results[:limit]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)

