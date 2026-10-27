export interface AuthUser {
  id: string;
  email: string;
  full_name?: string;
  role: string;
  is_superuser: boolean;
  permissions: string[];
}

export interface AuthState {
  token: string | null;
  user: AuthUser | null;
  isAuthenticated: boolean;
}

const TOKEN_KEY = 'fim_access_token';
const USER_KEY = 'fim_user_data';

export function getStoredAuth(): AuthState {
  const token = localStorage.getItem(TOKEN_KEY);
  const userJson = localStorage.getItem(USER_KEY);
  if (token && userJson) {
    try {
      const user = JSON.parse(userJson);
      return { token, user, isAuthenticated: true };
    } catch {
      clearAuth();
    }
  }
  return { token: null, user: null, isAuthenticated: false };
}

export function saveAuth(token: string, user: AuthUser) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export async function loginUser(email: string, password: string):Promise<{ success: boolean; error?: string; user?: AuthUser; token?: string }> {
  try {
    const res = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      return { success: false, error: errData.detail || 'Authentication failed. Please verify credentials.' };
    }

    const data = await res.json();
    saveAuth(data.access_token, data.user);
    return { success: true, user: data.user, token: data.access_token };
  } catch (err) {
    return { success: false, error: 'Network error connecting to authentication server.' };
  }
}
