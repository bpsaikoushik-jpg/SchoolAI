import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchMyClasses, fetchAttendanceToday, fetchHomeworkQueue, fetchMyCalendarToday, fetchMyStudents, createCalendarEvent } from '../services/teacher.service';

export function useCreateCalendarEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createCalendarEvent,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['calendar'] }),
  });
}

export function useMyStudents() {
  return useQuery({ queryKey: ['teacher-insights', 'my-students'], queryFn: fetchMyStudents });
}

export function useMyClasses() {
  return useQuery({ queryKey: ['teacher-insights', 'my-classes'], queryFn: fetchMyClasses });
}

export function useAttendanceToday() {
  return useQuery({ queryKey: ['teacher-insights', 'attendance-today'], queryFn: fetchAttendanceToday });
}

export function useHomeworkQueue(limit = 10) {
  return useQuery({ queryKey: ['teacher-insights', 'homework-queue', limit], queryFn: () => fetchHomeworkQueue(limit) });
}

export function useMyCalendarToday() {
  return useQuery({ queryKey: ['calendar', 'me', 'today'], queryFn: fetchMyCalendarToday });
}
