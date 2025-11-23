// frontend/src/components/PasswordModal.jsx
import { useState } from 'react';

// Nosso componente de Modal. Ele recebe 3 "props" (propriedades):
// isOpen: um booleano que diz se o modal deve estar visível.
// onClose: uma função para ser chamada quando o modal for fechado (clicando fora ou no 'cancelar').
// onSubmit: uma função que recebe a senha digitada quando o usuário clica em 'Confirmar'.
function PasswordModal({ isOpen, onClose, onSubmit }) {
  // O modal tem seu próprio estado para controlar o campo de senha.
  const [password, setPassword] = useState('');

  // Se 'isOpen' for falso, o componente não renderiza nada.
  if (!isOpen) {
    return null;
  }

  const handleSubmit = (event) => {
    event.preventDefault();
    // Chama a função 'onSubmit' que recebemos do componente pai, passando a senha.
    onSubmit(password);
  };

  return (
    // O 'backdrop' é o fundo semi-transparente que cobre a página.
    <div className="modal-backdrop" onClick={onClose}>
      {/* Usamos e.stopPropagation() para que um clique DENTRO do modal não feche o modal. */}
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h2>Sala Protegida</h2>
        <p>Por favor, digite a senha para entrar na taverna.</p>
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="salaPassword">Senha da Sala</label>
            <input
              type="password"
              id="salaPassword"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoFocus // Foca automaticamente no campo de senha quando o modal abre.
            />
          </div>
          <div className="modal-actions">
            <button type="button" className="login-button" style={{ backgroundColor: '#555' }} onClick={onClose}>
              Cancelar
            </button>
            <button type="submit" className="login-button">
              Confirmar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default PasswordModal;
