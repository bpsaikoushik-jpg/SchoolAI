import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import type { Role } from '../types/auth';

interface RoleRouteProps {
  allowed: Role[];
}

// Gate for a specific portal (e.g. only teacher/principal/founder can view
// the Teacher dashboard tree). Assumes ProtectedRoute already ran above it.
export function RoleRoute({ allowed }: RoleRouteProps) {
  const user = useAuthStore((s) => s.user);

  if (!user) return <Navigate to="/login" replace />;
  if (!allowed.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <Outlet />;
}
