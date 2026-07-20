import { useState } from 'react';
import { Plus, Pencil, UserX } from 'lucide-react';
import {
  Card, Table, Badge, FilterBar, Button, Dialog, Input, Select,
  FullPageSpinner, ErrorState, EmptyState,
} from '../../../components/ui';
import type { Column } from '../../../components/ui';
import {
  useStudents, useCreateStudent, useUpdateStudent, useDeactivateStudent, usePrincipalSchoolId,
} from '../../../hooks/usePrincipal';
import { useClassesBySchool } from '../../../hooks/useAcademic';
import type { StudentManageItem } from '../../../types/principal';

const ACCENT = 'var(--color-role-principal)';

export function StudentManagementPage() {
  const schoolId = usePrincipalSchoolId();
  const [search, setSearch] = useState('');
  const [classFilter, setClassFilter] = useState('');
  const { data: students, isLoading, isError, refetch } = useStudents(search || undefined, classFilter || undefined);
  const { data: classes } = useClassesBySchool(schoolId);

  const createStudent = useCreateStudent();
  const updateStudent = useUpdateStudent();
  const deactivateStudent = useDeactivateStudent();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<StudentManageItem | null>(null);
  const [form, setForm] = useState({
    email: '', password: '', full_name: '', student_id_number: '', grade_level: '', class_id: '',
  });

  function openCreate() {
    setEditing(null);
    setForm({ email: '', password: '', full_name: '', student_id_number: '', grade_level: '', class_id: '' });
    setDialogOpen(true);
  }

  function openEdit(s: StudentManageItem) {
    setEditing(s);
    setForm({
      email: s.email, password: '', full_name: s.full_name ?? '',
      student_id_number: s.student_id_number ?? '', grade_level: s.grade_level != null ? String(s.grade_level) : '',
      class_id: s.class_id ?? '',
    });
    setDialogOpen(true);
  }

  function handleSave() {
    if (editing) {
      updateStudent.mutate(
        {
          userId: editing.user_id,
          payload: {
            full_name: form.full_name || undefined,
            student_id_number: form.student_id_number || undefined,
            grade_level: form.grade_level ? Number(form.grade_level) : undefined,
          },
        },
        { onSuccess: () => setDialogOpen(false) }
      );
    } else {
      createStudent.mutate(
        {
          email: form.email,
          password: form.password,
          full_name: form.full_name,
          student_id_number: form.student_id_number || undefined,
          grade_level: form.grade_level ? Number(form.grade_level) : undefined,
          class_id: form.class_id || undefined,
        },
        { onSuccess: () => setDialogOpen(false) }
      );
    }
  }

  const columns: Column<StudentManageItem>[] = [
    { key: 'full_name', header: 'Student', render: (r) => r.full_name ?? 'Unnamed student' },
    { key: 'email', header: 'Email' },
    { key: 'class_name', header: 'Class', render: (r) => r.class_name ?? '—' },
    { key: 'grade_level', header: 'Grade', render: (r) => r.grade_level ?? '—' },
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
              onClick={() => deactivateStudent.mutate(r.user_id)}
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

  const classOptions = [{ value: '', label: 'All classes' }, ...((classes ?? []).map((c) => ({ value: c.id, label: c.name })))];
  const formClassOptions = [{ value: '', label: 'No class yet' }, ...((classes ?? []).map((c) => ({ value: c.id, label: c.name })))];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Student Management</h1>
          <p className="text-sm text-text-muted">Everyone enrolled across the school.</p>
        </div>
        <Button onClick={openCreate}><Plus size={16} className="mr-1.5" /> Add student</Button>
      </div>

      <FilterBar searchValue={search} onSearchChange={setSearch} searchPlaceholder="Search students…">
        <Select value={classFilter} onChange={(e) => setClassFilter(e.target.value)} options={classOptions} className="w-44" />
      </FilterBar>

      <Card padded={false}>
        <div className="p-4">
          {isLoading ? (
            <FullPageSpinner label="Loading students…" />
          ) : isError ? (
            <ErrorState description="Couldn't load students right now." onRetry={() => refetch()} />
          ) : (students ?? []).length === 0 ? (
            <EmptyState title="No students found" description="Try a different search, or add your first student." actionLabel="Add student" onAction={openCreate} />
          ) : (
            <Table columns={columns} data={students!} keyField="user_id" />
          )}
        </div>
      </Card>

      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        title={editing ? 'Edit student' : 'Add student'}
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button
              onClick={handleSave}
              isLoading={createStudent.isPending || updateStudent.isPending}
              style={{ background: ACCENT }}
            >
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
          <Input label="Student ID number" value={form.student_id_number} onChange={(e) => setForm((f) => ({ ...f, student_id_number: e.target.value }))} />
          <Input label="Grade level" type="number" value={form.grade_level} onChange={(e) => setForm((f) => ({ ...f, grade_level: e.target.value }))} />
          {!editing && (
            <Select label="Class" value={form.class_id} onChange={(e) => setForm((f) => ({ ...f, class_id: e.target.value }))} options={formClassOptions} />
          )}
        </div>
      </Dialog>
    </div>
  );
}
