import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { Footer } from './Footer';
import type { RoleConfig } from '../../lib/roles';
import { useNotifications, useMarkNotificationRead, useMarkAllNotificationsRead } from '../../hooks/useNotifications';
import { timeAgo } from '../../utils/time';
import type { NotificationItem } from './NotificationsDropdown';

// Shared shell used by every portal: Sidebar + Topbar + content + Footer.
// Each role route wraps its subtree with this, passing its own RoleConfig
// (nav items, base path, accent color) so the chrome stays identical while
// feeling like a distinct portal.
export function DashboardLayout({ config }: { config: RoleConfig }) {
  const { data: notifications } = useNotifications();
  const markRead = useMarkNotificationRead();
  const markAllRead = useMarkAllNotificationsRead();

  const items: NotificationItem[] = (notifications ?? []).map((n) => ({
    id: n.id,
    title: n.title,
    detail: n.message,
    time: timeAgo(n.created_at),
    unread: !n.is_read,
  }));

  return (
    <div className="flex min-h-screen bg-canvas">
      <Sidebar config={config} />
      <div className="flex min-h-screen flex-1 flex-col">
        <Topbar
          config={config}
          notifications={items}
          onNotificationClick={(id) => markRead.mutate(id)}
          onMarkAllRead={() => markAllRead.mutate()}
        />
        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
          <Outlet />
        </main>
        <Footer />
      </div>
    </div>
  );
}
