import { Card, CardHeader, DonutChart, BarChart, StatCard } from '../../../components/ui';
import { CalendarCheck, CalendarX, Clock } from 'lucide-react';
import { useAttendanceSummary } from '../../../hooks/useAttendance';

function monthlyBreakdown(records: { date: string; status: string }[]) {
  const byMonth: Record<string, { present: number; total: number }> = {};
  for (const r of records) {
    const month = new Date(r.date).toLocaleString('en-US', { month: 'short' });
    byMonth[month] = byMonth[month] || { present: 0, total: 0 };
    byMonth[month].total += 1;
    if (r.status === 'present') byMonth[month].present += 1;
  }
  return Object.entries(byMonth).map(([label, v]) => ({
    label,
    value: v.total === 0 ? 0 : Math.round((v.present / v.total) * 100),
  }));
}

export function AttendancePage() {
  const { data: records, isLoading, isError, summary } = useAttendanceSummary();

  if (isLoading) {
    return <p className="text-sm text-text-muted">Loading attendance…</p>;
  }

  if (isError) {
    return <p className="text-sm text-rose-500">Couldn't load your attendance right now. Please try again later.</p>;
  }

  const monthly = monthlyBreakdown(records ?? []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Attendance</h1>
        <p className="text-sm text-text-muted">Your attendance record for this term.</p>
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard label="Present" value={`${summary.present}%`} icon={CalendarCheck} tint="var(--color-mint-500)" />
        <StatCard label="Late" value={`${summary.late}%`} icon={Clock} tint="#f59e0b" />
        <StatCard label="Absent" value={`${summary.absent}%`} icon={CalendarX} tint="#f43f5e" />
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader title="Breakdown" />
          <DonutChart
            data={[
              { label: 'Present', value: summary.present, color: 'var(--color-mint-500)' },
              { label: 'Late', value: summary.late, color: '#f59e0b' },
              { label: 'Absent', value: summary.absent, color: '#f43f5e' },
            ]}
          />
        </Card>
        <Card className="lg:col-span-2">
          <CardHeader title="Monthly trend" subtitle="% present, by month recorded" />
          {monthly.length === 0 ? (
            <p className="py-8 text-center text-sm text-text-muted">No attendance records yet.</p>
          ) : (
            <BarChart data={monthly} tint="var(--color-role-student)" valueSuffix="%" />
          )}
        </Card>
      </div>
    </div>
  );
}
