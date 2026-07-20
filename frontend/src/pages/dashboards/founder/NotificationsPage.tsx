import { useState } from 'react';
import { Megaphone } from 'lucide-react';
import { Button, Dialog, Input, Select } from '../../../components/ui';
import { SharedNotificationsPage } from '../../shared/SharedNotificationsPage';
import { useOrgUsers } from '../../../hooks/useFounder';
import { broadcastAnnouncement } from '../../../services/notification.service';
import { useQueryClient } from '@tanstack/react-query';

const ACCENT = 'var(--color-role-founder)';

const AUDIENCE_OPTIONS = [
  { value: 'all', label: 'Everyone' },
  { value: 'student', label: 'All students' },
  { value: 'teacher', label: 'All teachers' },
  { value: 'principal', label: 'All principals' },
];

export function NotificationsPage() {
  const [open, setOpen] = useState(false);
  const [audience, setAudience] = useState('all');
  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);

  const { data: orgUsers } = useOrgUsers();
  const qc = useQueryClient();

  async function handleSend() {
    if (!title.trim() || !message.trim()) return;
    const userIds = (orgUsers ?? [])
      .filter((u) => audience === 'all' || u.role === audience)
      .map((u) => u.user_id);

    if (userIds.length === 0) return;
    setSending(true);
    try {
      await broadcastAnnouncement({ user_ids: userIds, title: title.trim(), message: message.trim(), type: 'announcement' });
      setOpen(false);
      setTitle('');
      setMessage('');
      qc.invalidateQueries({ queryKey: ['notifications'] });
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div />
        <Button onClick={() => setOpen(true)} style={{ background: ACCENT }}>
          <Megaphone size={16} className="mr-1.5" /> Send announcement
        </Button>
      </div>

      <SharedNotificationsPage
        title="Platform Notifications"
        subtitle="Announcements across every school on the platform."
        accentVar="--color-role-founder"
      />

      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        title="Send announcement"
        description="Broadcasts a notification to the selected audience, across every school."
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
            <Button onClick={handleSend} isLoading={sending} style={{ background: ACCENT }}>Send</Button>
          </div>
        }
      >
        <div className="space-y-4">
          <Select label="Audience" value={audience} onChange={(e) => setAudience(e.target.value)} options={AUDIENCE_OPTIONS} />
          <Input label="Title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Platform maintenance window" />
          <Input label="Message" value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Details for recipients…" />
        </div>
      </Dialog>
    </div>
  );
}
