from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


# Enums
Maturity = Literal["approved", "trial", "none"]


# Request/Response Models
class DiseaseBase(BaseModel):
    id: str
    name: str
    category: Optional[str] = None
    burden_score: Optional[float] = Field(None, ge=0, le=1)
    sources: Optional[List[str]] = None


class DiseaseCreate(DiseaseBase):
    pass


class Disease(DiseaseBase):
    class Config:
        from_attributes = True


class ProteinBase(BaseModel):
    id: str
    uniprot_id: str
    symbol: Optional[str] = None
    name: Optional[str] = None
    family: Optional[str] = None
    pathways: Optional[List[str]] = None
    sources: Optional[List[str]] = None


class ProteinCreate(ProteinBase):
    pass


class Protein(ProteinBase):
    class Config:
        from_attributes = True


class AssociationBase(BaseModel):
    id: str
    disease_id: str
    protein_id: str
    association_strength: Optional[float] = Field(None, ge=0, le=1)
    evidence_text: Optional[str] = None
    citations: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    maturity: Optional[Maturity] = None
    last_updated: Optional[str] = None


class AssociationCreate(AssociationBase):
    pass


class Association(AssociationBase):
    class Config:
        from_attributes = True


class TherapyBase(BaseModel):
    id: str
    name: str
    target_protein_id: str
    status: Maturity
    drugbank_id: Optional[str] = None
    chembl_id: Optional[str] = None
    indications: Optional[List[str]] = None
    sources: Optional[List[str]] = None


class TherapyCreate(TherapyBase):
    pass


class Therapy(TherapyBase):
    class Config:
        from_attributes = True


class ClinicalTrialBase(BaseModel):
    id: str
    nct_id: str
    phase: Optional[str] = None
    status: Optional[str] = None
    condition: Optional[str] = None
    target_protein_id: Optional[str] = None
    start_date: Optional[str] = None
    link: Optional[str] = None
    sources: Optional[List[str]] = None


class ClinicalTrialCreate(ClinicalTrialBase):
    pass


class ClinicalTrial(ClinicalTrialBase):
    class Config:
        from_attributes = True


# Graph Models
class GraphNode(BaseModel):
    id: str
    type: Literal["disease", "protein"]
    label: str
    burden: Optional[float] = None
    degree: Optional[int] = None
    maturity: Optional[Maturity] = None


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    strength: Optional[float] = None


class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


# Detailed Response Models
class AssociationWithProtein(Association):
    protein: Protein


class DiseaseWithAssociations(BaseModel):
    disease: Disease
    associations: List[AssociationWithProtein]


class AssociationWithDisease(Association):
    disease: Disease


class ProteinWithContext(BaseModel):
    protein: Protein
    diseases: List[AssociationWithDisease]
    therapies: List[Therapy]
    trials: List[ClinicalTrial]


# Opportunity Model
class Opportunity(BaseModel):
    disease_id: str
    protein_id: str
    gap_score: float
    rationale: str
    disease_name: Optional[str] = None
    protein_name: Optional[str] = None


# Search Model
class SearchResult(BaseModel):
    id: str
    type: Literal["disease", "protein"]
    score: float
    snippet: Optional[str] = None


# Seed Data Export
class SeedData(BaseModel):
    diseases: List[Disease]
    proteins: List[Protein]
    associations: List[Association]
    therapies: List[Therapy]
    trials: List[ClinicalTrial]

