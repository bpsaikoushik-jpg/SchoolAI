import { Card, CardHeader, LineChart, StatCard, Badge } from '../../../components/ui';
import { Wallet } from 'lucide-react';
import { FOUNDER_REVENUE_TREND, FOUNDER_OVERVIEW } from '../../../data/mock/founder';

// Placeholder — no billing backend exists yet.
export function RevenuePage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Revenue</h1>
          <p className="text-sm text-text-muted">Monthly recurring revenue across all schools.</p>
        </div>
        <Badge tone="info">Placeholder data</Badge>
      </div>
      <StatCard label="MRR" value={`$${FOUNDER_OVERVIEW.mrr.toLocaleString()}`} icon={Wallet} tint="var(--color-role-founder)" trend={{ value: '6%', direction: 'up' }} />
      <Card>
        <CardHeader title="Trend" subtitle="Last 6 months" />
        <LineChart data={FOUNDER_REVENUE_TREND} tint="var(--color-role-founder)" />
      </Card>
    </div>
  );
}
