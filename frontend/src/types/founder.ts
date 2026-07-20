// Mirrors backend/app/schemas/founder.py

export interface SchoolManageItem {
  id: string;
  name: string;
  address: string | null;
  phone: string | null;
  website: string | null;
  is_active: boolean;
  created_at: string;
  total_students: number;
  total_teachers: number;
  total_classes: number;
  average_score: number | null;
}

export interface SchoolCreateInput {
  name: string;
  address?: string;
  phone?: string;
  website?: string;
  principal_email?: string;
  principal_password?: string;
  principal_full_name?: string;
}

export interface SchoolUpdateInput {
  name?: string;
  address?: string;
  phone?: string;
  website?: string;
}

export interface OrgOverview {
  total_schools: number;
  active_schools: number;
  inactive_schools: number;
  total_students: number;
  total_teachers: number;
  total_parents: number;
  total_staff: number;
  average_score: number | null;
}

export interface RoleBreakdownItem {
  role: string;
  count: number;
}

export interface OrgUserItem {
  user_id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  school_id: string | null;
  school_name: string | null;
}

export interface FounderSchoolPerformance {
  school_id: string;
  school_name: string;
  is_active: boolean;
  average_score: number | null;
  total_students: number;
  total_teachers: number;
  total_classes: number;
}

export interface SchoolAttendanceSummary {
  school_id: string;
  school_name: string;
  present: number;
  absent: number;
  late: number;
  total_marked: number;
}

export interface OrgAttendanceOverview {
  date: string;
  present: number;
  absent: number;
  late: number;
  total_marked: number;
  by_school: SchoolAttendanceSummary[];
}

export interface OrgHomeworkSummary {
  school_id: string;
  school_name: string;
  total_assigned: number;
  total_submitted: number;
  total_students_covered: number;
  completion_rate: number | null;
}

export interface OrgExamSummary {
  school_id: string;
  school_name: string;
  total_exams: number;
  results_recorded: number;
  average_score: number | null;
}

export interface SchoolStudentSummary {
  school_id: string;
  school_name: string;
  student_count: number;
  average_score: number | null;
}

export interface GradeLevelSummary {
  grade_level: number | null;
  count: number;
}

export interface OrgStudentAnalytics {
  by_school: SchoolStudentSummary[];
  by_grade: GradeLevelSummary[];
}

export interface SchoolTeacherSummary {
  school_id: string;
  school_name: string;
  teacher_count: number;
}

export interface TopTeacher {
  teacher_id: string;
  full_name: string | null;
  school_name: string;
  subjects_taught: string[];
  average_student_score: number | null;
}

export interface OrgTeacherAnalytics {
  by_school: SchoolTeacherSummary[];
  top_teachers: TopTeacher[];
}

export interface FounderAISummary {
  data: {
    org_overview: OrgOverview;
    school_performance: FounderSchoolPerformance[];
    role_breakdown: RoleBreakdownItem[];
    attendance_today: OrgAttendanceOverview;
    risk_flags: Array<Record<string, unknown>>;
  };
  ai_recommendations: string | null;
}
