import api from './api';
import type { CalendarEvent } from '../types/teacher';

export async function fetchStudentCalendarEvents(params?: {
  studentId?: string;
  start?: string;
  end?: string;
}): Promise<CalendarEvent[]> {
  const { data } = await api.get<CalendarEvent[]>('/calendar/student', {
    params: {
      student_id: params?.studentId,
      start: params?.start,
      end: params?.end,
    },
  });
  return data;
}
