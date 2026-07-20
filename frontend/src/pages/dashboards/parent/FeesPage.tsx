import { Card, CardHeader, Badge } from '../../../components/ui';
import { Receipt } from 'lucide-react';

// Placeholder — no billing/payments backend exists yet. This page is not
// part of the current Parent Portal completion scope; the amounts below
// are static placeholders (not user data) pending a future billing module.
const PLACEHOLDER_FEE_STATUS = { due: 450, dueDate: 'Aug 15' };

export function FeesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Fee Status</h1>
        <p className="text-sm text-text-muted">Tuition and billing overview.</p>
      </div>
      <Card className="max-w-lg border-dashed">
        <CardHeader
          title="Term 2 Tuition"
          action={<Badge tone="warning">Due {PLACEHOLDER_FEE_STATUS.dueDate}</Badge>}
        />
        <div className="flex items-center gap-4">
          <div className="grid h-12 w-12 place-items-center rounded-xl text-white" style={{ background: 'var(--color-role-parent)' }}>
            <Receipt size={22} />
          </div>
          <div>
            <p className="text-sm text-text-muted">Amount due</p>
            <p className="text-2xl font-semibold text-text-primary">${PLACEHOLDER_FEE_STATUS.due}</p>
          </div>
        </div>
        <p className="mt-4 text-xs text-text-muted">Placeholder — billing and payments will connect to a future backend module.</p>
      </Card>
    </div>
  );
}
