/**
 * Resource-specific API methods. One file per resource keeps the surface small.
 */

import {apiRequest} from './client';
import type {Candidate, CandidateCreate, CandidateUpdate, PipelineStage} from './types';

interface ListOptions {
  limit?: number;
  offset?: number;
  pipelineStatus?: PipelineStage;
  region?: string;
  signal?: AbortSignal;
}

export const candidates = {
  list(opts: ListOptions = {}): Promise<Candidate[]> {
    return apiRequest<Candidate[]>('/candidates', {
      query: {
        limit: opts.limit ?? 200,
        offset: opts.offset,
        pipeline_status: opts.pipelineStatus,
        region: opts.region
      },
      signal: opts.signal
    });
  },

  get(id: string): Promise<Candidate> {
    return apiRequest<Candidate>(`/candidates/${id}`);
  },

  create(payload: CandidateCreate): Promise<Candidate> {
    return apiRequest<Candidate>('/candidates', {
      method: 'POST',
      body: payload
    });
  },

  update(id: string, payload: CandidateUpdate): Promise<Candidate> {
    return apiRequest<Candidate>(`/candidates/${id}`, {
      method: 'PATCH',
      body: payload
    });
  },

  setPipelineStage(id: string, stage: PipelineStage): Promise<Candidate> {
    return apiRequest<Candidate>(`/candidates/${id}`, {
      method: 'PATCH',
      body: {pipeline_status: stage}
    });
  },

  remove(id: string): Promise<void> {
    return apiRequest<void>(`/candidates/${id}`, {method: 'DELETE'});
  }
};
