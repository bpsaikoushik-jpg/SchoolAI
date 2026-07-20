import { Card, CardHeader, Badge } from '../../../components/ui';
import { useMyClasses } from '../../../hooks/useTeacherInsights';

export function ClassesPage() {
  const { data: classes } = useMyClasses();
  const myClasses = classes ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">My Classes</h1>
        <p className="text-sm text-text-muted">All sections you currently teach.</p>
      </div>
      {myClasses.length === 0 ? (
        <Card><p className="py-6 text-center text-sm text-text-muted">No classes assigned yet.</p></Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {myClasses.map((c) => (
            <Card key={c.class_id}>
              <CardHeader title={c.name} action={<Badge tone="info">{c.students} students</Badge>} />
              <p className="text-sm text-text-secondary">Average score</p>
              <p className="text-2xl font-semibold text-text-primary">{Math.round(c.avg_score)}%</p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
