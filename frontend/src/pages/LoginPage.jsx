// frontend/src/pages/LoginPage.jsx

// Importamos o 'useState' para controlar os campos do formulário.
import { useState } from 'react';
// Importamos o 'Link' para o link de "Criar conta". O useNavigate não é mais necessário aqui.
import { Link } from 'react-router-dom';
// 1. Importamos nosso hook 'useAuth', que nos dá acesso ao "Quadro de Avisos" (nosso AuthContext).
import { useAuth } from '../context/AuthContext';

// Define o componente da página de Login.
function LoginPage() {
  // Estados para guardar os valores dos campos do formulário (sem alterações).
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  // Estado para guardar mensagens de erro ou sucesso para o usuário.
  const [message, setMessage] = useState('');
  
  // 2. Usamos nosso hook para pegar a função 'login' que está centralizada no AuthContext.
  // Não precisamos mais do 'navigate' aqui, pois o próprio AuthContext cuidará do redirecionamento.
  const { login } = useAuth();

  // Esta é a nova função 'handleSubmit', agora muito mais simples.
  const handleSubmit = async (event) => {
    // Impede o recarregamento padrão da página.
    event.preventDefault(); 
    // Limpa mensagens de erro antigas.
    setMessage('');

    try {
      // 3. Simplesmente chamamos a função 'login' do nosso contexto, passando o usuário e a senha.
      // A função 'login' no AuthContext agora é responsável por fazer o fetch,
      // atualizar o estado global do usuário e redirecionar a página.
      const response = await login(username, password);
      
      // Se a resposta do login (que vem do AuthContext) indicar falha...
      if (!response.sucesso) {
        // ...mostramos a mensagem de erro que ela nos retornou.
        setMessage(response.mensagem);
      }
      // Não precisamos mais do 'else' ou do 'setTimeout', pois o AuthContext já cuida do sucesso.

    } catch (error) {
      // O catch ainda é útil para erros inesperados.
      setMessage("Ocorreu um erro inesperado.");
      console.error("Erro no handleSubmit do Login:", error);
    }
  };

  // O JSX do formulário (a parte visual) permanece exatamente o mesmo.
  return (
    <div className="login-container">
      <h1>Acesso à Fortaleza</h1>
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
        <button type="submit" className="login-button">Entrar</button>
      </form>

      {/* Exibe a mensagem de feedback (erro ou sucesso) para o usuário */}
      {message && <p className="feedback-message">{message}</p>}

      {/* Link para a página de cadastro */}
      <div className="register-link">
        <p>
          Não tem uma conta? 
          <Link to="/registrar"> Crie uma agora!</Link>
        </p>
      </div>
    </div>
  );
}

// Exporta o componente para ser usado pelo App.jsx.
export default LoginPage;