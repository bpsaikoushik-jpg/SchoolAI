// Mirrors backend `UserRole` (app/models/user.py). `parent` is added on the
// frontend only — the backend enum has no PARENT value yet even though a
// ParentProfile model exists. See README notes / final report for this gap.
export type Role = 'student' | 'teacher' | 'principal' | 'admin' | 'founder' | 'parent';

export interface AuthUser {
  id: string;
  email: string;
  full_name: string | null;
  role: Role;
  school_id: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
