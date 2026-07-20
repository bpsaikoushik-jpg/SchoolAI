import { useState, useRef, useEffect } from 'react';
import { Sparkles, Send, Loader2, TrendingUp, BookOpen, CalendarCheck } from 'lucide-react';
import { Card, CardHeader, FullPageSpinner, EmptyState } from '../../../components/ui';
import { useSelectedChild, useAiSummary } from '../../../hooks/useParent';
import { useMentorChat } from '../../../hooks/useMentor';
import { ChildSwitcher } from './ChildSwitcher';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  text: string;
}

const SUGGESTED_PROMPTS = [
  'How is my child doing this month?',
  'What subjects need more attention?',
  'Is there any homework overdue?',
  'How should I help them prepare for the next exam?',
];

export function AiAssistantPage() {
  const { children, selectedChild, selectedChildId, isLoading: loadingChildren } = useSelectedChild();
  const { data: summary, isLoading: loadingSummary } = useAiSummary(selectedChildId);
  const chat = useMentorChat();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMessages([]);
  }, [selectedChildId]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, chat.isPending]);

  if (loadingChildren) return <FullPageSpinner label="Loading your children…" />;
  if (children.length === 0) {
    return <EmptyState title="No children linked to your account yet" description="Once the school links your account to your child's profile, the AI assistant will be available here." />;
  }

  function send(text: string) {
    const trimmed = text.trim();
    if (!trimmed || !selectedChildId) return;
    const userMsg: ChatMessage = { id: crypto.randomUUID(), role: 'user', text: trimmed };
    setMessages((m) => [...m, userMsg]);
    setInput('');
    chat.mutate(
      { student_id: selectedChildId, message: trimmed },
      {
        onSuccess: (res) => {
          setMessages((m) => [...m, { id: crypto.randomUUID(), role: 'assistant', text: res.response }]);
        },
        onError: () => {
          setMessages((m) => [
            ...m,
            { id: crypto.randomUUID(), role: 'assistant', text: "I couldn't reach the assistant just now. Please try again in a moment." },
          ]);
        },
      },
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">AI Assistant</h1>
          <p className="text-sm text-text-muted">Ask anything about {selectedChild?.full_name ?? 'your child'}'s progress.</p>
        </div>
        <ChildSwitcher />
      </div>

      {!loadingSummary && summary && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Card className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-xl text-white" style={{ background: 'var(--color-role-parent)' }}>
              <TrendingUp size={18} />
            </div>
            <div>
              <p className="text-xs text-text-muted">Knowledge level</p>
              <p className="font-medium text-text-primary">{summary.data.progress.knowledge_level ?? 'Not yet assessed'}</p>
            </div>
          </Card>
          <Card className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-xl text-white" style={{ background: 'var(--color-role-parent)' }}>
              <BookOpen size={18} />
            </div>
            <div>
              <p className="text-xs text-text-muted">Pending homework</p>
              <p className="font-medium text-text-primary">{summary.data.pending_homework_count}</p>
            </div>
          </Card>
          <Card className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-xl text-white" style={{ background: 'var(--color-role-parent)' }}>
              <CalendarCheck size={18} />
            </div>
            <div>
              <p className="text-xs text-text-muted">Attendance rate</p>
              <p className="font-medium text-text-primary">
                {summary.data.attendance.attendance_rate != null ? `${summary.data.attendance.attendance_rate}%` : '—'}
              </p>
            </div>
          </Card>
        </div>
      )}

      <Card padded={false} className="flex flex-col" style={{ height: 520 }}>
        <div className="border-b border-border-subtle p-4">
          <CardHeader
            title="Chat"
            subtitle="Grounded in your child's live academic, attendance, and homework data."
          />
        </div>

        <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-4">
          {messages.length === 0 && (
            <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
              <div className="grid h-12 w-12 place-items-center rounded-full text-white" style={{ background: 'var(--color-role-parent)' }}>
                <Sparkles size={22} />
              </div>
              <div>
                <p className="font-medium text-text-primary">Ask about {selectedChild?.full_name ?? 'your child'}</p>
                <p className="mt-1 max-w-sm text-sm text-text-muted">
                  {summary?.ai_summary ?? "I can help you understand progress, attendance, homework, and exam readiness."}
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-2">
                {SUGGESTED_PROMPTS.map((p) => (
                  <button
                    key={p}
                    onClick={() => send(p)}
                    className="rounded-full border border-border-subtle px-3 py-1.5 text-xs text-text-secondary hover:bg-sunken"
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m) => (
            <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm ${
                  m.role === 'user'
                    ? 'text-white'
                    : 'border border-border-subtle bg-sunken text-text-primary'
                }`}
                style={m.role === 'user' ? { background: 'var(--color-role-parent)' } : undefined}
              >
                {m.text}
              </div>
            </div>
          ))}

          {chat.isPending && (
            <div className="flex justify-start">
              <div className="flex items-center gap-2 rounded-2xl border border-border-subtle bg-sunken px-4 py-2.5 text-sm text-text-muted">
                <Loader2 size={14} className="animate-spin" /> Thinking…
              </div>
            </div>
          )}
        </div>

        <form
          className="flex items-center gap-2 border-t border-border-subtle p-3"
          onSubmit={(e) => {
            e.preventDefault();
            send(input);
          }}
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={`Ask about ${selectedChild?.full_name ?? 'your child'}…`}
            className="flex-1 rounded-xl border border-border-subtle bg-transparent px-3 py-2 text-sm outline-none focus:border-[var(--color-role-parent)]"
          />
          <button
            type="submit"
            disabled={!input.trim() || chat.isPending}
            className="grid h-9 w-9 shrink-0 place-items-center rounded-xl text-white disabled:opacity-40"
            style={{ background: 'var(--color-role-parent)' }}
          >
            <Send size={16} />
          </button>
        </form>
      </Card>
    </div>
  );
}
