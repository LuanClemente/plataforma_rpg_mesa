// frontend/src/components/RoleSelectionModal.jsx
import React from 'react';

/**
 * Este componente é um modal que pergunta ao usuário se ele quer
 * entrar na sala como Mestre ou como Jogador.
 * @param {boolean} isOpen - Controla se o modal está visível.
 * @param {function} onClose - Função chamada quando o modal é fechado (clicando fora).
 * @param {function} onSelectRole - Função chamada quando o usuário escolhe um papel ('mestre' ou 'player').
 */
function RoleSelectionModal({ isOpen, onClose, onSelectRole }) {

  // Se o modal não deve estar aberto, ele não renderiza nada.
  if (!isOpen) {
    return null;
  }

  // Função para lidar com a escolha do papel.
  const handleSelect = (role) => {
    // Chama a função 'onSelectRole' que foi passada pelo componente pai (SalasPage),
    // enviando de volta o papel que foi escolhido.
    onSelectRole(role);
  };

  return (
    // O 'backdrop' é o fundo semi-transparente que cobre a página.
    <div className="modal-backdrop" onClick={onClose}>
      {/* e.stopPropagation() impede que um clique DENTRO do modal
        se propague para o 'backdrop' e feche o modal acidentalmente.
      */}
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h2>Como você quer entrar na sala?</h2>
        
        <div className="modal-actions">
          {/* O botão "Mestre" tem um estilo avermelhado para destacar */}
          <button 
            type="button" 
            className="login-button" 
            style={{ backgroundColor: '#ab4e4e' }} // Cor vermelha/de mestre
            onClick={() => handleSelect('mestre')}
          >
            Entrar como Mestre
          </button>
          
          <button 
            type="button" 
            className="login-button" 
            onClick={() => handleSelect('player')}
          >
            Entrar como Jogador
          </button>
        </div>
      </div>
    </div>
  );
}

export default RoleSelectionModal;