import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchExamsBySubject,
  fetchMyUpcomingExams,
  fetchUpcomingExamsForStudent,
  createExam,
  fetchStudentResults,
  fetchStudentResultsDetailed,
  fetchResultsForExam,
  recordResult,
} from '../services/exam.service';

export function useExamsBySubject(subjectId: string | undefined) {
  return useQuery({
    queryKey: ['exams', 'subject', subjectId],
    queryFn: () => fetchExamsBySubject(subjectId!),
    enabled: !!subjectId,
  });
}

export function useMyUpcomingExams() {
  return useQuery({ queryKey: ['exams', 'me', 'upcoming'], queryFn: fetchMyUpcomingExams });
}

export function useStudentUpcomingExams(studentId: string | undefined) {
  return useQuery({
    queryKey: ['exams', 'student', studentId, 'upcoming'],
    queryFn: () => fetchUpcomingExamsForStudent(studentId),
    enabled: !!studentId,
  });
}

export function useMyResults() {
  return useQuery({ queryKey: ['results', 'me'], queryFn: () => fetchStudentResults() });
}

export function useStudentResults(studentId: string | undefined) {
  return useQuery({
    queryKey: ['results', 'student', studentId],
    queryFn: () => fetchStudentResults(studentId),
    enabled: !!studentId,
  });
}

export function useStudentResultsDetailed(studentId: string | null | undefined) {
  return useQuery({
    queryKey: ['results', 'student', studentId, 'detailed'],
    queryFn: () => fetchStudentResultsDetailed(studentId ?? undefined),
    enabled: !!studentId,
  });
}

export function useResultsForExam(examId: string | undefined) {
  return useQuery({
    queryKey: ['results', 'exam', examId],
    queryFn: () => fetchResultsForExam(examId!),
    enabled: !!examId,
  });
}

export function useCreateExam() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createExam,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['exams'] }),
  });
}

export function useRecordResult() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: recordResult,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['results'] });
      qc.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}
