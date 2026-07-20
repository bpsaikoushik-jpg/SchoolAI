import { Card } from '../../components/ui';
import { useNotifications, useMarkNotificationRead, useMarkAllNotificationsRead } from '../../hooks/useNotifications';
import { timeAgo } from '../../utils/time';

interface SharedNotificationsPageProps {
  title: string;
  subtitle: string;
  accentVar: string; // e.g. '--color-role-parent'
}

export function SharedNotificationsPage({ title, subtitle, accentVar }: SharedNotificationsPageProps) {
  const { data: notifications, isLoading, isError } = useNotifications();
  const markRead = useMarkNotificationRead();
  const markAllRead = useMarkAllNotificationsRead();

  const unreadCount = (notifications ?? []).filter((n) => !n.is_read).length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">{title}</h1>
          <p className="text-sm text-text-muted">{subtitle}</p>
        </div>
        {unreadCount > 0 && (
          <button
            onClick={() => markAllRead.mutate()}
            className="text-sm font-medium text-brand-500 hover:underline"
          >
            Mark all read
          </button>
        )}
      </div>
      <Card padded={false}>
        {isLoading ? (
          <p className="px-5 py-8 text-center text-sm text-text-muted">Loading notifications…</p>
        ) : isError ? (
          <p className="px-5 py-8 text-center text-sm text-rose-500">Couldn't load notifications. Try again later.</p>
        ) : (notifications ?? []).length === 0 ? (
          <p className="px-5 py-8 text-center text-sm text-text-muted">You're all caught up.</p>
        ) : (
          notifications!.map((n) => (
            <div
              key={n.id}
              onClick={() => !n.is_read && markRead.mutate(n.id)}
              className="flex cursor-pointer gap-3 border-b border-border-subtle px-5 py-4 last:border-0 hover:bg-sunken/40"
            >
              <span
                className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full"
                style={{ background: n.is_read ? 'transparent' : `var(${accentVar})` }}
              />
              <div>
                <p className="text-sm font-medium text-text-primary">{n.title}</p>
                <p className="text-sm text-text-muted">{n.message}</p>
                <p className="mt-1 text-xs text-text-muted">{timeAgo(n.created_at)}</p>
              </div>
            </div>
          ))
        )}
      </Card>
    </div>
  );
}
