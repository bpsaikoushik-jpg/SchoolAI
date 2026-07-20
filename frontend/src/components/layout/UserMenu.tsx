import { useState, useRef, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { LogOut, Settings, User as UserIcon, ChevronDown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/useAuthStore';
import { Avatar } from '../ui/Avatar';

export function UserMenu({ accentColor }: { accentColor: string }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();

  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  function handleLogout() {
    logout();
    navigate('/login', { replace: true });
  }

  return (
    <div className="relative" ref={ref}>
      <button onClick={() => setOpen((o) => !o)} className="flex items-center gap-2 rounded-xl py-1 pl-1 pr-2 hover:bg-sunken">
        <Avatar name={user?.full_name} size={32} ringColor={accentColor} />
        <div className="hidden text-left sm:block">
          <p className="text-sm font-medium leading-tight text-text-primary">{user?.full_name ?? 'Account'}</p>
          <p className="text-xs capitalize leading-tight text-text-muted">{user?.role}</p>
        </div>
        <ChevronDown size={14} className="text-text-muted" />
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -6, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.98 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 top-12 z-40 w-56 overflow-hidden rounded-2xl border border-border-subtle bg-overlay shadow-2xl"
          >
            <div className="border-b border-border-subtle px-4 py-3">
              <p className="truncate text-sm font-medium text-text-primary">{user?.email}</p>
            </div>
            <div className="p-1.5">
              <button className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-sm text-text-secondary hover:bg-sunken hover:text-text-primary">
                <UserIcon size={15} /> Profile
              </button>
              <button className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-sm text-text-secondary hover:bg-sunken hover:text-text-primary">
                <Settings size={15} /> Settings
              </button>
              <button
                onClick={handleLogout}
                className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-sm text-rose-500 hover:bg-rose-500/10"
              >
                <LogOut size={15} /> Log out
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
