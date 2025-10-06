// frontend/src/pages/RegisterPage.jsx
import { useState } from 'react';
// useNavigate é uma ferramenta do React Router para redirecionar o usuário após uma ação.
import { useNavigate } from 'react-router-dom';

function RegisterPage() {
  // Criamos estados para cada campo do nosso formulário.
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  // Estado para guardar mensagens de erro ou sucesso.
  const [message, setMessage] = useState('');
  // Inicializamos o hook de navegação.
  const navigate = useNavigate();

  // Função chamada quando o formulário é enviado.
  const handleSubmit = async (event) => {
    // Impede o recarregamento padrão da página.
    event.preventDefault();

    // Verificação simples: a senha e a confirmação são iguais?
    if (password !== confirmPassword) {
      setMessage("As senhas não correspondem!");
      return; // Interrompe a função se as senhas forem diferentes.
    }

    // Tenta enviar os dados para a API de registro.
    try {
      const response = await fetch('http://127.0.0.1:5001/api/registrar', {
        method: 'POST', // O método agora é POST, pois estamos enviando dados.
        headers: {
          'Content-Type': 'application/json', // Avisa ao backend que estamos enviando JSON.
        },
        // Converte nosso objeto JavaScript para uma string JSON.
        body: JSON.stringify({ username, password }),
      });

      // Pega a resposta JSON do backend.
      const data = await response.json();

      // Define a mensagem de feedback para o usuário com base na resposta.
      setMessage(data.mensagem);

      // Se o registro for um sucesso...
      if (data.sucesso) {
        // ...espera 2 segundos e redireciona o usuário para a página de login.
        setTimeout(() => {
          navigate('/'); // A função navigate nos leva para a rota raiz (Login).
        }, 2000);
      }
    } catch (error) {
      // Em caso de erro de rede (backend offline, etc.)
      setMessage("Erro de conexão ao tentar registrar.");
      console.error("Erro de registro:", error);
    }
  };

  return (
    <div className="login-container"> {/* Reutilizando o estilo da página de login */}
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
      {/* Exibe a mensagem de feedback (erro ou sucesso) para o usuário */}
      {message && <p className="feedback-message">{message}</p>}
    </div>
  );
}

export default RegisterPage;