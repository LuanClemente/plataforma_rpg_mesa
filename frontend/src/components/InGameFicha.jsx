// frontend/src/components/InGameFicha.jsx
import React, { useState } from 'react';

/**
 * Este componente renderiza a ficha de personagem interativa dentro da sala de jogo.
 * Ele é um componente "controlado", o que significa que ele não gerencia seu próprio estado principal,
 * mas recebe os dados (a 'ficha') e as funções de alteração ('on...') de um componente pai (SalaPage).
 */
function InGameFicha({ ficha, onAttributeChange, onSkillAdd, onSave }) {
  // Estado local usado APENAS para o campo de texto de adicionar nova perícia.
  const [novaPericia, setNovaPericia] = useState('');

  // Se a ficha ainda não foi carregada (é 'null'), exibe uma mensagem de carregamento.
  if (!ficha) {
    return <div className="ficha-in-game-container">Carregando ficha...</div>;
  }

  // Desestrutura os dados da ficha para facilitar o uso no JSX.
  // ADICIONAMOS 'xp_atual' E 'xp_proximo_nivel' para a barra de progresso.
  const { 
    nome_personagem, classe, nivel, raca, antecedente, 
    atributos, pericias, xp_atual, xp_proximo_nivel 
  } = ficha;

  // --- NOVA LÓGICA DA BARRA DE XP ---
  // Calcula a porcentagem de XP para preencher a barra.
  // (xp_atual / xp_proximo_nivel) * 100
  // Usamos Math.max para garantir que não dê erro se xp_proximo_nivel for 0.
  const xpPercentage = (xp_atual / (xp_proximo_nivel || 1)) * 100;

  // Função local para lidar com o clique no botão de adicionar perícia.
  const handleAddPericiaClick = () => {
    if (novaPericia.trim() === '') return; // Não adiciona perícias vazias.
    onSkillAdd(novaPericia); // Chama a função 'pai' (passada via props) para atualizar o estado.
    setNovaPericia(''); // Limpa o campo de texto local.
  };

  // --- Renderização do Componente (JSX) ---
  return (
    <div className="ficha-in-game-container">
      <h2>{nome_personagem}</h2>
      <p>{raca} {classe}, Nível {nivel}</p>
      <p>Antecedente: {antecedente}</p>

      {/* --- SEÇÃO DE XP ADICIONADA --- */}
      <div className="xp-bar-container">
        {/* Exibe o texto (ex: "XP: 150 / 300") */}
        <label>XP: {xp_atual} / {xp_proximo_nivel}</label>
        {/* A barra de fundo */}
        <div className="xp-bar-background">
          {/* A barra de preenchimento, cujo 'width' é controlado pelo estado da ficha. */}
          {/* A 'style' inline é usada aqui por ser a forma mais fácil de aplicar um valor dinâmico (a porcentagem). */}
          <div className="xp-bar-fill" style={{ width: `${xpPercentage}%` }}></div>
        </div>
      </div>

      <h3>Atributos</h3>
      <div className="atributos-grid">
        {/* Mapeia o objeto de atributos para criar um painel para cada um. */}
        {Object.entries(atributos).map(([nome, valor]) => (
          <div key={nome} className="atributo-item-editavel">
            <span className="atributo-nome">{nome.substring(0, 3)}.</span>
            {/* Botão de diminuir, chama a função 'onAttributeChange' do componente pai. */}
            <button onClick={() => onAttributeChange(nome, -1)}>-</button>
            <span className="atributo-valor">{valor}</span>
            {/* Botão de aumentar, chama a função 'onAttributeChange' do componente pai. */}
            <button onClick={() => onAttributeChange(nome, 1)}>+</button>
          </div>
        ))}
      </div>

      <h3>Perícias</h3>
      <ul className="pericias-lista">
        {/* Mapeia a lista de perícias. */}
        {pericias.map(pericia => (
          <li key={pericia}>{pericia}</li>
        ))}
      </ul>
      
      {/* Formulário para adicionar novas perícias */}
      <div className="add-skill-form">
        <input
          type="text"
          value={novaPericia}
          onChange={(e) => setNovaPericia(e.target.value)}
          placeholder="Nova Perícia"
        />
        <button onClick={handleAddPericiaClick}>+</button>
      </div>

      {/* Botão para salvar todas as alterações (atributos e perícias) no banco de dados. */}
      <button onClick={onSave} className="login-button" style={{ marginTop: '1.5rem' }}>
        Salvar Ficha
      </button>
    </div>
  );
}

export default InGameFicha;
