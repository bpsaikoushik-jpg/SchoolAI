import api from './api';
import type { SchoolClass, Subject, Enrollment } from '../types/academic';

export async function fetchClassesBySchool(schoolId: string): Promise<SchoolClass[]> {
  const { data } = await api.get<SchoolClass[]>(`/academic/classes/school/${schoolId}`);
  return data;
}

export async function fetchClass(classId: string): Promise<SchoolClass> {
  const { data } = await api.get<SchoolClass>(`/academic/classes/${classId}`);
  return data;
}

export async function createClass(payload: { name: string; school_id: string }): Promise<SchoolClass> {
  const { data } = await api.post<SchoolClass>('/academic/classes', payload);
  return data;
}

export async function updateClass(classId: string, payload: { name?: string }): Promise<SchoolClass> {
  const { data } = await api.patch<SchoolClass>(`/academic/classes/${classId}`, payload);
  return data;
}

export async function deleteClass(classId: string): Promise<void> {
  await api.delete(`/academic/classes/${classId}`);
}

export async function fetchSubjectsByTeacher(teacherId: string): Promise<Subject[]> {
  const { data } = await api.get<Subject[]>(`/academic/subjects/teacher/${teacherId}`);
  return data;
}

export async function fetchSubjectsByClass(classId: string): Promise<Subject[]> {
  const { data } = await api.get<Subject[]>(`/academic/subjects/class/${classId}`);
  return data;
}

export async function fetchMySubjects(): Promise<Subject[]> {
  const { data } = await api.get<Subject[]>('/academic/subjects/me');
  return data;
}

export async function fetchSubjectsByStudent(studentId?: string): Promise<Subject[]> {
  const { data } = await api.get<Subject[]>('/academic/subjects/student', {
    params: { student_id: studentId },
  });
  return data;
}

export interface TeacherContact {
  subject_id: string;
  subject_name: string;
  teacher_id: string | null;
  teacher_name: string | null;
  specialization: string | null;
}

export async function fetchTeacherDirectoryByStudent(studentId?: string): Promise<TeacherContact[]> {
  const { data } = await api.get<TeacherContact[]>('/academic/teachers/student', {
    params: { student_id: studentId },
  });
  return data;
}

export async function createSubject(payload: { name: string; teacher_id?: string }): Promise<Subject> {
  const { data } = await api.post<Subject>('/academic/subjects', payload);
  return data;
}

export async function fetchMyEnrollments(): Promise<Enrollment[]> {
  const { data } = await api.get<Enrollment[]>('/academic/enrollments/me');
  return data;
}

export async function fetchEnrollmentsByClass(classId: string): Promise<Enrollment[]> {
  const { data } = await api.get<Enrollment[]>(`/academic/enrollments/class/${classId}`);
  return data;
}

export async function enrollStudent(payload: { student_id: string; class_id: string }): Promise<Enrollment> {
  const { data } = await api.post<Enrollment>('/academic/enrollments', payload);
  return data;
}

export async function fetchEnrollmentsByStudent(studentId?: string): Promise<Enrollment[]> {
  const { data } = await api.get<Enrollment[]>('/academic/enrollments/student', {
    params: { student_id: studentId },
  });
  return data;
}

export async function deleteEnrollment(enrollmentId: string): Promise<void> {
  await api.delete(`/academic/enrollments/${enrollmentId}`);
}
