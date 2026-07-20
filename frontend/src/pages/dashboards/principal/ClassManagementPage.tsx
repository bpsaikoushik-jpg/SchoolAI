import { useState } from 'react';
import { Plus, Pencil, Trash2, Users } from 'lucide-react';
import { Card, CardHeader, Button, Dialog, Input, FullPageSpinner, ErrorState, EmptyState, Badge } from '../../../components/ui';
import { useClassesBySchool, useCreateClass, useUpdateClass, useDeleteClass, useEnrollmentsByClass } from '../../../hooks/useAcademic';
import { usePrincipalSchoolId } from '../../../hooks/usePrincipal';
import type { SchoolClass } from '../../../types/academic';

const ACCENT = 'var(--color-role-principal)';

function ClassCard({ klass, onEdit, onDelete }: { klass: SchoolClass; onEdit: () => void; onDelete: () => void }) {
  const { data: enrollments } = useEnrollmentsByClass(klass.id);
  return (
    <Card>
      <CardHeader
        title={klass.name}
        action={<Badge tone="info"><Users size={12} className="mr-1 inline" />{(enrollments ?? []).length}</Badge>}
      />
      <div className="mt-3 flex justify-end gap-1">
        <button onClick={onEdit} className="grid h-8 w-8 place-items-center rounded-lg text-text-muted hover:bg-sunken hover:text-text-primary">
          <Pencil size={15} />
        </button>
        <button onClick={onDelete} className="grid h-8 w-8 place-items-center rounded-lg text-text-muted hover:bg-rose-500/10 hover:text-rose-500">
          <Trash2 size={15} />
        </button>
      </div>
    </Card>
  );
}

export function ClassManagementPage() {
  const schoolId = usePrincipalSchoolId();
  const { data: classes, isLoading, isError, refetch } = useClassesBySchool(schoolId);

  const createClass = useCreateClass();
  const updateClass = useUpdateClass();
  const deleteClass = useDeleteClass();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<SchoolClass | null>(null);
  const [name, setName] = useState('');

  function openCreate() {
    setEditing(null);
    setName('');
    setDialogOpen(true);
  }

  function openEdit(c: SchoolClass) {
    setEditing(c);
    setName(c.name);
    setDialogOpen(true);
  }

  function handleSave() {
    if (!name.trim()) return;
    if (editing) {
      updateClass.mutate({ classId: editing.id, payload: { name: name.trim() } }, { onSuccess: () => setDialogOpen(false) });
    } else if (schoolId) {
      createClass.mutate({ name: name.trim(), school_id: schoolId }, { onSuccess: () => setDialogOpen(false) });
    }
  }

  function handleDelete(c: SchoolClass) {
    if (window.confirm(`Delete "${c.name}"? This cannot be undone.`)) {
      deleteClass.mutate(c.id);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Class Management</h1>
          <p className="text-sm text-text-muted">Sections and sizes across the school.</p>
        </div>
        <Button onClick={openCreate}><Plus size={16} className="mr-1.5" /> Add class</Button>
      </div>

      {isLoading ? (
        <FullPageSpinner label="Loading classes…" />
      ) : isError ? (
        <ErrorState description="Couldn't load classes right now." onRetry={() => refetch()} />
      ) : (classes ?? []).length === 0 ? (
        <EmptyState title="No classes yet" description="Create your first class to start enrolling students." actionLabel="Add class" onAction={openCreate} />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {classes!.map((c) => (
            <ClassCard key={c.id} klass={c} onEdit={() => openEdit(c)} onDelete={() => handleDelete(c)} />
          ))}
        </div>
      )}

      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        title={editing ? 'Rename class' : 'Add class'}
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleSave} isLoading={createClass.isPending || updateClass.isPending} style={{ background: ACCENT }}>
              Save
            </Button>
          </div>
        }
      >
        <Input label="Class name" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Grade 9B" />
      </Dialog>
    </div>
  );
}
