import type { JsonObject } from '../../common'

export type FindContextType = 'memory' | 'resource' | 'skill'

export type SearchHit = {
  abstract?: string
  category?: string
  confidence?: number
  context_type?: FindContextType | (string & {})
  level?: number
  match_reason?: string
  overview?: string | null
  /** Unweighted retrieval score; relevance gating uses this value. */
  raw_score?: number
  /** Weighted ranking score: raw_score * (1 - 0.2 * (1 - confidence)). */
  score?: number
  uri?: string
}

export type SearchQueryPlanItem = {
  context_type?: FindContextType | null
  intent?: string | null
  priority?: number | null
  query: string
}

export type SearchQueryPlan = {
  queries: SearchQueryPlanItem[]
  reasoning?: string | null
}

export type SearchResult = {
  memories?: SearchHit[]
  provenance?: JsonObject[] | null
  query_plan?: SearchQueryPlan | null
  resources?: SearchHit[]
  skills?: SearchHit[]
  total?: number
}

export type FindResult = SearchResult
