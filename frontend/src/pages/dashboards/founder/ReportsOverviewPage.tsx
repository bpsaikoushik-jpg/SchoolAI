import { Link } from 'react-router-dom';
import { ArrowRight, Users, GraduationCap, CalendarCheck, ClipboardList, BarChart3, TrendingUp, Building2 } from 'lucide-react';
import { Card, CardHeader, Badge, FullPageSpinner } from '../../../components/ui';
import { ReportExportPanel } from '../../../components/reports/ReportExportPanel';
import {
  useOrgOverview, useOrgAttendance, useOrgHomework, useOrgExams,
} from '../../../hooks/useFounder';

const ACCENT = 'var(--color-role-founder)';

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
  const { data: overview, isLoading: l1 } = useOrgOverview();
  const { data: attendance, isLoading: l2 } = useOrgAttendance();
  const { data: homework, isLoading: l3 } = useOrgHomework();
  const { data: exams, isLoading: l4 } = useOrgExams();

  const isLoading = l1 || l2 || l3 || l4;
  const totalExams = (exams ?? []).reduce((sum, e) => sum + e.total_exams, 0);
  const gradedSchools = (exams ?? []).filter((e) => e.average_score != null).length;
  const avgHomeworkCompletion = (homework ?? []).length
    ? Math.round(
        (homework ?? []).reduce((sum, h) => sum + (h.completion_rate ?? 0), 0) / (homework ?? []).length
      )
    : null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Reports Overview</h1>
        <p className="text-sm text-text-muted">A live, organization-wide snapshot drawn from current data. Open any row for the full breakdown.</p>
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
                  label="Organization average score"
                  value={overview?.average_score != null ? `${overview.average_score}%` : '—'}
                  to="/founder/analytics"
                  icon={TrendingUp}
                />
                <ReportRow
                  label="Schools with recorded results"
                  value={`${gradedSchools}/${(exams ?? []).length}`}
                  to="/founder/results"
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
                  to="/founder/attendance"
                  icon={CalendarCheck}
                />
                <ReportRow
                  label="Average homework completion"
                  value={avgHomeworkCompletion != null ? `${avgHomeworkCompletion}%` : '—'}
                  to="/founder/homework"
                  icon={ClipboardList}
                />
              </div>
            </div>
          </Card>

          <Card padded={false}>
            <div className="p-4">
              <CardHeader title="People" />
              <div className="space-y-1">
                <ReportRow label="Total students" value={String(overview?.total_students ?? 0)} to="/founder/student-analytics" icon={Users} />
                <ReportRow label="Total teachers" value={String(overview?.total_teachers ?? 0)} to="/founder/teacher-analytics" icon={GraduationCap} />
              </div>
            </div>
          </Card>

          <Card padded={false}>
            <div className="p-4">
              <CardHeader title="Structure" />
              <div className="space-y-1">
                <ReportRow
                  label="Active schools"
                  value={`${overview?.active_schools ?? 0}/${overview?.total_schools ?? 0}`}
                  to="/founder/schools"
                  icon={Building2}
                />
                <ReportRow label="Total exams held" value={String(totalExams)} to="/founder/exams" icon={BarChart3} />
              </div>
            </div>
          </Card>
        </div>
      )}

      <ReportExportPanel accent={ACCENT} />
    </div>
  );
}
