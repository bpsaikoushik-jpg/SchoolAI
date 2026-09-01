import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Users,
  CalendarCheck,
  TrendingUp,
  Sparkles,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Lightbulb,
} from 'lucide-react';

import {
  Card,
  CardHeader,
  StatCard,
  BarChart,
  Badge,
  ProgressBar,
} from '../../../components/ui';

import { useAuthStore } from '../../../store/useAuthStore';

import {
  useMyClasses,
  useAttendanceToday,
  useHomeworkQueue,
  useMyCalendarToday,
} from '../../../hooks/useTeacherInsights';

import api from '../../../services/api';

const ACCENT = 'var(--color-role-teacher)';

type AIInsightResponse = {
  data?: {
    class_summary?: unknown;
    weak_students?: unknown[];
    strong_students?: unknown[];
    homework_completion?: unknown;
    attendance_correlation?: unknown;
  };
  ai_summary?: string;
};

export function TeacherDashboard() {
  const user = useAuthStore((s) => s.user);

  const { data: classes } = useMyClasses();
  const { data: attendanceToday } = useAttendanceToday();
  const { data: homeworkQueue } = useHomeworkQueue();
  const { data: calendarToday } = useMyCalendarToday();

  const [selectedClassId, setSelectedClassId] = useState<string>('');
  const [aiData, setAiData] = useState<AIInsightResponse | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');

  const myClasses = classes ?? [];

  const totalStudents = myClasses.reduce(
    (sum, c) => sum + c.students,
    0
  );

  const avgPerformance = myClasses.length
    ? Math.round(
        myClasses.reduce((sum, c) => sum + c.avg_score, 0) /
          myClasses.length
      )
    : 0;

  const homework = homeworkQueue ?? [];

  const attendance = attendanceToday ?? {
    present: 0,
    absent: 0,
    late: 0,
  };

  const performanceChart = myClasses.map((c) => ({
    label: c.name,
    value: c.avg_score,
  }));

  const calendarEvents = [...(calendarToday ?? [])].sort(
    (a, b) =>
      new Date(a.starts_at).getTime() -
      new Date(b.starts_at).getTime()
  );

  const formatTime = (iso: string) =>
    new Date(iso).toLocaleTimeString(undefined, {
      hour: 'numeric',
      minute: '2-digit',
    });

  const formatDue = (iso: string | null) =>
    iso
      ? new Date(iso).toLocaleDateString(undefined, {
          month: 'short',
          day: 'numeric',
        })
      : '—';

  async function loadAIInsights(classId?: string) {
    const id = classId || selectedClassId;

    if (!id) {
      setAiError('Please select a class first.');
      return;
    }

    setAiLoading(true);
    setAiError('');

    try {
      const response = await api.get<AIInsightResponse>(
        '/teacher/ai-summary',
        {
          params: {
            class_id: id,
          },
        }
      );

      setAiData(response.data);
    } catch (error: any) {
      console.error('Teacher AI error:', error);

      const message =
        error?.response?.data?.detail ||
        error?.response?.data?.message ||
        'Unable to generate AI insights right now. Please try again.';

      setAiError(
        typeof message === 'string'
          ? message
          : 'Unable to generate AI insights right now.'
      );
      setAiData(null);
    } finally {
      setAiLoading(false);
    }
  }

  return (
    <div className="space-y-6">

      {/* --------------------------------------------------------- */}
      {/* WELCOME */}
      {/* --------------------------------------------------------- */}

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-3xl border border-border-subtle p-6 sm:p-8"
        style={{
          background: `linear-gradient(
            120deg,
            color-mix(in srgb, ${ACCENT} 12%, var(--surface-raised)),
            var(--surface-raised)
          )`,
        }}
      >
        <p className="text-sm text-text-muted">
          Welcome back,
        </p>

        <h1 className="mt-1 text-2xl font-bold text-text-primary sm:text-3xl">
          {user?.full_name ?? 'Teacher'} 👋
        </h1>

        <p className="mt-2 max-w-xl text-sm text-text-secondary">
          You're teaching {myClasses.length} classes with{' '}
          {totalStudents} students total. {homework.length} homework
          sets need review.
        </p>
      </motion.div>

      {/* --------------------------------------------------------- */}
      {/* STATS */}
      {/* --------------------------------------------------------- */}

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">

        <StatCard
          label="My Classes"
          value={myClasses.length}
          icon={Users}
          tint={ACCENT}
          index={0}
        />

        <StatCard
          label="Total Students"
          value={totalStudents}
          icon={Users}
          tint={ACCENT}
          index={1}
        />

        <StatCard
          label="Present Today"
          value={attendance.present}
          icon={CalendarCheck}
          tint={ACCENT}
          index={2}
        />

        <StatCard
          label="Avg. Performance"
          value={`${avgPerformance}%`}
          icon={TrendingUp}
          tint={ACCENT}
          index={3}
        />

      </div>

      {/* --------------------------------------------------------- */}
      {/* CLASSES + AI INSIGHTS */}
      {/* --------------------------------------------------------- */}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">

        {/* MY CLASSES */}

        <Card className="lg:col-span-2">

          <CardHeader
            title="My Classes"
            subtitle="Select a class to generate AI insights"
          />

          <div className="space-y-2.5">

            {myClasses.length === 0 ? (

              <p className="py-6 text-center text-sm text-text-muted">
                No classes assigned yet.
              </p>

            ) : (

              myClasses.map((c) => (

                <button
                  key={c.class_id}
                  type="button"
                  onClick={() => {
                    setSelectedClassId(c.class_id);
                    loadAIInsights(c.class_id);
                  }}
                  className={`flex w-full items-center justify-between rounded-xl px-4 py-3 text-left transition ${
                    selectedClassId === c.class_id
                      ? 'ring-2 ring-current'
                      : ''
                  } bg-sunken/60 hover:bg-sunken`}
                  style={
                    selectedClassId === c.class_id
                      ? { color: ACCENT }
                      : undefined
                  }
                >

                  <div>
                    <p className="text-sm font-medium text-text-primary">
                      {c.name}
                    </p>

                    <p className="text-xs text-text-muted">
                      {c.students} students
                    </p>
                  </div>

                  <Badge
                    tone={
                      c.avg_score >= 85
                        ? 'success'
                        : c.avg_score >= 75
                        ? 'warning'
                        : 'danger'
                    }
                  >
                    {Math.round(c.avg_score)}% avg
                  </Badge>

                </button>

              ))

            )}

          </div>

        </Card>

        {/* AI INSIGHTS */}

        <Card>

          <div className="flex items-center justify-between">

            <div className="flex items-center gap-2.5">

              <div
                className="grid h-10 w-10 place-items-center rounded-xl text-white"
                style={{ background: ACCENT }}
              >
                <Sparkles size={18} />
              </div>

              <div>
                <p className="text-sm font-semibold text-text-primary">
                  AI Insights
                </p>

                <Badge tone="success">
                  Gemini AI
                </Badge>
              </div>

            </div>

            {selectedClassId && (

              <button
                type="button"
                onClick={() => loadAIInsights()}
                disabled={aiLoading}
                className="rounded-lg p-2 text-text-muted transition hover:bg-sunken hover:text-text-primary disabled:opacity-50"
                title="Refresh AI insights"
              >
                <RefreshCw
                  size={17}
                  className={aiLoading ? 'animate-spin' : ''}
                />
              </button>

            )}

          </div>

          {/* NO CLASS */}

          {!selectedClassId && !aiLoading && (

            <div className="mt-5 rounded-xl bg-sunken/60 p-4">

              <div className="flex items-start gap-3">

                <Sparkles
                  size={18}
                  className="mt-0.5 shrink-0"
                  style={{ color: ACCENT }}
                />

                <div>

                  <p className="text-sm font-medium text-text-primary">
                    AI-powered class analysis
                  </p>

                  <p className="mt-1 text-xs leading-5 text-text-secondary">
                    Select one of your classes to let SchoolAI
                    analyze student performance, attendance,
                    homework completion, and learning patterns.
                  </p>

                </div>

              </div>

            </div>

          )}

          {/* LOADING */}

          {aiLoading && (

            <div className="mt-5 rounded-xl bg-sunken/60 p-5">

              <div className="flex items-center gap-3">

                <RefreshCw
                  size={20}
                  className="animate-spin"
                  style={{ color: ACCENT }}
                />

                <div>

                  <p className="text-sm font-medium text-text-primary">
                    Analyzing class data...
                  </p>

                  <p className="mt-1 text-xs text-text-muted">
                    Gemini is generating teaching insights.
                  </p>

                </div>

              </div>

            </div>

          )}

          {/* ERROR */}

          {aiError && !aiLoading && (

            <div className="mt-5 rounded-xl border border-red-500/20 bg-red-500/5 p-4">

              <div className="flex items-start gap-3">

                <AlertTriangle
                  size={18}
                  className="mt-0.5 shrink-0 text-red-400"
                />

                <div>

                  <p className="text-sm font-medium text-text-primary">
                    AI Insights unavailable
                  </p>

                  <p className="mt-1 text-xs leading-5 text-text-secondary">
                    {aiError}
                  </p>

                </div>

              </div>

            </div>

          )}

          {/* SUCCESS */}

          {aiData?.ai_summary && !aiLoading && (

            <div className="mt-5 space-y-4">

              <div className="rounded-xl bg-sunken/60 p-4">

                <div className="mb-3 flex items-center gap-2">

                  <Sparkles
                    size={16}
                    style={{ color: ACCENT }}
                  />

                  <p className="text-sm font-semibold text-text-primary">
                    AI Class Analysis
                  </p>

                </div>

                <div className="whitespace-pre-wrap text-xs leading-5 text-text-secondary">
                  {aiData.ai_summary}
                </div>

              </div>

              <div className="grid grid-cols-2 gap-2">

                <div className="rounded-xl bg-sunken/60 p-3">

                  <div className="flex items-center gap-2">

                    <AlertTriangle size={15} />

                    <span className="text-xs text-text-muted">
                      Weak Students
                    </span>

                  </div>

                  <p className="mt-1 text-lg font-semibold text-text-primary">
                    {Array.isArray(
                      aiData.data?.weak_students
                    )
                      ? aiData.data!.weak_students.length
                      : 0}
                  </p>

                </div>

                <div className="rounded-xl bg-sunken/60 p-3">

                  <div className="flex items-center gap-2">

                    <CheckCircle2 size={15} />

                    <span className="text-xs text-text-muted">
                      Strong Students
                    </span>

                  </div>

                  <p className="mt-1 text-lg font-semibold text-text-primary">
                    {Array.isArray(
                      aiData.data?.strong_students
                    )
                      ? aiData.data!.strong_students.length
                      : 0}
                  </p>

                </div>

              </div>

            </div>

          )}

        </Card>

      </div>

      {/* --------------------------------------------------------- */}
      {/* CLASS PERFORMANCE */}
      {/* --------------------------------------------------------- */}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">

        <Card className="lg:col-span-2">

          <CardHeader
            title="Class Performance"
            subtitle="Average score by section"
          />

          {performanceChart.length === 0 ? (

            <p className="py-10 text-center text-sm text-text-muted">
              No performance data yet.
            </p>

          ) : (

            <BarChart
              data={performanceChart}
              tint={ACCENT}
              valueSuffix="%"
            />

          )}

        </Card>

        {/* CALENDAR */}

        <Card>

          <CardHeader title="Today's Calendar" />

          <div className="space-y-3">

            {calendarEvents.length === 0 ? (

              <p className="py-6 text-center text-sm text-text-muted">
                Nothing scheduled for today.
              </p>

            ) : (

              calendarEvents.map((e) => (

                <div
                  key={e.id}
                  className="flex items-center gap-3"
                >

                  <span className="w-16 shrink-0 text-xs font-medium text-text-muted">
                    {formatTime(e.starts_at)}
                  </span>

                  <span className="flex-1 truncate text-sm text-text-primary">
                    {e.title}
                  </span>

                  <Badge
                    tone={
                      e.event_type === 'class'
                        ? 'info'
                        : e.event_type === 'meeting'
                        ? 'warning'
                        : 'neutral'
                    }
                  >
                    {e.event_type}
                  </Badge>

                </div>

              ))

            )}

          </div>

        </Card>

      </div>

      {/* --------------------------------------------------------- */}
      {/* HOMEWORK */}
      {/* --------------------------------------------------------- */}

      <Card>

        <CardHeader title="Homework Review Queue" />

        <div className="space-y-3">

          {homework.length === 0 ? (

            <p className="py-6 text-center text-sm text-text-muted">
              No homework awaiting review.
            </p>

          ) : (

            homework.map((hw) => (

              <div
                key={hw.id}
                className="rounded-xl bg-sunken/60 p-4"
              >

                <div className="flex items-center justify-between">

                  <div>

                    <p className="text-sm font-medium text-text-primary">
                      {hw.title}
                    </p>

                    <p className="text-xs text-text-muted">
                      {hw.class_name} · Due{' '}
                      {formatDue(hw.due_date)}
                    </p>

                  </div>

                  <span className="text-xs font-medium text-text-secondary">
                    {hw.submitted}/{hw.total} submitted
                  </span>

                </div>

                <ProgressBar
                  value={
                    hw.total
                      ? (hw.submitted / hw.total) * 100
                      : 0
                  }
                  tint={ACCENT}
                  className="mt-2.5"
                />

              </div>

            ))

          )}

        </div>

      </Card>

    </div>
  );
}
