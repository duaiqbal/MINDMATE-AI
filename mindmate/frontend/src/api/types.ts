export interface ChatReply {
  reply: string;
  language: string;
  strategy: string;
  evidence: string[];
}
export interface MoodTrendPoint {
  day?: string;
  average_mood?: number;
  count?: number;
}
export interface MoodTrends {
  window?: string;
  window_days?: number;
  points: MoodTrendPoint[];
}
export interface MemoryItem {
  id: string;
  content: string;
}
export interface MemoryList {
  items: MemoryItem[];
}
export interface CrisisResource {
  id: string;
  name: string;
  phone: string | null;
  url: string | null;
  notes?: string | null;
}
export interface CrisisResources {
  resources: CrisisResource[];
}