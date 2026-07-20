import api from './api';
import type { ChildSummary, AISummaryResponse } from '../types/parent';

export async function fetchChildren(): Promise<ChildSummary[]> {
  const { data } = await api.get<ChildSummary[]>('/parent/children');
  return data;
}

export async function fetchAiSummary(studentId?: string): Promise<AISummaryResponse> {
  const { data } = await api.get<AISummaryResponse>('/parent/ai-summary', {
    params: { student_id: studentId },
  });
  return data;
}
