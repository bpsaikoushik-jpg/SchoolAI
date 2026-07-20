import { Sparkles, RefreshCw, AlertTriangle } from 'lucide-react';
import { Card, CardHeader, Badge, Button, FullPageSpinner, ErrorState } from '../../../components/ui';
import { usePrincipalAISummary } from '../../../hooks/usePrincipal';

const ACCENT = 'var(--color-role-principal)';

export function AiAssistantPage() {
  const { data, isLoading, isError, refetch, isFetching } = usePrincipalAISummary();

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">AI Principal Assistant</h1>
          <p className="text-sm text-text-muted">An AI-written executive summary grounded in live school data.</p>
        </div>
        <Button variant="outline" onClick={() => refetch()} isLoading={isFetching}>
          <RefreshCw size={15} className="mr-1.5" /> Refresh
        </Button>
      </div>

      {isLoading ? (
        <FullPageSpinner label="Analyzing school performance…" />
      ) : isError ? (
        <ErrorState description="Couldn't generate insights right now." onRetry={() => refetch()} />
      ) : (
        <>
          <Card padded={false} className="overflow-hidden">
            <div className="border-b border-border-subtle p-4">
              <div className="flex items-center gap-2.5">
                <div className="grid h-9 w-9 place-items-center rounded-xl text-white" style={{ background: ACCENT }}>
                  <Sparkles size={17} />
                </div>
                <CardHeader title="Executive summary" subtitle="Generated from current school, class, subject, and teacher performance." />
              </div>
            </div>
            <div className="p-5">
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-text-secondary">
                {data?.ai_recommendations ?? 'No recommendations available yet.'}
              </p>
            </div>
          </Card>

          <Card>
            <CardHeader title="Risk flags" subtitle="Classes or trends that may need attention." />
            {!data?.data.risk_flags || data.data.risk_flags.length === 0 ? (
              <p className="py-4 text-center text-sm text-text-muted">No risks detected right now.</p>
            ) : (
              <div className="space-y-3">
                {data.data.risk_flags.map((risk, i) => (
                  <div key={i} className="flex items-start gap-3 rounded-xl bg-sunken/60 p-4">
                    <div className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-rose-500/10 text-rose-500">
                      <AlertTriangle size={16} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <Badge tone="danger">{String(risk.type ?? 'risk').replace(/_/g, ' ')}</Badge>
                      <pre className="mt-2 whitespace-pre-wrap break-words text-xs text-text-muted">
                        {JSON.stringify(risk, null, 2)}
                      </pre>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Card>
              <p className="text-xs text-text-muted">AI conversations</p>
              <p className="mt-1 text-2xl font-semibold text-text-primary">{data?.data.ai_usage.total_conversations ?? 0}</p>
            </Card>
            <Card>
              <p className="text-xs text-text-muted">Quiz attempts</p>
              <p className="mt-1 text-2xl font-semibold text-text-primary">{data?.data.ai_usage.total_quiz_attempts ?? 0}</p>
            </Card>
            <Card>
              <p className="text-xs text-text-muted">Active students</p>
              <p className="mt-1 text-2xl font-semibold text-text-primary">{data?.data.ai_usage.active_students ?? 0}</p>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
