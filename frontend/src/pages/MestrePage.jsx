// frontend/src/pages/MestrePage.jsx



import React, { useEffect, useState } from 'react';

import { useAuth } from '../context/AuthContext';

import GerenciarMonstros from '../components/GerenciarMonstros';

import GerenciarItens from '../components/GerenciarItens';

import GerenciarHabilidades from '../components/GerenciarHabilidades';



// (Estilos in-line permanecem os mesmos)

const MestrePageStyles = {

  container: {

    padding: '2rem',

    color: 'white',

    maxWidth: '1200px',

    margin: '0 auto',

    backgroundColor: 'mestre-background',

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

  },

  activeTab: {

    color: 'white',

    borderBottom: '2px solid white',

    marginBottom: '-2px',

  }

};



function MestrePage() {

  const { user } = useAuth();

  const [abaAtiva, setAbaAtiva] = useState('monstros');



  // --- [CORREÇÃO DO USEEFFECT] ---

  // Define o fundo da página usando classList

  useEffect(() => {

    const classeFundo = 'mestre-background';

   

    // Adiciona a classe ao BODY quando o componente é montado

    document.body.classList.add(classeFundo);

   

    // A função de limpeza é executada quando o componente é desmontado

    return () => {

    };

  }, []); // O array vazio [] garante que isso rode apenas na montagem/desmontagem



  // Função para renderizar o conteúdo da aba correta

  const renderizarConteudoDaAba = () => {

    switch (abaAtiva) {

      case 'monstros':

        return <GerenciarMonstros />;

      case 'itens':

        return <GerenciarItens />;

      case 'habilidades':

        return <GerenciarHabilidades />;

      default:

        return null;

    }

  };



  return (

    <div style={MestrePageStyles.container}>

      {/* Título da Página */}

      <h1>Esconderijo do Mestre</h1>

      <p>Bem-vindo, {user?.name || 'Mestre'}. Use esta página para gerenciar o conteúdo base do jogo.</p>

     

      {/* Container das Abas */}

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

     

      {/* Conteúdo da Aba Ativa */}

      <div className="tab-content">

        {renderizarConteudoDaAba()}

      </div>

    </div>

  );

}



export default MestrePage;