import { useQuery } from '@tanstack/react-query';
import { fetchStudentCalendarEvents } from '../services/calendar.service';

export function useStudentCalendarEvents(studentId: string | undefined, start?: string, end?: string) {
  return useQuery({
    queryKey: ['calendar', 'student', studentId, start, end],
    queryFn: () => fetchStudentCalendarEvents({ studentId, start, end }),
    enabled: !!studentId,
  });
}
