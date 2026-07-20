export interface ChildSummary {
  student_id: string;
  full_name: string | null;
  grade_level: number | null;
  relationship_type: string;
}

export interface WeeklyProgressSnapshot {
  week_start_date: string;
  hours_studied: number | null;
  topics_covered: number | null;
  subjects_summary: Record<string, unknown> | null;
  average_score: number | null;
}

export interface MonthlyProgressSnapshot {
  month: number;
  year: number;
  hours_studied: number | null;
  average_score: number | null;
  improvement_trend: string | null;
}

export interface ChildProgress {
  knowledge_level: string | null;
  confidence_score: number | null;
  learning_speed: string | null;
  weak_subjects: string[] | null;
  strong_subjects: string[] | null;
  weak_chapters: string[] | null;
  forgotten_topics: string[] | null;
  latest_week: WeeklyProgressSnapshot | null;
  latest_month: MonthlyProgressSnapshot | null;
}

export interface AISummaryData {
  progress: ChildProgress;
  attendance: { attendance_rate: number | null };
  pending_homework_count: number;
  exam_preparation: string | null;
}

export interface AISummaryResponse {
  data: AISummaryData;
  ai_summary: string | null;
  ai_recommendations?: string | null;
}
