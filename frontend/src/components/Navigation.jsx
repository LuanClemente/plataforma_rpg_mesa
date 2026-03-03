// frontend/src/components/Navigation.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Navigation() {
  const { user, logout } = useAuth();

  return (
    <nav className="main-nav">
      <Link to="/cantigas">Início</Link>
      <Link to="/fichas">Minhas Fichas</Link>
      <Link to="/salas">Salas</Link>
      <Link to="/bestiario">Bestiário</Link>
      <Link to="/ferraria-arcana">Ferraria Arcana</Link>
      {user?.role === 'mestre' && <Link to="/mestre">Esconderijo do Mestre</Link>}
      <button onClick={logout} className="nav-logout-button">Sair</button>
    </nav>
  );
}

export default Navigation;