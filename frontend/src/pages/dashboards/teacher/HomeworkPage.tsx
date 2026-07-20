import { Card, ProgressBar } from '../../../components/ui';
import { useHomeworkQueue } from '../../../hooks/useTeacherInsights';

export function HomeworkPage() {
  const { data: homeworkQueue } = useHomeworkQueue(50);
  const homework = homeworkQueue ?? [];
  const formatDue = (iso: string | null) => (iso ? new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : '—');

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Homework</h1>
        <p className="text-sm text-text-muted">Assignments you've set, and submission progress.</p>
      </div>
      {homework.length === 0 ? (
        <Card><p className="py-6 text-center text-sm text-text-muted">No homework set yet.</p></Card>
      ) : (
        <div className="space-y-3">
          {homework.map((hw) => (
            <Card key={hw.id}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-text-primary">{hw.title}</p>
                  <p className="text-sm text-text-muted">{hw.class_name} · Due {formatDue(hw.due_date)}</p>
                </div>
                <span className="text-sm font-medium text-text-secondary">{hw.submitted}/{hw.total} submitted</span>
              </div>
              <ProgressBar value={hw.total ? (hw.submitted / hw.total) * 100 : 0} tint="var(--color-role-teacher)" className="mt-3" />
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
