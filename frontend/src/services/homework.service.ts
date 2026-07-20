import api from './api';
import type { Homework, AssignmentSubmission } from '../types/academic';

export async function fetchMyHomework(): Promise<Homework[]> {
  const { data } = await api.get<Homework[]>('/homework/me');
  return data;
}

export async function fetchHomeworkForStudent(studentId?: string): Promise<Homework[]> {
  const { data } = await api.get<Homework[]>('/homework/student', {
    params: { student_id: studentId },
  });
  return data;
}

export async function fetchHomeworkByClass(classId: string): Promise<Homework[]> {
  const { data } = await api.get<Homework[]>(`/homework/class/${classId}`);
  return data;
}

export async function createHomework(payload: {
  class_id: string;
  title: string;
  description?: string;
  due_date?: string;
}): Promise<Homework> {
  const { data } = await api.post<Homework>('/homework', payload);
  return data;
}

export async function updateHomework(id: string, payload: Partial<{ title: string; description: string; due_date: string }>): Promise<Homework> {
  const { data } = await api.patch<Homework>(`/homework/${id}`, payload);
  return data;
}

export async function deleteHomework(id: string): Promise<void> {
  await api.delete(`/homework/${id}`);
}

export async function submitHomework(payload: { homework_id: string; student_id: string; content?: string }): Promise<AssignmentSubmission> {
  const { data } = await api.post<AssignmentSubmission>('/homework/submissions', payload);
  return data;
}

export async function fetchMySubmissions(): Promise<AssignmentSubmission[]> {
  const { data } = await api.get<AssignmentSubmission[]>('/homework/submissions/me');
  return data;
}

export async function fetchSubmissionsForStudent(studentId?: string): Promise<AssignmentSubmission[]> {
  const { data } = await api.get<AssignmentSubmission[]>('/homework/submissions/student', {
    params: { student_id: studentId },
  });
  return data;
}

export async function fetchSubmissionsForHomework(homeworkId: string): Promise<AssignmentSubmission[]> {
  const { data } = await api.get<AssignmentSubmission[]>(`/homework/submissions/homework/${homeworkId}`);
  return data;
}

export async function gradeSubmission(id: string, grade: string): Promise<AssignmentSubmission> {
  const { data } = await api.patch<AssignmentSubmission>(`/homework/submissions/${id}/grade`, { grade });
  return data;
}
