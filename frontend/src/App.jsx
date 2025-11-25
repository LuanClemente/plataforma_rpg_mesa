// frontend/src/App.jsx

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';

// Componentes
import Navigation from './components/Navigation';
import PrivateRoute from './components/PrivateRoute';

// Páginas
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import SalasPage from './pages/SalasPage';
import BestiarioPage from './pages/BestiarioPage';
import CantigasPage from './pages/CantigasPage';
import MestrePage from './pages/MestrePage';
import FerrariaArcanaPage from './pages/FerrariaArcanaPage'; // <-- IMPORTANDO A NOVA PÁGINA

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app-container">
          {/* A navegação pode ser condicional para não aparecer na tela de login */}
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/*" element={
              <PrivateRoute>
                <Navigation />
                <main className="content">
                  <Routes>
                    <Route path="/home" element={<HomePage />} />
                    <Route path="/salas" element={<SalasPage />} />
                    <Route path="/bestiario" element={<BestiarioPage />} />
                    <Route path="/cantigas" element={<CantigasPage />} />
                    <Route path="/mestre" element={<MestrePage />} />
                    <Route path="/ferraria" element={<FerrariaArcanaPage />} /> {/* <-- NOSSA NOVA ROTA! */}
                  </Routes>
                </main>
              </PrivateRoute>
            } />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;