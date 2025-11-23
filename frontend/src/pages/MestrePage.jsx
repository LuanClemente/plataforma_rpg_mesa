// frontend/src/pages/MestrePage.jsx (VERSÃO FINAL COM COMPONENTES REAIS)

import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext'; 
// --- IMPORTS ATIVADOS ---
// Agora importamos os componentes que gerenciam cada aba
import GerenciarMonstros from '../components/GerenciarMonstros';
import GerenciarItens from '../components/GerenciarItens';
import GerenciarHabilidades from '../components/GerenciarHabilidades';
// -----------------------------

// Estilos in-line para o container principal e as abas (sem alterações)
const MestrePageStyles = {
  container: {
    padding: '2rem',
    color: 'white',
    maxWidth: '1200px',
    margin: '0 auto',
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    borderRadius: '8px',
  },
  tabs: {
    display: 'flex',
    marginBottom: '1rem',
    borderBottom: '2px solid #aa8342', 
  },
  tabButton: { 
    padding: '10px 20px',
    cursor: 'pointer',
    backgroundColor: 'transparent',
    border: 'none',
    color: '#aaa', 
    fontSize: '1.2rem',
    fontWeight: 'bold',
    fontFamily: 'MedievalSharp, cursive', 
  },
  activeTab: { 
    color: 'white', 
    borderBottom: '2px solid white', 
    marginBottom: '-2px', 
  }
};

function MestrePage() {
  // Log para indicar que esta é a versão final
  console.log('--- MestrePage: FINAL - Renderizando! ---'); 
  const { user } = useAuth(); // Pega dados do usuário logado
  const [abaAtiva, setAbaAtiva] = useState('monstros'); // Controla a aba visível

  // useEffect para o background (sem alterações)
  useEffect(() => {
    const classeFundo = 'mestre-background';
    console.log('--- MestrePage: FINAL - useEffect ADICIONANDO classe ---'); 
    document.body.classList.add(classeFundo);
    return () => {
      console.log('--- MestrePage: FINAL - useEffect REMOVENDO classe ---'); 
      document.body.classList.remove(classeFundo);
    };
  }, []); 

  // --- FUNÇÃO DE RENDERIZAÇÃO FINAL ---
  // Agora retorna os componentes reais importados
  const renderizarConteudoDaAba = () => {
    console.log(`--- MestrePage: FINAL - Renderizando componente da aba: ${abaAtiva} ---`); 
    switch (abaAtiva) {
      case 'monstros':
        // Renderiza o componente que gerencia monstros
        return <GerenciarMonstros />; 
      case 'itens':
        // Renderiza o componente que gerencia itens
        return <GerenciarItens />; 
      case 'habilidades':
        // Renderiza o componente que gerencia habilidades
        return <GerenciarHabilidades />; 
      default:
        // Caso padrão (não deve acontecer)
        return null;
    }
  };
  // ----------------------------------

  // Estrutura JSX da página (sem alterações na estrutura principal)
  return ( 
    <div style={MestrePageStyles.container}>
      <h1>Esconderijo do Mestre</h1>
      <p>Bem-vindo, {user?.name || 'Mestre'}. Use esta página para gerenciar o conteúdo base do jogo.</p>
      
      {/* Botões das Abas */}
      <div style={MestrePageStyles.tabs}>
        <button 
          style={{ ...MestrePageStyles.tabButton, ...(abaAtiva === 'monstros' ? MestrePageStyles.activeTab : {}) }}
          onClick={() => setAbaAtiva('monstros')}
        >
          Monstros
        </button>
        <button 
          style={{ ...MestrePageStyles.tabButton, ...(abaAtiva === 'itens' ? MestrePageStyles.activeTab : {}) }}
          onClick={() => setAbaAtiva('itens')}
        >
          Itens
        </button>
        <button 
          style={{ ...MestrePageStyles.tabButton, ...(abaAtiva === 'habilidades' ? MestrePageStyles.activeTab : {}) }}
          onClick={() => setAbaAtiva('habilidades')}
        >
          Habilidades
        </button>
      </div>
      
      {/* Área onde o conteúdo da aba ativa (o componente Gerenciar...) será exibido */}
      <div className="tab-content">
        {renderizarConteudoDaAba()} 
      </div>
    </div>
  );
}

export default MestrePage;
