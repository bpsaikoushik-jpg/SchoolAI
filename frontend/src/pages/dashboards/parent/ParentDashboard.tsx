import { motion } from 'framer-motion';
import { CalendarCheck, ClipboardList, Sparkles, TrendingUp } from 'lucide-react';
import { Card, CardHeader, StatCard, LineChart, Badge, Avatar, FullPageSpinner, EmptyState } from '../../../components/ui';
import { useAuthStore } from '../../../store/useAuthStore';
import { useSelectedChild, useAiSummary } from '../../../hooks/useParent';
import { useStudentHomework } from '../../../hooks/useHomework';
import { useStudentResults } from '../../../hooks/useExams';
import { ChildSwitcher } from './ChildSwitcher';

const ACCENT = 'var(--color-role-parent)';

export function ParentDashboard() {
  const user = useAuthStore((s) => s.user);
  const { children, selectedChild, selectedChildId, isLoading: loadingChildren } = useSelectedChild();
  const { data: summary, isLoading: loadingSummary } = useAiSummary(selectedChildId);
  const { data: homework } = useStudentHomework(selectedChildId ?? undefined);
  const { data: results } = useStudentResults(selectedChildId ?? undefined);

  if (loadingChildren) return <FullPageSpinner label="Loading your children…" />;

  if (children.length === 0) {
    return (
      <EmptyState
        title="No children linked to your account yet"
        description="Once the school links your account to your child's profile, their dashboard will appear here."
      />
    );
  }

  const attendanceRate = summary?.data.attendance.attendance_rate;
  const pendingHomework = summary?.data.pending_homework_count ?? (homework ?? []).length;
  const knowledgeLevel = summary?.data.progress.knowledge_level;

  const scoreTrend = (results ?? [])
    .filter((r) => r.score != null)
    .slice(-8)
    .map((r, i) => ({ label: `#${i + 1}`, value: r.score as number }));

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-3xl border border-border-subtle p-6 sm:p-8"
        style={{ background: `linear-gradient(120deg, color-mix(in srgb, ${ACCENT} 12%, var(--surface-raised)), var(--surface-raised))` }}
      >
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm text-text-muted">Welcome back,</p>
            <h1 className="mt-1 text-2xl font-bold text-text-primary sm:text-3xl">{user?.full_name ?? 'Parent'} 👋</h1>
            <p className="mt-2 max-w-xl text-sm text-text-secondary">
              Here's how {selectedChild?.full_name ?? 'your child'} is doing this term.
            </p>
          </div>
          <ChildSwitcher />
        </div>
      </motion.div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Knowledge Level" value={knowledgeLevel ?? '—'} icon={TrendingUp} tint={ACCENT} index={0} />
        <StatCard label="Attendance" value={attendanceRate != null ? `${Math.round(attendanceRate)}%` : '—'} icon={CalendarCheck} tint={ACCENT} index={1} />
        <StatCard label="Pending Homework" value={pendingHomework} icon={ClipboardList} tint={ACCENT} index={2} />
        <StatCard label="Grade Level" value={selectedChild?.grade_level ?? '—'} icon={Sparkles} tint={ACCENT} index={3} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="Recent Exam Scores" subtitle={`${selectedChild?.full_name ?? ''}`} />
          {scoreTrend.length === 0 ? (
            <p className="py-8 text-center text-sm text-text-muted">No exam results recorded yet.</p>
          ) : (
            <LineChart data={scoreTrend} tint={ACCENT} />
          )}
        </Card>

        <Card className="border-dashed">
          <div className="flex items-center gap-2.5">
            <div className="grid h-9 w-9 place-items-center rounded-xl text-white" style={{ background: ACCENT }}>
              <Sparkles size={17} />
            </div>
            <div>
              <p className="text-sm font-semibold text-text-primary">AI Report</p>
              <Badge tone="info">{loadingSummary ? 'Generating…' : 'Live'}</Badge>
            </div>
          </div>
          <p className="mt-4 text-sm text-text-secondary">
            {loadingSummary
              ? 'Putting together a plain-language summary of strengths, growth areas, and how to help at home…'
              : summary?.ai_summary ?? 'No AI summary available yet.'}
          </p>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Homework" subtitle="Currently assigned" />
          {(homework ?? []).length === 0 ? (
            <p className="py-6 text-center text-sm text-text-muted">Nothing assigned right now.</p>
          ) : (
            <div className="space-y-2.5">
              {(homework ?? []).slice(0, 5).map((hw) => (
                <div key={hw.id} className="flex items-center justify-between rounded-xl bg-sunken/60 px-4 py-3">
                  <div>
                    <p className="text-sm font-medium text-text-primary">{hw.title}</p>
                    <p className="text-xs text-text-muted">
                      Due {hw.due_date ? new Date(hw.due_date).toLocaleDateString() : 'No due date'}
                    </p>
                  </div>
                  <Badge tone="warning">Pending</Badge>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card>
          <CardHeader title={selectedChild?.full_name ?? 'Child'} subtitle="Quick profile" />
          <div className="flex items-center gap-4">
            <Avatar name={selectedChild?.full_name ?? undefined} size={56} ringColor={ACCENT} />
            <div>
              <p className="font-medium text-text-primary">{selectedChild?.full_name}</p>
              <p className="text-sm text-text-muted">
                {selectedChild?.grade_level != null ? `Grade ${selectedChild.grade_level}` : 'Grade not set'} · {selectedChild?.relationship_type}
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
