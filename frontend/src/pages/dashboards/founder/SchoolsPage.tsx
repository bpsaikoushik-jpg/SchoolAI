import { useState } from 'react';
import { Plus, Pencil, Power, PowerOff } from 'lucide-react';
import {
  Card, Table, Badge, FilterBar, Button, Dialog, Input,
  FullPageSpinner, ErrorState, EmptyState,
} from '../../../components/ui';
import type { Column } from '../../../components/ui';
import {
  useSchools, useCreateSchool, useUpdateSchool, useActivateSchool, useDeactivateSchool,
} from '../../../hooks/useFounder';
import type { SchoolManageItem } from '../../../types/founder';

const ACCENT = 'var(--color-role-founder)';

function scoreTone(score: number | null) {
  if (score == null) return 'neutral' as const;
  if (score >= 75) return 'success' as const;
  if (score >= 55) return 'warning' as const;
  return 'danger' as const;
}

export function SchoolsPage() {
  const [search, setSearch] = useState('');
  const { data: schools, isLoading, isError, refetch } = useSchools(search || undefined, true);

  const createSchool = useCreateSchool();
  const updateSchool = useUpdateSchool();
  const activateSchool = useActivateSchool();
  const deactivateSchool = useDeactivateSchool();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<SchoolManageItem | null>(null);
  const [includePrincipal, setIncludePrincipal] = useState(false);
  const [form, setForm] = useState({
    name: '', address: '', phone: '', website: '',
    principal_email: '', principal_password: '', principal_full_name: '',
  });

  function openCreate() {
    setEditing(null);
    setIncludePrincipal(false);
    setForm({ name: '', address: '', phone: '', website: '', principal_email: '', principal_password: '', principal_full_name: '' });
    setDialogOpen(true);
  }

  function openEdit(s: SchoolManageItem) {
    setEditing(s);
    setIncludePrincipal(false);
    setForm({
      name: s.name, address: s.address ?? '', phone: s.phone ?? '', website: s.website ?? '',
      principal_email: '', principal_password: '', principal_full_name: '',
    });
    setDialogOpen(true);
  }

  function handleSave() {
    if (!form.name.trim()) return;
    if (editing) {
      updateSchool.mutate(
        {
          schoolId: editing.id,
          payload: {
            name: form.name.trim(),
            address: form.address || undefined,
            phone: form.phone || undefined,
            website: form.website || undefined,
          },
        },
        { onSuccess: () => setDialogOpen(false) }
      );
    } else {
      createSchool.mutate(
        {
          name: form.name.trim(),
          address: form.address || undefined,
          phone: form.phone || undefined,
          website: form.website || undefined,
          principal_email: includePrincipal ? form.principal_email || undefined : undefined,
          principal_password: includePrincipal ? form.principal_password || undefined : undefined,
          principal_full_name: includePrincipal ? form.principal_full_name || undefined : undefined,
        },
        { onSuccess: () => setDialogOpen(false) }
      );
    }
  }

  function handleToggleActive(s: SchoolManageItem) {
    if (s.is_active) {
      if (window.confirm(`Deactivate "${s.name}"? Its staff and students will keep their data, but the school will be marked inactive.`)) {
        deactivateSchool.mutate(s.id);
      }
    } else {
      activateSchool.mutate(s.id);
    }
  }

  const columns: Column<SchoolManageItem>[] = [
    {
      key: 'name', header: 'School',
      render: (r) => (
        <div>
          <p className="font-medium text-text-primary">{r.name}</p>
          {r.address && <p className="text-xs text-text-muted">{r.address}</p>}
        </div>
      ),
    },
    { key: 'total_students', header: 'Students' },
    { key: 'total_teachers', header: 'Teachers' },
    { key: 'total_classes', header: 'Classes' },
    {
      key: 'average_score', header: 'Average score',
      render: (r) => <Badge tone={scoreTone(r.average_score)}>{r.average_score != null ? `${r.average_score}%` : '—'}</Badge>,
    },
    {
      key: 'is_active', header: 'Status',
      render: (r) => <Badge tone={r.is_active ? 'success' : 'neutral'}>{r.is_active ? 'Active' : 'Inactive'}</Badge>,
    },
    {
      key: 'id', header: '',
      render: (r) => (
        <div className="flex justify-end gap-1">
          <button onClick={() => openEdit(r)} className="grid h-8 w-8 place-items-center rounded-lg text-text-muted hover:bg-sunken hover:text-text-primary">
            <Pencil size={15} />
          </button>
          <button
            onClick={() => handleToggleActive(r)}
            className={`grid h-8 w-8 place-items-center rounded-lg text-text-muted hover:text-text-primary ${r.is_active ? 'hover:bg-rose-500/10 hover:text-rose-500' : 'hover:bg-emerald-500/10 hover:text-emerald-500'}`}
            title={r.is_active ? 'Deactivate' : 'Activate'}
          >
            {r.is_active ? <PowerOff size={15} /> : <Power size={15} />}
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">School Management</h1>
          <p className="text-sm text-text-muted">Every school on the SchoolAI platform, compared side by side.</p>
        </div>
        <Button onClick={openCreate}><Plus size={16} className="mr-1.5" /> Add school</Button>
      </div>

      <FilterBar searchValue={search} onSearchChange={setSearch} searchPlaceholder="Search schools…" />

      <Card padded={false}>
        <div className="p-4">
          {isLoading ? (
            <FullPageSpinner label="Loading schools…" />
          ) : isError ? (
            <ErrorState description="Couldn't load schools right now." onRetry={() => refetch()} />
          ) : (schools ?? []).length === 0 ? (
            <EmptyState title="No schools yet" description="Add the first school on the platform to get started." actionLabel="Add school" onAction={openCreate} />
          ) : (
            <Table columns={columns} data={schools!} keyField="id" />
          )}
        </div>
      </Card>

      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        title={editing ? 'Edit school' : 'Add school'}
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button
              onClick={handleSave}
              isLoading={createSchool.isPending || updateSchool.isPending}
              style={{ background: ACCENT }}
            >
              Save
            </Button>
          </div>
        }
      >
        <div className="space-y-4">
          <Input label="School name" value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} placeholder="e.g. Lincoln High School" />
          <Input label="Address" value={form.address} onChange={(e) => setForm((f) => ({ ...f, address: e.target.value }))} />
          <Input label="Phone" value={form.phone} onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))} />
          <Input label="Website" value={form.website} onChange={(e) => setForm((f) => ({ ...f, website: e.target.value }))} />

          {!editing && (
            <div className="rounded-xl border border-border-subtle p-3">
              <button
                type="button"
                onClick={() => setIncludePrincipal((v) => !v)}
                className="text-sm font-medium"
                style={{ color: ACCENT }}
              >
                {includePrincipal ? '− Skip principal account' : '+ Also create a Principal account'}
              </button>
              {includePrincipal && (
                <div className="mt-3 space-y-3">
                  <Input label="Principal name" value={form.principal_full_name} onChange={(e) => setForm((f) => ({ ...f, principal_full_name: e.target.value }))} />
                  <Input label="Principal email" type="email" value={form.principal_email} onChange={(e) => setForm((f) => ({ ...f, principal_email: e.target.value }))} />
                  <Input label="Temporary password" type="password" value={form.principal_password} onChange={(e) => setForm((f) => ({ ...f, principal_password: e.target.value }))} />
                </div>
              )}
            </div>
          )}
        </div>
      </Dialog>
    </div>
  );
}
