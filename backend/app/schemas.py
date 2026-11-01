from datetime import date
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

class PaginatedMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    pagination: PaginatedMeta


class LocalizedOption(BaseModel):
    code: str
    label_en: str
    label_hi: str

class SectorOption(BaseModel):
    code: str
    name_en: str
    name_hi: str

class SkillOption(BaseModel):
    code: str
    name_en: str
    name_hi: str
    sector_code: str | None = None

class DistrictOption(BaseModel):
    name_en: str
    name_hi: str

class StateDistrictOption(BaseModel):
    state_en: str
    state_hi: str
    districts: List[DistrictOption]

class WorkModeOption(BaseModel):
    code: str
    label_en: str
    label_hi: str

class OptionsResponse(BaseModel):
    education_categories: List[LocalizedOption]
    sectors: List[SectorOption]
    skills: List[SkillOption]
    states_and_districts: List[StateDistrictOption]
    work_modes: List[WorkModeOption]


class SkillSummary(BaseModel):
    id: int
    code: str
    name_en: str
    name_hi: str

class EducationSummary(BaseModel):
    id: int
    code: str
    label_en: str
    label_hi: str

class SectorSummary(BaseModel):
    id: int
    code: str
    name_en: str
    name_hi: str

class InternshipBase(BaseModel):
    id: str
    title: str
    organization_name: str
    sector: SectorSummary
    state: str
    district: str
    work_mode: str
    duration_months: int
    stipend_inr: int
    deadline: date
    is_active: bool
    allows_no_skills: bool
    is_sample: bool = True

class InternshipDetail(InternshipBase):
    model_config = ConfigDict(from_attributes=True)

    description: str
    required_skills: List[SkillSummary] = []
    accepted_educations: List[EducationSummary] = []


class CandidateProfile(BaseModel):
    # Required: Education category code (e.g., "tenth_pass", "twelfth_pass", "iti", "diploma", "bachelors", "masters")
    education: str = Field(..., max_length=50, description="Canonical education code")

    # Optional skills (bounded array)
    skills: List[str] = Field(default_factory=list, max_length=20, description="List of skill codes or free-text skills")

    # Optional sector interests (bounded array)
    sectors: List[str] = Field(default_factory=list, max_length=10, description="List of sector codes")

    # Location preferences
    state: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)

    # Work mode preference: "onsite", "hybrid", "remote", or "any"
    preferred_work_mode: str = Field("any", max_length=20)

    # Explicit constraint flags (Preferences vs Mandatory constraints)
    is_work_mode_mandatory: bool = Field(False, description="If True, only internships with exact work_mode are considered")
    is_location_mandatory: bool = Field(False, description="If True, only internships in the specified district/state are considered")
    willing_to_relocate: bool = Field(True, description="If True, boosts score for opportunities outside home district/state")

    # Optional resume text for semantic matching
    resume_text: Optional[str] = Field(None, max_length=5000, description="Extracted resume text for semantic matching")

class RecommendationRequest(BaseModel):
    profile: CandidateProfile
    limit: int = Field(5, ge=1, le=5, description="Requested number of recommendations (default 5, max 5)")

class ComponentScores(BaseModel):
    skill_score: Optional[float] = None
    sector_score: Optional[float] = None
    location_score: Optional[float] = None
    text_score: Optional[float] = None

class EffectiveWeights(BaseModel):
    skill_weight: float
    sector_weight: float
    location_weight: float
    text_weight: float

class ReasonCode(BaseModel):
    code: str
    params: Dict[str, Any] = Field(default_factory=dict)
    text_en: str
    text_hi: str

class RecommendedInternship(BaseModel):
    internship: InternshipDetail
    relative_score: float = Field(..., description="Relative match score between 0.0 and 1.0 (or percentage 0-100)")
    match_tier: str = Field(..., description="'strong', 'good', 'moderate', or 'exploratory'")
    component_scores: ComponentScores
    effective_weights: EffectiveWeights
    missing_skills: List[str] = Field(default_factory=list)
    reasons: List[ReasonCode] = Field(default_factory=list)
    is_sample: bool = True

class RecommendationResponse(BaseModel):
    results: List[RecommendedInternship]
    total_eligible: int
    has_limited_profile: bool = False
    profile_summary_en: str
    profile_summary_hi: str
    disclaimer: str = "Demonstration prototype. Sample internships only. Not an official government portal."
