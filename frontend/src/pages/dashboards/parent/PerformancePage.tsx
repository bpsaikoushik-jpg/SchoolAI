import { Card, CardHeader, LineChart, BarChart, DonutChart, FullPageSpinner, EmptyState } from '../../../components/ui';
import { useSelectedChild } from '../../../hooks/useParent';
import { useStudentResultsDetailed } from '../../../hooks/useExams';
import { useStudentAttendance } from '../../../hooks/useAttendance';
import { ChildSwitcher } from './ChildSwitcher';

export function PerformancePage() {
  const { children, selectedChild, selectedChildId, isLoading: loadingChildren } = useSelectedChild();
  const { data: results, isLoading } = useStudentResultsDetailed(selectedChildId);
  const { summary } = useStudentAttendance(selectedChildId ?? undefined);

  if (loadingChildren) return <FullPageSpinner label="Loading your children…" />;
  if (children.length === 0) {
    return <EmptyState title="No children linked to your account yet" description="Once the school links your account to your child's profile, performance charts will appear here." />;
  }

  const scored = (results ?? []).filter((r) => r.score !== null);
  const trend = [...scored]
    .sort((a, b) => new Date(a.exam_date ?? a.created_at).getTime() - new Date(b.exam_date ?? b.created_at).getTime())
    .slice(-8)
    .map((r) => ({ label: r.exam_title.length > 10 ? `${r.exam_title.slice(0, 9)}…` : r.exam_title, value: r.score ?? 0 }));

  const bySubject = new Map<string, { total: number; count: number }>();
  for (const r of scored) {
    const cur = bySubject.get(r.subject_name) ?? { total: 0, count: 0 };
    cur.total += r.score ?? 0;
    cur.count += 1;
    bySubject.set(r.subject_name, cur);
  }
  const subjectBars = [...bySubject.entries()].map(([label, v]) => ({
    label: label.length > 10 ? `${label.slice(0, 9)}…` : label,
    value: Math.round(v.total / v.count),
  }));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Performance</h1>
          <p className="text-sm text-text-muted">Visual trends for {selectedChild?.full_name ?? 'your child'}.</p>
        </div>
        <ChildSwitcher />
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12"><FullPageSpinner label="Loading performance data…" /></div>
      ) : scored.length === 0 ? (
        <Card className="py-10 text-center text-sm text-text-muted">No graded results yet — charts will populate once exams are marked.</Card>
      ) : (
        <>
          <Card>
            <CardHeader title="Score trend" subtitle="Most recent graded exams" />
            <LineChart data={trend} tint="var(--color-role-parent)" />
          </Card>
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <Card className="lg:col-span-2">
              <CardHeader title="Average score by subject" />
              <BarChart data={subjectBars} tint="var(--color-role-parent)" valueSuffix="%" />
            </Card>
            <Card>
              <CardHeader title="Attendance" subtitle="This term" />
              <DonutChart
                centerValue={`${summary.present}%`}
                centerLabel="Present"
                data={[
                  { label: 'Present', value: summary.present, color: 'var(--color-mint-500)' },
                  { label: 'Late', value: summary.late, color: '#f59e0b' },
                  { label: 'Absent', value: summary.absent, color: '#f43f5e' },
                ]}
              />
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
