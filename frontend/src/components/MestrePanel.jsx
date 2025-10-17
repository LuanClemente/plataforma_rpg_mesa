// frontend/src/components/MestrePanel.jsx
import React, { useState } from 'react';

// Este componente receberá o 'socket' e o 'salaId' como props.
function MestrePanel({ socket, salaId }) {
  const [xpAmount, setXpAmount] = useState(0);
  const [targetPlayer, setTargetPlayer] = useState('all'); // 'all' ou um ficha_id

  const handleDarXp = (e) => {
    e.preventDefault();
    alert(`Dando ${xpAmount} de XP para ${targetPlayer} (LÓGICA AINDA NÃO IMPLEMENTADA)`);
    // Aqui emitiremos o evento 'mestre_dar_xp' no futuro.
  };
  
  return (
    <div className="mestre-panel-container">
      <h2>Painel do Mestre</h2>
      
      {/* Formulário de XP */}
      <form onSubmit={handleDarXp} className="mestre-form">
        <h3>Distribuir Experiência</h3>
        <div className="form-group">
          <label htmlFor="xpAmount">Quantidade de XP</label>
          <input
            type="number"
            id="xpAmount"
            value={xpAmount}
            onChange={(e) => setXpAmount(e.target.value)}
          />
        </div>
        
        {/* O seletor de alvo será implementado quando tivermos a lista de jogadores */}
        <p>Alvo: Todos</p> 
        
        <button type="submit" className="login-button">Dar XP</button>
      </form>

      {/* Aqui adicionaremos outras ferramentas do Mestre no futuro */}
    </div>
  );
}

export default MestrePanel;