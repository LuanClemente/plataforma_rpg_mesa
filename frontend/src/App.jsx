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

// Importa nossos componentes reutilizáveis.
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';

// Este é o componente principal que orquestra toda a aplicação.
function App() {
  // O 'return' define a estrutura geral do nosso site.
  return (
    // A div principal que envolve toda a aplicação.
    <div className="app-container">
      
      {/* Renderiza nosso componente de navegação inteligente. */}
      {/* A Navbar irá mudar seus links dependendo se o usuário está logado ou não. */}
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
          {/* Ela está "envelopada" pelo nosso componente ProtectedRoute, */}
          {/* o que significa que um usuário só pode acessá-la se estiver logado. */}
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

          {/* --- ROTA ADICIONADA E CORRIGIDA --- */}
          {/* Rota para a página da sala de jogo INDIVIDUAL. */}
          {/* O ':id' na URL é um parâmetro dinâmico que representa o ID da sala. */}
          <Route 
            path="/salas/:id" 
            element={
              <ProtectedRoute>
                <SalaPage />
              </ProtectedRoute>
            } 
          />
          
        </Routes>
      </main>
      
    </div>
  );
}

// Exporta o componente App para ser usado pelo main.jsx.
export default App;