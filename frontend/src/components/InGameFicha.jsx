// frontend/src/components/InGameFicha.jsx
import React, { useState } from 'react';

// O componente agora recebe várias "props":
// - ficha: os dados do personagem.
// - onAttributeChange: a função a ser chamada quando clicamos em + ou -.
// - onSkillAdd: a função a ser chamada para adicionar uma nova perícia.
// - onSave: a função a ser chamada quando clicamos em "Salvar".
function InGameFicha({ ficha, onAttributeChange, onSkillAdd, onSave }) {
  // Estado local apenas para o campo de texto da nova perícia.
  const [novaPericia, setNovaPericia] = useState('');

  if (!ficha) {
    return <div className="ficha-in-game-container">Carregando ficha...</div>;
  }

  // Desestrutura os dados da ficha para facilitar o uso.
  const { nome_personagem, classe, nivel, raca, antecedente, atributos, pericias } = ficha;

  const handleAddPericiaClick = () => {
    if (novaPericia.trim() === '') return;
    onSkillAdd(novaPericia); // Envia a nova perícia para o componente pai (SalaPage).
    setNovaPericia(''); // Limpa o campo.
  };

  return (
    <div className="ficha-in-game-container">
      <h2>{nome_personagem}</h2>
      <p>{raca} {classe}, Nível {nivel}</p>
      <p>Antecedente: {antecedente}</p>

      <h3>Atributos</h3>
      <div className="atributos-grid">
        {Object.entries(atributos).map(([nome, valor]) => (
          <div key={nome} className="atributo-item-editavel">
            <span className="atributo-nome">{nome.substring(0, 3)}.</span>
            {/* Botão de diminuir, chama a função do componente pai */}
            <button onClick={() => onAttributeChange(nome, -1)}>-</button>
            <span className="atributo-valor">{valor}</span>
            {/* Botão de aumentar, chama a função do componente pai */}
            <button onClick={() => onAttributeChange(nome, 1)}>+</button>
          </div>
        ))}
      </div>

      <h3>Perícias</h3>
      <ul className="pericias-lista">
        {pericias.map(pericia => (
          <li key={pericia}>{pericia}</li>
        ))}
      </ul>
      {/* Novo formulário para adicionar perícias */}
      <div className="add-skill-form">
        <input
          type="text"
          value={novaPericia}
          onChange={(e) => setNovaPericia(e.target.value)}
          placeholder="Nova Perícia"
        />
        <button onClick={handleAddPericiaClick}>+</button>
      </div>

      {/* Botão para salvar todas as alterações */}
      <button onClick={onSave} className="login-button" style={{ marginTop: '1.5rem' }}>
        Salvar Ficha
      </button>
    </div>
  );
}

export default InGameFicha;