// frontend/src/main.jsx

// Importa as bibliotecas principais do React.
import React from 'react';
import ReactDOM from 'react-dom/client';
// Importa o BrowserRouter para gerenciar as rotas da aplicação.
import { BrowserRouter } from 'react-router-dom';
// Importa nosso AuthProvider, o gerenciador do estado de autenticação.
import { AuthProvider } from './context/AuthContext';
// Importa nosso componente principal App.
import App from './App.jsx';
// Importa a folha de estilos global.
import './index.css';

// Encontra o elemento 'root' no index.html e inicia a aplicação React nele.
ReactDOM.createRoot(document.getElementById('root')).render(
  // React.StrictMode ajuda a detectar problemas potenciais no código.
  <React.StrictMode>
    {/* O BrowserRouter deve ser um dos 'envelopes' mais externos, para gerenciar todas as URLs. */}
    <BrowserRouter>
      {/* O AuthProvider deve 'envelopar' o App. */}
      {/* Isso garante que CADA componente dentro de App (LoginPage, HomePage, etc.) */}
      {/* possa usar o hook 'useAuth()' para saber quem está logado, fazer login ou logout. */}
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);