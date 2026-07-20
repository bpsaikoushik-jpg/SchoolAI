import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchSchools, createSchool, updateSchool, activateSchool, deactivateSchool,
  fetchOrgOverview, fetchUserBreakdown, fetchOrgUsers,
  fetchSchoolPerformance, fetchOrgAttendance, fetchOrgHomework, fetchOrgExams,
  fetchOrgStudentAnalytics, fetchOrgTeacherAnalytics, fetchFounderAISummary,
} from '../services/founder.service';
import type { SchoolCreateInput, SchoolUpdateInput } from '../types/founder';

// ---------------------------------------------------------------------------
// School management
// ---------------------------------------------------------------------------
export function useSchools(search?: string, includeInactive = true) {
  return useQuery({
    queryKey: ['founder', 'schools', search, includeInactive],
    queryFn: () => fetchSchools({ search, includeInactive }),
  });
}

export function useCreateSchool() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: SchoolCreateInput) => createSchool(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['founder', 'schools'] }),
  });
}

export function useUpdateSchool() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ schoolId, payload }: { schoolId: string; payload: SchoolUpdateInput }) =>
      updateSchool(schoolId, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['founder', 'schools'] }),
  });
}

export function useActivateSchool() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (schoolId: string) => activateSchool(schoolId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['founder', 'schools'] }),
  });
}

export function useDeactivateSchool() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (schoolId: string) => deactivateSchool(schoolId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['founder', 'schools'] }),
  });
}

// ---------------------------------------------------------------------------
// Organization overview
// ---------------------------------------------------------------------------
export function useOrgOverview() {
  return useQuery({ queryKey: ['founder', 'overview'], queryFn: fetchOrgOverview });
}

export function useUserBreakdown() {
  return useQuery({ queryKey: ['founder', 'user-breakdown'], queryFn: fetchUserBreakdown });
}

// ---------------------------------------------------------------------------
// Org-wide user directory
// ---------------------------------------------------------------------------
export function useOrgUsers(role?: string, search?: string) {
  return useQuery({
    queryKey: ['founder', 'users', role, search],
    queryFn: () => fetchOrgUsers({ role, search }),
  });
}

// ---------------------------------------------------------------------------
// Org-wide analytics
// ---------------------------------------------------------------------------
export function useSchoolPerformance() {
  return useQuery({ queryKey: ['founder', 'school-performance'], queryFn: fetchSchoolPerformance });
}

export function useOrgAttendance(onDate?: string) {
  return useQuery({ queryKey: ['founder', 'attendance', onDate], queryFn: () => fetchOrgAttendance(onDate) });
}

export function useOrgHomework() {
  return useQuery({ queryKey: ['founder', 'homework'], queryFn: fetchOrgHomework });
}

export function useOrgExams() {
  return useQuery({ queryKey: ['founder', 'exams'], queryFn: fetchOrgExams });
}

export function useOrgStudentAnalytics() {
  return useQuery({ queryKey: ['founder', 'student-analytics'], queryFn: fetchOrgStudentAnalytics });
}

export function useOrgTeacherAnalytics() {
  return useQuery({ queryKey: ['founder', 'teacher-analytics'], queryFn: fetchOrgTeacherAnalytics });
}

// ---------------------------------------------------------------------------
// AI Founder Assistant
// ---------------------------------------------------------------------------
export function useFounderAISummary() {
  return useQuery({ queryKey: ['founder', 'ai-summary'], queryFn: fetchFounderAISummary });
}
