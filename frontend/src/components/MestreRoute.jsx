// frontend/src/components/MestreRoute.jsx (Teste Renderizando MestrePage Importada)

import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
// --- NOVA IMPORTAÇÃO ---
// Importa a MestrePage (ultra-simplificada) diretamente aqui
import MestrePage from '../pages/MestrePage'; 
// --------------------

function MestreRoute() {
  console.log('--- MestreRoute: Iniciando verificação de Mestre ---'); 
  const { user } = useAuth();
  console.log('MestreRoute: User recebido do contexto:', user); 

  if (!user) {
    console.log('MestreRoute: BLOQUEADO - Usuário não logado. Redirecionando para /'); 
    return <Navigate to="/" replace />;
  }

  if (user.role !== 'mestre') {
    console.log(`MestreRoute: BLOQUEADO - Role='${user.role}' não é 'mestre'. Redirecionando para /home`); 
    return <Navigate to="/home" replace />;
  }

  console.log('MestreRoute: PERMITIDO - Tentando renderizar <MestrePage /> importada...'); 
  // --- MUDANÇA AQUI ---
  // Em vez de <Outlet />, retorna a MestrePage importada diretamente
  return <MestrePage />; 
  // --- FIM DA MUDANÇA ---
}

export default MestreRoute;