import { Menu } from 'lucide-react';
import { useUIStore } from '../../store/useUIStore';
import { SearchBar } from './SearchBar';
import { NotificationsDropdown, type NotificationItem } from './NotificationsDropdown';
import { ThemeToggle } from './ThemeToggle';
import { UserMenu } from './UserMenu';
import { Breadcrumbs } from './Breadcrumbs';
import type { RoleConfig } from '../../lib/roles';

interface TopbarProps {
  config: RoleConfig;
  notifications: NotificationItem[];
  onNotificationClick?: (id: string) => void;
  onMarkAllRead?: () => void;
}

export function Topbar({ config, notifications, onNotificationClick, onMarkAllRead }: TopbarProps) {
  const openMobileSidebar = useUIStore((s) => s.openMobileSidebar);
  const accent = `var(${config.accentVar})`;

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-border-subtle bg-raised/80 px-4 backdrop-blur-md sm:px-6">
      <button
        onClick={openMobileSidebar}
        aria-label="Open menu"
        className="grid h-9 w-9 shrink-0 place-items-center rounded-xl border border-border-subtle text-text-secondary lg:hidden"
      >
        <Menu size={17} />
      </button>
      <div className="hidden lg:block">
        <Breadcrumbs basePath={config.basePath} rootLabel={config.label} />
      </div>
      <SearchBar />
      <div className="ml-auto flex items-center gap-2 sm:gap-3">
        <ThemeToggle />
        <NotificationsDropdown items={notifications} onItemClick={onNotificationClick} onMarkAllRead={onMarkAllRead} />
        <div className="h-6 w-px bg-border-subtle" />
        <UserMenu accentColor={accent} />
      </div>
    </header>
  );
}
