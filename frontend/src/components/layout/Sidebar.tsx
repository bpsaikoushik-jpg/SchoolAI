import { NavLink } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { ChevronsLeft, ChevronsRight, X, Sparkles } from 'lucide-react';
import { cn } from '../../utils/cn';
import { useUIStore } from '../../store/useUIStore';
import type { RoleConfig } from '../../lib/roles';

interface SidebarProps {
  config: RoleConfig;
}

function NavList({ config, onNavigate }: { config: RoleConfig; onNavigate?: () => void }) {
  return (
    <nav className="flex-1 space-y-1 overflow-y-auto scroll-thin px-3 py-4">
      {config.nav.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          end={item.path === config.basePath}
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors',
              isActive
                ? 'text-white'
                : 'text-text-secondary hover:bg-sunken hover:text-text-primary'
            )
          }
          style={({ isActive }) => (isActive ? { background: `var(${config.accentVar})` } : undefined)}
        >
          <item.icon size={18} />
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}

export function Sidebar({ config }: SidebarProps) {
  const { sidebarCollapsed, toggleSidebarCollapsed, mobileSidebarOpen, closeMobileSidebar } = useUIStore();

  return (
    <>
      {/* Desktop sidebar */}
      <aside
        className={cn(
          'sticky top-0 hidden h-screen shrink-0 flex-col border-r border-border-subtle bg-raised transition-all duration-200 lg:flex',
          sidebarCollapsed ? 'w-[76px]' : 'w-64'
        )}
      >
        <div className="flex h-16 items-center gap-2.5 border-b border-border-subtle px-4">
          <div
            className="grid h-8 w-8 shrink-0 place-items-center rounded-lg text-white"
            style={{ background: `var(${config.accentVar})` }}
          >
            <Sparkles size={16} />
          </div>
          {!sidebarCollapsed && (
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-text-primary">SchoolAI</p>
              <p className="truncate text-[11px] text-text-muted">{config.label} Portal</p>
            </div>
          )}
        </div>
        <NavList config={config} />
        <button
          onClick={toggleSidebarCollapsed}
          className="flex items-center gap-2 border-t border-border-subtle px-4 py-3 text-xs text-text-muted hover:text-text-primary"
        >
          {sidebarCollapsed ? <ChevronsRight size={15} /> : <><ChevronsLeft size={15} /> Collapse</>}
        </button>
      </aside>

      {/* Mobile sidebar (drawer) */}
      <AnimatePresence>
        {mobileSidebarOpen && (
          <div className="fixed inset-0 z-50 lg:hidden">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/50"
              onClick={closeMobileSidebar}
            />
            <motion.aside
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'tween', duration: 0.22 }}
              className="relative flex h-full w-72 flex-col bg-raised shadow-2xl"
            >
              <div className="flex h-16 items-center justify-between border-b border-border-subtle px-4">
                <div className="flex items-center gap-2.5">
                  <div
                    className="grid h-8 w-8 place-items-center rounded-lg text-white"
                    style={{ background: `var(${config.accentVar})` }}
                  >
                    <Sparkles size={16} />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-text-primary">SchoolAI</p>
                    <p className="text-[11px] text-text-muted">{config.label} Portal</p>
                  </div>
                </div>
                <button onClick={closeMobileSidebar} aria-label="Close menu" className="grid h-8 w-8 place-items-center rounded-lg text-text-muted hover:bg-sunken">
                  <X size={16} />
                </button>
              </div>
              <NavList config={config} onNavigate={closeMobileSidebar} />
            </motion.aside>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}
