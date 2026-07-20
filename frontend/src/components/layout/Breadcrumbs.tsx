import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

function titleCase(segment: string) {
  return segment
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

export function Breadcrumbs({ basePath, rootLabel }: { basePath: string; rootLabel: string }) {
  const { pathname } = useLocation();
  const rest = pathname.replace(basePath, '').split('/').filter(Boolean);

  return (
    <nav className="flex items-center gap-1.5 text-sm text-text-muted">
      <Link to={basePath} className="flex items-center gap-1 hover:text-text-primary">
        <Home size={13} /> {rootLabel}
      </Link>
      {rest.map((seg, i) => {
        const path = `${basePath}/${rest.slice(0, i + 1).join('/')}`;
        const isLast = i === rest.length - 1;
        return (
          <span key={path} className="flex items-center gap-1.5">
            <ChevronRight size={13} />
            {isLast ? (
              <span className="font-medium text-text-primary">{titleCase(seg)}</span>
            ) : (
              <Link to={path} className="hover:text-text-primary">{titleCase(seg)}</Link>
            )}
          </span>
        );
      })}
    </nav>
  );
}
