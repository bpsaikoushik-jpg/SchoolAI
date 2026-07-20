import { useMemo, useState } from 'react';
import { Card, CardHeader, Badge, FullPageSpinner, EmptyState, ErrorState } from '../../../components/ui';
import { ChevronLeft, ChevronRight, CalendarDays } from 'lucide-react';
import { useSelectedChild } from '../../../hooks/useParent';
import { useStudentCalendarEvents } from '../../../hooks/useCalendar';
import type { CalendarEventType } from '../../../types/teacher';
import { ChildSwitcher } from './ChildSwitcher';

const TYPE_TONE: Record<CalendarEventType, 'info' | 'warning' | 'success' | 'neutral'> = {
  class: 'info',
  meeting: 'warning',
  task: 'success',
  other: 'neutral',
};

function startOfMonth(d: Date) {
  return new Date(d.getFullYear(), d.getMonth(), 1);
}
function endOfMonth(d: Date) {
  return new Date(d.getFullYear(), d.getMonth() + 1, 0, 23, 59, 59);
}

export function CalendarPage() {
  const { children, selectedChild, selectedChildId, isLoading: loadingChildren } = useSelectedChild();
  const [cursor, setCursor] = useState(() => new Date());

  const rangeStart = startOfMonth(cursor);
  const rangeEnd = endOfMonth(cursor);
  const { data: events, isLoading, isError, refetch } = useStudentCalendarEvents(
    selectedChildId ?? undefined,
    rangeStart.toISOString(),
    rangeEnd.toISOString(),
  );

  const grouped = useMemo(() => {
    const byDay = new Map<string, typeof events>();
    for (const e of events ?? []) {
      const key = new Date(e.starts_at).toDateString();
      const list = byDay.get(key) ?? [];
      list.push(e);
      byDay.set(key, list as any);
    }
    return [...byDay.entries()].sort(
      (a, b) => new Date(a[0]).getTime() - new Date(b[0]).getTime(),
    );
  }, [events]);

  if (loadingChildren) return <FullPageSpinner label="Loading your children…" />;
  if (children.length === 0) {
    return <EmptyState title="No children linked to your account yet" description="Once the school links your account to your child's profile, their calendar will appear here." />;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Calendar</h1>
          <p className="text-sm text-text-muted">Classes, meetings and tasks for {selectedChild?.full_name ?? 'your child'}.</p>
        </div>
        <ChildSwitcher />
      </div>

      <Card>
        <CardHeader
          title={cursor.toLocaleString(undefined, { month: 'long', year: 'numeric' })}
          action={
            <div className="flex items-center gap-1">
              <button
                className="grid h-8 w-8 place-items-center rounded-lg border border-border-subtle text-text-muted hover:bg-sunken"
                onClick={() => setCursor(new Date(cursor.getFullYear(), cursor.getMonth() - 1, 1))}
              >
                <ChevronLeft size={16} />
              </button>
              <button
                className="grid h-8 w-8 place-items-center rounded-lg border border-border-subtle text-text-muted hover:bg-sunken"
                onClick={() => setCursor(new Date(cursor.getFullYear(), cursor.getMonth() + 1, 1))}
              >
                <ChevronRight size={16} />
              </button>
            </div>
          }
        />

        {isLoading ? (
          <p className="py-8 text-center text-sm text-text-muted">Loading calendar…</p>
        ) : isError ? (
          <ErrorState description="Couldn't load the calendar right now." onRetry={() => refetch()} />
        ) : grouped.length === 0 ? (
          <p className="py-8 text-center text-sm text-text-muted">No events scheduled this month.</p>
        ) : (
          <div className="space-y-5">
            {grouped.map(([day, dayEvents]) => (
              <div key={day}>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-text-muted">
                  {new Date(day).toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' })}
                </p>
                <div className="space-y-2">
                  {dayEvents!.map((e) => (
                    <div key={e.id} className="flex items-center justify-between rounded-xl border border-border-subtle p-3">
                      <div className="flex items-center gap-3">
                        <div className="grid h-9 w-9 place-items-center rounded-lg text-white" style={{ background: 'var(--color-role-parent)' }}>
                          <CalendarDays size={16} />
                        </div>
                        <div>
                          <p className="font-medium text-text-primary">{e.title}</p>
                          <p className="text-xs text-text-muted">
                            {new Date(e.starts_at).toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })}
                            {e.ends_at ? ` – ${new Date(e.ends_at).toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })}` : ''}
                            {e.description ? ` · ${e.description}` : ''}
                          </p>
                        </div>
                      </div>
                      <Badge tone={TYPE_TONE[e.event_type]}>{e.event_type}</Badge>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
