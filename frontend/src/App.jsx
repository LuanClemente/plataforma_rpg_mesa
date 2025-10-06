// frontend/src/App.jsx

// Importa as ferramentas de roteamento que instalamos:
// Routes: O container que gerencia qual rota está ativa.
// Route: Define uma regra individual ("quando a URL for X, mostre o componente Y").
// Link: Cria links de navegação que não recarregam a página.
import { Routes, Route, Link } from 'react-router-dom';

// Importa os nossos novos componentes de página.
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';


// Esta é a nova função do nosso componente App.
function App() {
  return (
    <div className="app-container">
      <nav className="main-nav">
        {/* Adicionaremos um link para a página de registro na LoginPage */}
        <Link to="/">Login</Link>
        <Link to="/home">Bestiário</Link>
      </nav>

      <main>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/home" element={<HomePage />} />
          {/* 2. Adicione a nova rota para o cadastro! */}
          <Route path="/registrar" element={<RegisterPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;