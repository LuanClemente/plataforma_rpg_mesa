import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="main-nav">
      {user ? (
        <>
          <Link to="/">Bestiário</Link>
          <Link to="/fichas">Minhas Fichas</Link>
          <Link to="/salas">Salas</Link>
          <Link to="/cantigas">Cantigas</Link>

          {user.role === 'mestre' && (
            <Link to="/mestre">Esconderijo</Link>
          )}

          <button onClick={logout} className="nav-logout-button">Sair</button>
        </>
      ) : (
        <Link to="/login">Login</Link>
      )}
    </nav>
  );
}

export default Navbar;
