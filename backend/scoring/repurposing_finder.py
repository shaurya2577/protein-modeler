from sqlalchemy.orm import Session
from typing import List, Dict
import json

from database import TherapyDB, AssociationDB, DiseaseDB, ProteinDB


def find_repurposing_opportunities(db: Session, min_strength: float = 0.4) -> List[Dict]:
    """
    Find drug repurposing opportunities
    Identifies approved drugs that could be used for additional diseases
    """
    
    opportunities = []
    
    # Get all approved therapies
    therapies = db.query(TherapyDB).filter(TherapyDB.status == "approved").all()
    
    for therapy in therapies:
        # Get the target protein
        protein = db.query(ProteinDB).filter(
            ProteinDB.id == therapy.target_protein_id
        ).first()
        
        if not protein:
            continue
        
        # Get all diseases associated with this protein
        associations = db.query(AssociationDB).filter(
            AssociationDB.protein_id == therapy.target_protein_id,
            AssociationDB.association_strength >= min_strength
        ).all()
        
        # Current indications
        current_indications = set(therapy.indications) if therapy.indications else set()
        
        # Find new potential indications
        for assoc in associations:
            disease = db.query(DiseaseDB).filter(DiseaseDB.id == assoc.disease_id).first()
            
            if disease and disease.name not in current_indications:
                # This is a potential repurposing opportunity
                opportunities.append({
                    "therapy_id": therapy.id,
                    "therapy_name": therapy.name,
                    "target_protein": protein.symbol or protein.name,
                    "current_indications": list(current_indications),
                    "new_disease": disease.name,
                    "new_disease_id": disease.id,
                    "association_strength": assoc.association_strength,
                    "evidence": assoc.evidence_text,
                    "repurposing_score": calculate_repurposing_score(
                        assoc.association_strength,
                        disease.burden_score,
                        assoc.maturity
                    )
                })
    
    # Sort by repurposing score
    opportunities.sort(key=lambda x: x["repurposing_score"], reverse=True)
    
    return opportunities


def calculate_repurposing_score(
    association_strength: float | None,
    disease_burden: float | None,
    maturity: str | None
) -> float:
    """
    Calculate repurposing potential score
    Higher for strong associations with high-burden diseases lacking therapy
    """
    
    strength = association_strength or 0.5
    burden = disease_burden or 0.5
    
    # Bonus if no approved therapy exists
    maturity_bonus = 1.5 if maturity in ["none", None] else 1.0
    
    # Risk reduction factor (repurposing has lower risk than new drug)
    risk_factor = 1.2
    
    return strength * burden * maturity_bonus * risk_factor


def find_multi_indication_proteins(db: Session, min_indications: int = 3) -> List[Dict]:
    """
    Find proteins targeted by drugs with multiple indications
    These are validated therapeutic targets
    """
    
    results = []
    
    # Get all approved therapies
    therapies = db.query(TherapyDB).filter(TherapyDB.status == "approved").all()
    
    # Group by protein
    protein_therapies = {}
    for therapy in therapies:
        if therapy.target_protein_id not in protein_therapies:
            protein_therapies[therapy.target_protein_id] = []
        protein_therapies[therapy.target_protein_id].append(therapy)
    
    for protein_id, therapy_list in protein_therapies.items():
        # Collect all unique indications
        all_indications = set()
        for therapy in therapy_list:
            if therapy.indications:
                all_indications.update(therapy.indications)
        
        if len(all_indications) >= min_indications:
            protein = db.query(ProteinDB).filter(ProteinDB.id == protein_id).first()
            
            if protein:
                results.append({
                    "protein_id": protein_id,
                    "protein_name": protein.symbol or protein.name,
                    "therapy_count": len(therapy_list),
                    "indication_count": len(all_indications),
                    "indications": list(all_indications),
                    "therapies": [t.name for t in therapy_list]
                })
    
    # Sort by indication count
    results.sort(key=lambda x: x["indication_count"], reverse=True)
    
    return results

