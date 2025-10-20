// frontend/src/components/MestrePanel.jsx
import React, { useState } from 'react';

// Este componente receberá o 'socket', 'salaId' e a lista de 'jogadores' como props.
function MestrePanel({ socket, salaId, jogadores }) {
  const [xpAmount, setXpAmount] = useState(100);
  const [targetFichaId, setTargetFichaId] = useState('all'); // 'all' ou um ficha_id

  const handleDarXp = (e) => {
    e.preventDefault();
    if (!socket || !salaId || xpAmount <= 0) {
      alert("Erro: Não foi possível enviar o comando de XP.");
      return;
    }

    const token = localStorage.getItem('authToken');
    const payload = {
      token,
      sala_id: salaId,
      alvo_id: targetFichaId, // O ID da ficha do alvo ou 'all'
      quantidade: parseInt(xpAmount, 10),
    };

    console.log("Emitindo 'mestre_dar_xp' com payload:", payload);
    socket.emit('mestre_dar_xp', payload);
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
        
        <div className="form-group">
          <label htmlFor="targetPlayer">Alvo</label>
          <select 
            id="targetPlayer" 
            value={targetFichaId} 
            onChange={(e) => setTargetFichaId(e.target.value)}
          >
            <option value="all">-- Todos os Jogadores --</option>
            {jogadores.map(jogador => (
              <option key={jogador.id} value={jogador.id}>{jogador.nome_personagem}</option>
            ))}
          </select>
        </div>
        
        <button type="submit" className="login-button">Dar XP</button>
      </form>

      {/* Aqui adicionaremos outras ferramentas do Mestre no futuro */}
    </div>
  );
}

export default MestrePanel;