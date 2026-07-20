import { Users } from 'lucide-react';
import { Select } from '../../../components/ui/Select';
import { useSelectedChild } from '../../../hooks/useParent';

/**
 * Compact child selector shown at the top of every Parent Portal page.
 * Renders nothing when the parent has only one (or zero) linked children,
 * since there's nothing to switch between.
 */
export function ChildSwitcher() {
  const { children, selectedChildId, setSelectedChildId, isLoading } = useSelectedChild();

  if (isLoading || children.length <= 1) return null;

  return (
    <div className="flex items-center gap-2">
      <Users size={16} className="text-text-muted" />
      <Select
        aria-label="Select child"
        value={selectedChildId ?? ''}
        onChange={(e) => setSelectedChildId(e.target.value)}
        options={children.map((c) => ({
          value: c.student_id,
          label: c.full_name ?? 'Unnamed Student',
        }))}
        className="!py-2 text-sm"
      />
    </div>
  );
}
