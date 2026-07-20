import { Card, Badge, FilterBar, FullPageSpinner, ErrorState, EmptyState } from '../../../components/ui';
import { GraduationCap } from 'lucide-react';
import { useState } from 'react';
import { useExamsOverview } from '../../../hooks/usePrincipal';

export function ExamMonitoringPage() {
  const { data, isLoading, isError, refetch } = useExamsOverview();
  const [query, setQuery] = useState('');

  const now = Date.now();
  const filtered = (data ?? []).filter((e) =>
    e.title.toLowerCase().includes(query.toLowerCase()) || e.subject_name.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Exam Monitoring</h1>
        <p className="text-sm text-text-muted">Every exam scheduled across the school's subjects.</p>
      </div>

      <FilterBar searchValue={query} onSearchChange={setQuery} searchPlaceholder="Search by title or subject…" />

      {isLoading ? (
        <FullPageSpinner label="Loading exams…" />
      ) : isError ? (
        <ErrorState description="Couldn't load exams right now." onRetry={() => refetch()} />
      ) : filtered.length === 0 ? (
        <EmptyState icon={GraduationCap} title="No exams found" description="Once teachers schedule exams, they'll appear here." />
      ) : (
        <div className="space-y-3">
          {filtered.map((exam) => {
            const isUpcoming = exam.date ? new Date(exam.date).getTime() >= now : false;
            return (
              <Card key={exam.id} className="flex flex-wrap items-center justify-between gap-4">
                <div className="min-w-[200px] flex-1">
                  <p className="font-medium text-text-primary">{exam.title}</p>
                  <p className="text-sm text-text-muted">
                    {exam.subject_name}{exam.class_name ? ` · ${exam.class_name}` : ''} ·{' '}
                    {exam.date ? new Date(exam.date).toLocaleDateString() : 'No date set'}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge tone={isUpcoming ? 'info' : 'neutral'}>{isUpcoming ? 'Upcoming' : 'Completed'}</Badge>
                  <Badge tone="neutral">{exam.results_recorded} results recorded</Badge>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
