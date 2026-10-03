import React, { createContext, useContext, useState } from 'react';

export interface User {
  username: string;
  email: string;
  role: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (usernameOrEmail: string, password: string, remember: boolean) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const AUTH_STORAGE_KEY = 'firewatcher_auth_session';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    // Recupera sessão persistida se existir
    const local = localStorage.getItem(AUTH_STORAGE_KEY);
    if (local) {
      try {
        return JSON.parse(local);
      } catch {
        return null;
      }
    }
    const session = sessionStorage.getItem(AUTH_STORAGE_KEY);
    if (session) {
      try {
        return JSON.parse(session);
      } catch {
        return null;
      }
    }
    return null;
  });

  const login = async (usernameOrEmail: string, password: string, remember: boolean): Promise<{ success: boolean; error?: string }> => {
    const cleanUser = usernameOrEmail.trim().toLowerCase();
    const cleanPass = password.trim();

    // Verificação teste / teste (aceita 'teste', 'teste@firewatcher.com', etc.)
    const isUserValid = cleanUser === 'teste' || cleanUser.startsWith('teste@');
    const isPassValid = cleanPass === 'teste';

    if (!isUserValid || !isPassValid) {
      return {
        success: false,
        error: 'Credenciais inválidas. Para testar, utilize usuário "teste" e senha "teste".',
      };
    }

    const authenticatedUser: User = {
      username: 'teste',
      email: cleanUser.includes('@') ? cleanUser : 'teste@firewatcher.gov.br',
      name: 'Operador Teste',
      role: 'Analista de Monitoramento e Sensoriamento Remoto',
    };

    if (remember) {
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(authenticatedUser));
    } else {
      sessionStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(authenticatedUser));
    }

    setUser(authenticatedUser);
    return { success: true };
  };

  const logout = () => {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    sessionStorage.removeItem(AUTH_STORAGE_KEY);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser utilizado dentro de um AuthProvider');
  }
  return context;
};
