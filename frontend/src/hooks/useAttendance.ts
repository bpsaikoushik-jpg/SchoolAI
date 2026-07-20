import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchStudentAttendance, fetchClassAttendance, markAttendance, summarizeAttendance } from '../services/attendance.service';

export function useMyAttendance() {
  return useQuery({
    queryKey: ['attendance', 'student', 'me'],
    queryFn: () => fetchStudentAttendance(),
  });
}

export function useStudentAttendance(studentId: string | undefined) {
  const query = useQuery({
    queryKey: ['attendance', 'student', studentId],
    queryFn: () => fetchStudentAttendance({ studentId }),
    enabled: !!studentId,
  });
  return {
    ...query,
    summary: query.data ? summarizeAttendance(query.data) : { present: 0, absent: 0, late: 0, total: 0 },
  };
}

export function useAttendanceSummary() {
  const query = useMyAttendance();
  return {
    ...query,
    summary: query.data ? summarizeAttendance(query.data) : { present: 0, absent: 0, late: 0, total: 0 },
  };
}

export function useClassAttendance(classId: string | undefined) {
  return useQuery({
    queryKey: ['attendance', 'class', classId],
    queryFn: () => fetchClassAttendance(classId!),
    enabled: !!classId,
  });
}

export function useMarkAttendance() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: markAttendance,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['attendance'] });
    },
  });
}
