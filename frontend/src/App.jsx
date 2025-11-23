import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

// Importação das Páginas
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import SalasPage from './pages/SalasPage';
import SalaPage from './pages/SalaPage';
import FichasPage from './pages/FichasPage';
import FichaEditPage from './pages/FichaEditPage';
import MestrePage from './pages/MestrePage';
import HomePage from './pages/HomePage';
import CantigasPage from './pages/CantigasPage'; // Importação da nova página
import Navbar from './components/Navbar';

// Componente para proteger rotas privadas
const PrivateRoute = ({ children }) => {
  const { user } = useAuth();
  const isAuthenticated = !!user;

  return isAuthenticated ? children : <Navigate to="/login" />;
};

function App() {
  const { user } = useAuth();

  return (
    <>
      {user && <Navbar />}
      <Routes>
        {/* Rotas Públicas */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/registrar" element={<RegisterPage />} />

        {/* Rotas Privadas */}
        <Route path="/" element={<PrivateRoute><HomePage /></PrivateRoute>} />
        <Route path="/cantigas" element={<PrivateRoute><CantigasPage /></PrivateRoute>} />
        <Route path="/salas" element={<PrivateRoute><SalasPage /></PrivateRoute>} />
        <Route path="/salas/:id" element={<PrivateRoute><SalaPage /></PrivateRoute>} />
        <Route path="/fichas" element={<PrivateRoute><FichasPage /></PrivateRoute>} />
        <Route path="/fichas/nova" element={<PrivateRoute><FichaEditPage /></PrivateRoute>} />
        <Route path="/fichas/:id" element={<PrivateRoute><FichaEditPage /></PrivateRoute>} />
        <Route path="/mestre" element={<PrivateRoute><MestrePage /></PrivateRoute>} />

        {/* Rota de Fallback */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </>
  );
}

export default App;
