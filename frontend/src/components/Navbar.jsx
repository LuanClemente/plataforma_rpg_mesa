// frontend/src/components/Navbar.jsx

// Importa o Link para navegação e o nosso hook useAuth para acessar o contexto
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Navbar() {
  // Olhamos para o "quadro de avisos" (AuthContext).
  // Agora, 'user' é um objeto completo: { token, role, name, id } ou null.
  const { user, logout } = useAuth();

  return (
    <nav className="main-nav">
      {/* Esta é a renderização condicional principal: */}
      { user ? (
        // Se 'user' EXISTE (está logado), mostre estes links:
        <>
          <Link to="/home">Bestiário</Link>
          <Link to="/fichas">Minhas Fichas</Link>
          <Link to="/salas">Salas</Link>

          {/* --- [NOVA LÓGICA DE MESTRE] --- */}
          {/* Verificamos se o 'user' existe E se o 'role' dele é 'mestre'.
              O '&&' (E lógico) do React significa: 
              "Se a condição da esquerda for verdadeira, renderize o que está à direita."
          */}
          { user.role === 'mestre' && (
            <Link to="/esconderijo-do-mestre">Esconderijo</Link>
          )}
          {/* --- FIM DA NOVA LÓGICA --- */}

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