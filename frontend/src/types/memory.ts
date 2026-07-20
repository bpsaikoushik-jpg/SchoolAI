// Mirrors backend/app/schemas/memory.py (AI Memory Engine + Recommendation Engine)

export interface DailyProgress {
  id: string;
  student_id: string;
  date: string; // ISO date "YYYY-MM-DD"
  hours_studied: number;
  topics_covered: string[];
  subjects_summary: Record<string, number>;
  quizzes_taken: number;
  homework_completed: number;
  average_confidence: number | null;
  mood: string | null;
  created_at: string;
}

export type RecommendationPriority = 'high' | 'medium' | 'low';

export interface Recommendation {
  id: string;
  student_id: string;
  type: string; // daily_plan, weekly_plan, revision_plan, practice_questions, homework, exam_prep
  subject: string | null;
  title: string;
  content: Record<string, unknown>;
  priority: RecommendationPriority;
  due_date: string | null;
  is_completed: boolean;
  created_at: string;
}

export type ActivityType = 'quiz' | 'homework' | 'mistake';

export interface ActivityEvent {
  id: string;
  type: ActivityType;
  text: string;
  timestamp: string;
}
