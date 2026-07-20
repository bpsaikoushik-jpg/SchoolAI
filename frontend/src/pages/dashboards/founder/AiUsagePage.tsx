import { Card, CardHeader, BarChart, Badge } from '../../../components/ui';
import { FOUNDER_AI_USAGE } from '../../../data/mock/founder';

export function AiUsagePage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">AI Usage</h1>
          <p className="text-sm text-text-muted">Requests handled by the AI mentor platform-wide.</p>
        </div>
        <Badge tone="info">Placeholder data</Badge>
      </div>
      <Card>
        <CardHeader title="Requests This Week" />
        <BarChart data={FOUNDER_AI_USAGE} tint="var(--color-role-founder)" />
      </Card>
    </div>
  );
}
