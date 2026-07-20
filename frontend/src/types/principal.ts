// Mirrors backend/app/schemas/principal.py

export interface PrincipalSchool {
  id: string;
  name: string;
  address: string | null;
  phone: string | null;
  website: string | null;
  created_at: string;
}

export interface StudentManageItem {
  user_id: string;
  student_id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  student_id_number: string | null;
  grade_level: number | null;
  class_id: string | null;
  class_name: string | null;
}

export interface StudentCreateInput {
  email: string;
  password: string;
  full_name: string;
  student_id_number?: string;
  grade_level?: number;
  class_id?: string;
}

export interface StudentUpdateInput {
  full_name?: string;
  student_id_number?: string;
  grade_level?: number;
  is_active?: boolean;
}

export interface TeacherManageItem {
  user_id: string;
  teacher_id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  employee_id: string | null;
  specialization: string | null;
  subjects_count: number;
}

export interface TeacherCreateInput {
  email: string;
  password: string;
  full_name: string;
  employee_id?: string;
  specialization?: string;
}

export interface TeacherUpdateInput {
  full_name?: string;
  employee_id?: string;
  specialization?: string;
  is_active?: boolean;
}

export interface ClassAttendanceSummary {
  class_id: string;
  class_name: string;
  present: number;
  absent: number;
  late: number;
  total_marked: number;
}

export interface AttendanceOverview {
  date: string;
  present: number;
  absent: number;
  late: number;
  total_marked: number;
  by_class: ClassAttendanceSummary[];
}

export interface HomeworkOverviewItem {
  id: string;
  title: string;
  class_id: string;
  class_name: string;
  due_date: string | null;
  submitted: number;
  total_students: number;
  completion_rate: number | null;
}

export interface ExamOverviewItem {
  id: string;
  title: string;
  subject_id: string;
  subject_name: string;
  class_id: string | null;
  class_name: string | null;
  date: string | null;
  results_recorded: number;
  average_score: number | null;
}

// Mirrors backend/app/schemas/memory.py analytics response shapes
export interface SchoolPerformance {
  school_id: string;
  school_name: string;
  average_score: number | null;
  total_students: number;
  total_teachers: number;
  total_classes: number;
}

export interface ClassPerformance {
  class_id: string;
  class_name: string;
  student_count: number;
  average_score: number | null;
  homework_completion_rate: number | null;
  attendance_rate: number | null;
}

export interface SubjectPerformance {
  subject_id: string;
  subject_name: string;
  average_score: number | null;
  total_exams: number;
}

export interface TeacherPerformance {
  teacher_id: string;
  full_name: string | null;
  subjects_taught: string[];
  average_student_score: number | null;
}

export interface AIUsageStats {
  total_conversations: number;
  total_quiz_attempts: number;
  active_students: number;
  average_conversations_per_student: number;
}

export interface PrincipalAISummary {
  data: {
    school_performance: SchoolPerformance;
    class_performance: ClassPerformance[];
    subject_performance: SubjectPerformance[];
    teacher_performance: TeacherPerformance[];
    ai_usage: AIUsageStats;
    risk_flags: Array<Record<string, unknown>>;
  };
  ai_recommendations: string | null;
}
