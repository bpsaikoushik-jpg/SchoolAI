import { useState } from 'react';
import { Card, Table, Badge, FilterBar, Pagination } from '../../../components/ui';
import type { Column } from '../../../components/ui';
import { useMyStudents } from '../../../hooks/useTeacherInsights';

interface Row { id: string; name: string; grade: string; attendance: string; className: string }

const columns: Column<Row>[] = [
  { key: 'name', header: 'Student' },
  { key: 'className', header: 'Class' },
  { key: 'grade', header: 'Avg. Score', render: (r) => <Badge tone={r.grade === '—' ? 'neutral' : Number(r.grade) >= 80 ? 'success' : Number(r.grade) >= 60 ? 'warning' : 'danger'}>{r.grade}{r.grade === '—' ? '' : '%'}</Badge> },
  { key: 'attendance', header: 'Attendance', render: (r) => r.attendance },
];

export function StudentsPage() {
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(1);
  const { data: students } = useMyStudents();

  const rows: Row[] = (students ?? []).map((s) => ({
    id: s.student_id,
    name: s.full_name ?? 'Unnamed student',
    grade: s.average_score > 0 ? String(Math.round(s.average_score)) : '—',
    attendance: s.attendance_rate != null ? `${Math.round(s.attendance_rate)}%` : '—',
    className: s.class_name,
  }));
  const filtered = rows.filter((s) => s.name.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Students</h1>
        <p className="text-sm text-text-muted">Everyone enrolled across your classes.</p>
      </div>
      <FilterBar searchValue={query} onSearchChange={setQuery} searchPlaceholder="Search students…" />
      <Card padded={false}>
        <div className="p-4">
          {filtered.length === 0 ? (
            <p className="py-6 text-center text-sm text-text-muted">No students found.</p>
          ) : (
            <>
              <Table columns={columns} data={filtered} keyField="id" />
              <Pagination page={page} totalPages={1} onPageChange={setPage} />
            </>
          )}
        </div>
      </Card>
    </div>
  );
}
