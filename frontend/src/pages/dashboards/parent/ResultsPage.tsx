import { Card, Table, Badge, FullPageSpinner, EmptyState, ErrorState } from '../../../components/ui';
import type { Column } from '../../../components/ui';
import { useSelectedChild } from '../../../hooks/useParent';
import { useStudentResultsDetailed } from '../../../hooks/useExams';
import type { ExamResultDetail } from '../../../services/exam.service';
import { ChildSwitcher } from './ChildSwitcher';

function grade(score: number | null) {
  if (score === null) return { label: 'Pending', tone: 'neutral' as const };
  if (score >= 85) return { label: 'Excellent', tone: 'success' as const };
  if (score >= 70) return { label: 'Good', tone: 'success' as const };
  if (score >= 50) return { label: 'Needs work', tone: 'warning' as const };
  return { label: 'At risk', tone: 'danger' as const };
}

const columns: Column<ExamResultDetail>[] = [
  { key: 'exam_title', header: 'Exam' },
  { key: 'subject_name', header: 'Subject' },
  {
    key: 'exam_date', header: 'Date',
    render: (r) => (r.exam_date ? new Date(r.exam_date).toLocaleDateString() : '—'),
  },
  {
    key: 'score', header: 'Score',
    render: (r) => (r.score === null ? '—' : `${r.score}%`),
  },
  {
    key: 'remarks', header: 'Result',
    render: (r) => {
      const g = grade(r.score);
      return <Badge tone={g.tone}>{g.label}</Badge>;
    },
  },
];

export function ResultsPage() {
  const { children, selectedChild, selectedChildId, isLoading: loadingChildren } = useSelectedChild();
  const { data: results, isLoading, isError, refetch } = useStudentResultsDetailed(selectedChildId);

  if (loadingChildren) return <FullPageSpinner label="Loading your children…" />;
  if (children.length === 0) {
    return <EmptyState title="No children linked to your account yet" description="Once the school links your account to your child's profile, their exam results will appear here." />;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Results</h1>
          <p className="text-sm text-text-muted">Published exam results for {selectedChild?.full_name ?? 'your child'}.</p>
        </div>
        <ChildSwitcher />
      </div>
      <Card padded={false}>
        <div className="p-4">
          {isLoading ? (
            <p className="py-8 text-center text-sm text-text-muted">Loading results…</p>
          ) : isError ? (
            <ErrorState description="Couldn't load results right now." onRetry={() => refetch()} />
          ) : (results ?? []).length === 0 ? (
            <p className="py-8 text-center text-sm text-text-muted">No results published yet.</p>
          ) : (
            <Table columns={columns} data={results!} keyField="id" />
          )}
        </div>
      </Card>
    </div>
  );
}
