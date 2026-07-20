import { motion } from 'framer-motion';
import { Users, CalendarCheck, TrendingUp, Sparkles } from 'lucide-react';
import { Card, CardHeader, StatCard, BarChart, Badge, ProgressBar } from '../../../components/ui';
import { useAuthStore } from '../../../store/useAuthStore';
import { useMyClasses, useAttendanceToday, useHomeworkQueue, useMyCalendarToday } from '../../../hooks/useTeacherInsights';

const ACCENT = 'var(--color-role-teacher)';

export function TeacherDashboard() {
  const user = useAuthStore((s) => s.user);
  const { data: classes } = useMyClasses();
  const { data: attendanceToday } = useAttendanceToday();
  const { data: homeworkQueue } = useHomeworkQueue();
  const { data: calendarToday } = useMyCalendarToday();

  const myClasses = classes ?? [];
  const totalStudents = myClasses.reduce((sum, c) => sum + c.students, 0);
  const avgPerformance = myClasses.length
    ? Math.round(myClasses.reduce((sum, c) => sum + c.avg_score, 0) / myClasses.length)
    : 0;
  const homework = homeworkQueue ?? [];
  const attendance = attendanceToday ?? { present: 0, absent: 0, late: 0 };
  const performanceChart = myClasses.map((c) => ({ label: c.name, value: c.avg_score }));
  const calendarEvents = [...(calendarToday ?? [])].sort(
    (a, b) => new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime()
  );
  const formatTime = (iso: string) => new Date(iso).toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });
  const formatDue = (iso: string | null) => (iso ? new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : '—');

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-3xl border border-border-subtle p-6 sm:p-8"
        style={{ background: `linear-gradient(120deg, color-mix(in srgb, ${ACCENT} 12%, var(--surface-raised)), var(--surface-raised))` }}
      >
        <p className="text-sm text-text-muted">Welcome back,</p>
        <h1 className="mt-1 text-2xl font-bold text-text-primary sm:text-3xl">{user?.full_name ?? 'Teacher'} 👋</h1>
        <p className="mt-2 max-w-xl text-sm text-text-secondary">
          You're teaching {myClasses.length} classes with {totalStudents} students total. {homework.length} homework sets need review.
        </p>
      </motion.div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="My Classes" value={myClasses.length} icon={Users} tint={ACCENT} index={0} />
        <StatCard label="Total Students" value={totalStudents} icon={Users} tint={ACCENT} index={1} />
        <StatCard label="Present Today" value={attendance.present} icon={CalendarCheck} tint={ACCENT} index={2} />
        <StatCard label="Avg. Performance" value={`${avgPerformance}%`} icon={TrendingUp} tint={ACCENT} index={3} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="My Classes" />
          <div className="space-y-2.5">
            {myClasses.length === 0 ? (
              <p className="py-6 text-center text-sm text-text-muted">No classes assigned yet.</p>
            ) : (
              myClasses.map((c) => (
                <div key={c.class_id} className="flex items-center justify-between rounded-xl bg-sunken/60 px-4 py-3">
                  <div>
                    <p className="text-sm font-medium text-text-primary">{c.name}</p>
                    <p className="text-xs text-text-muted">{c.students} students</p>
                  </div>
                  <Badge tone={c.avg_score >= 85 ? 'success' : c.avg_score >= 75 ? 'warning' : 'danger'}>{Math.round(c.avg_score)}% avg</Badge>
                </div>
              ))
            )}
          </div>
        </Card>

        <Card className="border-dashed">
          <div className="flex items-center gap-2.5">
            <div className="grid h-9 w-9 place-items-center rounded-xl text-white" style={{ background: ACCENT }}>
              <Sparkles size={17} />
            </div>
            <div>
              <p className="text-sm font-semibold text-text-primary">AI Insights</p>
              <Badge tone="info">Coming soon</Badge>
            </div>
          </div>
          <p className="mt-4 text-sm text-text-secondary">
            AI-generated class insights — at-risk students, pacing suggestions, and grading assistance — will surface here.
          </p>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="Class Performance" subtitle="Average score by section" />
          {performanceChart.length === 0 ? (
            <p className="py-10 text-center text-sm text-text-muted">No performance data yet.</p>
          ) : (
            <BarChart data={performanceChart} tint={ACCENT} valueSuffix="%" />
          )}
        </Card>

        <Card>
          <CardHeader title="Today's Calendar" />
          <div className="space-y-3">
            {calendarEvents.length === 0 ? (
              <p className="py-6 text-center text-sm text-text-muted">Nothing scheduled for today.</p>
            ) : (
              calendarEvents.map((e) => (
                <div key={e.id} className="flex items-center gap-3">
                  <span className="w-16 shrink-0 text-xs font-medium text-text-muted">{formatTime(e.starts_at)}</span>
                  <span className="flex-1 truncate text-sm text-text-primary">{e.title}</span>
                  <Badge tone={e.event_type === 'class' ? 'info' : e.event_type === 'meeting' ? 'warning' : 'neutral'}>{e.event_type}</Badge>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>

      <Card>
        <CardHeader title="Homework Review Queue" />
        <div className="space-y-3">
          {homework.length === 0 ? (
            <p className="py-6 text-center text-sm text-text-muted">No homework awaiting review.</p>
          ) : (
            homework.map((hw) => (
              <div key={hw.id} className="rounded-xl bg-sunken/60 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-text-primary">{hw.title}</p>
                    <p className="text-xs text-text-muted">{hw.class_name} · Due {formatDue(hw.due_date)}</p>
                  </div>
                  <span className="text-xs font-medium text-text-secondary">{hw.submitted}/{hw.total} submitted</span>
                </div>
                <ProgressBar value={hw.total ? (hw.submitted / hw.total) * 100 : 0} tint={ACCENT} className="mt-2.5" />
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  );
}
