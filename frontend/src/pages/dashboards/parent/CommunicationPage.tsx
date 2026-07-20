import { Card, CardHeader, Badge, Avatar, FullPageSpinner, EmptyState } from '../../../components/ui';
import { Bell, GraduationCap } from 'lucide-react';
import { useSelectedChild } from '../../../hooks/useParent';
import { useTeacherDirectoryByStudent } from '../../../hooks/useAcademic';
import { useNotifications, useMarkNotificationRead } from '../../../hooks/useNotifications';
import { timeAgo } from '../../../utils/time';
import { ChildSwitcher } from './ChildSwitcher';

export function CommunicationPage() {
  const { children, selectedChild, selectedChildId, isLoading: loadingChildren } = useSelectedChild();
  const { data: teachers, isLoading: loadingTeachers } = useTeacherDirectoryByStudent(selectedChildId);
  const { data: notifications, isLoading: loadingNotifications } = useNotifications();
  const markRead = useMarkNotificationRead();

  if (loadingChildren) return <FullPageSpinner label="Loading your children…" />;
  if (children.length === 0) {
    return <EmptyState title="No children linked to your account yet" description="Once the school links your account to your child's profile, communication tools will appear here." />;
  }

  const academicUpdates = (notifications ?? []).filter((n) => n.type === 'academic' || n.type === null);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Communication</h1>
          <p className="text-sm text-text-muted">Updates from school and {selectedChild?.full_name ?? 'your child'}'s teachers.</p>
        </div>
        <ChildSwitcher />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="Recent updates" subtitle="Homework, exam results and school notices" />
          {loadingNotifications ? (
            <p className="py-8 text-center text-sm text-text-muted">Loading updates…</p>
          ) : academicUpdates.length === 0 ? (
            <p className="py-8 text-center text-sm text-text-muted">No updates yet — you're all caught up.</p>
          ) : (
            <div className="space-y-2">
              {academicUpdates.map((n) => (
                <button
                  key={n.id}
                  onClick={() => !n.is_read && markRead.mutate(n.id)}
                  className="flex w-full items-start gap-3 rounded-xl border border-border-subtle p-3 text-left transition-colors hover:bg-sunken"
                >
                  <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg text-white" style={{ background: 'var(--color-role-parent)' }}>
                    <Bell size={15} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="truncate font-medium text-text-primary">{n.title}</p>
                      {!n.is_read && <span className="h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: 'var(--color-role-parent)' }} />}
                    </div>
                    <p className="text-sm text-text-muted">{n.message}</p>
                    <p className="mt-0.5 text-xs text-text-muted">{timeAgo(n.created_at)}</p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </Card>

        <Card>
          <CardHeader title="Class teachers" subtitle="Who's teaching this term" />
          {loadingTeachers ? (
            <p className="py-8 text-center text-sm text-text-muted">Loading teachers…</p>
          ) : !teachers || teachers.length === 0 ? (
            <p className="py-8 text-center text-sm text-text-muted">No subjects enrolled yet.</p>
          ) : (
            <div className="space-y-3">
              {teachers.map((t) => (
                <div key={t.subject_id} className="flex items-center gap-3">
                  <Avatar name={t.teacher_name ?? t.subject_name} />
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-text-primary">{t.teacher_name ?? 'Not yet assigned'}</p>
                    <p className="truncate text-xs text-text-muted">{t.subject_name}{t.specialization ? ` · ${t.specialization}` : ''}</p>
                  </div>
                  {!t.teacher_id && <Badge tone="neutral">Unassigned</Badge>}
                </div>
              ))}
            </div>
          )}
          <div className="mt-4 flex items-center gap-2 rounded-xl bg-sunken p-3 text-xs text-text-muted">
            <GraduationCap size={14} className="shrink-0" />
            Direct messaging isn't available yet — for anything urgent, please contact the school office.
          </div>
        </Card>
      </div>
    </div>
  );
}
