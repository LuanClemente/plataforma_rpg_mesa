// frontend/src/components/ProtectedRoute.jsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// Este componente age como um "invólucro" ou "guarda".
function ProtectedRoute({ children }) {
  // Ele olha para o nosso "quadro de avisos" para ver se há um usuário logado.
  const { user } = useAuth();

  // Se NÃO houver um usuário...
  if (!user) {
    // ...ele renderiza o componente <Navigate>, que redireciona o usuário para a página de login.
    // O 'replace' impede que o usuário use o botão "voltar" do navegador para acessar a página protegida.
    return <Navigate to="/" replace />;
  }

  // Se houver um usuário, ele simplesmente renderiza o conteúdo que deveria estar lá (os 'children').
  return children;
}

export default ProtectedRoute;