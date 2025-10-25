from sqlalchemy.orm import Session
from typing import Dict, List, Tuple
from collections import defaultdict

from database import ProteinDB, AssociationDB


def identify_protein_hubs(db: Session, min_diseases: int = 5) -> List[Tuple[str, int]]:
    """
    Identify protein hubs - proteins involved in multiple diseases
    Returns list of (protein_id, disease_count) tuples
    """
    
    # Count diseases per protein
    protein_disease_counts = defaultdict(int)
    
    associations = db.query(AssociationDB).all()
    for assoc in associations:
        protein_disease_counts[assoc.protein_id] += 1
    
    # Filter to hubs
    hubs = [(pid, count) for pid, count in protein_disease_counts.items() 
            if count >= min_diseases]
    
    # Sort by count descending
    hubs.sort(key=lambda x: x[1], reverse=True)
    
    return hubs


def get_hub_details(db: Session, protein_id: str) -> Dict:
    """Get detailed information about a protein hub"""
    
    protein = db.query(ProteinDB).filter(ProteinDB.id == protein_id).first()
    if not protein:
        return {}
    
    # Get all disease associations
    associations = db.query(AssociationDB).filter(
        AssociationDB.protein_id == protein_id
    ).all()
    
    disease_ids = [assoc.disease_id for assoc in associations]
    
    # Calculate average association strength
    strengths = [assoc.association_strength for assoc in associations 
                 if assoc.association_strength is not None]
    avg_strength = sum(strengths) / len(strengths) if strengths else 0.5
    
    return {
        "protein_id": protein_id,
        "protein_name": protein.symbol or protein.name,
        "disease_count": len(disease_ids),
        "disease_ids": disease_ids,
        "avg_association_strength": avg_strength,
        "family": protein.family
    }


def find_disease_clusters(db: Session, min_shared_proteins: int = 3) -> List[Dict]:
    """
    Find disease clusters that share multiple proteins
    These indicate related disease mechanisms
    """
    
    # Build disease -> proteins mapping
    disease_proteins = defaultdict(set)
    
    associations = db.query(AssociationDB).all()
    for assoc in associations:
        disease_proteins[assoc.disease_id].add(assoc.protein_id)
    
    # Find disease pairs with shared proteins
    clusters = []
    disease_ids = list(disease_proteins.keys())
    
    for i, disease1_id in enumerate(disease_ids):
        for disease2_id in disease_ids[i+1:]:
            shared = disease_proteins[disease1_id] & disease_proteins[disease2_id]
            
            if len(shared) >= min_shared_proteins:
                clusters.append({
                    "disease1_id": disease1_id,
                    "disease2_id": disease2_id,
                    "shared_proteins": list(shared),
                    "shared_count": len(shared)
                })
    
    # Sort by shared count
    clusters.sort(key=lambda x: x["shared_count"], reverse=True)
    
    return clusters

