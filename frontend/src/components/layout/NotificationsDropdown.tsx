import { useState, useRef, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Bell } from 'lucide-react';

export interface NotificationItem {
  id: string;
  title: string;
  detail: string;
  time: string;
  unread?: boolean;
}

interface NotificationsDropdownProps {
  items: NotificationItem[];
  onItemClick?: (id: string) => void;
  onMarkAllRead?: () => void;
}

export function NotificationsDropdown({ items, onItemClick, onMarkAllRead }: NotificationsDropdownProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const unreadCount = items.filter((i) => i.unread).length;

  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((o) => !o)}
        aria-label="Notifications"
        className="relative grid h-9 w-9 place-items-center rounded-xl border border-border-subtle bg-raised text-text-secondary hover:text-text-primary"
      >
        <Bell size={16} />
        {unreadCount > 0 && (
          <span className="absolute -right-1 -top-1 grid h-4 w-4 place-items-center rounded-full bg-rose-500 text-[10px] font-semibold text-white">
            {unreadCount}
          </span>
        )}
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -6, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.98 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 top-11 z-40 w-80 overflow-hidden rounded-2xl border border-border-subtle bg-overlay shadow-2xl"
          >
            <div className="flex items-center justify-between border-b border-border-subtle px-4 py-3">
              <p className="text-sm font-semibold text-text-primary">Notifications</p>
              {onMarkAllRead && unreadCount > 0 ? (
                <button onClick={onMarkAllRead} className="text-xs font-medium text-brand-500 hover:underline">
                  Mark all read
                </button>
              ) : (
                <span className="text-xs text-text-muted">{unreadCount} new</span>
              )}
            </div>
            <div className="scroll-thin max-h-80 overflow-y-auto">
              {items.length === 0 ? (
                <p className="px-4 py-8 text-center text-sm text-text-muted">You're all caught up.</p>
              ) : (
                items.map((n) => (
                  <div
                    key={n.id}
                    onClick={() => onItemClick?.(n.id)}
                    className="flex cursor-pointer gap-3 border-b border-border-subtle px-4 py-3 last:border-0 hover:bg-sunken/60"
                  >
                    <span className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${n.unread ? 'bg-brand-500' : 'bg-transparent'}`} />
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-text-primary">{n.title}</p>
                      <p className="truncate text-xs text-text-muted">{n.detail}</p>
                      <p className="mt-0.5 text-[11px] text-text-muted">{n.time}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
