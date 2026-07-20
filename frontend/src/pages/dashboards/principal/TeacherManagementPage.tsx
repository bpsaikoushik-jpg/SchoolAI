import { useState } from 'react';
import { Plus, Pencil, UserX } from 'lucide-react';
import {
  Card, Table, Badge, FilterBar, Button, Dialog, Input,
  FullPageSpinner, ErrorState, EmptyState,
} from '../../../components/ui';
import type { Column } from '../../../components/ui';
import { useTeachers, useCreateTeacher, useUpdateTeacher, useDeactivateTeacher } from '../../../hooks/usePrincipal';
import type { TeacherManageItem } from '../../../types/principal';

const ACCENT = 'var(--color-role-principal)';

export function TeacherManagementPage() {
  const [search, setSearch] = useState('');
  const { data: teachers, isLoading, isError, refetch } = useTeachers(search || undefined);

  const createTeacher = useCreateTeacher();
  const updateTeacher = useUpdateTeacher();
  const deactivateTeacher = useDeactivateTeacher();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<TeacherManageItem | null>(null);
  const [form, setForm] = useState({ email: '', password: '', full_name: '', employee_id: '', specialization: '' });

  function openCreate() {
    setEditing(null);
    setForm({ email: '', password: '', full_name: '', employee_id: '', specialization: '' });
    setDialogOpen(true);
  }

  function openEdit(t: TeacherManageItem) {
    setEditing(t);
    setForm({
      email: t.email, password: '', full_name: t.full_name ?? '',
      employee_id: t.employee_id ?? '', specialization: t.specialization ?? '',
    });
    setDialogOpen(true);
  }

  function handleSave() {
    if (editing) {
      updateTeacher.mutate(
        {
          userId: editing.user_id,
          payload: {
            full_name: form.full_name || undefined,
            employee_id: form.employee_id || undefined,
            specialization: form.specialization || undefined,
          },
        },
        { onSuccess: () => setDialogOpen(false) }
      );
    } else {
      createTeacher.mutate(
        {
          email: form.email, password: form.password, full_name: form.full_name,
          employee_id: form.employee_id || undefined, specialization: form.specialization || undefined,
        },
        { onSuccess: () => setDialogOpen(false) }
      );
    }
  }

  const columns: Column<TeacherManageItem>[] = [
    { key: 'full_name', header: 'Teacher', render: (r) => r.full_name ?? 'Unnamed teacher' },
    { key: 'email', header: 'Email' },
    { key: 'specialization', header: 'Specialization', render: (r) => r.specialization ?? '—' },
    { key: 'subjects_count', header: 'Subjects', render: (r) => r.subjects_count },
    {
      key: 'is_active', header: 'Status',
      render: (r) => <Badge tone={r.is_active ? 'success' : 'neutral'}>{r.is_active ? 'Active' : 'Inactive'}</Badge>,
    },
    {
      key: 'user_id', header: '',
      render: (r) => (
        <div className="flex justify-end gap-1">
          <button onClick={() => openEdit(r)} className="grid h-8 w-8 place-items-center rounded-lg text-text-muted hover:bg-sunken hover:text-text-primary">
            <Pencil size={15} />
          </button>
          {r.is_active && (
            <button
              onClick={() => deactivateTeacher.mutate(r.user_id)}
              className="grid h-8 w-8 place-items-center rounded-lg text-text-muted hover:bg-rose-500/10 hover:text-rose-500"
              title="Deactivate"
            >
              <UserX size={15} />
            </button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Teacher Management</h1>
          <p className="text-sm text-text-muted">Faculty roster for the school.</p>
        </div>
        <Button onClick={openCreate}><Plus size={16} className="mr-1.5" /> Add teacher</Button>
      </div>

      <FilterBar searchValue={search} onSearchChange={setSearch} searchPlaceholder="Search teachers…" />

      <Card padded={false}>
        <div className="p-4">
          {isLoading ? (
            <FullPageSpinner label="Loading teachers…" />
          ) : isError ? (
            <ErrorState description="Couldn't load teachers right now." onRetry={() => refetch()} />
          ) : (teachers ?? []).length === 0 ? (
            <EmptyState title="No teachers found" description="Try a different search, or add your first teacher." actionLabel="Add teacher" onAction={openCreate} />
          ) : (
            <Table columns={columns} data={teachers!} keyField="user_id" />
          )}
        </div>
      </Card>

      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        title={editing ? 'Edit teacher' : 'Add teacher'}
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleSave} isLoading={createTeacher.isPending || updateTeacher.isPending} style={{ background: ACCENT }}>
              Save
            </Button>
          </div>
        }
      >
        <div className="space-y-4">
          <Input label="Full name" value={form.full_name} onChange={(e) => setForm((f) => ({ ...f, full_name: e.target.value }))} />
          {!editing && (
            <>
              <Input label="Email" type="email" value={form.email} onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))} />
              <Input label="Temporary password" type="password" value={form.password} onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))} />
            </>
          )}
          <Input label="Employee ID" value={form.employee_id} onChange={(e) => setForm((f) => ({ ...f, employee_id: e.target.value }))} />
          <Input label="Specialization" value={form.specialization} onChange={(e) => setForm((f) => ({ ...f, specialization: e.target.value }))} />
        </div>
      </Dialog>
    </div>
  );
}
