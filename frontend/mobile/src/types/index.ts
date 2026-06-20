export interface QueryRequest {
  text: string;
  language?: string;
}

export interface QueryResponse {
  response: string;
  iteration_count: number;
  feedback_log: string[];
}

export interface HealthResponse {
  status: string;
  project: string;
}

export type QueryInputMode = 'text' | 'voice' | 'image';

export type AppScreen = 'Home' | 'Query';
