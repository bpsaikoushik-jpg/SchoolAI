import { UserCheck, UserX, Clock } from 'lucide-react';
import { Card, CardHeader, StatCard, DonutChart, Table, FullPageSpinner, ErrorState } from '../../../components/ui';
import type { Column } from '../../../components/ui';
import { useOrgAttendance } from '../../../hooks/useFounder';
import type { SchoolAttendanceSummary } from '../../../types/founder';

const ACCENT = 'var(--color-role-founder)';

const columns: Column<SchoolAttendanceSummary>[] = [
  { key: 'school_name', header: 'School' },
  { key: 'present', header: 'Present' },
  { key: 'absent', header: 'Absent' },
  { key: 'late', header: 'Late' },
  { key: 'total_marked', header: 'Total marked' },
];

export function AttendanceAnalyticsPage() {
  const { data, isLoading, isError, refetch } = useOrgAttendance();

  if (isLoading) return <FullPageSpinner label="Loading attendance…" />;
  if (isError) return <ErrorState description="Couldn't load attendance right now." onRetry={() => refetch()} />;

  const donutData = data
    ? [
        { label: 'Present', value: data.present, color: 'var(--color-role-teacher)' },
        { label: 'Absent', value: data.absent, color: 'var(--color-role-parent)' },
        { label: 'Late', value: data.late, color: ACCENT },
      ]
    : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Attendance Analytics</h1>
        <p className="text-sm text-text-muted">Organization-wide attendance for {data?.date}.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard label="Present" value={data?.present ?? 0} icon={UserCheck} tint={ACCENT} index={0} />
        <StatCard label="Absent" value={data?.absent ?? 0} icon={UserX} tint={ACCENT} index={1} />
        <StatCard label="Late" value={data?.late ?? 0} icon={Clock} tint={ACCENT} index={2} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader title="Today's split" />
          {data?.total_marked ? <DonutChart data={donutData} /> : <p className="py-6 text-center text-sm text-text-muted">No attendance marked yet today.</p>}
        </Card>

        <Card className="lg:col-span-2" padded={false}>
          <div className="p-4">
            <CardHeader title="By school" />
            {(data?.by_school ?? []).length === 0 ? (
              <p className="py-8 text-center text-sm text-text-muted">No schools to show.</p>
            ) : (
              <Table columns={columns} data={data!.by_school} keyField="school_id" />
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
