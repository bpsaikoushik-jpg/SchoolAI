import { Card, Badge, FullPageSpinner, EmptyState, ErrorState } from '../../../components/ui';
import { useSelectedChild } from '../../../hooks/useParent';
import { useStudentHomework, useStudentSubmissions } from '../../../hooks/useHomework';
import { ChildSwitcher } from './ChildSwitcher';

export function HomeworkPage() {
  const { children, selectedChild, selectedChildId, isLoading: loadingChildren } = useSelectedChild();
  const { data: homework, isLoading, isError, refetch } = useStudentHomework(selectedChildId ?? undefined);
  const { data: submissions } = useStudentSubmissions(selectedChildId ?? undefined);

  if (loadingChildren) return <FullPageSpinner label="Loading your children…" />;
  if (children.length === 0) {
    return <EmptyState title="No children linked to your account yet" description="Once the school links your account to your child's profile, their homework will appear here." />;
  }

  const submittedIds = new Set((submissions ?? []).map((s) => s.homework_id));
  const sorted = [...(homework ?? [])].sort((a, b) => {
    if (!a.due_date) return 1;
    if (!b.due_date) return -1;
    return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Homework</h1>
          <p className="text-sm text-text-muted">What's currently assigned to {selectedChild?.full_name ?? 'your child'}.</p>
        </div>
        <ChildSwitcher />
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12"><FullPageSpinner label="Loading homework…" /></div>
      ) : isError ? (
        <ErrorState description="Couldn't load homework right now." onRetry={() => refetch()} />
      ) : sorted.length === 0 ? (
        <Card className="py-10 text-center text-sm text-text-muted">Nothing assigned right now.</Card>
      ) : (
        <div className="space-y-3">
          {sorted.map((hw) => {
            const submitted = submittedIds.has(hw.id);
            return (
              <Card key={hw.id} className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-text-primary">{hw.title}</p>
                  <p className="text-sm text-text-muted">
                    {hw.description ? `${hw.description} · ` : ''}
                    Due {hw.due_date ? new Date(hw.due_date).toLocaleDateString() : 'No due date'}
                  </p>
                </div>
                <Badge tone={submitted ? 'success' : 'warning'}>{submitted ? 'Submitted' : 'Pending'}</Badge>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
