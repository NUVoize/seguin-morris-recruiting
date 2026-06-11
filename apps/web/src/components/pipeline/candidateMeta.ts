import type {Candidate} from '@/lib/api/types';

/**
 * Source-of-discovery, derived client-side from data the API already
 * returns (profile_url domain, candidate_type). No backend change needed.
 */
export interface SourceInfo {
  label: string;
  kind: 'board' | 'school' | 'social' | 'other';
}

export function candidateSource(c: Candidate): SourceInfo | null {
  const url = c.profile_url?.toLowerCase() ?? '';
  if (url.includes('jobillico')) return {label: 'Jobillico', kind: 'board'};
  if (url.includes('indeed')) return {label: 'Indeed', kind: 'board'};
  if (url.includes('jobboom')) return {label: 'Jobboom', kind: 'board'};
  if (url.includes('workopolis')) return {label: 'Workopolis', kind: 'board'};
  if (url.includes('linkedin')) return {label: 'LinkedIn', kind: 'social'};
  if ((c.candidate_type ?? '').toLowerCase().includes('finissant')) {
    return {label: 'CFP \u00b7 DEP', kind: 'school'};
  }
  if (url) {
    try {
      const host = new URL(c.profile_url as string).hostname.replace(/^www\./, '');
      return {label: host, kind: 'other'};
    } catch {
      return null;
    }
  }
  return null;
}

/** Whole days since an ISO timestamp. */
export function daysSince(iso: string | null | undefined): number | null {
  if (!iso) return null;
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return null;
  return Math.max(0, Math.floor((Date.now() - then) / 86_400_000));
}
