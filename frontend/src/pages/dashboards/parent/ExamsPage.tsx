import { Card, Badge, FullPageSpinner, EmptyState, ErrorState } from '../../../components/ui';
import { GraduationCap } from 'lucide-react';
import { useSelectedChild } from '../../../hooks/useParent';
import { useStudentUpcomingExams } from '../../../hooks/useExams';
import { ChildSwitcher } from './ChildSwitcher';

export function ExamsPage() {
  const { children, selectedChild, selectedChildId, isLoading: loadingChildren } = useSelectedChild();
  const { data: exams, isLoading, isError, refetch } = useStudentUpcomingExams(selectedChildId ?? undefined);

  if (loadingChildren) return <FullPageSpinner label="Loading your children…" />;
  if (children.length === 0) {
    return <EmptyState title="No children linked to your account yet" description="Once the school links your account to your child's profile, their exams will appear here." />;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Exams</h1>
          <p className="text-sm text-text-muted">Upcoming exams for {selectedChild?.full_name ?? 'your child'}.</p>
        </div>
        <ChildSwitcher />
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12"><FullPageSpinner label="Loading exams…" /></div>
      ) : isError ? (
        <ErrorState description="Couldn't load exams right now." onRetry={() => refetch()} />
      ) : (exams ?? []).length === 0 ? (
        <Card className="py-10 text-center text-sm text-text-muted">No upcoming exams scheduled right now.</Card>
      ) : (
        <div className="space-y-3">
          {exams!.map((exam) => (
            <Card key={exam.id} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="grid h-10 w-10 place-items-center rounded-xl text-white" style={{ background: 'var(--color-role-parent)' }}>
                  <GraduationCap size={18} />
                </div>
                <div>
                  <p className="font-medium text-text-primary">{exam.title}</p>
                  <p className="text-sm text-text-muted">
                    {exam.date ? new Date(exam.date).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' }) : 'Date to be announced'}
                  </p>
                </div>
              </div>
              <Badge tone="info">Upcoming</Badge>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
