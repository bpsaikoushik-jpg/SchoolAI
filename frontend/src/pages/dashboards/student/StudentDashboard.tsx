import { motion } from 'framer-motion';
import { CalendarCheck, ClipboardList, GraduationCap, Sparkles, TrendingUp } from 'lucide-react';
import { Card, CardHeader, StatCard, Badge, DonutChart, BarChart } from '../../../components/ui';
import { useAuthStore } from '../../../store/useAuthStore';
import { useMyHomework } from '../../../hooks/useHomework';
import { useAttendanceSummary } from '../../../hooks/useAttendance';
import { useMyUpcomingExams } from '../../../hooks/useExams';
import { useMySubjects } from '../../../hooks/useAcademic';
import { useMyStudyHours, useMyRecentActivity, useMyRecommendations } from '../../../hooks/useStudentMemory';
import { timeAgo } from '../../../utils/time';

const ACCENT = 'var(--color-role-student)';

export function StudentDashboard() {
  const user = useAuthStore((s) => s.user);
  const { data: homework } = useMyHomework();
  const { summary: attendance } = useAttendanceSummary();
  const { data: upcomingExams } = useMyUpcomingExams();
  const { data: subjects } = useMySubjects();
  const { data: studyHours } = useMyStudyHours(7);
  const { data: recentActivity } = useMyRecentActivity(6);
  const { data: recommendations } = useMyRecommendations();

  const todaysHomework = homework ?? [];
  const pendingHomework = todaysHomework.length;
  const exams = upcomingExams ?? [];
  const subjectNameById = new Map((subjects ?? []).map((s) => [s.id, s.name]));
  const daysUntil = (dateStr: string) => Math.max(0, Math.ceil((new Date(dateStr).getTime() - Date.now()) / 86400000));

  // Backend returns most-recent-first by date; chart reads left-to-right chronologically.
  const weeklyStudyHours = [...(studyHours ?? [])]
    .reverse()
    .map((d) => ({
      label: new Date(d.date).toLocaleDateString(undefined, { weekday: 'short' }),
      value: Math.round(d.hours_studied * 10) / 10,
    }));

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-3xl border border-border-subtle p-6 sm:p-8"
        style={{ background: `linear-gradient(120deg, color-mix(in srgb, ${ACCENT} 12%, var(--surface-raised)), var(--surface-raised))` }}
      >
        <p className="text-sm text-text-muted">Welcome back,</p>
        <h1 className="mt-1 text-2xl font-bold text-text-primary sm:text-3xl">{user?.full_name ?? 'Student'} 👋</h1>
        <p className="mt-2 max-w-xl text-sm text-text-secondary">
          You have {pendingHomework} homework item{pendingHomework === 1 ? '' : 's'} on record. Keep it up!
        </p>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Attendance" value={`${attendance.present}%`} icon={CalendarCheck} tint={ACCENT} index={0} />
        <StatCard label="Pending Homework" value={pendingHomework} icon={ClipboardList} tint={ACCENT} index={1} />
        <StatCard label="Upcoming Exams" value={exams.length} icon={GraduationCap} tint={ACCENT} index={2} />
        <StatCard label="Overall Grade" value="A-" icon={TrendingUp} tint={ACCENT} index={3} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* AI Mentor placeholder */}
        <Card className="lg:col-span-1 flex flex-col justify-between border-dashed">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="grid h-9 w-9 place-items-center rounded-xl text-white" style={{ background: ACCENT }}>
                <Sparkles size={17} />
              </div>
              <div>
                <p className="text-sm font-semibold text-text-primary">AI Mentor</p>
                <Badge tone="info">Coming soon</Badge>
              </div>
            </div>
            <p className="mt-4 text-sm text-text-secondary">
              Your personal AI mentor will live here — a 24/7 study companion tuned to how you learn.
              This panel is a placeholder reserved for that integration.
            </p>
          </div>
          <div className="mt-5 rounded-xl bg-sunken px-3 py-2.5 text-xs text-text-muted">Not yet connected to backend</div>
        </Card>

        {/* Homework on record */}
        <Card className="lg:col-span-2">
          <CardHeader title="Homework" subtitle={`${pendingHomework} on record`} />
          <div className="space-y-2.5">
            {todaysHomework.length === 0 ? (
              <p className="py-6 text-center text-sm text-text-muted">No homework assigned yet.</p>
            ) : (
              todaysHomework.slice(0, 5).map((hw) => (
                <div key={hw.id} className="flex items-center justify-between rounded-xl bg-sunken/60 px-4 py-3">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-text-primary">{hw.title}</p>
                    <p className="text-xs text-text-muted">
                      Due {hw.due_date ? new Date(hw.due_date).toLocaleDateString() : 'No due date'}
                    </p>
                  </div>
                  <Badge tone="warning">Pending</Badge>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Attendance */}
        <Card>
          <CardHeader title="Attendance" subtitle="This term" />
          <DonutChart
            centerValue={`${attendance.present}%`}
            centerLabel="Present"
            data={[
              { label: 'Present', value: attendance.present, color: 'var(--color-mint-500)' },
              { label: 'Late', value: attendance.late, color: '#f59e0b' },
              { label: 'Absent', value: attendance.absent, color: '#f43f5e' },
            ]}
          />
        </Card>

        {/* Upcoming Exams — resolved via enrollments → subjects → exams */}
        <Card>
          <CardHeader title="Upcoming Exams" />
          <div className="space-y-3">
            {exams.length === 0 ? (
              <p className="py-6 text-center text-sm text-text-muted">No upcoming exams scheduled.</p>
            ) : (
              exams.slice(0, 5).map((exam) => {
                const daysLeft = exam.date ? daysUntil(exam.date) : null;
                return (
                  <div key={exam.id} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-text-primary">{exam.title}</p>
                      <p className="text-xs text-text-muted">
                        {subjectNameById.get(exam.subject_id) ?? 'Subject'} ·{' '}
                        {exam.date ? new Date(exam.date).toLocaleDateString() : 'Date TBA'}
                      </p>
                    </div>
                    {daysLeft !== null && (
                      <Badge tone={daysLeft <= 5 ? 'danger' : 'neutral'}>{daysLeft}d</Badge>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </Card>

        {/* Recommended Study */}
        <Card>
          <CardHeader title="Recommended Study" subtitle="Personalized for you" />
          <div className="space-y-3">
            {(recommendations ?? []).length === 0 ? (
              <p className="py-6 text-center text-sm text-text-muted">No recommendations yet — keep studying and your AI mentor will suggest next steps.</p>
            ) : (
              (recommendations ?? []).slice(0, 4).map((rec) => (
                <div key={rec.id} className="rounded-xl bg-sunken/60 p-3">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-text-primary">{rec.title}</p>
                    <Badge tone={rec.priority === 'high' ? 'danger' : rec.priority === 'medium' ? 'warning' : 'neutral'}>{rec.priority}</Badge>
                  </div>
                  <p className="mt-1 text-xs text-text-muted">{rec.subject ?? rec.type.replace('_', ' ')}</p>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Study hours — from AI Memory Engine daily progress */}
        <Card className="lg:col-span-2">
          <CardHeader title="Study Hours" subtitle="Last 7 days" />
          {weeklyStudyHours.length === 0 ? (
            <p className="py-10 text-center text-sm text-text-muted">No study time logged yet this week.</p>
          ) : (
            <BarChart data={weeklyStudyHours} tint={ACCENT} valueSuffix="h" />
          )}
        </Card>

        {/* Recent Activity — aggregated from quiz attempts, submissions, and mistake log */}
        <Card>
          <CardHeader title="Recent Activity" />
          {(recentActivity ?? []).length === 0 ? (
            <p className="py-6 text-center text-sm text-text-muted">No recent activity yet.</p>
          ) : (
            <ul className="space-y-3">
              {(recentActivity ?? []).map((a) => (
                <li key={a.id} className="flex gap-3 text-sm">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: ACCENT }} />
                  <div>
                    <p className="text-text-primary">{a.text}</p>
                    <p className="text-xs text-text-muted">{timeAgo(a.timestamp)}</p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
