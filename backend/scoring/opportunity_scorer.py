from sqlalchemy.orm import Session
from typing import List
import json

from database import DiseaseDB, ProteinDB, AssociationDB
from models import Opportunity


def normalize(x: float | None, min_val=0, max_val=1, fallback=0) -> float:
    """Normalize a value to 0-1 range with safe fallback"""
    if x is None or not isinstance(x, (int, float)):
        return fallback
    clamped = max(min_val, min(max_val, x))
    range_val = max_val - min_val
    if range_val == 0:
        return fallback
    return (clamped - min_val) / range_val


def calculate_gap_score(
    association_strength: float | None,
    burden: float | None,
    maturity: str | None
) -> float:
    """Calculate therapeutic gap score"""
    
    s = normalize(association_strength, 0, 1, 0.3)
    b = normalize(burden, 0, 1, 0.5)
    
    # Maturity penalty: higher score for less mature therapies
    if maturity == "none" or maturity is None:
        m = 1.0  # No therapy exists - highest opportunity
    elif maturity == "trial":
        m = 0.5  # Therapy in development - medium opportunity
    elif maturity == "approved":
        m = 0.1  # Approved therapy exists - low opportunity
    else:
        m = 0.8  # Unknown status - assume some opportunity
    
    return s * b * m


def generate_rationale(
    disease_name: str,
    protein_name: str,
    association_strength: float | None,
    burden: float | None,
    maturity: str | None,
    gap_score: float
) -> str:
    """Generate human-readable rationale for opportunity"""
    
    strength = association_strength or 0.5
    burden_val = burden or 0.5
    
    rationale = f"Therapeutic opportunity for {protein_name} in {disease_name}. "
    
    if strength > 0.7:
        rationale += f"Strong association ({strength:.0%}) between target and disease. "
    elif strength > 0.5:
        rationale += f"Moderate association ({strength:.0%}) between target and disease. "
    else:
        rationale += f"Association ({strength:.0%}) identified between target and disease. "
    
    if burden_val > 0.7:
        rationale += "High disease burden indicates significant unmet need. "
    elif burden_val > 0.5:
        rationale += "Moderate disease burden suggests therapeutic value. "
    
    if maturity == "none" or maturity is None:
        rationale += "No approved therapies currently target this protein-disease pair. "
    elif maturity == "trial":
        rationale += "Therapies are in development but not yet approved. "
    elif maturity == "approved":
        rationale += "Approved therapies exist but may have limitations. "
    
    rationale += f"Opportunity score: {gap_score:.0%}."
    
    return rationale


def calculate_opportunities(db: Session, limit: int = 20) -> List[Opportunity]:
    """Calculate and rank therapeutic opportunities"""
    
    opportunities = []
    
    # Get all associations
    associations = db.query(AssociationDB).all()
    
    for assoc in associations:
        # Focus on gaps (none or trial maturity)
        if assoc.maturity in ["none", "trial", None]:
            # Get disease and protein
            disease = db.query(DiseaseDB).filter(DiseaseDB.id == assoc.disease_id).first()
            protein = db.query(ProteinDB).filter(ProteinDB.id == assoc.protein_id).first()
            
            if disease and protein:
                gap_score = calculate_gap_score(
                    assoc.association_strength,
                    disease.burden_score,
                    assoc.maturity
                )
                
                protein_display = protein.symbol or protein.name or protein.id
                
                rationale = generate_rationale(
                    disease.name,
                    protein_display,
                    assoc.association_strength,
                    disease.burden_score,
                    assoc.maturity,
                    gap_score
                )
                
                opportunities.append(Opportunity(
                    disease_id=assoc.disease_id,
                    protein_id=assoc.protein_id,
                    gap_score=gap_score,
                    rationale=rationale,
                    disease_name=disease.name,
                    protein_name=protein_display
                ))
    
    # Sort by gap score descending
    opportunities.sort(key=lambda x: x.gap_score, reverse=True)
    
    return opportunities[:limit]

