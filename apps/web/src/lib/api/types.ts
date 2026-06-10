/**
 * Shared TypeScript types mirroring the FastAPI Pydantic schemas.
 *
 * These should track the backend `app/schemas/*.py` and `app/models/enums.py`.
 * If/when the team grows, generating these from OpenAPI is the right next step
 * (FastAPI exposes /api/openapi.json) — for now we hand-write the small surface.
 */

// ---------- Enums (mirror app/models/enums.py) ----------

export const PIPELINE_STAGES = [
  'new',
  'to_review',
  'contacted',
  'interested',
  'interview',
  'offer',
  'hired',
  'rejected',
  'archived',
] as const;

export type PipelineStage = (typeof PIPELINE_STAGES)[number];

export type CampaignStatus = 'draft' | 'active' | 'paused' | 'closed';

export type SourceType =
  | 'job_board'
  | 'school'
  | 'association'
  | 'event'
  | 'social'
  | 'company_site'
  | 'government'
  | 'manual';

// ---------- Resources ----------

export interface Candidate {
  id: string;
  full_name: string | null;
  current_title: string | null;
  region: string | null;
  candidate_type: string;
  contact_email: string | null;
  contact_phone: string | null;
  profile_url: string | null;
  pipeline_status: PipelineStage;
  fit_score: number | null;
  fit_label: string | null;
  fit_summary: string | null;
  source_confidence: number | null;
  consent_status: string;
  last_seen_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CandidateCreate {
  full_name?: string | null;
  current_title?: string | null;
  region?: string | null;
  candidate_type?: string;
  contact_email?: string | null;
  contact_phone?: string | null;
  profile_url?: string | null;
  pipeline_status?: PipelineStage;
}

export type CandidateUpdate = Partial<CandidateCreate> & {
  fit_score?: number | null;
  fit_label?: string | null;
  fit_summary?: string | null;
  consent_status?: string;
};

export interface Campaign {
  id: string;
  title: string;
  division: string;
  role_type: string;
  region: string;
  employment_type: string | null;
  requirements: Record<string, unknown>;
  status: CampaignStatus;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface LeadSource {
  id: string;
  name: string;
  source_type: SourceType;
  url: string;
  access_method: string;
  allowed_to_scrape: boolean;
  notes: string | null;
  last_checked_at: string | null;
  created_at: string;
  updated_at: string;
}
