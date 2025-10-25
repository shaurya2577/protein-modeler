from typing import List, Dict, Optional
from datetime import datetime
from data_collection.ai_extractor import get_extractor


def build_disease_protein_association(
    disease: Dict,
    protein: Dict
) -> Optional[Dict]:
    """
    Use AI to analyze and score the association between a disease and protein
    """
    
    extractor = get_extractor()
    
    disease_name = disease.get("name")
    protein_name = protein.get("symbol") or protein.get("name")
    
    prompt = f"""Analyze the relationship between the disease "{disease_name}" and the protein "{protein_name}".

Provide:
1. association_strength: Score from 0.0 to 1.0 indicating how strongly this protein is linked to this disease
   - 0.9-1.0: Direct causal relationship, validated therapeutic target
   - 0.7-0.8: Strong association with good evidence
   - 0.5-0.6: Moderate association, some evidence
   - 0.3-0.4: Weak association or indirect role
   - Below 0.3: Not significantly associated

2. evidence_text: 1-2 sentences explaining the relationship

3. maturity: Therapeutic development status for this specific protein-disease pair
   - "approved": FDA-approved drugs exist targeting this protein for this disease
   - "trial": Drugs in clinical trials
   - "none": No drugs currently in development

4. confidence: How confident are you in this assessment (0.0-1.0)

If there is NO significant relationship, return null or set association_strength to 0.

Return as JSON with fields: association_strength, evidence_text, maturity, confidence."""
    
    system_prompt = """You are a biomedical researcher expert in disease mechanisms and drug development.
Base your assessments on established scientific knowledge."""
    
    result = extractor.extract_json(prompt, system_prompt)
    
    if not result or result.get("association_strength", 0) < 0.3:
        return None
    
    # Build association object
    association = {
        "id": f"{disease['id']}-{protein['id']}",
        "disease_id": disease["id"],
        "protein_id": protein["id"],
        "association_strength": result.get("association_strength", 0.5),
        "evidence_text": result.get("evidence_text", ""),
        "maturity": result.get("maturity", "none"),
        "citations": [],
        "sources": ["AI-generated"],
        "last_updated": datetime.now().isoformat()
    }
    
    return association


def batch_build_associations(
    disease: Dict,
    proteins: List[Dict],
    min_strength: float = 0.3
) -> List[Dict]:
    """
    Build associations for a disease with multiple proteins
    Uses batch prompting for efficiency
    """
    
    extractor = get_extractor()
    
    disease_name = disease.get("name")
    protein_names = [p.get("symbol") or p.get("name") for p in proteins]
    
    prompt = f"""For the disease "{disease_name}", evaluate the association with each of these proteins:
{chr(10).join(f"{i+1}. {name}" for i, name in enumerate(protein_names))}

For EACH protein, provide:
- protein_index: The number (1-{len(proteins)})
- association_strength: 0.0-1.0 score
- evidence_text: Brief explanation
- maturity: "approved", "trial", or "none"

Only include proteins with association_strength >= {min_strength}.

Return as JSON array of association objects."""
    
    system_prompt = """You are a biomedical expert analyzing disease-protein relationships.
Be conservative - only report strong, evidence-based associations."""
    
    result = extractor.extract_json(prompt, system_prompt)
    
    associations = []
    
    if isinstance(result, dict) and "associations" in result:
        result_list = result["associations"]
    elif isinstance(result, list):
        result_list = result
    else:
        return []
    
    for assoc_data in result_list:
        idx = assoc_data.get("protein_index", 0) - 1
        if 0 <= idx < len(proteins):
            protein = proteins[idx]
            
            association = {
                "id": f"{disease['id']}-{protein['id']}",
                "disease_id": disease["id"],
                "protein_id": protein["id"],
                "association_strength": assoc_data.get("association_strength", 0.5),
                "evidence_text": assoc_data.get("evidence_text", ""),
                "maturity": assoc_data.get("maturity", "none"),
                "citations": [],
                "sources": ["AI-generated"],
                "last_updated": datetime.now().isoformat()
            }
            
            associations.append(association)
    
    return associations


def enhance_association_with_literature(association: Dict) -> Dict:
    """
    Use AI to find supporting literature and citations
    """
    
    extractor = get_extractor()
    
    prompt = f"""For the relationship between disease and protein described as:
"{association.get('evidence_text')}"

Suggest 2-3 relevant PubMed search queries that would find supporting literature.
Also suggest likely PubMed IDs (PMIDs) if you know of specific landmark papers.

Return as JSON with: search_queries (array), suggested_pmids (array)."""
    
    system_prompt = "You are a scientific literature expert."
    
    result = extractor.extract_json(prompt, system_prompt)
    
    if result.get("suggested_pmids"):
        # Format as PubMed URLs
        association["citations"] = [
            f"https://pubmed.ncbi.nlm.nih.gov/{pmid}"
            for pmid in result["suggested_pmids"]
        ]
    
    return association


def validate_associations(associations: List[Dict], min_strength: float = 0.3) -> List[Dict]:
    """Validate and filter associations"""
    
    validated = []
    
    for assoc in associations:
        # Required fields
        if not all(k in assoc for k in ["id", "disease_id", "protein_id"]):
            continue
        
        # Minimum strength threshold
        strength = assoc.get("association_strength", 0)
        if strength < min_strength:
            continue
        
        # Normalize strength
        assoc["association_strength"] = max(0.0, min(1.0, strength))
        
        # Validate maturity
        if assoc.get("maturity") not in ["approved", "trial", "none"]:
            assoc["maturity"] = "none"
        
        validated.append(assoc)
    
    return validated

