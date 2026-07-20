import api from './api';
import type {
  SchoolManageItem, SchoolCreateInput, SchoolUpdateInput,
  OrgOverview, RoleBreakdownItem, OrgUserItem,
  FounderSchoolPerformance, OrgAttendanceOverview, OrgHomeworkSummary, OrgExamSummary,
  OrgStudentAnalytics, OrgTeacherAnalytics, FounderAISummary,
} from '../types/founder';

// ---------------------------------------------------------------------------
// School management
// ---------------------------------------------------------------------------
export async function fetchSchools(params?: { search?: string; includeInactive?: boolean }): Promise<SchoolManageItem[]> {
  const { data } = await api.get<SchoolManageItem[]>('/founder/schools', {
    params: { search: params?.search || undefined, include_inactive: params?.includeInactive ?? true },
  });
  return data;
}

export async function createSchool(payload: SchoolCreateInput): Promise<SchoolManageItem> {
  const { data } = await api.post<SchoolManageItem>('/founder/schools', payload);
  return data;
}

export async function updateSchool(schoolId: string, payload: SchoolUpdateInput): Promise<SchoolManageItem> {
  const { data } = await api.patch<SchoolManageItem>(`/founder/schools/${schoolId}`, payload);
  return data;
}

export async function activateSchool(schoolId: string): Promise<SchoolManageItem> {
  const { data } = await api.post<SchoolManageItem>(`/founder/schools/${schoolId}/activate`);
  return data;
}

export async function deactivateSchool(schoolId: string): Promise<SchoolManageItem> {
  const { data } = await api.post<SchoolManageItem>(`/founder/schools/${schoolId}/deactivate`);
  return data;
}

// ---------------------------------------------------------------------------
// Organization overview
// ---------------------------------------------------------------------------
export async function fetchOrgOverview(): Promise<OrgOverview> {
  const { data } = await api.get<OrgOverview>('/founder/overview');
  return data;
}

export async function fetchUserBreakdown(): Promise<RoleBreakdownItem[]> {
  const { data } = await api.get<RoleBreakdownItem[]>('/founder/user-breakdown');
  return data;
}

// ---------------------------------------------------------------------------
// Org-wide user directory
// ---------------------------------------------------------------------------
export async function fetchOrgUsers(params?: { role?: string; search?: string }): Promise<OrgUserItem[]> {
  const { data } = await api.get<OrgUserItem[]>('/founder/users', {
    params: { role: params?.role || undefined, search: params?.search || undefined },
  });
  return data;
}

// ---------------------------------------------------------------------------
// Org-wide analytics
// ---------------------------------------------------------------------------
export async function fetchSchoolPerformance(): Promise<FounderSchoolPerformance[]> {
  const { data } = await api.get<FounderSchoolPerformance[]>('/founder-analytics/school-performance');
  return data;
}

export async function fetchOrgAttendance(onDate?: string): Promise<OrgAttendanceOverview> {
  const { data } = await api.get<OrgAttendanceOverview>('/founder-analytics/attendance', {
    params: { on_date: onDate },
  });
  return data;
}

export async function fetchOrgHomework(): Promise<OrgHomeworkSummary[]> {
  const { data } = await api.get<OrgHomeworkSummary[]>('/founder-analytics/homework');
  return data;
}

export async function fetchOrgExams(): Promise<OrgExamSummary[]> {
  const { data } = await api.get<OrgExamSummary[]>('/founder-analytics/exams');
  return data;
}

export async function fetchOrgStudentAnalytics(): Promise<OrgStudentAnalytics> {
  const { data } = await api.get<OrgStudentAnalytics>('/founder-analytics/students');
  return data;
}

export async function fetchOrgTeacherAnalytics(): Promise<OrgTeacherAnalytics> {
  const { data } = await api.get<OrgTeacherAnalytics>('/founder-analytics/teachers');
  return data;
}

// ---------------------------------------------------------------------------
// AI Founder Assistant
// ---------------------------------------------------------------------------
export async function fetchFounderAISummary(): Promise<FounderAISummary> {
  const { data } = await api.get<FounderAISummary>('/founder-ai/analytics');
  return data;
}
