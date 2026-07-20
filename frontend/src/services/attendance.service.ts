import api from './api';
import type { AttendanceRecord, AttendanceStatus } from '../types/academic';

export async function fetchStudentAttendance(params?: {
  studentId?: string;
  start?: string;
  end?: string;
}): Promise<AttendanceRecord[]> {
  const { data } = await api.get<AttendanceRecord[]>('/attendance/student', {
    params: {
      student_id: params?.studentId,
      start: params?.start,
      end: params?.end,
    },
  });
  return data;
}

export async function fetchClassAttendance(classId: string, start?: string, end?: string): Promise<AttendanceRecord[]> {
  const { data } = await api.get<AttendanceRecord[]>(`/attendance/class/${classId}`, {
    params: { start, end },
  });
  return data;
}

export async function markAttendance(payload: {
  student_id: string;
  date: string;
  status: AttendanceStatus;
}): Promise<AttendanceRecord> {
  const { data } = await api.post<AttendanceRecord>('/attendance', payload);
  return data;
}

export function summarizeAttendance(records: AttendanceRecord[]) {
  const total = records.length;
  const counts = { present: 0, absent: 0, late: 0 };
  for (const r of records) counts[r.status] += 1;
  const pct = (n: number) => (total === 0 ? 0 : Math.round((n / total) * 100));
  return {
    present: pct(counts.present),
    absent: pct(counts.absent),
    late: pct(counts.late),
    total,
  };
}
