// frontend/src/App.jsx

// Importa as ferramentas de roteamento que instalamos.
import { Routes, Route } from 'react-router-dom';

// Importa nossos componentes de página.
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import FichasPage from './pages/FichasPage';
import FichaEditPage from './pages/FichaEditPage';
import SalasPage from './pages/SalasPage'; // A página com a LISTA de salas.
import SalaPage from './pages/SalaPage';   // A página da sala de jogo INDIVIDUAL.

// --- [NOVA IMPORTAÇÃO] ---
// Importa a nova página do Esconderijo do Mestre.
// (Nós vamos criar este arquivo logo após este passo!)
import MestrePage from './pages/MestrePage';

// Importa nossos componentes reutilizáveis.
import ProtectedRoute from './components/ProtectedRoute';
// --- [NOVA IMPORTAÇÃO] ---
// Importa o nosso novo "porteiro" de rotas de Mestre.
import MestreRoute from './components/MestreRoute';
import Navbar from './components/Navbar';

// Este é o componente principal que orquestra toda a aplicação.
function App() {
  // O 'return' define a estrutura geral do nosso site.
  return (
    // A div principal que envolve toda a aplicação.
    <div className="app-container">
      
      {/* Renderiza nosso componente de navegação inteligente. */}
      {/* A Navbar agora mostra "Esconderijo" se o usuário for Mestre. */}
      <Navbar />

      {/* A tag <main> contém o conteúdo principal da página, que mudará de acordo com a rota. */}
      <main>
        {/* O componente <Routes> é o cérebro do nosso roteador. */}
        {/* Ele olha a URL atual e decide qual <Route> deve ser renderizada. */}
        <Routes>
          {/* Rota para a página de Login. É a nossa página raiz ('/'). */}
          <Route path="/" element={<LoginPage />} />
          
          {/* Rota para a página de Registro. */}
          <Route path="/registrar" element={<RegisterPage />} />
          
          {/* Rota para a Home Page (Bestiário). */}
          {/* Protegida pelo ProtectedRoute (só precisa estar logado). */}
          <Route 
            path="/home" 
            element={
              <ProtectedRoute>
                <HomePage />
              </ProtectedRoute>
            } 
          />

          {/* Rota para a página "Minhas Fichas". Também protegida. */}
          <Route 
            path="/fichas" 
            element={
              <ProtectedRoute>
                <FichasPage />
              </ProtectedRoute>
            } 
          />

          {/* Rota para a página de edição de uma ficha específica. O ':id' é um parâmetro dinâmico. */}
          <Route 
            path="/fichas/editar/:id" 
            element={
              <ProtectedRoute>
                <FichaEditPage />
              </ProtectedRoute>
            } 
          />

          {/* Rota para a página com a LISTA de salas. Também protegida. */}
          <Route 
            path="/salas" 
            element={
              <ProtectedRoute>
                <SalasPage />
              </ProtectedRoute>
            } 
          />

          {/* Rota para a página da sala de jogo INDIVIDUAL. */}
          <Route 
            path="/salas/:id" 
            element={
              <ProtectedRoute>
                <SalaPage />
              </ProtectedRoute>
            } 
          />

          {/* --- [NOVA ROTA DO MESTRE] --- */}
          {/* Esta é a nova rota para o "Esconderijo do Mestre". */}
          {/* Ela é protegida pelo nosso componente MestreRoute. */}
          {/* O MestreRoute verifica se o usuário está logado E se user.role == 'mestre'. */}
          <Route 
            path="/esconderijo-do-mestre" 
            element={
              <MestreRoute>
                <MestrePage />
              </MestreRoute>
            } 
          />
          
        </Routes>
      </main>
      
    </div>
  );
}

// Exporta o componente App para ser usado pelo main.jsx.
export default App;