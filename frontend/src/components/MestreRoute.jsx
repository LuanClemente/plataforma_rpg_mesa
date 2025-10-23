// frontend/src/components/MestreRoute.jsx

// Importa ferramentas do React Router e nosso hook de autenticação
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * Este componente é um "Porteiro" ou "Sentinela" para rotas de Mestre.
 * Ele verifica DUAS coisas:
 * 1. O usuário está logado?
 * 2. O usuário logado é um Mestre?
 */
function MestreRoute() {
  // Pega o objeto 'user' do nosso contexto
  const { user } = useAuth();

  // Caso 1: O usuário NÃO está logado (user é nulo)
  // Se 'user' for nulo, o usuário não está autenticado.
  if (!user) {
    // Redireciona o usuário para a página de Login.
    // 'replace' impede que o usuário volte para esta página com o botão "Voltar".
    return <Navigate to="/" replace />;
  }

  // Caso 2: O usuário ESTÁ logado, mas NÃO é um Mestre
  // Se o 'role' não for 'mestre', ele é um 'player' comum.
  if (user.role !== 'mestre') {
    console.log(`MestreRoute: Usuário logado, mas role='${user.role}'. Redirecionando para /home`);
    // Redireciona o 'player' para a página Home (ou qualquer outra página principal).
    // Não queremos que ele veja uma página de "Acesso Negado",
    // apenas o mandamos de volta para um lugar seguro.
    return <Navigate to="/home" replace />;
  }

  // Caso 3: O usuário ESTÁ logado E É um Mestre
  // Se passou pelas duas verificações acima, permitimos o acesso.
  // O <Outlet /> é um componente especial do React Router que diz:
  // "Renderize qualquer componente filho que esta rota estiver protegendo".
  // (No caso, ele vai renderizar a <MestrePage />)
  return <Outlet />;
}

export default MestreRoute;