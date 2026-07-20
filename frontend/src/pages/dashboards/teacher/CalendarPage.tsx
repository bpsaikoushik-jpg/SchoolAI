import { useState } from 'react';
import { Card, Badge, Button, Dialog, Input, Select } from '../../../components/ui';
import { useMyCalendarToday, useCreateCalendarEvent } from '../../../hooks/useTeacherInsights';
import type { CalendarEventType } from '../../../types/teacher';

const EVENT_TYPE_OPTIONS: { value: CalendarEventType; label: string }[] = [
  { value: 'class', label: 'Class' },
  { value: 'meeting', label: 'Meeting' },
  { value: 'task', label: 'Task' },
  { value: 'other', label: 'Other' },
];

function toLocalInputValue(date: Date) {
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function CalendarPage() {
  const { data: calendarToday } = useMyCalendarToday();
  const createEvent = useCreateCalendarEvent();
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [type, setType] = useState<CalendarEventType>('task');
  const [startsAt, setStartsAt] = useState(() => toLocalInputValue(new Date()));

  const events = [...(calendarToday ?? [])].sort(
    (a, b) => new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime()
  );
  const formatTime = (iso: string) => new Date(iso).toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });

  function handleCreate() {
    if (!title.trim()) return;
    createEvent.mutate(
      { title: title.trim(), event_type: type, starts_at: new Date(startsAt).toISOString() },
      { onSuccess: () => { setOpen(false); setTitle(''); setType('task'); setStartsAt(toLocalInputValue(new Date())); } }
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Calendar</h1>
          <p className="text-sm text-text-muted">Today's schedule.</p>
        </div>
        <Button onClick={() => setOpen(true)}>Add event</Button>
      </div>
      <Card>
        {events.length === 0 ? (
          <p className="py-6 text-center text-sm text-text-muted">Nothing scheduled for today.</p>
        ) : (
          <div className="space-y-4">
            {events.map((e) => (
              <div key={e.id} className="flex items-center gap-4 border-b border-border-subtle pb-4 last:border-0 last:pb-0">
                <span className="w-20 shrink-0 text-sm font-medium text-text-secondary">{formatTime(e.starts_at)}</span>
                <span className="flex-1 text-sm text-text-primary">{e.title}</span>
                <Badge tone={e.event_type === 'class' ? 'info' : e.event_type === 'meeting' ? 'warning' : 'neutral'}>{e.event_type}</Badge>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        title="Add calendar event"
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
            <Button onClick={handleCreate} isLoading={createEvent.isPending}>Save</Button>
          </div>
        }
      >
        <div className="space-y-4">
          <Input label="Title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Grade quiz submissions" />
          <Select label="Type" value={type} onChange={(e) => setType(e.target.value as CalendarEventType)} options={EVENT_TYPE_OPTIONS} />
          <Input label="Starts at" type="datetime-local" value={startsAt} onChange={(e) => setStartsAt(e.target.value)} />
        </div>
      </Dialog>
    </div>
  );
}
