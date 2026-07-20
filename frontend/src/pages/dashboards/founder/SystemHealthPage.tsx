import { Card, Badge } from '../../../components/ui';
import { FOUNDER_SYSTEM_HEALTH } from '../../../data/mock/founder';

export function SystemHealthPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">System Health</h1>
        <p className="text-sm text-text-muted">Live status of core platform services.</p>
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {FOUNDER_SYSTEM_HEALTH.map((s) => (
          <Card key={s.name} className="flex items-center justify-between">
            <div>
              <p className="font-medium text-text-primary">{s.name}</p>
              <p className="text-sm text-text-muted">Latency: {s.latency}</p>
            </div>
            <Badge tone={s.status === 'operational' ? 'success' : 'warning'}>{s.status}</Badge>
          </Card>
        ))}
      </div>
    </div>
  );
}
