// frontend/src/components/CharacterSelectionModal.jsx

// Este componente mostra uma lista de fichas para o usuário escolher.
function CharacterSelectionModal({ isOpen, onClose, fichas, onSelect }) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h2>Escolha seu Aventureiro</h2>
        <div className="character-selection-list">
          {fichas.length > 0 ? (
            fichas.map(ficha => (
              <div key={ficha.id} className="character-card" onClick={() => onSelect(ficha)}>
                <h3>{ficha.nome_personagem}</h3>
                <p>{ficha.classe} - Nível {ficha.nivel}</p>
              </div>
            ))
          ) : (
            <p>Você não tem nenhuma ficha criada. Volte e crie uma na aba "Minhas Fichas"!</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default CharacterSelectionModal;
