import { useState, type FormEvent } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, Lock, Sparkles, AlertCircle } from 'lucide-react';
import { Button } from '../../components/Button';
import { Input } from '../../components/ui/Input';
import { useAuthStore } from '../../store/useAuthStore';
import { login, fetchCurrentUser } from '../../services/auth.service';
import { dashboardPathForRole } from '../../lib/roles';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const setAuth = useAuthStore((s) => s.setAuth);
  const navigate = useNavigate();
  const location = useLocation();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      const { access_token } = await login({ email, password });
      // Auth store needs the user's role before setAuth persists, so we
      // stash the token first, then hydrate the profile via /users/me.
      localStorage.setItem('token', access_token);
      const user = await fetchCurrentUser();
      setAuth(user, access_token);

      const from = (location.state as { from?: string } | null)?.from;
      navigate(from ?? dashboardPathForRole(user.role), { replace: true });
    } catch {
      localStorage.removeItem('token');
      setError('Incorrect email or password. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-canvas px-4">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="w-full max-w-md rounded-3xl border border-border-subtle bg-raised p-8 shadow-[var(--shadow-card)]"
      >
        <Link to="/" className="mb-8 flex items-center gap-2.5">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-tr from-brand-500 to-mint-500 text-white">
            <Sparkles size={18} />
          </div>
          <span className="text-lg font-bold text-text-primary">SchoolAI</span>
        </Link>

        <h1 className="text-2xl font-bold text-text-primary">Welcome back</h1>
        <p className="mt-1 text-sm text-text-muted">Sign in to your dashboard to continue.</p>

        <form onSubmit={handleSubmit} className="mt-7 space-y-4">
          <Input
            label="Email"
            type="email"
            required
            icon={<Mail size={16} />}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@school.edu"
            autoComplete="email"
          />
          <Input
            label="Password"
            type="password"
            required
            icon={<Lock size={16} />}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            autoComplete="current-password"
          />

          {error && (
            <div className="flex items-center gap-2 rounded-xl bg-rose-500/10 px-3 py-2.5 text-sm text-rose-500">
              <AlertCircle size={15} className="shrink-0" />
              {error}
            </div>
          )}

          <Button type="submit" className="w-full" size="lg" isLoading={isLoading}>
            Sign in
          </Button>
        </form>

        <p className="mt-6 text-center text-xs text-text-muted">
          Roles are assigned by your school administrator. New here?{' '}
          <Link to="/" className="font-medium text-brand-600 hover:underline">Learn more</Link>
        </p>
      </motion.div>
    </div>
  );
};
