import api from './api';
import type {
  TeacherClassSummary, AttendanceTodaySummary, HomeworkQueueItem,
  CalendarEvent, CalendarEventCreateInput, StudentRosterItem,
} from '../types/teacher';

export async function fetchMyStudents(): Promise<StudentRosterItem[]> {
  const { data } = await api.get<StudentRosterItem[]>('/teacher-insights/my-students');
  return data;
}

export async function fetchMyClasses(): Promise<TeacherClassSummary[]> {
  const { data } = await api.get<TeacherClassSummary[]>('/teacher-insights/my-classes');
  return data;
}

export async function fetchAttendanceToday(): Promise<AttendanceTodaySummary> {
  const { data } = await api.get<AttendanceTodaySummary>('/teacher-insights/attendance-today');
  return data;
}

export async function fetchHomeworkQueue(limit = 10): Promise<HomeworkQueueItem[]> {
  const { data } = await api.get<HomeworkQueueItem[]>('/teacher-insights/homework-queue', { params: { limit } });
  return data;
}

export async function fetchMyCalendarToday(): Promise<CalendarEvent[]> {
  const { data } = await api.get<CalendarEvent[]>('/calendar/me/today');
  return data;
}

export async function createCalendarEvent(input: CalendarEventCreateInput): Promise<CalendarEvent> {
  const { data } = await api.post<CalendarEvent>('/calendar', input);
  return data;
}
