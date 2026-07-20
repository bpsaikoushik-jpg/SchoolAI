import { Card, Badge } from '../../../components/ui';
import { FOUNDER_LOGS } from '../../../data/mock/founder';

export function LogsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Logs</h1>
        <p className="text-sm text-text-muted">Recent platform activity.</p>
      </div>
      <Card padded={false}>
        <div className="divide-y divide-border-subtle">
          {FOUNDER_LOGS.map((log) => (
            <div key={log.id} className="flex items-center gap-3 px-5 py-3.5 text-sm">
              <Badge tone={log.level === 'error' ? 'danger' : log.level === 'warn' ? 'warning' : 'neutral'}>{log.level}</Badge>
              <span className="flex-1 text-text-primary">{log.message}</span>
              <span className="text-xs text-text-muted">{log.time}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
