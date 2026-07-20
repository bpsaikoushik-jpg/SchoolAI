import React from 'react';
import { Search, SlidersHorizontal } from 'lucide-react';
import { cn } from '../../utils/cn';

interface FilterBarProps {
  searchValue?: string;
  onSearchChange?: (value: string) => void;
  searchPlaceholder?: string;
  children?: React.ReactNode; // extra filter selects/pills
  className?: string;
}

export function FilterBar({ searchValue, onSearchChange, searchPlaceholder = 'Search…', children, className }: FilterBarProps) {
  return (
    <div className={cn('flex flex-wrap items-center gap-3 rounded-xl border border-border-subtle bg-raised p-3', className)}>
      {onSearchChange && (
        <div className="relative min-w-[200px] flex-1">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
          <input
            value={searchValue}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder={searchPlaceholder}
            className="w-full rounded-lg bg-sunken py-2 pl-8 pr-3 text-sm text-text-primary outline-none placeholder:text-text-muted focus:ring-2 focus:ring-brand-500/20"
          />
        </div>
      )}
      {children && <div className="flex flex-wrap items-center gap-2">{children}</div>}
      <SlidersHorizontal size={15} className="ml-auto text-text-muted shrink-0" />
    </div>
  );
}
