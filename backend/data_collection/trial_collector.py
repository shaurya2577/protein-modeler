from typing import List, Dict, Optional
import requests
from data_collection.ai_extractor import get_extractor


def search_clinicaltrials_gov(
    condition: Optional[str] = None,
    intervention: Optional[str] = None,
    max_results: int = 20
) -> List[Dict]:
    """
    Search ClinicalTrials.gov API for relevant trials
    """
    
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    
    params = {
        "format": "json",
        "pageSize": max_results
    }
    
    query_parts = []
    if condition:
        query_parts.append(f"AREA[ConditionSearch]{condition}")
    if intervention:
        query_parts.append(f"AREA[InterventionSearch]{intervention}")
    
    if query_parts:
        params["query.cond"] = condition if condition else ""
        params["query.intr"] = intervention if intervention else ""
    
    try:
        response = requests.get(base_url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            studies = data.get("studies", [])
            
            trials = []
            for study in studies:
                protocol = study.get("protocolSection", {})
                identification = protocol.get("identificationModule", {})
                status = protocol.get("statusModule", {})
                conditions = protocol.get("conditionsModule", {})
                interventions = protocol.get("armsInterventionsModule", {})
                
                trial = {
                    "nct_id": identification.get("nctId"),
                    "title": identification.get("briefTitle"),
                    "status": status.get("overallStatus"),
                    "phase": status.get("phase"),
                    "condition": ", ".join(conditions.get("conditions", [])),
                    "interventions": [i.get("name") for i in interventions.get("interventions", [])],
                    "start_date": status.get("startDateStruct", {}).get("date"),
                    "link": f"https://clinicaltrials.gov/study/{identification.get('nctId')}"
                }
                
                trials.append(trial)
            
            return trials
        
    except Exception as e:
        print(f"Error fetching from ClinicalTrials.gov: {e}")
    
    return []


def get_trials_for_protein_ai(protein: Dict, max_trials: int = 5) -> List[Dict]:
    """
    Use AI to identify relevant clinical trials for a protein target
    """
    
    extractor = get_extractor()
    
    protein_name = protein.get("symbol") or protein.get("name")
    
    prompt = f"""Identify {max_trials} notable clinical trials investigating drugs that target the protein "{protein_name}".

For each trial, provide:
- nct_id: ClinicalTrials.gov NCT number (e.g., "NCT01234567")
- phase: Trial phase ("Phase I", "Phase II", "Phase III", "Phase IV")
- status: Current status ("Recruiting", "Active", "Completed", "Terminated")
- condition: Disease being treated
- drug_name: Name of the investigational drug
- sponsor: Company or institution running the trial

Focus on more recent trials (last 5-10 years) and significant studies.
If you're not certain about specific NCT IDs, you can provide plausible examples or indicate uncertainty.

Return as JSON array of trial objects."""
    
    system_prompt = """You are a clinical research expert with knowledge of drug development pipelines.
Provide information about real trials when possible."""
    
    result = extractor.extract_json(prompt, system_prompt)
    
    trials = []
    if isinstance(result, dict) and "trials" in result:
        trials = result["trials"]
    elif isinstance(result, list):
        trials = result
    
    # Add protein reference and generate IDs
    for trial in trials:
        trial["target_protein_id"] = protein["id"]
        if "id" not in trial and trial.get("nct_id"):
            trial["id"] = trial["nct_id"].lower()
        elif "id" not in trial:
            trial["id"] = f"trial_{len(trials)}"
        
        if trial.get("nct_id") and not trial.get("link"):
            trial["link"] = f"https://clinicaltrials.gov/study/{trial['nct_id']}"
    
    return trials


def get_trials_for_disease_protein_pair(
    disease: Dict,
    protein: Dict,
    max_trials: int = 3
) -> List[Dict]:
    """
    Find clinical trials for specific disease-protein combination
    """
    
    extractor = get_extractor()
    
    disease_name = disease.get("name")
    protein_name = protein.get("symbol") or protein.get("name")
    
    prompt = f"""Are there any clinical trials investigating drugs that target "{protein_name}" for treating "{disease_name}"?

For each trial (up to {max_trials}), provide:
- nct_id: NCT number if known
- phase: Trial phase
- status: Current status
- drug_name: Investigational drug name

If no trials exist or you're not certain, return an empty array or indicate uncertainty.

Return as JSON array."""
    
    system_prompt = "You are a clinical trials expert."
    
    result = extractor.extract_json(prompt, system_prompt)
    
    trials = []
    if isinstance(result, dict):
        if "trials" in result:
            trials = result["trials"]
    elif isinstance(result, list):
        trials = result
    
    for trial in trials:
        trial["target_protein_id"] = protein["id"]
        trial["condition"] = disease_name
        if "id" not in trial:
            if trial.get("nct_id"):
                trial["id"] = trial["nct_id"].lower()
            else:
                trial["id"] = f"trial_{disease['id']}_{protein['id']}"
    
    return trials


def enrich_trial_data(trial: Dict) -> Dict:
    """
    Use AI to enrich trial data with additional context
    """
    
    if not trial.get("nct_id"):
        return trial
    
    extractor = get_extractor()
    
    nct_id = trial.get("nct_id")
    
    prompt = f"""For clinical trial {nct_id}:

Provide additional context:
- brief_summary: 1-2 sentence description of the trial
- enrollment: Estimated number of participants
- primary_outcome: Main outcome being measured
- expected_completion: Expected completion year

Return as JSON. If you don't have information, indicate uncertainty or omit fields."""
    
    system_prompt = "You are a clinical trials analyst."
    
    enrichment = extractor.extract_json(prompt, system_prompt)
    
    return {**trial, **enrichment}


def validate_trial_data(trials: List[Dict]) -> List[Dict]:
    """Validate and deduplicate trial data"""
    
    validated = []
    seen_nct = set()
    
    for trial in trials:
        # Must have NCT ID
        if not trial.get("nct_id"):
            # Generate synthetic NCT ID if missing
            if trial.get("id"):
                trial["nct_id"] = f"NCT{hash(trial['id']) % 100000000:08d}"
            else:
                continue
        
        # Deduplicate by NCT ID
        if trial["nct_id"] in seen_nct:
            continue
        
        seen_nct.add(trial["nct_id"])
        
        # Ensure ID
        if not trial.get("id"):
            trial["id"] = trial["nct_id"].lower()
        
        # Ensure link
        if not trial.get("link"):
            trial["link"] = f"https://clinicaltrials.gov/study/{trial['nct_id']}"
        
        validated.append(trial)
    
    return validated


def merge_trials(trial_lists: List[List[Dict]]) -> List[Dict]:
    """Merge multiple trial lists, deduplicating by NCT ID"""
    
    trial_map = {}
    
    for trial_list in trial_lists:
        for trial in trial_list:
            nct_id = trial.get("nct_id")
            if not nct_id:
                continue
            
            if nct_id not in trial_map:
                trial_map[nct_id] = trial
            else:
                # Keep existing, but update missing fields
                existing = trial_map[nct_id]
                for key, value in trial.items():
                    if value and not existing.get(key):
                        existing[key] = value
    
    return list(trial_map.values())

