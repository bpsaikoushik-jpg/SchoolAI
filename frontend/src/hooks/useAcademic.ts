import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchClassesBySchool,
  fetchClass,
  createClass,
  updateClass,
  deleteClass,
  fetchSubjectsByTeacher,
  fetchSubjectsByClass,
  fetchMySubjects,
  fetchSubjectsByStudent,
  fetchTeacherDirectoryByStudent,
  createSubject,
  fetchMyEnrollments,
  fetchEnrollmentsByClass,
  fetchEnrollmentsByStudent,
  enrollStudent,
  deleteEnrollment,
} from '../services/academic.service';

export function useClassesBySchool(schoolId: string | undefined) {
  return useQuery({
    queryKey: ['classes', 'school', schoolId],
    queryFn: () => fetchClassesBySchool(schoolId!),
    enabled: !!schoolId,
  });
}

export function useClass(classId: string | undefined) {
  return useQuery({
    queryKey: ['classes', classId],
    queryFn: () => fetchClass(classId!),
    enabled: !!classId,
  });
}

export function useMyEnrollments() {
  return useQuery({ queryKey: ['enrollments', 'me'], queryFn: fetchMyEnrollments });
}

export function useEnrollmentsByClass(classId: string | undefined) {
  return useQuery({
    queryKey: ['enrollments', 'class', classId],
    queryFn: () => fetchEnrollmentsByClass(classId!),
    enabled: !!classId,
  });
}

export function useSubjectsByTeacher(teacherId: string | undefined) {
  return useQuery({
    queryKey: ['subjects', 'teacher', teacherId],
    queryFn: () => fetchSubjectsByTeacher(teacherId!),
    enabled: !!teacherId,
  });
}

export function useSubjectsByClass(classId: string | undefined) {
  return useQuery({
    queryKey: ['subjects', 'class', classId],
    queryFn: () => fetchSubjectsByClass(classId!),
    enabled: !!classId,
  });
}

export function useMySubjects() {
  return useQuery({ queryKey: ['subjects', 'me'], queryFn: fetchMySubjects });
}

export function useSubjectsByStudent(studentId: string | null | undefined) {
  return useQuery({
    queryKey: ['subjects', 'student', studentId],
    queryFn: () => fetchSubjectsByStudent(studentId ?? undefined),
    enabled: !!studentId,
  });
}

export function useEnrollmentsByStudent(studentId: string | null | undefined) {
  return useQuery({
    queryKey: ['enrollments', 'student', studentId],
    queryFn: () => fetchEnrollmentsByStudent(studentId ?? undefined),
    enabled: !!studentId,
  });
}

export function useTeacherDirectoryByStudent(studentId: string | null | undefined) {
  return useQuery({
    queryKey: ['teachers', 'student', studentId],
    queryFn: () => fetchTeacherDirectoryByStudent(studentId ?? undefined),
    enabled: !!studentId,
  });
}

export function useCreateClass() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createClass,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['classes'] }),
  });
}

export function useUpdateClass() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ classId, payload }: { classId: string; payload: { name?: string } }) => updateClass(classId, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['classes'] }),
  });
}

export function useDeleteClass() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (classId: string) => deleteClass(classId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['classes'] }),
  });
}

export function useDeleteEnrollment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (enrollmentId: string) => deleteEnrollment(enrollmentId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['enrollments'] }),
  });
}

export function useCreateSubject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createSubject,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['subjects'] }),
  });
}

export function useEnrollStudent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: enrollStudent,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['enrollments'] }),
  });
}
