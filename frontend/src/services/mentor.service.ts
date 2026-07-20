import api from './api';

export interface MentorChatRequest {
  student_id?: string;
  message: string;
  subject?: string;
  subject_id?: string;
  topic?: string;
  mode?: 'easy' | 'normal' | 'advanced';
}

export interface MentorChatResponse {
  response: string;
  provider: string;
  model: string;
  subject?: string | null;
  subject_id?: string | null;
  topic?: string | null;
}

export async function sendMentorChat(payload: MentorChatRequest): Promise<MentorChatResponse> {
  const { data } = await api.post<MentorChatResponse>('/mentor/chat', payload);
  return data;
}
