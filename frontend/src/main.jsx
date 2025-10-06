// frontend/src/main.jsx

// Importa as bibliotecas principais do React.
import React from 'react';
import ReactDOM from 'react-dom/client';
// 1. Importamos o BrowserRouter, o "mapa" principal do nosso sistema de rotas.
import { BrowserRouter } from 'react-router-dom';

// Importa nosso componente App, que agora contém as definições de rotas.
import App from './App.jsx';
// Importa nosso arquivo de estilo principal.
import './index.css';

// Encontra a "tela de pintura" no nosso index.html e prepara a raiz do React.
ReactDOM.createRoot(document.getElementById('root')).render(
  // React.StrictMode é uma ferramenta que ajuda a encontrar problemas potenciais na sua aplicação.
  <React.StrictMode>
    {/* 2. Envelopamos nosso componente <App /> com o <BrowserRouter>. */}
    {/* A partir de agora, todos os componentes dentro de App (HomePage, LoginPage, etc.) */}
    {/* terão acesso às funcionalidades de roteamento. */}
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);