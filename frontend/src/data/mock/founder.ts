export const FOUNDER_OVERVIEW = { schools: 14, users: 18420, mrr: 42500, activeSessions: 312 };

export const FOUNDER_REVENUE_TREND = [
  { label: 'Feb', value: 31000 }, { label: 'Mar', value: 33500 }, { label: 'Apr', value: 35200 },
  { label: 'May', value: 37800 }, { label: 'Jun', value: 40100 }, { label: 'Jul', value: 42500 },
];

export const FOUNDER_SCHOOLS = [
  { id: '1', name: 'Lincoln High School', plan: 'Enterprise', students: 1240, status: 'active' as const },
  { id: '2', name: 'Riverside Academy', plan: 'Growth', students: 860, status: 'active' as const },
  { id: '3', name: 'Maple Grove School', plan: 'Starter', students: 320, status: 'trial' as const },
  { id: '4', name: 'Oak Valley Prep', plan: 'Growth', students: 705, status: 'active' as const },
];

export const FOUNDER_USER_BREAKDOWN = [
  { label: 'Students', value: 14200, color: 'var(--color-role-student)' },
  { label: 'Teachers', value: 2400, color: 'var(--color-role-teacher)' },
  { label: 'Parents', value: 1600, color: 'var(--color-role-parent)' },
  { label: 'Staff', value: 220, color: 'var(--color-role-principal)' },
];

export const FOUNDER_AI_USAGE = [
  { label: 'Mon', value: 4200 }, { label: 'Tue', value: 4800 }, { label: 'Wed', value: 4600 },
  { label: 'Thu', value: 5200 }, { label: 'Fri', value: 5600 }, { label: 'Sat', value: 3100 }, { label: 'Sun', value: 2800 },
];

export const FOUNDER_SYSTEM_HEALTH = [
  { name: 'API', status: 'operational' as const, latency: '84ms' },
  { name: 'Database', status: 'operational' as const, latency: '12ms' },
  { name: 'Auth Service', status: 'operational' as const, latency: '61ms' },
  { name: 'AI Inference', status: 'degraded' as const, latency: '1.2s' },
];

export const FOUNDER_LOGS = [
  { id: '1', level: 'info' as const, message: 'Scheduled backup completed', time: '2m ago' },
  { id: '2', level: 'warn' as const, message: 'AI Inference latency above threshold', time: '14m ago' },
  { id: '3', level: 'info' as const, message: 'New school onboarded: Oak Valley Prep', time: '1h ago' },
  { id: '4', level: 'error' as const, message: 'Failed webhook delivery to school #12', time: '3h ago' },
];
