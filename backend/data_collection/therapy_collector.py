from typing import List, Dict, Optional
import requests
from data_collection.ai_extractor import get_extractor


def get_therapies_for_protein_ai(protein: Dict) -> List[Dict]:
    """
    Use AI to identify approved drugs and therapies targeting a protein
    """
    
    extractor = get_extractor()
    
    protein_name = protein.get("symbol") or protein.get("name")
    
    prompt = f"""List approved drugs that target the protein "{protein_name}".

For each drug, provide:
- name: Drug name (generic/INN name preferred)
- drugbank_id: DrugBank ID if known (e.g., "DB00051")
- status: "approved" (only include approved drugs)
- indications: Array of disease names this drug is approved to treat
- drug_class: Class of drug (e.g., "Monoclonal Antibody", "Small Molecule", "Kinase Inhibitor")

Only include FDA-approved or EMA-approved drugs with strong evidence.
If there are no approved drugs targeting this protein, return an empty array.

Return as JSON array of therapy objects."""
    
    system_prompt = """You are a pharmaceutical expert with knowledge of approved drugs and their targets.
Only include drugs with regulatory approval."""
    
    result = extractor.extract_json(prompt, system_prompt)
    
    therapies = []
    if isinstance(result, dict) and "therapies" in result:
        therapies = result["therapies"]
    elif isinstance(result, dict) and "drugs" in result:
        therapies = result["drugs"]
    elif isinstance(result, list):
        therapies = result
    
    # Add protein reference and generate IDs
    for therapy in therapies:
        therapy["target_protein_id"] = protein["id"]
        if "id" not in therapy:
            therapy["id"] = therapy.get("name", "").lower().replace(" ", "_")
        if "status" not in therapy:
            therapy["status"] = "approved"
    
    return therapies


def get_therapies_for_disease_protein_pair(disease: Dict, protein: Dict) -> List[Dict]:
    """
    Find therapies specifically for a disease-protein combination
    """
    
    extractor = get_extractor()
    
    disease_name = disease.get("name")
    protein_name = protein.get("symbol") or protein.get("name")
    
    prompt = f"""Are there any approved drugs that target "{protein_name}" for treating "{disease_name}"?

If yes, list each drug with:
- name: Drug name
- drugbank_id: DrugBank ID if known
- status: "approved"
- approval_year: Year of FDA/EMA approval if known

If no approved drugs exist, return an empty array.

Return as JSON array."""
    
    system_prompt = "You are a clinical pharmacology expert."
    
    result = extractor.extract_json(prompt, system_prompt)
    
    therapies = []
    if isinstance(result, dict):
        if "drugs" in result:
            therapies = result["drugs"]
        elif "therapies" in result:
            therapies = result["therapies"]
    elif isinstance(result, list):
        therapies = result
    
    for therapy in therapies:
        therapy["target_protein_id"] = protein["id"]
        therapy["indications"] = [disease_name]
        if "id" not in therapy:
            therapy["id"] = therapy.get("name", "").lower().replace(" ", "_")
    
    return therapies


def fetch_drugbank_data(drugbank_id: str) -> Optional[Dict]:
    """
    Fetch drug data from DrugBank (requires API key)
    Note: DrugBank API requires commercial license for full access
    """
    
    # DrugBank API is commercial, so we'll use AI as primary source
    # This is a placeholder for potential future integration
    return None


def enrich_therapy_data(therapy: Dict) -> Dict:
    """
    Use AI to enrich therapy data with additional information
    """
    
    extractor = get_extractor()
    
    drug_name = therapy.get("name")
    
    prompt = f"""For the drug "{drug_name}":

Provide:
- mechanism: Brief mechanism of action (1 sentence)
- drug_class: Type of drug (e.g., "Monoclonal Antibody", "Small Molecule Inhibitor")
- route: Route of administration (e.g., "IV", "Oral", "Subcutaneous")
- common_side_effects: Array of 3-5 common side effects
- approval_year: Year of first FDA approval

Return as JSON."""
    
    system_prompt = "You are a clinical pharmacology expert."
    
    enrichment = extractor.extract_json(prompt, system_prompt)
    
    return {**therapy, **enrichment}


def validate_therapy_data(therapies: List[Dict]) -> List[Dict]:
    """Validate and deduplicate therapy data"""
    
    validated = []
    seen_ids = set()
    seen_names = set()
    
    for therapy in therapies:
        # Must have name and target
        if not therapy.get("name") or not therapy.get("target_protein_id"):
            continue
        
        # Deduplicate by name (case-insensitive)
        name_lower = therapy["name"].lower()
        if name_lower in seen_names:
            continue
        
        seen_names.add(name_lower)
        
        # Ensure unique ID
        if not therapy.get("id"):
            therapy["id"] = name_lower.replace(" ", "_")
        
        if therapy["id"] in seen_ids:
            therapy["id"] = f"{therapy['id']}_{len(seen_ids)}"
        
        seen_ids.add(therapy["id"])
        
        # Ensure status
        if therapy.get("status") not in ["approved", "trial", "none"]:
            therapy["status"] = "approved"
        
        # Ensure indications is array
        if "indications" in therapy and not isinstance(therapy["indications"], list):
            therapy["indications"] = [therapy["indications"]]
        
        validated.append(therapy)
    
    return validated


def merge_therapies(therapy_lists: List[List[Dict]]) -> List[Dict]:
    """Merge multiple therapy lists, deduplicating by name"""
    
    therapy_map = {}
    
    for therapy_list in therapy_lists:
        for therapy in therapy_list:
            name = therapy.get("name", "").lower()
            if not name:
                continue
            
            if name not in therapy_map:
                therapy_map[name] = therapy
            else:
                # Merge indications
                existing = therapy_map[name]
                if "indications" in therapy:
                    if "indications" not in existing:
                        existing["indications"] = []
                    for indication in therapy["indications"]:
                        if indication not in existing["indications"]:
                            existing["indications"].append(indication)
    
    return list(therapy_map.values())

