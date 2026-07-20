import { Building2, Users, GraduationCap, TrendingUp } from 'lucide-react';
import { Card, CardHeader, BarChart, DonutChart, StatCard, Table, Badge, FullPageSpinner, ErrorState } from '../../../components/ui';
import type { Column } from '../../../components/ui';
import { useOrgOverview, useSchoolPerformance, useUserBreakdown } from '../../../hooks/useFounder';
import type { FounderSchoolPerformance } from '../../../types/founder';

const ACCENT = 'var(--color-role-founder)';

const ROLE_COLORS: Record<string, string> = {
  student: 'var(--color-role-student)',
  teacher: 'var(--color-role-teacher)',
  parent: 'var(--color-role-parent)',
  principal: 'var(--color-role-principal)',
  admin: ACCENT,
  founder: ACCENT,
};

function scoreTone(score: number | null) {
  if (score == null) return 'neutral' as const;
  if (score >= 75) return 'success' as const;
  if (score >= 55) return 'warning' as const;
  return 'danger' as const;
}

const columns: Column<FounderSchoolPerformance>[] = [
  { key: 'school_name', header: 'School' },
  { key: 'total_students', header: 'Students' },
  { key: 'total_teachers', header: 'Teachers' },
  { key: 'total_classes', header: 'Classes' },
  {
    key: 'average_score', header: 'Average score',
    render: (r) => <Badge tone={scoreTone(r.average_score)}>{r.average_score != null ? `${r.average_score}%` : '—'}</Badge>,
  },
];

export function PlatformAnalyticsPage() {
  const { data: overview, isLoading, isError, refetch } = useOrgOverview();
  const { data: schoolPerf } = useSchoolPerformance();
  const { data: breakdown } = useUserBreakdown();

  if (isLoading) return <FullPageSpinner label="Loading organization performance…" />;
  if (isError) return <ErrorState description="Couldn't load organization performance right now." onRetry={() => refetch()} />;

  const chartData = (schoolPerf ?? [])
    .filter((s) => s.average_score != null)
    .map((s) => ({ label: s.school_name, value: s.average_score as number }));

  const donutData = (breakdown ?? []).map((r) => ({
    label: r.role.charAt(0).toUpperCase() + r.role.slice(1),
    value: r.count,
    color: ROLE_COLORS[r.role] ?? ACCENT,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Organization Performance</h1>
        <p className="text-sm text-text-muted">A live cross-section of the whole organization: schools, people, and outcomes.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Schools" value={`${overview?.active_schools ?? 0}/${overview?.total_schools ?? 0}`} icon={Building2} tint={ACCENT} index={0} />
        <StatCard label="Students" value={overview?.total_students ?? 0} icon={Users} tint={ACCENT} index={1} />
        <StatCard label="Teachers" value={overview?.total_teachers ?? 0} icon={GraduationCap} tint={ACCENT} index={2} />
        <StatCard label="Org average" value={overview?.average_score != null ? `${overview.average_score}%` : '—'} icon={TrendingUp} tint={ACCENT} index={3} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Average score by school" />
          {chartData.length === 0 ? <p className="py-8 text-center text-sm text-text-muted">No graded results yet.</p> : <BarChart data={chartData} tint={ACCENT} valueSuffix="%" />}
        </Card>
        <Card>
          <CardHeader title="User composition" />
          {donutData.length === 0 ? <p className="py-6 text-center text-sm text-text-muted">No users yet.</p> : <DonutChart data={donutData} />}
        </Card>
      </div>

      <Card padded={false}>
        <div className="p-4">
          <CardHeader title="Schools" />
          {(schoolPerf ?? []).length === 0 ? (
            <p className="py-8 text-center text-sm text-text-muted">No schools yet.</p>
          ) : (
            <Table columns={columns} data={schoolPerf!} keyField="school_id" />
          )}
        </div>
      </Card>
    </div>
  );
}
