import api from './api';
import type {
  PrincipalSchool,
  StudentManageItem, StudentCreateInput, StudentUpdateInput,
  TeacherManageItem, TeacherCreateInput, TeacherUpdateInput,
  AttendanceOverview, HomeworkOverviewItem, ExamOverviewItem,
  SchoolPerformance, ClassPerformance, SubjectPerformance, TeacherPerformance, AIUsageStats,
  PrincipalAISummary,
} from '../types/principal';

// ---------------------------------------------------------------------------
// School overview
// ---------------------------------------------------------------------------
export async function fetchSchool(schoolId: string): Promise<PrincipalSchool> {
  const { data } = await api.get<PrincipalSchool>(`/principal/school/${schoolId}`);
  return data;
}

// ---------------------------------------------------------------------------
// Student management
// ---------------------------------------------------------------------------
export async function fetchStudents(
  schoolId: string,
  params?: { search?: string; classId?: string }
): Promise<StudentManageItem[]> {
  const { data } = await api.get<StudentManageItem[]>(`/principal/students/${schoolId}`, {
    params: { search: params?.search || undefined, class_id: params?.classId || undefined },
  });
  return data;
}

export async function createStudent(schoolId: string, payload: StudentCreateInput): Promise<StudentManageItem> {
  const { data } = await api.post<StudentManageItem>(`/principal/students/${schoolId}`, payload);
  return data;
}

export async function updateStudent(
  schoolId: string, userId: string, payload: StudentUpdateInput
): Promise<StudentManageItem> {
  const { data } = await api.patch<StudentManageItem>(`/principal/students/${schoolId}/${userId}`, payload);
  return data;
}

export async function deactivateStudent(schoolId: string, userId: string): Promise<void> {
  await api.delete(`/principal/students/${schoolId}/${userId}`);
}

// ---------------------------------------------------------------------------
// Teacher management
// ---------------------------------------------------------------------------
export async function fetchTeachers(schoolId: string, search?: string): Promise<TeacherManageItem[]> {
  const { data } = await api.get<TeacherManageItem[]>(`/principal/teachers/${schoolId}`, {
    params: { search: search || undefined },
  });
  return data;
}

export async function createTeacher(schoolId: string, payload: TeacherCreateInput): Promise<TeacherManageItem> {
  const { data } = await api.post<TeacherManageItem>(`/principal/teachers/${schoolId}`, payload);
  return data;
}

export async function updateTeacher(
  schoolId: string, userId: string, payload: TeacherUpdateInput
): Promise<TeacherManageItem> {
  const { data } = await api.patch<TeacherManageItem>(`/principal/teachers/${schoolId}/${userId}`, payload);
  return data;
}

export async function deactivateTeacher(schoolId: string, userId: string): Promise<void> {
  await api.delete(`/principal/teachers/${schoolId}/${userId}`);
}

// ---------------------------------------------------------------------------
// Attendance / homework / exam monitoring
// ---------------------------------------------------------------------------
export async function fetchAttendanceOverview(schoolId: string, onDate?: string): Promise<AttendanceOverview> {
  const { data } = await api.get<AttendanceOverview>(`/principal/attendance-overview/${schoolId}`, {
    params: { on_date: onDate },
  });
  return data;
}

export async function fetchHomeworkOverview(schoolId: string): Promise<HomeworkOverviewItem[]> {
  const { data } = await api.get<HomeworkOverviewItem[]>(`/principal/homework-overview/${schoolId}`);
  return data;
}

export async function fetchExamsOverview(schoolId: string): Promise<ExamOverviewItem[]> {
  const { data } = await api.get<ExamOverviewItem[]>(`/principal/exams-overview/${schoolId}`);
  return data;
}

// ---------------------------------------------------------------------------
// School-wide analytics (existing /principal-analytics + /principal/analytics)
// ---------------------------------------------------------------------------
export async function fetchSchoolPerformance(schoolId: string): Promise<SchoolPerformance> {
  const { data } = await api.get<SchoolPerformance>(`/principal-analytics/school-performance/${schoolId}`);
  return data;
}

export async function fetchClassPerformance(schoolId: string): Promise<ClassPerformance[]> {
  const { data } = await api.get<ClassPerformance[]>(`/principal-analytics/class-performance/${schoolId}`);
  return data;
}

export async function fetchSubjectPerformance(schoolId: string): Promise<SubjectPerformance[]> {
  const { data } = await api.get<SubjectPerformance[]>(`/principal-analytics/subject-performance/${schoolId}`);
  return data;
}

export async function fetchTeacherPerformance(schoolId: string): Promise<TeacherPerformance[]> {
  const { data } = await api.get<TeacherPerformance[]>(`/principal-analytics/teacher-performance/${schoolId}`);
  return data;
}

export async function fetchAiUsageStats(schoolId: string): Promise<AIUsageStats> {
  const { data } = await api.get<AIUsageStats>(`/principal-analytics/ai-usage/${schoolId}`);
  return data;
}

export async function fetchPrincipalAISummary(schoolId: string): Promise<PrincipalAISummary> {
  const { data } = await api.get<PrincipalAISummary>('/principal/analytics', {
    params: { school_id: schoolId },
  });
  return data;
}
