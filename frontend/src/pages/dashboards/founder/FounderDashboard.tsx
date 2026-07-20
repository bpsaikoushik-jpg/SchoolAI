import { motion } from 'framer-motion';
import { Building2, Users, GraduationCap, TrendingUp, Sparkles, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Card, CardHeader, StatCard, BarChart, DonutChart, Badge, FullPageSpinner, ErrorState } from '../../../components/ui';
import { useAuthStore } from '../../../store/useAuthStore';
import { useOrgOverview, useSchoolPerformance, useUserBreakdown, useFounderAISummary } from '../../../hooks/useFounder';
import { useNotifications } from '../../../hooks/useNotifications';
import { timeAgo } from '../../../utils/time';

const ACCENT = 'var(--color-role-founder)';

const ROLE_COLORS: Record<string, string> = {
  student: 'var(--color-role-student)',
  teacher: 'var(--color-role-teacher)',
  parent: 'var(--color-role-parent)',
  principal: 'var(--color-role-principal)',
  admin: 'var(--color-role-founder)',
  founder: 'var(--color-role-founder)',
};

export function FounderDashboard() {
  const user = useAuthStore((s) => s.user);
  const { data: overview, isLoading, isError, refetch } = useOrgOverview();
  const { data: schoolPerf } = useSchoolPerformance();
  const { data: roleBreakdown } = useUserBreakdown();
  const { data: aiSummary, isLoading: loadingAi } = useFounderAISummary();
  const { data: notifications } = useNotifications();

  const chartData = (schoolPerf ?? [])
    .filter((s) => s.average_score != null)
    .slice(0, 8)
    .map((s) => ({ label: s.school_name, value: s.average_score as number }));

  const donutData = (roleBreakdown ?? []).map((r) => ({
    label: r.role.charAt(0).toUpperCase() + r.role.slice(1),
    value: r.count,
    color: ROLE_COLORS[r.role] ?? 'var(--color-role-founder)',
  }));

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-3xl border border-border-subtle p-6 sm:p-8"
        style={{ background: `linear-gradient(120deg, color-mix(in srgb, ${ACCENT} 12%, var(--surface-raised)), var(--surface-raised))` }}
      >
        <p className="text-sm text-text-muted">Welcome back,</p>
        <h1 className="mt-1 text-2xl font-bold text-text-primary sm:text-3xl">{user?.full_name ?? 'Founder'} 👋</h1>
        <p className="mt-2 max-w-xl text-sm text-text-secondary">
          Platform-wide view across {overview?.total_schools ?? 0} schools, {overview?.total_students ?? 0} students,{' '}
          and {overview?.total_teachers ?? 0} teachers.
        </p>
      </motion.div>

      {isLoading ? (
        <FullPageSpinner label="Loading organization overview…" />
      ) : isError ? (
        <ErrorState description="Couldn't load the organization overview right now." onRetry={() => refetch()} />
      ) : (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <StatCard label="Schools" value={`${overview?.active_schools ?? 0}/${overview?.total_schools ?? 0}`} icon={Building2} tint={ACCENT} index={0} />
          <StatCard label="Students" value={overview?.total_students ?? 0} icon={Users} tint={ACCENT} index={1} />
          <StatCard label="Teachers" value={overview?.total_teachers ?? 0} icon={GraduationCap} tint={ACCENT} index={2} />
          <StatCard
            label="Org average"
            value={overview?.average_score != null ? `${overview.average_score}%` : '—'}
            icon={TrendingUp}
            tint={ACCENT}
            index={3}
          />
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="Performance by school" subtitle="Average score, top schools" />
          {chartData.length === 0 ? (
            <p className="py-8 text-center text-sm text-text-muted">No graded results yet.</p>
          ) : (
            <BarChart data={chartData} tint={ACCENT} valueSuffix="%" />
          )}
        </Card>

        <Card className="border-dashed">
          <div className="flex items-center gap-2.5">
            <div className="grid h-9 w-9 place-items-center rounded-xl text-white" style={{ background: ACCENT }}>
              <Sparkles size={17} />
            </div>
            <div>
              <p className="text-sm font-semibold text-text-primary">AI Organization Insights</p>
              <Badge tone="info">{loadingAi ? 'Generating…' : 'Live'}</Badge>
            </div>
          </div>
          <p className="mt-4 line-clamp-6 text-sm text-text-secondary">
            {aiSummary?.ai_recommendations ?? 'Risk flags and platform-wide recommendations will appear here.'}
          </p>
          <Link to="/founder/ai-assistant" className="mt-4 inline-flex items-center gap-1 text-sm font-medium" style={{ color: ACCENT }}>
            Open AI Assistant <ArrowRight size={14} />
          </Link>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Users by role" />
          {donutData.length === 0 ? (
            <p className="py-6 text-center text-sm text-text-muted">No users yet.</p>
          ) : (
            <DonutChart data={donutData} />
          )}
        </Card>

        <Card>
          <CardHeader
            title="Notifications"
            action={<Link to="/founder/notifications" className="text-sm font-medium" style={{ color: ACCENT }}>View all</Link>}
          />
          <div className="space-y-3">
            {(notifications ?? []).length === 0 ? (
              <p className="py-4 text-center text-sm text-text-muted">You're all caught up.</p>
            ) : (
              notifications!.slice(0, 5).map((n) => (
                <div key={n.id} className="flex gap-3">
                  <span className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${!n.is_read ? 'bg-[var(--color-role-founder)]' : 'bg-transparent'}`} />
                  <div>
                    <p className="text-sm font-medium text-text-primary">{n.title}</p>
                    <p className="text-xs text-text-muted">{n.message} · {timeAgo(n.created_at)}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
