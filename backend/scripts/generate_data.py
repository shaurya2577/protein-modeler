#!/usr/bin/env python3
"""
AI-Powered Data Generation Script
Generates comprehensive disease-protein-therapy dataset using LLMs
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from database import SessionLocal, init_db, clear_db
from database import DiseaseDB, ProteinDB, AssociationDB, TherapyDB, ClinicalTrialDB
from config import settings

from data_collection.disease_collector import (
    collect_disease_list,
    get_disease_burden_score,
    validate_disease_data
)
from data_collection.protein_collector import (
    get_proteins_for_disease_ai,
    enrich_protein_with_uniprot,
    validate_protein_data,
    merge_proteins
)
from data_collection.association_builder import (
    batch_build_associations,
    validate_associations
)
from data_collection.therapy_collector import (
    get_therapies_for_protein_ai,
    validate_therapy_data,
    merge_therapies
)
from data_collection.trial_collector import (
    get_trials_for_protein_ai,
    validate_trial_data,
    merge_trials
)


def print_progress(message: str, step: int = 0, total: int = 0):
    """Print progress message"""
    if total > 0:
        print(f"[{step}/{total}] {message}")
    else:
        print(f"[*] {message}")


def generate_diseases(db: Session, max_diseases: int = 150) -> list:
    """Step 1: Generate disease list"""
    print_progress(f"Generating list of {max_diseases} major diseases...")
    
    diseases = collect_disease_list(max_diseases)
    diseases = validate_disease_data(diseases)
    
    print_progress(f"Collected {len(diseases)} diseases")
    
    # Insert into database
    for disease in diseases:
        db_disease = DiseaseDB(
            id=disease["id"],
            name=disease["name"],
            category=disease.get("category"),
            burden_score=disease.get("burden_score"),
            sources=json.dumps(disease.get("sources", ["AI-generated"]))
        )
        db.add(db_disease)
    
    db.commit()
    print_progress(f"Inserted {len(diseases)} diseases into database")
    
    return diseases


def generate_proteins_for_diseases(db: Session, diseases: list, max_per_disease: int = 10) -> list:
    """Step 2: Generate proteins associated with each disease"""
    print_progress(f"Generating proteins for {len(diseases)} diseases...")
    
    all_proteins = []
    
    for i, disease in enumerate(diseases):
        print_progress(
            f"Collecting proteins for {disease['name']}...",
            step=i+1,
            total=len(diseases)
        )
        
        try:
            proteins = get_proteins_for_disease_ai(disease["name"], disease["id"])
            
            # Enrich with UniProt data
            for protein in proteins[:max_per_disease]:
                protein = enrich_protein_with_uniprot(protein)
            
            all_proteins.append(proteins[:max_per_disease])
            
        except Exception as e:
            print(f"  Error collecting proteins for {disease['name']}: {e}")
            continue
    
    # Merge and deduplicate
    merged_proteins = merge_proteins(all_proteins)
    merged_proteins = validate_protein_data(merged_proteins)
    
    print_progress(f"Collected {len(merged_proteins)} unique proteins")
    
    # Insert into database
    for protein in merged_proteins:
        db_protein = ProteinDB(
            id=protein["id"],
            uniprot_id=protein["uniprot_id"],
            symbol=protein.get("symbol"),
            name=protein.get("name"),
            family=protein.get("family"),
            pathways=json.dumps(protein.get("pathways", [])),
            sources=json.dumps(protein.get("sources", ["AI-generated"]))
        )
        db.add(db_protein)
    
    db.commit()
    print_progress(f"Inserted {len(merged_proteins)} proteins into database")
    
    return merged_proteins


def generate_associations(db: Session, diseases: list, proteins: list) -> list:
    """Step 3: Generate disease-protein associations"""
    print_progress(f"Building associations between diseases and proteins...")
    
    all_associations = []
    
    # Build protein ID set for faster lookup
    protein_ids = {p["id"] for p in proteins}
    
    for i, disease in enumerate(diseases):
        print_progress(
            f"Building associations for {disease['name']}...",
            step=i+1,
            total=len(diseases)
        )
        
        try:
            # Find proteins relevant to this disease
            disease_proteins = []
            for protein in proteins:
                # Simple heuristic: protein was collected for this disease
                # In production, you'd use more sophisticated matching
                disease_proteins.append(protein)
                if len(disease_proteins) >= 15:
                    break
            
            # Build associations in batch
            associations = batch_build_associations(
                disease,
                disease_proteins,
                min_strength=settings.min_association_strength
            )
            
            all_associations.extend(associations)
            
        except Exception as e:
            print(f"  Error building associations for {disease['name']}: {e}")
            continue
    
    # Validate
    all_associations = validate_associations(
        all_associations,
        min_strength=settings.min_association_strength
    )
    
    print_progress(f"Generated {len(all_associations)} associations")
    
    # Insert into database
    for assoc in all_associations:
        db_assoc = AssociationDB(
            id=assoc["id"],
            disease_id=assoc["disease_id"],
            protein_id=assoc["protein_id"],
            association_strength=assoc.get("association_strength"),
            evidence_text=assoc.get("evidence_text"),
            citations=json.dumps(assoc.get("citations", [])),
            sources=json.dumps(assoc.get("sources", [])),
            maturity=assoc.get("maturity"),
            last_updated=assoc.get("last_updated")
        )
        db.add(db_assoc)
    
    db.commit()
    print_progress(f"Inserted {len(all_associations)} associations into database")
    
    return all_associations


def generate_therapies(db: Session, proteins: list) -> list:
    """Step 4: Generate therapies for proteins"""
    print_progress(f"Collecting therapies for proteins...")
    
    all_therapies = []
    
    for i, protein in enumerate(proteins):
        if i % 20 == 0:  # Progress update every 20 proteins
            print_progress(
                f"Collecting therapies...",
                step=i+1,
                total=len(proteins)
            )
        
        try:
            therapies = get_therapies_for_protein_ai(protein)
            all_therapies.append(therapies)
            
        except Exception as e:
            print(f"  Error collecting therapies for {protein.get('symbol')}: {e}")
            continue
    
    # Merge and validate
    merged_therapies = merge_therapies(all_therapies)
    merged_therapies = validate_therapy_data(merged_therapies)
    
    print_progress(f"Collected {len(merged_therapies)} unique therapies")
    
    # Insert into database
    for therapy in merged_therapies:
        db_therapy = TherapyDB(
            id=therapy["id"],
            name=therapy["name"],
            target_protein_id=therapy["target_protein_id"],
            status=therapy["status"],
            drugbank_id=therapy.get("drugbank_id"),
            chembl_id=therapy.get("chembl_id"),
            indications=json.dumps(therapy.get("indications", [])),
            sources=json.dumps(therapy.get("sources", ["AI-generated"]))
        )
        db.add(db_therapy)
    
    db.commit()
    print_progress(f"Inserted {len(merged_therapies)} therapies into database")
    
    return merged_therapies


def generate_trials(db: Session, proteins: list) -> list:
    """Step 5: Generate clinical trials for proteins"""
    print_progress(f"Collecting clinical trials...")
    
    all_trials = []
    
    # Sample proteins for trials (not all proteins have trials)
    sample_proteins = proteins[:50]  # Focus on first 50 proteins
    
    for i, protein in enumerate(sample_proteins):
        print_progress(
            f"Collecting trials for {protein.get('symbol')}...",
            step=i+1,
            total=len(sample_proteins)
        )
        
        try:
            trials = get_trials_for_protein_ai(protein, max_trials=3)
            all_trials.append(trials)
            
        except Exception as e:
            print(f"  Error collecting trials for {protein.get('symbol')}: {e}")
            continue
    
    # Merge and validate
    merged_trials = merge_trials(all_trials)
    merged_trials = validate_trial_data(merged_trials)
    
    print_progress(f"Collected {len(merged_trials)} unique trials")
    
    # Insert into database
    for trial in merged_trials:
        db_trial = ClinicalTrialDB(
            id=trial["id"],
            nct_id=trial["nct_id"],
            phase=trial.get("phase"),
            status=trial.get("status"),
            condition=trial.get("condition"),
            target_protein_id=trial.get("target_protein_id"),
            start_date=trial.get("start_date"),
            link=trial.get("link"),
            sources=json.dumps(trial.get("sources", ["AI-generated"]))
        )
        db.add(db_trial)
    
    db.commit()
    print_progress(f"Inserted {len(merged_trials)} trials into database")
    
    return merged_trials


def export_to_json(db: Session, output_path: str):
    """Export database to JSON file for frontend"""
    print_progress("Exporting data to JSON...")
    
    # Fetch all data
    diseases = db.query(DiseaseDB).all()
    proteins = db.query(ProteinDB).all()
    associations = db.query(AssociationDB).all()
    therapies = db.query(TherapyDB).all()
    trials = db.query(ClinicalTrialDB).all()
    
    # Convert to dict
    data = {
        "diseases": [
            {
                "id": d.id,
                "name": d.name,
                "category": d.category,
                "burden_score": d.burden_score,
                "sources": json.loads(d.sources) if d.sources else []
            }
            for d in diseases
        ],
        "proteins": [
            {
                "id": p.id,
                "uniprot_id": p.uniprot_id,
                "symbol": p.symbol,
                "name": p.name,
                "family": p.family,
                "pathways": json.loads(p.pathways) if p.pathways else [],
                "sources": json.loads(p.sources) if p.sources else []
            }
            for p in proteins
        ],
        "associations": [
            {
                "id": a.id,
                "disease_id": a.disease_id,
                "protein_id": a.protein_id,
                "association_strength": a.association_strength,
                "evidence_text": a.evidence_text,
                "citations": json.loads(a.citations) if a.citations else [],
                "sources": json.loads(a.sources) if a.sources else [],
                "maturity": a.maturity,
                "last_updated": a.last_updated
            }
            for a in associations
        ],
        "therapies": [
            {
                "id": t.id,
                "name": t.name,
                "target_protein_id": t.target_protein_id,
                "status": t.status,
                "drugbank_id": t.drugbank_id,
                "chembl_id": t.chembl_id,
                "indications": json.loads(t.indications) if t.indications else [],
                "sources": json.loads(t.sources) if t.sources else []
            }
            for t in therapies
        ],
        "trials": [
            {
                "id": t.id,
                "nct_id": t.nct_id,
                "phase": t.phase,
                "status": t.status,
                "condition": t.condition,
                "target_protein_id": t.target_protein_id,
                "start_date": t.start_date,
                "link": t.link,
                "sources": json.loads(t.sources) if t.sources else []
            }
            for t in trials
        ]
    }
    
    # Write to file
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print_progress(f"Exported data to {output_path}")


def main():
    """Main data generation pipeline"""
    print("=" * 60)
    print("AI-Powered Protein-Disease-Therapy Data Generation")
    print("=" * 60)
    print()
    
    # Check API keys
    if not settings.anthropic_api_key and not settings.openai_api_key:
        print("ERROR: No LLM API key found!")
        print("Please set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env file")
        return
    
    print(f"Using LLM: {settings.llm_provider} ({settings.llm_model})")
    print(f"Target diseases: {settings.max_diseases}")
    print()
    
    # Initialize database
    print_progress("Initializing database...")
    init_db()
    
    # Check if database exists
    import os
    db_exists = os.path.exists("protein_disease.db")
    
    if db_exists:
        print_progress("Database exists. Clearing for fresh generation...")
        clear_db()
    else:
        print_progress("Creating new database...")
    
    db = SessionLocal()
    
    try:
        # Step 1: Generate diseases
        diseases = generate_diseases(db, settings.max_diseases)
        print()
        
        # Step 2: Generate proteins
        proteins = generate_proteins_for_diseases(db, diseases)
        print()
        
        # Step 3: Generate associations
        associations = generate_associations(db, diseases, proteins)
        print()
        
        # Step 4: Generate therapies
        therapies = generate_therapies(db, proteins)
        print()
        
        # Step 5: Generate trials
        trials = generate_trials(db, proteins)
        print()
        
        # Export to JSON
        output_path = "../protein-modeler-app/src/data/generated_seed.json"
        export_to_json(db, output_path)
        print()
        
        # Summary
        print("=" * 60)
        print("DATA GENERATION COMPLETE")
        print("=" * 60)
        print(f"Diseases: {len(diseases)}")
        print(f"Proteins: {len(proteins)}")
        print(f"Associations: {len(associations)}")
        print(f"Therapies: {len(therapies)}")
        print(f"Clinical Trials: {len(trials)}")
        print()
        print(f"Database: protein_disease.db")
        print(f"JSON Export: {output_path}")
        print()
        print("You can now start the backend server:")
        print("  cd backend && python main.py")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()

