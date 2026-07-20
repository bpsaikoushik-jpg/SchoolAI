import api from './api';
import type { AppNotification } from '../types/academic';

export async function fetchNotifications(unreadOnly = false): Promise<AppNotification[]> {
  const { data } = await api.get<AppNotification[]>('/notifications', {
    params: { unread_only: unreadOnly },
  });
  return data;
}

export async function fetchUnreadCount(): Promise<number> {
  const { data } = await api.get<{ unread: number }>('/notifications/unread-count');
  return data.unread;
}

export async function markNotificationRead(id: string): Promise<number> {
  const { data } = await api.post<{ unread: number }>(`/notifications/${id}/read`);
  return data.unread;
}

export async function markAllNotificationsRead(): Promise<number> {
  const { data } = await api.post<{ unread: number }>('/notifications/read-all');
  return data.unread;
}

export async function deleteNotification(id: string): Promise<void> {
  await api.delete(`/notifications/${id}`);
}

export async function broadcastAnnouncement(payload: {
  user_ids: string[];
  title: string;
  message: string;
  type?: string;
}): Promise<number> {
  const { data } = await api.post<{ unread: number }>('/notifications/broadcast', payload);
  return data.unread;
}
