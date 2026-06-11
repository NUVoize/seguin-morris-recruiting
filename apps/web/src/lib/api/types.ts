/**
 * Shared TypeScript types mirroring the FastAPI Pydantic schemas.
 *
 * These should track the backend `app/schemas/*.py` and `app/models/enums.py`.
 * If/when the team grows, generating these from OpenAPI is the right next step
 * (FastAPI exposes /api/openapi.json) â€” for now we hand-write the small surface.
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

export const AGENT_TYPES = [
  'employment_source',
  'school_pipeline',
  'event_discovery',
  'lead_enrichment',
  'candidate_vetting',
  'fit_ranking',
  'outreach',
  'email_sync',
  'assistant_knowledge',
  'reporting',
] as const;

export type AgentType = (typeof AGENT_TYPES)[number];

export type AgentRunStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

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

// ---------- Agent runs (Phase 3) ----------

export interface AgentStep {
  ts: string;
  icon: string;
  message: string;
  detail?: Record<string, unknown> | null;
}

export interface AgentRunOutput {
  agent_type: string;
  display_name: string;
  icon: string;
  status: string;
  steps: AgentStep[];
  counts: Record<string, number>;
}

export interface AgentRun {
  id: string;
  campaign_id: string | null;
  agent_type: AgentType;
  status: AgentRunStatus;
  started_at: string | null;
  completed_at: string | null;
  output: AgentRunOutput | null;
  error_log: Record<string, unknown> | null;
}

export interface TriggerAgentRunResponse {
  started_at: string;
  campaign_id: string | null;
  agents: string[];
  message: string;
}

// ---------- Real-data track: school program directory ----------

export type ProgramType = 'DEP' | 'DEC' | 'AEC';

export interface SchoolProgram {
  id: string;
  institution_name: string;
  program_name: string;
  program_type: ProgramType;
  city: string | null;
  province: string | null;
  country: string;
  public_contact_name: string | null;
  public_contact_email: string | null;
  public_contact_phone: string | null;
  cohort_start: string | null;
  cohort_end: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}
