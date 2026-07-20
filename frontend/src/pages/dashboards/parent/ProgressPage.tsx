import { Card, CardHeader, ProgressBar, Badge, FullPageSpinner, EmptyState, ErrorState } from '../../../components/ui';
import { useSelectedChild, useAiSummary } from '../../../hooks/useParent';
import { useSubjectsByStudent } from '../../../hooks/useAcademic';
import { useStudentResultsDetailed } from '../../../hooks/useExams';
import { ChildSwitcher } from './ChildSwitcher';

export function ProgressPage() {
  const { children, selectedChild, selectedChildId, isLoading: loadingChildren } = useSelectedChild();
  const { data: subjects, isLoading: loadingSubjects, isError, refetch } = useSubjectsByStudent(selectedChildId);
  const { data: results } = useStudentResultsDetailed(selectedChildId);
  const { data: summary, isLoading: loadingSummary } = useAiSummary(selectedChildId);

  if (loadingChildren) return <FullPageSpinner label="Loading your children…" />;
  if (children.length === 0) {
    return <EmptyState title="No children linked to your account yet" description="Once the school links your account to your child's profile, their academic progress will appear here." />;
  }

  const bySubject = (subjects ?? []).map((subject) => {
    const scored = (results ?? []).filter((r) => r.subject_id === subject.id && r.score !== null);
    const avg = scored.length ? Math.round(scored.reduce((sum, r) => sum + (r.score ?? 0), 0) / scored.length) : null;
    return { subject, avg, count: scored.length };
  });

  const progress = summary?.data.progress;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Academic Progress</h1>
          <p className="text-sm text-text-muted">How {selectedChild?.full_name ?? 'your child'} is trending across every subject.</p>
        </div>
        <ChildSwitcher />
      </div>

      {!loadingSummary && progress && (
        <Card>
          <CardHeader title="AI Progress Snapshot" subtitle="Derived from recent activity across subjects" />
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div>
              <p className="text-xs text-text-muted">Knowledge level</p>
              <p className="font-medium text-text-primary">{progress.knowledge_level ?? 'Not yet assessed'}</p>
            </div>
            <div>
              <p className="text-xs text-text-muted">Learning speed</p>
              <p className="font-medium text-text-primary">{progress.learning_speed ?? 'Not yet assessed'}</p>
            </div>
            <div>
              <p className="text-xs text-text-muted">Confidence score</p>
              <p className="font-medium text-text-primary">{progress.confidence_score != null ? `${progress.confidence_score}%` : '—'}</p>
            </div>
          </div>
          {(progress.strong_subjects?.length || progress.weak_subjects?.length) ? (
            <div className="mt-4 flex flex-wrap gap-4">
              {progress.strong_subjects && progress.strong_subjects.length > 0 && (
                <div>
                  <p className="mb-1.5 text-xs text-text-muted">Strong subjects</p>
                  <div className="flex flex-wrap gap-1.5">
                    {progress.strong_subjects.map((s) => <Badge key={s} tone="success">{s}</Badge>)}
                  </div>
                </div>
              )}
              {progress.weak_subjects && progress.weak_subjects.length > 0 && (
                <div>
                  <p className="mb-1.5 text-xs text-text-muted">Needs attention</p>
                  <div className="flex flex-wrap gap-1.5">
                    {progress.weak_subjects.map((s) => <Badge key={s} tone="warning">{s}</Badge>)}
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </Card>
      )}

      {loadingSubjects ? (
        <div className="flex justify-center py-12"><FullPageSpinner label="Loading subjects…" /></div>
      ) : isError ? (
        <ErrorState description="Couldn't load subjects right now." onRetry={() => refetch()} />
      ) : bySubject.length === 0 ? (
        <Card className="py-10 text-center text-sm text-text-muted">Not enrolled in any subjects yet.</Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {bySubject.map(({ subject, avg, count }) => (
            <Card key={subject.id}>
              <CardHeader
                title={subject.name}
                subtitle={subject.teacher_id ? 'Teacher assigned' : 'No teacher assigned yet'}
                action={
                  <Badge tone={avg === null ? 'neutral' : avg >= 70 ? 'success' : avg >= 50 ? 'warning' : 'danger'}>
                    {avg === null ? 'No results yet' : `${avg}%`}
                  </Badge>
                }
              />
              <p className="mb-1.5 text-xs text-text-muted">Average exam score</p>
              <ProgressBar value={avg ?? 0} tint="var(--color-role-parent)" />
              <p className="mt-1.5 text-right text-xs font-medium text-text-secondary">
                {count} graded exam{count === 1 ? '' : 's'}
              </p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
