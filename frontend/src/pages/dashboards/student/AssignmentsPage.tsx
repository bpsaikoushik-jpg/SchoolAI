import { Card, ProgressBar, Table, Badge } from '../../../components/ui';
import type { Column } from '../../../components/ui';
import { useMyHomework } from '../../../hooks/useHomework';
import { useMySubmissions } from '../../../hooks/useHomework';

interface Row {
  id: string;
  title: string;
  due: string;
  status: 'not_started' | 'in_progress' | 'complete';
  grade: string | null;
}

const columns: Column<Row>[] = [
  { key: 'title', header: 'Assignment' },
  { key: 'due', header: 'Due' },
  {
    key: 'status', header: 'Progress',
    render: (row) => (
      <div className="flex items-center gap-2">
        <ProgressBar
          value={row.status === 'complete' ? 100 : row.status === 'in_progress' ? 50 : 0}
          tint="var(--color-role-student)"
          className="w-24"
        />
        <span className="text-xs text-text-muted">
          {row.status === 'complete' ? '100%' : row.status === 'in_progress' ? '50%' : '0%'}
        </span>
      </div>
    ),
  },
  {
    key: 'grade', header: 'Status',
    render: (row) => (
      <Badge tone={row.status === 'complete' ? 'success' : row.status === 'in_progress' ? 'warning' : 'neutral'}>
        {row.grade ? `Graded: ${row.grade}` : row.status === 'complete' ? 'Submitted' : row.status === 'in_progress' ? 'In progress' : 'Not started'}
      </Badge>
    ),
  },
];

export function AssignmentsPage() {
  const { data: homework, isLoading: loadingHw, isError: errHw } = useMyHomework();
  const { data: submissions, isLoading: loadingSub, isError: errSub } = useMySubmissions();

  const isLoading = loadingHw || loadingSub;
  const isError = errHw || errSub;

  const rows: Row[] = (homework ?? []).map((hw) => {
    const submission = (submissions ?? []).find((s) => s.homework_id === hw.id);
    return {
      id: hw.id,
      title: hw.title,
      due: hw.due_date ? new Date(hw.due_date).toLocaleDateString() : 'No due date',
      status: submission ? (submission.grade ? 'complete' : 'in_progress') : 'not_started',
      grade: submission?.grade ?? null,
    };
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Assignments</h1>
        <p className="text-sm text-text-muted">Track everything in flight across your subjects.</p>
      </div>
      <Card padded={false}>
        <div className="p-4">
          {isLoading ? (
            <p className="py-8 text-center text-sm text-text-muted">Loading assignments…</p>
          ) : isError ? (
            <p className="py-8 text-center text-sm text-rose-500">Couldn't load assignments right now.</p>
          ) : rows.length === 0 ? (
            <p className="py-8 text-center text-sm text-text-muted">No homework assigned yet.</p>
          ) : (
            <Table columns={columns} data={rows} keyField="id" />
          )}
        </div>
      </Card>
    </div>
  );
}
