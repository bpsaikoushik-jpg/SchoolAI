import { Card, CardHeader, StatCard, Table, DonutChart, FullPageSpinner, ErrorState, EmptyState } from '../../../components/ui';
import type { Column } from '../../../components/ui';
import { CalendarCheck, UserCheck, UserX, Clock } from 'lucide-react';
import { useAttendanceOverview } from '../../../hooks/usePrincipal';
import type { ClassAttendanceSummary } from '../../../types/principal';

const ACCENT = 'var(--color-role-principal)';

const columns: Column<ClassAttendanceSummary>[] = [
  { key: 'class_name', header: 'Class' },
  { key: 'present', header: 'Present' },
  { key: 'absent', header: 'Absent' },
  { key: 'late', header: 'Late' },
  {
    key: 'total_marked', header: 'Attendance rate',
    render: (r) => (r.total_marked > 0 ? `${Math.round((r.present / r.total_marked) * 100)}%` : '—'),
  },
];

export function AttendanceAnalyticsPage() {
  const { data, isLoading, isError, refetch } = useAttendanceOverview();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Attendance Monitoring</h1>
        <p className="text-sm text-text-muted">School-wide attendance for {data?.date ?? 'today'}.</p>
      </div>

      {isLoading ? (
        <FullPageSpinner label="Loading attendance…" />
      ) : isError ? (
        <ErrorState description="Couldn't load attendance right now." onRetry={() => refetch()} />
      ) : !data || data.by_class.length === 0 ? (
        <EmptyState icon={CalendarCheck} title="No classes to show yet" description="Once classes and attendance records exist, they'll appear here." />
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard label="Present" value={data.present} icon={UserCheck} tint={ACCENT} index={0} />
            <StatCard label="Absent" value={data.absent} icon={UserX} tint={ACCENT} index={1} />
            <StatCard label="Late" value={data.late} icon={Clock} tint={ACCENT} index={2} />
            <StatCard
              label="Overall rate"
              value={data.total_marked > 0 ? `${Math.round((data.present / data.total_marked) * 100)}%` : '—'}
              icon={CalendarCheck}
              tint={ACCENT}
              index={3}
            />
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <Card className="lg:col-span-2" padded={false}>
              <div className="p-4">
                <CardHeader title="Attendance by class" />
                <Table columns={columns} data={data.by_class} keyField="class_id" />
              </div>
            </Card>
            <Card>
              <CardHeader title="Today's split" />
              <DonutChart
                data={[
                  { label: 'Present', value: data.present, color: '#10b981' },
                  { label: 'Absent', value: data.absent, color: '#f43f5e' },
                  { label: 'Late', value: data.late, color: '#f59e0b' },
                ]}
                centerLabel="Marked"
                centerValue={String(data.total_marked)}
              />
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
