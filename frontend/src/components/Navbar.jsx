// frontend/src/components/Navbar.jsx
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Navbar() {
  // Olhamos para o "quadro de avisos" para ver se 'user' existe e pegar a função 'logout'.
  const { user, logout } = useAuth();

  return (
    <nav className="main-nav">
      {/* Esta é a renderização condicional: */}
      { user ? (
        // Se 'user' EXISTE (está logado), mostre estes links:
        <>
          <Link to="/home">Bestiário</Link>
          <Link to="/fichas">Minhas Fichas</Link>
          <Link to="/salas">Salas</Link>
          {/* Este não é um Link, é um botão que chama a função de logout */}
          <button onClick={logout} className="nav-logout-button">Sair</button>
        </>
      ) : (
        // Se 'user' NÃO EXISTE (está deslogado), mostre apenas este link:
        <Link to="/">Login</Link>
      )}
    </nav>
  );
}
export default Navbar;