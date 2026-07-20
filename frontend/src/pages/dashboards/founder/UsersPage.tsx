import { useState } from 'react';
import { Users } from 'lucide-react';
import { Card, CardHeader, DonutChart, StatCard, Table, Badge, FilterBar, FullPageSpinner, ErrorState } from '../../../components/ui';
import type { Column } from '../../../components/ui';
import { useOrgOverview, useUserBreakdown, useOrgUsers } from '../../../hooks/useFounder';
import type { OrgUserItem } from '../../../types/founder';

const ACCENT = 'var(--color-role-founder)';

const ROLE_COLORS: Record<string, string> = {
  student: 'var(--color-role-student)',
  teacher: 'var(--color-role-teacher)',
  parent: 'var(--color-role-parent)',
  principal: 'var(--color-role-principal)',
  admin: ACCENT,
  founder: ACCENT,
};

const columns: Column<OrgUserItem>[] = [
  { key: 'full_name', header: 'Name', render: (r) => r.full_name ?? '—' },
  { key: 'email', header: 'Email' },
  { key: 'role', header: 'Role', render: (r) => <Badge tone="neutral">{r.role}</Badge> },
  { key: 'school_name', header: 'School', render: (r) => r.school_name ?? '—' },
  { key: 'is_active', header: 'Status', render: (r) => <Badge tone={r.is_active ? 'success' : 'neutral'}>{r.is_active ? 'Active' : 'Inactive'}</Badge> },
];

export function UsersPage() {
  const [search, setSearch] = useState('');
  const { data: overview } = useOrgOverview();
  const { data: breakdown } = useUserBreakdown();
  const { data: users, isLoading, isError, refetch } = useOrgUsers(undefined, search || undefined);

  const totalUsers = (overview?.total_students ?? 0) + (overview?.total_teachers ?? 0) + (overview?.total_parents ?? 0) + (overview?.total_staff ?? 0);
  const donutData = (breakdown ?? []).map((r) => ({
    label: r.role.charAt(0).toUpperCase() + r.role.slice(1),
    value: r.count,
    color: ROLE_COLORS[r.role] ?? ACCENT,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Users</h1>
        <p className="text-sm text-text-muted">Platform-wide user directory and role breakdown.</p>
      </div>

      <StatCard label="Total Users" value={totalUsers.toLocaleString()} icon={Users} tint={ACCENT} />

      <Card>
        <CardHeader title="By Role" />
        {donutData.length === 0 ? <p className="py-6 text-center text-sm text-text-muted">No users yet.</p> : <DonutChart data={donutData} />}
      </Card>

      <FilterBar searchValue={search} onSearchChange={setSearch} searchPlaceholder="Search users by name or email…" />

      <Card padded={false}>
        <div className="p-4">
          {isLoading ? (
            <FullPageSpinner label="Loading users…" />
          ) : isError ? (
            <ErrorState description="Couldn't load users right now." onRetry={() => refetch()} />
          ) : (users ?? []).length === 0 ? (
            <p className="py-8 text-center text-sm text-text-muted">No users match your search.</p>
          ) : (
            <Table columns={columns} data={users!.slice(0, 200)} keyField="user_id" />
          )}
        </div>
      </Card>
    </div>
  );
}
