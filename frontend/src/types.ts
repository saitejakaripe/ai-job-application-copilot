export type CandidateLevel = "fresher" | "intern" | "experienced";
export type JobType = "Internship" | "Full-time" | "Part-time" | "Contract" | "Remote";
export type MarketScope = "india" | "abroad" | "both";

export interface ResumeProfile {
  candidate_name: string;
  skills: string[];
  education: string[];
  projects: string[];
  certifications: string[];
  work_experience: string[];
  technical_tools: string[];
  keywords: string[];
  years_experience: number | null;
  suitable_roles: string[];
}

export interface Preferences {
  candidate_level: CandidateLevel;
  years_experience: number | null;
  job_types: JobType[];
  locations: string[];
  custom_location?: string | null;
  interested_roles: string[];
  open_to_relocation: boolean;
  expected_salary_min_lpa?: number | null;
  expected_salary_max_lpa?: number | null;
  market_scope: MarketScope;
  min_match_percentage: number;
  skill_filters: string[];
  source_filters: string[];
}

export interface JobRecommendation {
  id: string;
  job_title: string;
  company_name: string;
  location: string;
  country: string;
  job_type: string;
  required_experience: string;
  required_skills: string[];
  matched_skills: string[];
  missing_skills: string[];
  resume_match_percentage: number;
  match_reason: string;
  direct_apply_link: string;
  source_website: string;
  salary_range: string | null;
  is_remote: boolean;
  region: "india" | "global";
}

export interface ResumeImprovementBundle {
  missing_skills: string[];
  keywords_to_add: string[];
  project_suggestions: string[];
  certification_suggestions: string[];
  ats_suggestions: string[];
}

export interface SourceLink {
  label: string;
  url: string;
  region: "india" | "global";
}

export interface ApplicationLink {
  label: string;
  url: string;
  source_website: string;
  role: string;
  location: string;
  job_type: string;
  region: "india" | "global";
  is_remote: boolean;
}

export interface JobRecommendationResponse {
  profile: ResumeProfile;
  preferences: Preferences;
  jobs: JobRecommendation[];
  resume_improvements: ResumeImprovementBundle;
  source_links: SourceLink[];
  application_links: ApplicationLink[];
  total_matches: number;
  returned_matches: number;
  generated_application_links_count: number;
  generated_at: string;
}
