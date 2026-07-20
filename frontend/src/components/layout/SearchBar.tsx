import { Search } from 'lucide-react';
import { useState } from 'react';

export function SearchBar() {
  const [value, setValue] = useState('');

  return (
    <div className="relative hidden w-full max-w-sm md:block">
      <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Search students, classes, reports…"
        className="w-full rounded-xl border border-border-subtle bg-sunken py-2 pl-9 pr-3 text-sm text-text-primary outline-none placeholder:text-text-muted transition-colors focus:border-brand-500 focus:ring-2 focus:ring-brand-500/15"
      />
      <kbd className="absolute right-2.5 top-1/2 -translate-y-1/2 rounded border border-border-strong px-1.5 py-0.5 text-[10px] text-text-muted">/</kbd>
    </div>
  );
}
