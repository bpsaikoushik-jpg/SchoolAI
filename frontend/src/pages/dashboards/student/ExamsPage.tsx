import { Card, Badge } from '../../../components/ui';
import { useMyResults } from '../../../hooks/useExams';

export function ExamsPage() {
  const { data: results, isLoading, isError } = useMyResults();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Exams</h1>
        <p className="text-sm text-text-muted">Your recorded exam results.</p>
      </div>
      <div className="space-y-3">
        {isLoading ? (
          <p className="text-sm text-text-muted">Loading exam results…</p>
        ) : isError ? (
          <p className="text-sm text-rose-500">Couldn't load exam results right now.</p>
        ) : (results ?? []).length === 0 ? (
          <Card className="py-10 text-center text-sm text-text-muted">
            No exam results recorded yet. They'll show up here as soon as a teacher publishes them.
          </Card>
        ) : (
          results!.map((r) => (
            <Card key={r.id} className="flex items-center justify-between">
              <div>
                <p className="font-medium text-text-primary">Exam result</p>
                <p className="text-sm text-text-muted">
                  {r.remarks || 'No remarks provided'}
                </p>
              </div>
              <Badge tone={r.score != null && r.score >= 50 ? 'success' : 'danger'}>
                {r.score != null ? `${r.score}` : 'Pending'}
              </Badge>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
