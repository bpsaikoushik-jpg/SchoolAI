import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchChildren, fetchAiSummary } from '../services/parent.service';
import { useParentStore } from '../store/useParentStore';

export function useChildren() {
  return useQuery({ queryKey: ['parent', 'children'], queryFn: fetchChildren });
}

/**
 * Resolves which child is "active" across the Parent Portal. Falls back to
 * the first linked child whenever no selection has been made yet, or the
 * previously-selected child is no longer in the list.
 */
export function useSelectedChild() {
  const { data: children, isLoading, isError, error } = useChildren();
  const selectedChildId = useParentStore((s) => s.selectedChildId);
  const setSelectedChildId = useParentStore((s) => s.setSelectedChildId);

  useEffect(() => {
    if (!children || children.length === 0) return;
    const stillValid = children.some((c) => c.student_id === selectedChildId);
    if (!stillValid) {
      setSelectedChildId(children[0].student_id);
    }
  }, [children, selectedChildId, setSelectedChildId]);

  const effectiveId = children?.some((c) => c.student_id === selectedChildId)
    ? selectedChildId
    : children?.[0]?.student_id ?? null;

  const selectedChild = children?.find((c) => c.student_id === effectiveId) ?? null;

  return {
    children: children ?? [],
    isLoading,
    isError,
    error,
    selectedChildId: effectiveId,
    selectedChild,
    setSelectedChildId,
  };
}

export function useAiSummary(studentId: string | null | undefined) {
  return useQuery({
    queryKey: ['parent', 'ai-summary', studentId],
    queryFn: () => fetchAiSummary(studentId ?? undefined),
    enabled: !!studentId,
  });
}
