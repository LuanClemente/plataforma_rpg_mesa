// frontend/src/pages/RegisterPage.jsx

// Importa as ferramentas 'useState' e 'useEffect' do React e 'useNavigate' do React Router.
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

// Define o componente da página de Registro.
function RegisterPage() {
  // --- Estados do Componente ---
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState(''); // Guarda mensagens de feedback (ex: "Usuário criado!").
  const navigate = useNavigate(); // Hook para redirecionar o usuário.

  // --- Efeitos do Componente ---
  // Este useEffect gerencia o fundo temático da página.
  useEffect(() => {
    // Adiciona a mesma classe da página de login para manter a consistência visual.
    document.body.classList.add('login-page-body');
    // A função de limpeza (return) é executada quando o usuário sai desta página.
    return () => {
      // Remove a classe para que as outras páginas não tenham a mesma imagem de fundo.
      document.body.classList.remove('login-page-body');
    };
  }, []); // O array vazio '[]' garante que este efeito rode apenas uma vez.

  // --- Funções de Lógica ---
  // Função chamada quando o formulário é enviado.
  const handleSubmit = async (event) => {
    event.preventDefault(); // Impede o recarregamento padrão da página.

    // Validação no frontend: verifica se a senha e a confirmação são iguais.
    if (password !== confirmPassword) {
      setMessage("As senhas não correspondem!");
      return; // Interrompe a função se as senhas forem diferentes.
    }

    try {
      // Envia os dados para a API de registro no backend.
      const response = await fetch('http://127.0.0.1:5001/api/registrar', {
        method: 'POST', // Usamos POST para criar um novo recurso (usuário).
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }), // Envia o usuário e a senha no corpo da requisição.
      });

      const data = await response.json(); // Lê a resposta do backend.
      setMessage(data.mensagem); // Mostra a mensagem de sucesso ou erro do backend.

      if (data.sucesso) {
        // Se o registro for bem-sucedido, espera 2 segundos e redireciona para a página de login.
        setTimeout(() => {
          navigate('/'); // Redireciona para a rota raiz ('/').
        }, 2000);
      }
    } catch (error) {
      setMessage("Erro de conexão ao tentar registrar.");
      console.error("Erro de registro:", error);
    }
  };

  // --- Renderização do Componente (JSX) ---
  return (
    <div className="login-container">
      <h1>Criar Nova Conta</h1>
      <form onSubmit={handleSubmit} className="login-form">
        <div className="form-group">
          <label htmlFor="username">Nome de Usuário</label>
          <input 
            type="text" 
            id="username" 
            value={username}
            onChange={(e) => setUsername(e.target.value)} 
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Palavra-Passe</label>
          <input 
            type="password" 
            id="password" 
            value={password}
            onChange={(e) => setPassword(e.target.value)} 
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="confirmPassword">Confirmar Palavra-Passe</label>
          <input 
            type="password" 
            id="confirmPassword" 
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)} 
            required
          />
        </div>
        <button type="submit" className="login-button">Registrar</button>
      </form>
      {/* Exibe a mensagem de feedback para o usuário */}
      {message && <p className="feedback-message">{message}</p>}
    </div>
  );
}

export default RegisterPage;