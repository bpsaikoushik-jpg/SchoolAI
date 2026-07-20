import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchMyHomework,
  fetchHomeworkForStudent,
  fetchHomeworkByClass,
  createHomework,
  updateHomework,
  deleteHomework,
  submitHomework,
  fetchMySubmissions,
  fetchSubmissionsForStudent,
  fetchSubmissionsForHomework,
  gradeSubmission,
} from '../services/homework.service';

export function useMyHomework() {
  return useQuery({ queryKey: ['homework', 'me'], queryFn: fetchMyHomework });
}

export function useStudentHomework(studentId: string | undefined) {
  return useQuery({
    queryKey: ['homework', 'student', studentId],
    queryFn: () => fetchHomeworkForStudent(studentId),
    enabled: !!studentId,
  });
}

export function useStudentSubmissions(studentId: string | undefined) {
  return useQuery({
    queryKey: ['submissions', 'student', studentId],
    queryFn: () => fetchSubmissionsForStudent(studentId),
    enabled: !!studentId,
  });
}

export function useClassHomework(classId: string | undefined) {
  return useQuery({
    queryKey: ['homework', 'class', classId],
    queryFn: () => fetchHomeworkByClass(classId!),
    enabled: !!classId,
  });
}

export function useMySubmissions() {
  return useQuery({ queryKey: ['submissions', 'me'], queryFn: fetchMySubmissions });
}

export function useSubmissionsForHomework(homeworkId: string | undefined) {
  return useQuery({
    queryKey: ['submissions', 'homework', homeworkId],
    queryFn: () => fetchSubmissionsForHomework(homeworkId!),
    enabled: !!homeworkId,
  });
}

export function useCreateHomework() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createHomework,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['homework'] }),
  });
}

export function useUpdateHomework() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Parameters<typeof updateHomework>[1] }) => updateHomework(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['homework'] }),
  });
}

export function useDeleteHomework() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deleteHomework,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['homework'] }),
  });
}

export function useSubmitHomework() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: submitHomework,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['submissions'] }),
  });
}

export function useGradeSubmission() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, grade }: { id: string; grade: string }) => gradeSubmission(id, grade),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['submissions'] });
      qc.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}
