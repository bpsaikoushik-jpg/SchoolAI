import { Card, Table, Badge, FilterBar, FullPageSpinner, ErrorState, EmptyState } from '../../../components/ui';
import type { Column } from '../../../components/ui';
import { useState } from 'react';
import { FileCheck2 } from 'lucide-react';
import { useHomeworkOverview } from '../../../hooks/usePrincipal';
import type { HomeworkOverviewItem } from '../../../types/principal';

function completionTone(rate: number | null) {
  if (rate == null) return 'neutral' as const;
  if (rate >= 80) return 'success' as const;
  if (rate >= 40) return 'warning' as const;
  return 'danger' as const;
}

const columns: Column<HomeworkOverviewItem>[] = [
  { key: 'title', header: 'Assignment' },
  { key: 'class_name', header: 'Class' },
  { key: 'due_date', header: 'Due', render: (r) => (r.due_date ? new Date(r.due_date).toLocaleDateString() : '—') },
  { key: 'submitted', header: 'Submitted', render: (r) => `${r.submitted}/${r.total_students}` },
  {
    key: 'completion_rate', header: 'Completion',
    render: (r) => <Badge tone={completionTone(r.completion_rate)}>{r.completion_rate != null ? `${r.completion_rate}%` : '—'}</Badge>,
  },
];

export function AssignmentMonitoringPage() {
  const { data, isLoading, isError, refetch } = useHomeworkOverview();
  const [query, setQuery] = useState('');

  const filtered = (data ?? []).filter((hw) =>
    hw.title.toLowerCase().includes(query.toLowerCase()) || hw.class_name.toLowerCase().includes(query.toLowerCase())
  );
  const sorted = [...filtered].sort((a, b) => (a.completion_rate ?? 0) - (b.completion_rate ?? 0));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Assignment Monitoring</h1>
        <p className="text-sm text-text-muted">Completion rates across the school, lowest first.</p>
      </div>

      <FilterBar searchValue={query} onSearchChange={setQuery} searchPlaceholder="Search by title or class…" />

      <Card padded={false}>
        <div className="p-4">
          {isLoading ? (
            <FullPageSpinner label="Loading assignments…" />
          ) : isError ? (
            <ErrorState description="Couldn't load assignments right now." onRetry={() => refetch()} />
          ) : sorted.length === 0 ? (
            <EmptyState icon={FileCheck2} title="No assignments found" description="Once homework is assigned, submission rates will show up here." />
          ) : (
            <Table columns={columns} data={sorted} keyField="id" />
          )}
        </div>
      </Card>
    </div>
  );
}
