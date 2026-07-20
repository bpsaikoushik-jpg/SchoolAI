import api from './api';
import type { DailyProgress, Recommendation, ActivityEvent } from '../types/memory';

export async function fetchMyDailyProgress(limit = 7): Promise<DailyProgress[]> {
  const { data } = await api.get<DailyProgress[]>('/memory/daily-progress/me/list', { params: { limit } });
  return data;
}

export async function fetchMyRecentActivity(limit = 10): Promise<ActivityEvent[]> {
  const { data } = await api.get<ActivityEvent[]>('/memory/recent-activity/me/list', { params: { limit } });
  return data;
}

export async function fetchMyRecommendations(type?: string): Promise<Recommendation[]> {
  const { data } = await api.get<Recommendation[]>('/learning/recommendations/me/list', { params: type ? { type } : undefined });
  return data;
}
