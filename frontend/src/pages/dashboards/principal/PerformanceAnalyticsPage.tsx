import { Card, CardHeader, Table, Badge, StatCard, FullPageSpinner, ErrorState, EmptyState } from '../../../components/ui';
import type { Column } from '../../../components/ui';
import { TrendingUp, Users, GraduationCap, School } from 'lucide-react';
import { useSchoolPerformance, useClassPerformance } from '../../../hooks/usePrincipal';
import type { ClassPerformance } from '../../../types/principal';

const ACCENT = 'var(--color-role-principal)';

function scoreTone(score: number | null) {
  if (score == null) return 'neutral' as const;
  if (score >= 75) return 'success' as const;
  if (score >= 55) return 'warning' as const;
  return 'danger' as const;
}

const columns: Column<ClassPerformance>[] = [
  { key: 'class_name', header: 'Class' },
  { key: 'student_count', header: 'Students' },
  {
    key: 'average_score', header: 'Average score',
    render: (r) => <Badge tone={scoreTone(r.average_score)}>{r.average_score != null ? `${r.average_score}%` : '—'}</Badge>,
  },
];

export function PerformanceAnalyticsPage() {
  const { data: school, isLoading: loadingSchool } = useSchoolPerformance();
  const { data: classes, isLoading: loadingClasses, isError, refetch } = useClassPerformance();

  const isLoading = loadingSchool || loadingClasses;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">School Performance</h1>
        <p className="text-sm text-text-muted">Class-by-class academic performance across the school.</p>
      </div>

      {isLoading ? (
        <FullPageSpinner label="Loading performance data…" />
      ) : isError ? (
        <ErrorState description="Couldn't load performance data right now." onRetry={() => refetch()} />
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard label="School average" value={school?.average_score != null ? `${school.average_score}%` : '—'} icon={TrendingUp} tint={ACCENT} index={0} />
            <StatCard label="Students" value={school?.total_students ?? 0} icon={Users} tint={ACCENT} index={1} />
            <StatCard label="Teachers" value={school?.total_teachers ?? 0} icon={GraduationCap} tint={ACCENT} index={2} />
            <StatCard label="Classes" value={school?.total_classes ?? 0} icon={School} tint={ACCENT} index={3} />
          </div>

          <Card padded={false}>
            <div className="p-4">
              <CardHeader title="Performance by class" />
              {(classes ?? []).length === 0 ? (
                <EmptyState title="No class performance data yet" description="Once exam results are recorded, class averages will appear here." />
              ) : (
                <Table columns={columns} data={classes!} keyField="class_id" />
              )}
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
