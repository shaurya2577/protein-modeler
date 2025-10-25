from typing import List, Dict, Optional
import requests
from data_collection.ai_extractor import get_extractor


def get_proteins_for_disease_ai(disease_name: str, disease_id: str) -> List[Dict]:
    """
    Use AI to identify key proteins associated with a disease
    """
    
    extractor = get_extractor()
    
    prompt = f"""For the disease "{disease_name}", identify the top 5-10 most important proteins that are:
1. Directly involved in disease pathogenesis
2. Validated or promising therapeutic targets
3. Biomarkers for the disease

For each protein, provide:
- symbol: Gene symbol (e.g., "TNF", "APP", "BRCA1")
- name: Full protein name
- uniprot_id: UniProt accession ID if known (e.g., "P01375")
- family: Protein family (e.g., "Cytokine", "Enzyme", "Receptor")
- pathways: Key biological pathways (array of strings)
- role: Brief description of role in this disease

Return as JSON array of protein objects. Only include well-established proteins with strong evidence."""
    
    system_prompt = """You are a molecular biology expert specializing in disease-protein relationships.
Provide accurate protein information based on scientific literature and databases."""
    
    result = extractor.extract_json(prompt, system_prompt)
    
    proteins = []
    if isinstance(result, dict) and "proteins" in result:
        proteins = result["proteins"]
    elif isinstance(result, list):
        proteins = result
    
    # Generate IDs if missing
    for protein in proteins:
        if "id" not in protein and "symbol" in protein:
            protein["id"] = protein["symbol"]
        elif "id" not in protein:
            protein["id"] = protein.get("uniprot_id", f"PROT_{len(proteins)}")
    
    return proteins


def fetch_uniprot_data(uniprot_id: str) -> Optional[Dict]:
    """
    Fetch protein data from UniProt REST API
    """
    
    try:
        url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant fields
            protein_data = {
                "uniprot_id": uniprot_id,
                "name": data.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value"),
                "gene_names": [],
                "organism": data.get("organism", {}).get("scientificName"),
                "function": None
            }
            
            # Gene names
            if "genes" in data:
                for gene in data["genes"]:
                    if "geneName" in gene:
                        protein_data["gene_names"].append(gene["geneName"].get("value"))
            
            # Function description
            if "comments" in data:
                for comment in data["comments"]:
                    if comment.get("commentType") == "FUNCTION":
                        protein_data["function"] = comment.get("texts", [{}])[0].get("value")
                        break
            
            return protein_data
        
    except Exception as e:
        print(f"Error fetching UniProt data for {uniprot_id}: {e}")
    
    return None


def enrich_protein_with_uniprot(protein: Dict) -> Dict:
    """Enrich protein data with UniProt information"""
    
    if protein.get("uniprot_id"):
        uniprot_data = fetch_uniprot_data(protein["uniprot_id"])
        if uniprot_data:
            # Merge data, preferring existing values
            if not protein.get("name") and uniprot_data.get("name"):
                protein["name"] = uniprot_data["name"]
            
            if not protein.get("symbol") and uniprot_data.get("gene_names"):
                protein["symbol"] = uniprot_data["gene_names"][0]
            
            if uniprot_data.get("function"):
                protein["function"] = uniprot_data["function"]
    
    return protein


def normalize_protein_symbol(symbol: str) -> str:
    """Normalize protein gene symbol"""
    return symbol.upper().strip()


def validate_protein_data(proteins: List[Dict]) -> List[Dict]:
    """Validate and deduplicate protein data"""
    
    validated = []
    seen_ids = set()
    seen_uniprot = set()
    
    for protein in proteins:
        # Must have ID and uniprot_id
        if not protein.get("id") or not protein.get("uniprot_id"):
            continue
        
        # Normalize symbol
        if protein.get("symbol"):
            protein["symbol"] = normalize_protein_symbol(protein["symbol"])
        
        # Deduplicate by uniprot_id
        if protein["uniprot_id"] in seen_uniprot:
            continue
        
        # Ensure unique ID
        if protein["id"] in seen_ids:
            protein["id"] = f"{protein['id']}_{protein['uniprot_id']}"
        
        seen_ids.add(protein["id"])
        seen_uniprot.add(protein["uniprot_id"])
        
        validated.append(protein)
    
    return validated


def merge_proteins(protein_lists: List[List[Dict]]) -> List[Dict]:
    """Merge multiple protein lists, deduplicating by uniprot_id"""
    
    protein_map = {}
    
    for protein_list in protein_lists:
        for protein in protein_list:
            uniprot_id = protein.get("uniprot_id")
            if not uniprot_id:
                continue
            
            if uniprot_id not in protein_map:
                protein_map[uniprot_id] = protein
            else:
                # Merge data, keeping most complete information
                existing = protein_map[uniprot_id]
                for key, value in protein.items():
                    if value and not existing.get(key):
                        existing[key] = value
    
    return list(protein_map.values())

