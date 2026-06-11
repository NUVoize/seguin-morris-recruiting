/**
 * Agent runs - trigger a pipeline run and poll its progress.
 *
 * Backend routes live in app/api/routes/agent_runs.py. The UI polls list()
 * every ~800ms during a run to render the live agent theater.
 */

import {apiRequest} from './client';
import type {AgentRun, TriggerAgentRunResponse} from './types';

interface ListOptions {
  campaignId?: string;
  since?: string; // ISO timestamp - only return runs started at or after this
  limit?: number;
  signal?: AbortSignal;
}

export const agentRuns = {
  trigger(campaignId?: string): Promise<TriggerAgentRunResponse> {
    return apiRequest<TriggerAgentRunResponse>('/agent-runs', {
      method: 'POST',
      query: {campaign_id: campaignId}
    });
  },

  list(opts: ListOptions = {}): Promise<AgentRun[]> {
    return apiRequest<AgentRun[]>('/agent-runs', {
      query: {
        campaign_id: opts.campaignId,
        since: opts.since,
        limit: opts.limit ?? 50
      },
      signal: opts.signal
    });
  },

  get(id: string): Promise<AgentRun> {
    return apiRequest<AgentRun>(`/agent-runs/${id}`);
  }
};