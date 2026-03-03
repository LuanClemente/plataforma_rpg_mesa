// frontend/src/App.jsx
import React from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';

import Navigation from './components/Navigation';
import PrivateRoute from './components/PrivateRoute';
import MusicPlayer from './components/MusicPlayer';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import BestiarioPage from './pages/HomePage';
import SalasPage from './pages/SalasPage';
import CantigasPage from './pages/CantigasPage';
import MestrePage from './pages/MestrePage';
import FerrariaArcanaPage from './pages/FerrariaArcanaPage';
import FichasPage from './pages/FichasPage';
import FichaEditPage from './pages/FichaEditPage';
import SalaPage from './pages/SalaPage';

function AppContent() {
  const location = useLocation();
  const rotasPublicas = ['/login', '/registrar'];
  const mostrarMusica = !rotasPublicas.includes(location.pathname);

  return (
    <div className="app-container">
      {/* Botão de música visível em todas as páginas exceto login/registro */}
      {mostrarMusica && <MusicPlayer />}

      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/registrar" element={<RegisterPage />} />

        <Route path="/" element={<PrivateRoute><Navigation /><main className="content"><CantigasPage /></main></PrivateRoute>} />
        <Route path="/cantigas" element={<PrivateRoute><Navigation /><main className="content"><CantigasPage /></main></PrivateRoute>} />
        <Route path="/bestiario" element={<PrivateRoute><Navigation /><main className="content"><BestiarioPage /></main></PrivateRoute>} />
        <Route path="/salas" element={<PrivateRoute><Navigation /><main className="content"><SalasPage /></main></PrivateRoute>} />
        <Route path="/fichas" element={<PrivateRoute><Navigation /><main className="content"><FichasPage /></main></PrivateRoute>} />
        <Route path="/fichas/editar/:id" element={<PrivateRoute><Navigation /><main className="content"><FichaEditPage /></main></PrivateRoute>} />
        <Route path="/mestre" element={<PrivateRoute><Navigation /><main className="content"><MestrePage /></main></PrivateRoute>} />
        <Route path="/ferraria-arcana" element={<PrivateRoute><Navigation /><main className="content"><FerrariaArcanaPage /></main></PrivateRoute>} />
        <Route path="/salas/:id" element={<PrivateRoute><SalaPage /></PrivateRoute>} />
      </Routes>
    </div>
  );
}

function App() {
  return <AppContent />;
}

export default App;