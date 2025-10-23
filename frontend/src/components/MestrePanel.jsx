// frontend/src/components/MestrePanel.jsx
import React, { useState } from 'react';

/**
 * Este componente renderiza o painel de ferramentas do Mestre,
 * como a distribuição de XP.
 * Recebe o 'socket', 'salaId' e a lista de 'jogadores' como props.
 */
function MestrePanel({ socket, salaId, jogadores }) {
  // Estado para a quantidade de XP a ser dada.
  const [xpAmount, setXpAmount] = useState(100);
  // Estado para o ID da ficha alvo (ou 'all' para todos).
  const [targetFichaId, setTargetFichaId] = useState('all');
  // Estado para feedback (ex: "XP enviado!").
  const [mensagemMestre, setMensagemMestre] = useState('');

  // Função chamada ao clicar no botão "Dar XP".
  const handleDarXp = (e) => {
    e.preventDefault();
    // Verifica se temos uma conexão de socket ativa e uma quantidade de XP válida.
    if (!socket || !salaId || xpAmount <= 0) {
      setMensagemMestre("Erro: Conexão perdida ou XP inválido.");
      return;
    }

    // Pega o token para autenticar o Mestre no backend.
    const token = localStorage.getItem('authToken');
    
    // Monta o "pacote de dados" (payload) para enviar ao servidor.
    const payload = {
      token,
      sala_id: salaId,
      alvo_id: targetFichaId, // "all" ou o ID da ficha específica.
      quantidade: parseInt(xpAmount, 10), // Garante que é um número.
    };

    console.log("Emitindo 'mestre_dar_xp' com payload:", payload);
    // Emite o evento 'mestre_dar_xp' para o servidor WebSocket.
    socket.emit('mestre_dar_xp', payload);

    // Fornece feedback imediato para o Mestre.
    setMensagemMestre(`${xpAmount} XP distribuído!`);
    setTimeout(() => setMensagemMestre(''), 3000); // Limpa a mensagem após 3 segundos.
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
          {/* O seletor de alvo, agora funcional! */}
          <select 
            id="targetPlayer" 
            value={targetFichaId} 
            onChange={(e) => setTargetFichaId(e.target.value)}
          >
            {/* Opção padrão para "Todos" */}
            <option value="all">-- Todos os Jogadores --</option>
            
            {/* Mapeia a lista de 'jogadores' recebida via props. */}
            {jogadores
              // Filtramos para mostrar apenas jogadores (não o mestre).
              .filter(jogador => jogador.role === 'player')
              // Criamos uma <option> para cada jogador.
              .map(jogador => (
                <option key={jogador.ficha_id} value={jogador.ficha_id}>
                  {jogador.nome_personagem}
                </option>
            ))}
          </select>
        </div>
        
        <button type="submit" className="login-button">Dar XP</button>
        {/* Exibe a mensagem de feedback para o Mestre */}
        {mensagemMestre && <p className="feedback-message" style={{fontSize: '0.9rem'}}>{mensagemMestre}</p>}
      </form>
    </div>
  );
}

export default MestrePanel;