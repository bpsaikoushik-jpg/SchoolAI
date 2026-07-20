// Mirrors backend/app/schemas/{academic,tracking,communication}.py

export interface SchoolClass {
  id: string;
  name: string;
  school_id: string;
  created_at: string;
  updated_at: string;
}

export interface Subject {
  id: string;
  name: string;
  teacher_id: string | null;
  class_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Enrollment {
  id: string;
  student_id: string;
  class_id: string;
  created_at: string;
  updated_at: string;
}

export type AttendanceStatus = 'present' | 'absent' | 'late';

export interface AttendanceRecord {
  id: string;
  student_id: string;
  date: string;
  status: AttendanceStatus;
  created_at: string;
  updated_at: string;
}

export interface Homework {
  id: string;
  class_id: string;
  title: string;
  description: string | null;
  due_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface AssignmentSubmission {
  id: string;
  homework_id: string;
  student_id: string;
  content: string | null;
  grade: string | null;
  created_at: string;
  updated_at: string;
}

export interface Exam {
  id: string;
  subject_id: string;
  title: string;
  date: string | null;
  created_at: string;
  updated_at: string;
}

export interface ExamResult {
  id: string;
  exam_id: string;
  student_id: string;
  score: number | null;
  remarks: string | null;
  created_at: string;
  updated_at: string;
}

export interface AppNotification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  is_read: boolean;
  type: string | null;
  created_at: string;
}
