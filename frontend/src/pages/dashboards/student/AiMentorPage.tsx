import { useState } from 'react';
import {
  Sparkles,
  Send,
  Bot,
  User,
  BookOpen,
  Brain,
  Lightbulb,
  RefreshCw,
} from 'lucide-react';

import { Card, Button } from '../../../components/ui';
import { useMentorChat } from '../../../hooks/useMentor';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export function AiMentorPage() {
  const [message, setMessage] = useState('');
  const [subject, setSubject] = useState('');
  const [mode, setMode] = useState<'easy' | 'normal' | 'advanced'>('normal');

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content:
        "Hi! I'm your SchoolAI Mentor. 👋\n\nI can help you understand lessons, solve doubts, prepare for exams, create study plans, and practice difficult topics.\n\nWhat would you like to learn today?",
    },
  ]);

  const mentorChat = useMentorChat();

  const sendMessage = async (text?: string) => {
    const question = (text ?? message).trim();

    if (!question || mentorChat.isPending) {
      return;
    }

    setMessages((prev) => [
      ...prev,
      {
        role: 'user',
        content: question,
      },
    ]);

    setMessage('');

    try {
      const result = await mentorChat.mutateAsync({
        message: question,
        subject: subject || undefined,
        mode,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: result.response,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            'Sorry, I could not connect to the AI Mentor right now. Please try again in a moment.',
        },
      ]);
    }
  };

  const quickQuestions = [
    'Explain this topic in simple words',
    'Help me prepare for my exam',
    'Give me a study plan for today',
    'Quiz me on what I learned',
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div
              className="grid h-11 w-11 place-items-center rounded-xl text-white"
              style={{ background: 'var(--color-role-student)' }}
            >
              <Sparkles size={22} />
            </div>

            <div>
              <h1 className="text-2xl font-bold text-text-primary">
                AI Mentor
              </h1>

              <p className="text-sm text-text-muted">
                Your personalized SchoolAI study companion
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={mode}
            onChange={(e) =>
              setMode(e.target.value as 'easy' | 'normal' | 'advanced')
            }
            className="rounded-lg border border-border-subtle bg-surface px-3 py-2 text-sm text-text-primary outline-none"
          >
            <option value="easy">Easy Mode</option>
            <option value="normal">Normal Mode</option>
            <option value="advanced">Advanced Mode</option>
          </select>
        </div>
      </div>

      {/* Subject selector */}
      <Card>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="flex items-center gap-2 text-sm font-medium text-text-primary">
            <BookOpen size={17} />
            Subject
          </div>

          <select
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            className="flex-1 rounded-lg border border-border-subtle bg-surface px-3 py-2 text-sm text-text-primary outline-none"
          >
            <option value="">All Subjects</option>
            <option value="Mathematics">Mathematics</option>
            <option value="Science">Science</option>
            <option value="English">English</option>
            <option value="Social Studies">Social Studies</option>
          </select>
        </div>
      </Card>

      {/* Quick actions */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {quickQuestions.map((question, index) => {
          const icons = [Brain, BookOpen, Lightbulb, Sparkles];
          const Icon = icons[index];

          return (
            <button
              key={question}
              type="button"
              onClick={() => sendMessage(question)}
              disabled={mentorChat.isPending}
              className="rounded-xl border border-border-subtle bg-surface p-4 text-left transition hover:-translate-y-0.5 hover:shadow-lg disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Icon size={19} className="mb-2 text-text-primary" />

              <p className="text-sm font-medium text-text-primary">
                {question}
              </p>
            </button>
          );
        })}
      </div>

      {/* Chat */}
      <Card padded={false} className="overflow-hidden">
        {/* Chat header */}
        <div className="flex items-center justify-between border-b border-border-subtle p-4">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-full bg-blue-500/10 text-blue-500">
              <Bot size={20} />
            </div>

            <div>
              <p className="font-semibold text-text-primary">
                SchoolAI Mentor
              </p>

              <p className="text-xs text-text-muted">
                {mentorChat.isPending
                  ? 'Thinking...'
                  : 'Online • Ready to help'}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={() =>
              setMessages([
                {
                  role: 'assistant',
                  content:
                    "Fresh conversation started. 👋\n\nWhat would you like to learn today?",
                },
              ])
            }
            className="rounded-lg p-2 text-text-muted transition hover:bg-sunken hover:text-text-primary"
            title="New conversation"
          >
            <RefreshCw size={17} />
          </button>
        </div>

        {/* Messages */}
        <div className="min-h-[420px] max-h-[560px] space-y-5 overflow-y-auto p-5">
          {messages.map((item, index) => (
            <div
              key={index}
              className={`flex gap-3 ${
                item.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {item.role === 'assistant' && (
                <div className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-blue-500/10 text-blue-500">
                  <Bot size={18} />
                </div>
              )}

              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  item.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-sunken text-text-primary'
                }`}
              >
                <div className="flex items-center gap-2">
                  {item.role === 'user' && <User size={15} />}

                  <span className="text-xs font-semibold opacity-70">
                    {item.role === 'user' ? 'You' : 'AI Mentor'}
                  </span>
                </div>

                <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
                  {item.content}
                </p>
              </div>

              {item.role === 'user' && (
                <div className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-blue-600 text-white">
                  <User size={17} />
                </div>
              )}
            </div>
          ))}

          {mentorChat.isPending && (
            <div className="flex gap-3">
              <div className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-blue-500/10 text-blue-500">
                <Bot size={18} />
              </div>

              <div className="rounded-2xl bg-sunken px-4 py-3">
                <div className="flex items-center gap-2 text-sm text-text-muted">
                  <span className="animate-pulse">AI Mentor is thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-border-subtle p-4">
          <div className="flex gap-3">
            <input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              placeholder="Ask your AI Mentor anything..."
              disabled={mentorChat.isPending}
              className="flex-1 rounded-xl border border-border-subtle bg-surface px-4 py-3 text-sm text-text-primary outline-none transition focus:ring-2 focus:ring-blue-500/30 disabled:opacity-50"
            />

            <Button
              onClick={() => sendMessage()}
              disabled={!message.trim() || mentorChat.isPending}
              isLoading={mentorChat.isPending}
            >
              {!mentorChat.isPending && <Send size={17} />}
              <span className="hidden sm:inline">Send</span>
            </Button>
          </div>

          <p className="mt-2 text-center text-xs text-text-muted">
            SchoolAI Mentor uses your learning context to personalize
            responses.
          </p>
        </div>
      </Card>
    </div>
  );
}
