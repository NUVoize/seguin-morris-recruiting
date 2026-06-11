/**
 * LeadSource API methods — the source-policy directory.
 */

import {apiRequest} from './client';
import type {LeadSource, SourceType} from './types';

export const sources = {
  list(opts: {limit?: number; sourceType?: SourceType} = {}): Promise<LeadSource[]> {
    return apiRequest<LeadSource[]>('/sources', {
      query: {limit: opts.limit ?? 100, source_type: opts.sourceType}
    });
  },

  setScrapePolicy(id: string, allowed: boolean): Promise<LeadSource> {
    return apiRequest<LeadSource>(`/sources/${id}`, {
      method: 'PATCH',
      body: {allowed_to_scrape: allowed}
    });
  },

  updateNotes(id: string, notes: string): Promise<LeadSource> {
    return apiRequest<LeadSource>(`/sources/${id}`, {
      method: 'PATCH',
      body: {notes}
    });
  }
};
