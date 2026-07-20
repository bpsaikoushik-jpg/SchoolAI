import { Link } from 'react-router-dom';
import { ArrowRight, Users, GraduationCap, CalendarCheck, ClipboardList, BarChart3, TrendingUp } from 'lucide-react';
import { Card, CardHeader, Badge, FullPageSpinner } from '../../../components/ui';
import { ReportExportPanel } from '../../../components/reports/ReportExportPanel';
import {
  useSchoolPerformance, useAttendanceOverview, useHomeworkOverview, useExamsOverview,
} from '../../../hooks/usePrincipal';

const ACCENT = 'var(--color-role-principal)';

function ReportRow({ label, value, to, icon: Icon }: { label: string; value: string; to: string; icon: typeof Users }) {
  return (
    <Link to={to} className="flex items-center justify-between gap-3 rounded-xl px-3 py-3 hover:bg-sunken/60">
      <div className="flex items-center gap-3">
        <div className="grid h-9 w-9 place-items-center rounded-lg" style={{ background: `color-mix(in srgb, ${ACCENT} 14%, transparent)`, color: ACCENT }}>
          <Icon size={16} />
        </div>
        <span className="text-sm text-text-primary">{label}</span>
      </div>
      <div className="flex items-center gap-2">
        <Badge tone="neutral">{value}</Badge>
        <ArrowRight size={14} className="text-text-muted" />
      </div>
    </Link>
  );
}

export function ReportsOverviewPage() {
  const { data: school, isLoading: l1 } = useSchoolPerformance();
  const { data: attendance, isLoading: l2 } = useAttendanceOverview();
  const { data: homework, isLoading: l3 } = useHomeworkOverview();
  const { data: exams, isLoading: l4 } = useExamsOverview();

  const isLoading = l1 || l2 || l3 || l4;
  const gradedExams = (exams ?? []).filter((e) => e.average_score != null);
  const avgHomeworkCompletion = (homework ?? []).length
    ? Math.round(
        (homework ?? []).reduce((sum, h) => sum + (h.completion_rate ?? 0), 0) / (homework ?? []).length
      )
    : null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Reports Overview</h1>
        <p className="text-sm text-text-muted">A live snapshot of the school, drawn from current data. Open any row for the full breakdown.</p>
      </div>

      {isLoading ? (
        <FullPageSpinner label="Compiling report…" />
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Card padded={false}>
            <div className="p-4">
              <CardHeader title="Academics" />
              <div className="space-y-1">
                <ReportRow
                  label="School average score"
                  value={school?.average_score != null ? `${school.average_score}%` : '—'}
                  to="/principal/performance"
                  icon={TrendingUp}
                />
                <ReportRow
                  label="Exams with recorded results"
                  value={`${gradedExams.length}/${(exams ?? []).length}`}
                  to="/principal/results"
                  icon={BarChart3}
                />
              </div>
            </div>
          </Card>

          <Card padded={false}>
            <div className="p-4">
              <CardHeader title="Operations" />
              <div className="space-y-1">
                <ReportRow
                  label="Attendance marked today"
                  value={attendance ? `${attendance.total_marked}` : '—'}
                  to="/principal/attendance"
                  icon={CalendarCheck}
                />
                <ReportRow
                  label="Average homework completion"
                  value={avgHomeworkCompletion != null ? `${avgHomeworkCompletion}%` : '—'}
                  to="/principal/homework"
                  icon={ClipboardList}
                />
              </div>
            </div>
          </Card>

          <Card padded={false}>
            <div className="p-4">
              <CardHeader title="People" />
              <div className="space-y-1">
                <ReportRow label="Total students" value={String(school?.total_students ?? 0)} to="/principal/students" icon={Users} />
                <ReportRow label="Total teachers" value={String(school?.total_teachers ?? 0)} to="/principal/teachers" icon={GraduationCap} />
              </div>
            </div>
          </Card>

          <Card padded={false}>
            <div className="p-4">
              <CardHeader title="Structure" />
              <div className="space-y-1">
                <ReportRow label="Total classes" value={String(school?.total_classes ?? 0)} to="/principal/classes" icon={Users} />
              </div>
            </div>
          </Card>
        </div>
      )}

      <ReportExportPanel accent={ACCENT} />
    </div>
  );
}
