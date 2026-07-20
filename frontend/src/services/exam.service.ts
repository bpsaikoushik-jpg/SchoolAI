import api from './api';
import type { Exam, ExamResult } from '../types/academic';

export async function fetchExamsBySubject(subjectId: string): Promise<Exam[]> {
  const { data } = await api.get<Exam[]>(`/exams/subject/${subjectId}`);
  return data;
}

export async function fetchMyUpcomingExams(): Promise<Exam[]> {
  const { data } = await api.get<Exam[]>('/exams/me/upcoming');
  return data;
}

export async function fetchUpcomingExamsForStudent(studentId?: string): Promise<Exam[]> {
  const { data } = await api.get<Exam[]>('/exams/student/upcoming', {
    params: { student_id: studentId },
  });
  return data;
}

export async function createExam(payload: { subject_id: string; title: string; date?: string }): Promise<Exam> {
  const { data } = await api.post<Exam>('/exams', payload);
  return data;
}

export interface ExamResultDetail {
  id: string;
  exam_id: string;
  student_id: string;
  score: number | null;
  remarks: string | null;
  exam_title: string;
  exam_date: string | null;
  subject_id: string;
  subject_name: string;
  created_at: string;
}

export async function fetchStudentResults(studentId?: string): Promise<ExamResult[]> {
  const { data } = await api.get<ExamResult[]>('/exams/results/student', {
    params: { student_id: studentId },
  });
  return data;
}

export async function fetchStudentResultsDetailed(studentId?: string): Promise<ExamResultDetail[]> {
  const { data } = await api.get<ExamResultDetail[]>('/exams/results/student/detailed', {
    params: { student_id: studentId },
  });
  return data;
}

export async function fetchResultsForExam(examId: string): Promise<ExamResult[]> {
  const { data } = await api.get<ExamResult[]>(`/exams/results/exam/${examId}`);
  return data;
}

export async function recordResult(payload: {
  exam_id: string;
  student_id: string;
  score?: number;
  remarks?: string;
}): Promise<ExamResult> {
  const { data } = await api.post<ExamResult>('/exams/results', payload);
  return data;
}
