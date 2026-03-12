export interface MatchScoreItem {
  title: string;
  description: string;
  score: number;
}

export interface MatchResult {
  score: number;
  summary: string;
  strengths: MatchScoreItem[];
  weaknesses: MatchScoreItem[];
}

export interface ComparisonHistory {
  resumeName: string;
  resumeUuid?: string;
  score: number;
  comparedAt: string;
}

export interface SavedJD {
  id: string;
  title: string;
  company: string;
  savedAt: string;
  snippet: string;
  content: string;
  comparisons: ComparisonHistory[];
}
