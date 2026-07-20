import { useQuery } from '@tanstack/react-query';
import { fetchMyDailyProgress, fetchMyRecentActivity, fetchMyRecommendations } from '../services/memory.service';

export function useMyStudyHours(days = 7) {
  return useQuery({ queryKey: ['memory', 'daily-progress', 'me', days], queryFn: () => fetchMyDailyProgress(days) });
}

export function useMyRecentActivity(limit = 10) {
  return useQuery({ queryKey: ['memory', 'recent-activity', 'me', limit], queryFn: () => fetchMyRecentActivity(limit) });
}

export function useMyRecommendations(type?: string) {
  return useQuery({ queryKey: ['learning', 'recommendations', 'me', type], queryFn: () => fetchMyRecommendations(type) });
}
