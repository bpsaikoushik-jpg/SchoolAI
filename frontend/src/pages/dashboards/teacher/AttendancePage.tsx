import { Card, CardHeader, DonutChart, StatCard } from '../../../components/ui';
import { CalendarCheck, CalendarX, Clock } from 'lucide-react';
import { useAttendanceToday, useMyClasses } from '../../../hooks/useTeacherInsights';

export function AttendancePage() {
  const { data: attendanceToday } = useAttendanceToday();
  const { data: classes } = useMyClasses();
  const attendance = attendanceToday ?? { present: 0, absent: 0, late: 0 };
  const myClasses = classes ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Attendance</h1>
        <p className="text-sm text-text-muted">Today's attendance across your classes.</p>
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard label="Present" value={attendance.present} icon={CalendarCheck} tint="var(--color-mint-500)" />
        <StatCard label="Late" value={attendance.late} icon={Clock} tint="#f59e0b" />
        <StatCard label="Absent" value={attendance.absent} icon={CalendarX} tint="#f43f5e" />
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader title="Today's Breakdown" />
          <DonutChart
            data={[
              { label: 'Present', value: attendance.present, color: 'var(--color-mint-500)' },
              { label: 'Late', value: attendance.late, color: '#f59e0b' },
              { label: 'Absent', value: attendance.absent, color: '#f43f5e' },
            ]}
          />
        </Card>
        <Card className="lg:col-span-2">
          <CardHeader title="By Class" />
          <div className="space-y-2.5">
            {myClasses.length === 0 ? (
              <p className="py-6 text-center text-sm text-text-muted">No classes assigned yet.</p>
            ) : (
              myClasses.map((c) => (
                <div key={c.class_id} className="flex items-center justify-between rounded-xl bg-sunken/60 px-4 py-3 text-sm">
                  <span className="text-text-primary">{c.name}</span>
                  <span className="text-text-muted">{c.students} enrolled</span>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
