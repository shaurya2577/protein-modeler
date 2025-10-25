from typing import List, Dict
import requests
from data_collection.ai_extractor import get_extractor


def collect_disease_list(max_diseases: int = 200) -> List[Dict]:
    """
    Use AI to compile a comprehensive list of major diseases
    across different categories
    """
    
    extractor = get_extractor()
    
    prompt = f"""Generate a list of {max_diseases} major diseases that have significant health burden globally.
    
Include diseases from these categories:
- Cancers (lung, breast, colorectal, prostate, leukemia, etc.)
- Cardiovascular diseases (heart disease, stroke, hypertension, etc.)
- Metabolic diseases (diabetes, obesity, metabolic syndrome, etc.)
- Neurodegenerative diseases (Alzheimer's, Parkinson's, ALS, Huntington's, etc.)
- Autoimmune diseases (rheumatoid arthritis, lupus, MS, Crohn's, psoriasis, etc.)
- Infectious diseases (HIV, hepatitis, tuberculosis, malaria, etc.)
- Respiratory diseases (COPD, asthma, pulmonary fibrosis, etc.)
- Kidney diseases (chronic kidney disease, nephrotic syndrome, etc.)
- Liver diseases (cirrhosis, hepatitis, fatty liver disease, etc.)
- Mental health disorders (depression, schizophrenia, bipolar disorder, etc.)
- Rare diseases with known genetic causes

For each disease, provide:
- id: A short unique identifier (e.g., "ALZ", "T2D", "RA")
- name: Full disease name
- category: One of (Cancer, Cardiovascular, Metabolic, Neurodegenerative, Autoimmune, Infectious, Respiratory, Kidney, Liver, Mental Health, Rare Disease, Other)
- burden_score: Estimated disease burden (0.0 to 1.0, where 1.0 is highest burden based on mortality, prevalence, and impact on quality of life)

Return as a JSON array of disease objects."""
    
    system_prompt = """You are a medical data expert specializing in disease classification and epidemiology.
Your goal is to create a comprehensive, accurate list of major diseases with appropriate burden scores."""
    
    result = extractor.extract_json(prompt, system_prompt)
    
    if isinstance(result, dict) and "diseases" in result:
        return result["diseases"]
    elif isinstance(result, list):
        return result
    else:
        return []


def enrich_disease_data(disease: Dict) -> Dict:
    """
    Use AI to enrich disease data with additional information
    """
    
    extractor = get_extractor()
    
    prompt = f"""For the disease "{disease['name']}" (category: {disease.get('category', 'Unknown')}):

Provide additional information:
- A brief description (1-2 sentences)
- Estimated global prevalence (percentage or number of cases)
- Key risk factors (list of 3-5)
- Primary affected organs/systems
- Typical age of onset
- Whether it's primarily genetic, environmental, or multifactorial

Return as JSON with these fields: description, prevalence, risk_factors (array), affected_systems (array), age_of_onset, etiology."""
    
    system_prompt = "You are a medical expert providing accurate disease information."
    
    enriched = extractor.extract_json(prompt, system_prompt)
    
    # Merge with original disease data
    return {**disease, **enriched}


def get_disease_burden_score(disease_name: str) -> float:
    """
    Use AI to estimate disease burden score based on multiple factors
    """
    
    extractor = get_extractor()
    
    prompt = f"""Estimate the overall disease burden score for "{disease_name}" on a scale of 0.0 to 1.0.

Consider:
- Mortality rate (how deadly is it?)
- Prevalence (how common is it?)
- Morbidity (impact on quality of life)
- Economic burden
- Years of life lost
- Disability-adjusted life years (DALYs)

High burden (0.8-1.0): Diseases like cardiovascular disease, Alzheimer's, major cancers
Medium burden (0.5-0.7): Diseases like type 2 diabetes, COPD, rheumatoid arthritis
Lower burden (0.3-0.4): Less common or less severe diseases

Respond with just a number between 0.0 and 1.0."""
    
    system_prompt = "You are an epidemiologist expert in disease burden assessment."
    
    try:
        response = extractor.extract_structured_data(prompt, system_prompt)
        # Extract number from response
        score = float(response.strip())
        return max(0.0, min(1.0, score))
    except:
        return 0.5  # Default fallback


def validate_disease_data(diseases: List[Dict]) -> List[Dict]:
    """Validate and clean disease data"""
    
    validated = []
    seen_ids = set()
    
    for disease in diseases:
        # Required fields
        if not disease.get("id") or not disease.get("name"):
            continue
        
        # Unique IDs
        if disease["id"] in seen_ids:
            disease["id"] = f"{disease['id']}_{len(seen_ids)}"
        
        seen_ids.add(disease["id"])
        
        # Normalize burden score
        if "burden_score" not in disease or disease["burden_score"] is None:
            disease["burden_score"] = 0.5
        else:
            disease["burden_score"] = max(0.0, min(1.0, float(disease["burden_score"])))
        
        # Default category
        if not disease.get("category"):
            disease["category"] = "Other"
        
        validated.append(disease)
    
    return validated

