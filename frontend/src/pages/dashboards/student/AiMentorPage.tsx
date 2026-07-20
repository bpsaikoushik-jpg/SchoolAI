import { Sparkles } from 'lucide-react';
import { Card, Badge } from '../../../components/ui';

// Placeholder screen only — per the brief, AI Mentor chat/voice/memory logic
// is explicitly out of scope for this pass.
export function AiMentorPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">AI Mentor</h1>
        <p className="text-sm text-text-muted">Your personalized study companion.</p>
      </div>
      <Card className="flex flex-col items-center gap-4 border-dashed py-16 text-center">
        <div className="grid h-14 w-14 place-items-center rounded-full text-white" style={{ background: 'var(--color-role-student)' }}>
          <Sparkles size={24} />
        </div>
        <div>
          <p className="font-semibold text-text-primary">AI Mentor is coming soon</p>
          <p className="mt-1 max-w-sm text-sm text-text-muted">
            This space is reserved for a future AI mentor experience — chat, voice, and adaptive guidance
            are intentionally not part of this dashboard framework release.
          </p>
        </div>
        <Badge tone="info">Placeholder</Badge>
      </Card>
    </div>
  );
}
