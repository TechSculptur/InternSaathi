export interface LocalizedOption {
  code: string;
  label_en: string;
  label_hi: string;
}

export interface SectorOption {
  code: string;
  name_en: string;
  name_hi: string;
}

export interface SkillOption {
  code: string;
  name_en: string;
  name_hi: string;
  sector_code?: string;
}

export interface DistrictOption {
  name_en: string;
  name_hi: string;
}

export interface StateDistrictOption {
  state_en: string;
  state_hi: string;
  districts: DistrictOption[];
}

export interface WorkModeOption {
  code: string;
  label_en: string;
  label_hi: string;
}

export interface OptionsResponse {
  education_categories: LocalizedOption[];
  sectors: SectorOption[];
  skills: SkillOption[];
  states_and_districts: StateDistrictOption[];
  work_modes: WorkModeOption[];
}

export interface SkillSummary {
  id: number;
  code: string;
  name_en: string;
  name_hi: string;
}

export interface EducationSummary {
  id: number;
  code: string;
  label_en: string;
  label_hi: string;
}

export interface SectorSummary {
  id: number;
  code: string;
  name_en: string;
  name_hi: string;
}

export interface Internship {
  id: string;
  title: string;
  organization_name: string;
  description?: string;
  sector: SectorSummary;
  state: string;
  district: string;
  work_mode: string;
  duration_months: number;
  stipend_inr: number;
  deadline: string;
  is_active: boolean;
  allows_no_skills: boolean;
  is_sample: boolean;
  required_skills?: SkillSummary[];
  accepted_educations?: EducationSummary[];
}

export interface CandidateProfile {
  education: string;
  skills: string[];
  sectors: string[];
  state?: string;
  district?: string;
  preferred_work_mode: string;
  is_work_mode_mandatory: boolean;
  is_location_mandatory: boolean;
  willing_to_relocate: boolean;
  resume_text?: string;
}

export interface ReasonCode {
  code: string;
  params: Record<string, any>;
  text_en: string;
  text_hi: string;
}

export interface ComponentScores {
  skill_score?: number | null;
  sector_score?: number | null;
  location_score?: number | null;
  text_score?: number | null;
}

export interface EffectiveWeights {
  skill_weight: number;
  sector_weight: number;
  location_weight: number;
  text_weight: number;
}

export interface RecommendedInternship {
  internship: Internship;
  relative_score: number;
  match_tier: "strong" | "good" | "moderate" | "exploratory";
  component_scores: ComponentScores;
  effective_weights: EffectiveWeights;
  missing_skills: string[];
  reasons: ReasonCode[];
  is_sample: boolean;
}

export interface RecommendationResponse {
  results: RecommendedInternship[];
  total_eligible: number;
  has_limited_profile: boolean;
  profile_summary_en: string;
  profile_summary_hi: string;
  disclaimer: string;
}

export interface ParsedResumeResponse {
  detected_skills: string[];
  detected_education: string | null;
  resume_text: string;
  privacy_note_en: string;
  privacy_note_hi: string;
}
