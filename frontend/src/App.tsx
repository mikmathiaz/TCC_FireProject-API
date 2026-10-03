import { useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

function AppNavigator() {
  const { isAuthenticated } = useAuth();

  // Sincronização inteligente com a barra de endereços do navegador (History API)
  useEffect(() => {
    if (isAuthenticated) {
      if (window.location.pathname !== '/dashboard') {
        window.history.pushState({ page: 'dashboard' }, '', '/dashboard');
      }
    } else {
      if (window.location.pathname === '/dashboard') {
        window.history.pushState({ page: 'login' }, '', '/login');
      }
    }
  }, [isAuthenticated]);

  return (
    <AnimatePresence mode="wait">
      {isAuthenticated ? (
        <motion.div
          key="dashboard-view"
          initial={{ opacity: 0, scale: 0.99 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.99 }}
          transition={{ duration: 0.35, ease: 'easeOut' }}
          className="w-full min-h-screen"
        >
          <Dashboard />
        </motion.div>
      ) : (
        <motion.div
          key="login-view"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3, ease: 'easeInOut' }}
          className="w-full min-h-screen"
        >
          <Login />
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppNavigator />
    </AuthProvider>
  );
}

export default App;
