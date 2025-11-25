// frontend/src/components/Navigation.jsx

import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Navigation() {
  const { user, logout } = useAuth();

  return (
    <nav className="main-navigation">
      <Link to="/home">Início</Link>
      <Link to="/salas">Salas</Link>
      <Link to="/bestiario">Bestiário</Link>
      <Link to="/cantigas">Cantigas</Link>
      <Link to="/ferraria">Ferraria Arcana</Link> {/* <-- NOVO LINK! */}
      {user?.is_gm && <Link to="/mestre">Esconderijo do Mestre</Link>}
      <button onClick={logout} className="logout-button">Sair</button>
    </nav>
  );
}

export default Navigation;