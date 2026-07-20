import { Moon, Sun } from 'lucide-react';
import { useThemeStore } from '../../store/useThemeStore';

export function ThemeToggle() {
  const { theme, toggleTheme } = useThemeStore();
  const isDark = theme === 'dark';

  return (
    <button
      onClick={toggleTheme}
      aria-label="Toggle theme"
      className="relative grid h-9 w-9 place-items-center rounded-xl border border-border-subtle bg-raised text-text-secondary transition-colors hover:text-text-primary"
    >
      {isDark ? <Sun size={16} /> : <Moon size={16} />}
    </button>
  );
}
