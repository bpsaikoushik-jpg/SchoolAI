import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '../store/useAuthStore';
import {
  fetchSchool,
  fetchStudents, createStudent, updateStudent, deactivateStudent,
  fetchTeachers, createTeacher, updateTeacher, deactivateTeacher,
  fetchAttendanceOverview, fetchHomeworkOverview, fetchExamsOverview,
  fetchSchoolPerformance, fetchClassPerformance, fetchSubjectPerformance,
  fetchTeacherPerformance, fetchAiUsageStats, fetchPrincipalAISummary,
} from '../services/principal.service';
import type { StudentCreateInput, StudentUpdateInput, TeacherCreateInput, TeacherUpdateInput } from '../types/principal';

/** Resolves the school_id the Principal Portal should scope every query to. */
export function usePrincipalSchoolId(): string | undefined {
  const user = useAuthStore((s) => s.user);
  return user?.school_id ?? undefined;
}

// ---------------------------------------------------------------------------
// School overview
// ---------------------------------------------------------------------------
export function useSchool() {
  const schoolId = usePrincipalSchoolId();
  return useQuery({
    queryKey: ['principal', 'school', schoolId],
    queryFn: () => fetchSchool(schoolId!),
    enabled: !!schoolId,
  });
}

// ---------------------------------------------------------------------------
// Student management
// ---------------------------------------------------------------------------
export function useStudents(search?: string, classId?: string) {
  const schoolId = usePrincipalSchoolId();
  return useQuery({
    queryKey: ['principal', 'students', schoolId, search, classId],
    queryFn: () => fetchStudents(schoolId!, { search, classId }),
    enabled: !!schoolId,
  });
}

export function useCreateStudent() {
  const schoolId = usePrincipalSchoolId();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: StudentCreateInput) => createStudent(schoolId!, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['principal', 'students', schoolId] }),
  });
}

export function useUpdateStudent() {
  const schoolId = usePrincipalSchoolId();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, payload }: { userId: string; payload: StudentUpdateInput }) =>
      updateStudent(schoolId!, userId, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['principal', 'students', schoolId] }),
  });
}

export function useDeactivateStudent() {
  const schoolId = usePrincipalSchoolId();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) => deactivateStudent(schoolId!, userId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['principal', 'students', schoolId] }),
  });
}

// ---------------------------------------------------------------------------
// Teacher management
// ---------------------------------------------------------------------------
export function useTeachers(search?: string) {
  const schoolId = usePrincipalSchoolId();
  return useQuery({
    queryKey: ['principal', 'teachers', schoolId, search],
    queryFn: () => fetchTeachers(schoolId!, search),
    enabled: !!schoolId,
  });
}

export function useCreateTeacher() {
  const schoolId = usePrincipalSchoolId();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: TeacherCreateInput) => createTeacher(schoolId!, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['principal', 'teachers', schoolId] }),
  });
}

export function useUpdateTeacher() {
  const schoolId = usePrincipalSchoolId();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, payload }: { userId: string; payload: TeacherUpdateInput }) =>
      updateTeacher(schoolId!, userId, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['principal', 'teachers', schoolId] }),
  });
}

export function useDeactivateTeacher() {
  const schoolId = usePrincipalSchoolId();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) => deactivateTeacher(schoolId!, userId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['principal', 'teachers', schoolId] }),
  });
}

// ---------------------------------------------------------------------------
// Attendance / homework / exam monitoring
// ---------------------------------------------------------------------------
export function useAttendanceOverview(onDate?: string) {
  const schoolId = usePrincipalSchoolId();
  return useQuery({
    queryKey: ['principal', 'attendance-overview', schoolId, onDate],
    queryFn: () => fetchAttendanceOverview(schoolId!, onDate),
    enabled: !!schoolId,
  });
}

export function useHomeworkOverview() {
  const schoolId = usePrincipalSchoolId();
  return useQuery({
    queryKey: ['principal', 'homework-overview', schoolId],
    queryFn: () => fetchHomeworkOverview(schoolId!),
    enabled: !!schoolId,
  });
}

export function useExamsOverview() {
  const schoolId = usePrincipalSchoolId();
  return useQuery({
    queryKey: ['principal', 'exams-overview', schoolId],
    queryFn: () => fetchExamsOverview(schoolId!),
    enabled: !!schoolId,
  });
}

// ---------------------------------------------------------------------------
// School-wide analytics
// ---------------------------------------------------------------------------
export function useSchoolPerformance() {
  const schoolId = usePrincipalSchoolId();
  return useQuery({
    queryKey: ['principal', 'school-performance', schoolId],
    queryFn: () => fetchSchoolPerformance(schoolId!),
    enabled: !!schoolId,
  });
}

export function useClassPerformance() {
  const schoolId = usePrincipalSchoolId();
  return useQuery({
    queryKey: ['principal', 'class-performance', schoolId],
    queryFn: () => fetchClassPerformance(schoolId!),
    enabled: !!schoolId,
  });
}

export function useSubjectPerformance() {
  const schoolId = usePrincipalSchoolId();
  return useQuery({
    queryKey: ['principal', 'subject-performance', schoolId],
    queryFn: () => fetchSubjectPerformance(schoolId!),
    enabled: !!schoolId,
  });
}

export function useTeacherPerformance() {
  const schoolId = usePrincipalSchoolId();
  return useQuery({
    queryKey: ['principal', 'teacher-performance', schoolId],
    queryFn: () => fetchTeacherPerformance(schoolId!),
    enabled: !!schoolId,
  });
}

export function useAiUsageStats() {
  const schoolId = usePrincipalSchoolId();
  return useQuery({
    queryKey: ['principal', 'ai-usage', schoolId],
    queryFn: () => fetchAiUsageStats(schoolId!),
    enabled: !!schoolId,
  });
}

export function usePrincipalAISummary() {
  const schoolId = usePrincipalSchoolId();
  return useQuery({
    queryKey: ['principal', 'ai-summary', schoolId],
    queryFn: () => fetchPrincipalAISummary(schoolId!),
    enabled: !!schoolId,
  });
}
