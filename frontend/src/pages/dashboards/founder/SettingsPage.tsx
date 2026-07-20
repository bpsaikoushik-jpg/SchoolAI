import { Building2, Mail, ShieldCheck, User, Users, GraduationCap } from 'lucide-react';
import { Card, CardHeader, Badge, FullPageSpinner } from '../../../components/ui';
import { useAuthStore } from '../../../store/useAuthStore';
import { useOrgOverview } from '../../../hooks/useFounder';

const ACCENT = 'var(--color-role-founder)';

function InfoRow({ icon: Icon, label, value }: { icon: typeof User; label: string; value: string }) {
  return (
    <div className="flex items-center gap-3 py-2.5">
      <div className="grid h-9 w-9 place-items-center rounded-lg" style={{ background: `color-mix(in srgb, ${ACCENT} 14%, transparent)`, color: ACCENT }}>
        <Icon size={16} />
      </div>
      <div>
        <p className="text-xs text-text-muted">{label}</p>
        <p className="text-sm font-medium text-text-primary">{value || '—'}</p>
      </div>
    </div>
  );
}

export function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const { data: overview, isLoading } = useOrgOverview();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Settings</h1>
        <p className="text-sm text-text-muted">Your account and platform-wide details.</p>
      </div>

      <Card>
        <CardHeader title="Your profile" />
        <div className="divide-y divide-border-subtle">
          <InfoRow icon={User} label="Full name" value={user?.full_name ?? ''} />
          <InfoRow icon={Mail} label="Email" value={user?.email ?? ''} />
          <InfoRow icon={ShieldCheck} label="Role" value={user?.role ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : ''} />
        </div>
      </Card>

      <Card>
        <CardHeader title="Platform" action={<Badge tone="info">Read-only</Badge>} />
        {isLoading ? (
          <FullPageSpinner label="Loading platform details…" />
        ) : (
          <div className="divide-y divide-border-subtle">
            <InfoRow icon={Building2} label="Schools" value={`${overview?.active_schools ?? 0} active / ${overview?.total_schools ?? 0} total`} />
            <InfoRow icon={Users} label="Students" value={String(overview?.total_students ?? 0)} />
            <InfoRow icon={GraduationCap} label="Teachers" value={String(overview?.total_teachers ?? 0)} />
          </div>
        )}
        <p className="mt-4 text-xs text-text-muted">
          Platform-wide settings beyond school management aren't wired up to an API yet — this view is read-only for now.
        </p>
      </Card>
    </div>
  );
}
