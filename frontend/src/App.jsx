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
import ProtectedRoute from './components/ProtectedRoute';

// Esta é a nova função do nosso componente App.
function App() {
  return (
    <div className="app-container">
      {/* ... (código da <nav>) ... */}
      <main>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/registrar" element={<RegisterPage />} />
          
          {/* ROTA ATUALIZADA */}
          <Route 
            path="/home" 
            element={
              <ProtectedRoute>
                <HomePage />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </main>
    </div>
  );
}
export default App;