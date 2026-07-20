import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '../../utils/cn';

interface PaginationProps {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ page, totalPages, onPageChange }: PaginationProps) {
  if (totalPages <= 1) return null;

  const pages = Array.from({ length: totalPages }, (_, i) => i + 1).filter(
    (p) => p === 1 || p === totalPages || Math.abs(p - page) <= 1
  );

  return (
    <div className="flex items-center justify-between pt-4">
      <p className="text-xs text-text-muted">Page {page} of {totalPages}</p>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onPageChange(Math.max(1, page - 1))}
          disabled={page === 1}
          className="grid h-8 w-8 place-items-center rounded-lg text-text-secondary hover:bg-sunken disabled:opacity-30"
        >
          <ChevronLeft size={16} />
        </button>
        {pages.map((p, i) => (
          <React.Fragment key={p}>
            {i > 0 && pages[i - 1] !== p - 1 && <span className="px-1 text-text-muted">…</span>}
            <button
              onClick={() => onPageChange(p)}
              className={cn(
                'h-8 min-w-8 rounded-lg px-2 text-sm font-medium',
                p === page ? 'bg-brand-600 text-white' : 'text-text-secondary hover:bg-sunken'
              )}
            >
              {p}
            </button>
          </React.Fragment>
        ))}
        <button
          onClick={() => onPageChange(Math.min(totalPages, page + 1))}
          disabled={page === totalPages}
          className="grid h-8 w-8 place-items-center rounded-lg text-text-secondary hover:bg-sunken disabled:opacity-30"
        >
          <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}

