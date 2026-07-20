import { motion } from 'framer-motion';
import { Users, GraduationCap, School, Sparkles, TrendingUp, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Card, CardHeader, StatCard, BarChart, Badge, FullPageSpinner, ErrorState } from '../../../components/ui';
import { useAuthStore } from '../../../store/useAuthStore';
import {
  useSchool, useSchoolPerformance, useClassPerformance, usePrincipalAISummary,
} from '../../../hooks/usePrincipal';
import { useNotifications } from '../../../hooks/useNotifications';
import { timeAgo } from '../../../utils/time';

const ACCENT = 'var(--color-role-principal)';

export function PrincipalDashboard() {
  const user = useAuthStore((s) => s.user);
  const { data: school } = useSchool();
  const { data: performance, isLoading: loadingPerf, isError: errPerf, refetch } = useSchoolPerformance();
  const { data: classPerf } = useClassPerformance();
  const { data: aiSummary, isLoading: loadingAi } = usePrincipalAISummary();
  const { data: notifications } = useNotifications();

  const chartData = (classPerf ?? [])
    .filter((c) => c.average_score != null)
    .slice(0, 8)
    .map((c) => ({ label: c.class_name, value: c.average_score as number }));

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-3xl border border-border-subtle p-6 sm:p-8"
        style={{ background: `linear-gradient(120deg, color-mix(in srgb, ${ACCENT} 12%, var(--surface-raised)), var(--surface-raised))` }}
      >
        <p className="text-sm text-text-muted">Welcome back,</p>
        <h1 className="mt-1 text-2xl font-bold text-text-primary sm:text-3xl">{user?.full_name ?? 'Principal'} 👋</h1>
        <p className="mt-2 max-w-xl text-sm text-text-secondary">
          {school?.name ?? 'Your school'} at a glance: {performance?.total_students ?? 0} students,{' '}
          {performance?.total_teachers ?? 0} teachers, {performance?.total_classes ?? 0} classes.
        </p>
      </motion.div>

      {loadingPerf ? (
        <FullPageSpinner label="Loading school overview…" />
      ) : errPerf ? (
        <ErrorState description="Couldn't load the school overview right now." onRetry={() => refetch()} />
      ) : (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <StatCard label="Students" value={performance?.total_students ?? 0} icon={Users} tint={ACCENT} index={0} />
          <StatCard label="Teachers" value={performance?.total_teachers ?? 0} icon={GraduationCap} tint={ACCENT} index={1} />
          <StatCard label="Classes" value={performance?.total_classes ?? 0} icon={School} tint={ACCENT} index={2} />
          <StatCard
            label="School average"
            value={performance?.average_score != null ? `${performance.average_score}%` : '—'}
            icon={TrendingUp}
            tint={ACCENT}
            index={3}
          />
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="Performance by class" subtitle="Average score, top classes" />
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
              <p className="text-sm font-semibold text-text-primary">AI School Insights</p>
              <Badge tone="info">{loadingAi ? 'Generating…' : 'Live'}</Badge>
            </div>
          </div>
          <p className="mt-4 line-clamp-6 text-sm text-text-secondary">
            {aiSummary?.ai_recommendations ?? "Risk flags, staffing suggestions, and performance forecasts will appear here."}
          </p>
          <Link to="/principal/ai-assistant" className="mt-4 inline-flex items-center gap-1 text-sm font-medium" style={{ color: ACCENT }}>
            Open AI Assistant <ArrowRight size={14} />
          </Link>
        </Card>
      </div>

      <Card>
        <CardHeader
          title="School Notifications"
          action={<Link to="/principal/notifications" className="text-sm font-medium" style={{ color: ACCENT }}>View all</Link>}
        />
        <div className="space-y-3">
          {(notifications ?? []).length === 0 ? (
            <p className="py-4 text-center text-sm text-text-muted">You're all caught up.</p>
          ) : (
            notifications!.slice(0, 5).map((n) => (
              <div key={n.id} className="flex gap-3">
                <span className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${!n.is_read ? 'bg-[var(--color-role-principal)]' : 'bg-transparent'}`} />
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
  );
}
