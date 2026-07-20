// Mirrors backend/app/services/teacher_insight_service.py + calendar module

export interface TeacherClassSummary {
  class_id: string;
  subject_id: string;
  name: string;
  students: number;
  avg_score: number;
}

export interface AttendanceTodaySummary {
  present: number;
  absent: number;
  late: number;
}

export interface HomeworkQueueItem {
  id: string;
  title: string;
  class_name: string;
  due_date: string | null;
  submitted: number;
  total: number;
}

export type CalendarEventType = 'class' | 'meeting' | 'task' | 'other';

export interface CalendarEvent {
  id: string;
  school_id: string;
  owner_id: string;
  class_id: string | null;
  title: string;
  description: string | null;
  event_type: CalendarEventType;
  starts_at: string;
  ends_at: string | null;
  created_at: string;
}

export interface StudentRosterItem {
  student_id: string;
  full_name: string | null;
  class_name: string;
  average_score: number;
  attendance_rate: number | null;
}

export interface CalendarEventCreateInput {
  title: string;
  description?: string;
  event_type?: CalendarEventType;
  starts_at: string;
  ends_at?: string;
  class_id?: string;
}

