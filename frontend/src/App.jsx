// frontend/src/App.jsx

// Importa as ferramentas de roteamento que instalamos.
import { Routes, Route } from 'react-router-dom';

// Importa nossos componentes de página.
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import FichasPage from './pages/FichasPage'; // A nossa nova página!

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
          {/* Ela está "envelopada" pelo nosso componente ProtectedRoute. */}
          {/* Isso significa que um usuário só pode acessar /home se estiver logado. */}
          <Route 
            path="/home" 
            element={
              <ProtectedRoute>
                <HomePage />
              </ProtectedRoute>
            } 
          />

          {/* --- NOVA ROTA ADICIONADA --- */}
          {/* Rota para a página "Minhas Fichas". */}
          {/* Ela também está protegida, garantindo que apenas usuários logados possam ver suas fichas. */}
          <Route 
            path="/fichas" 
            element={
              <ProtectedRoute>
                <FichasPage />
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