import { Link } from 'react-router-dom';
import { Button } from '../../components/Button';
import { ShieldAlert } from 'lucide-react';
import { useAuthStore } from '../../store/useAuthStore';
import { dashboardPathForRole } from '../../lib/roles';

export function UnauthorizedPage() {
  const user = useAuthStore((s) => s.user);
  const home = user ? dashboardPathForRole(user.role) : '/login';

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-canvas px-4 text-center">
      <div className="grid h-14 w-14 place-items-center rounded-full bg-rose-500/10 text-rose-500">
        <ShieldAlert size={26} />
      </div>
      <h1 className="text-3xl font-bold text-text-primary">Access restricted</h1>
      <p className="max-w-sm text-text-muted">Your account doesn't have permission to view that portal.</p>
      <Link to={home}><Button>Back to my dashboard</Button></Link>
    </div>
  );
}
