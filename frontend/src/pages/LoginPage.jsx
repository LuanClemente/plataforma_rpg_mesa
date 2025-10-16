// frontend/src/pages/LoginPage.jsx

// Importa as ferramentas 'useState' e 'useEffect' do React.
// useState para gerenciar dados que mudam (o texto nos inputs).
// useEffect para executar "efeitos colaterais" (como modificar o <body> do HTML).
import { useState, useEffect } from 'react';
// Importa o componente 'Link' do React Router para criar links de navegação que não recarregam a página.
import { Link } from 'react-router-dom';
// Importamos nosso hook 'useAuth' para acessar a função de login centralizada no nosso AuthContext.
import { useAuth } from '../context/AuthContext';

// Define o componente da página de Login.
function LoginPage() {
  // --- Estados do Componente ---
  // Estado para guardar o valor do campo de usuário.
  const [username, setUsername] = useState('');
  // Estado para guardar o valor do campo de senha.
  const [password, setPassword] = useState('');
  // Estado para guardar mensagens de erro ou sucesso para o usuário.
  const [message, setMessage] = useState('');
  
  // Usamos nosso hook para pegar a função 'login' do AuthContext.
  const { login } = useAuth();

  // --- Efeito para o Fundo da Página ---
  // Este useEffect gerencia a classe CSS no <body> para o fundo temático.
  useEffect(() => {
    // Quando o componente LoginPage é "montado" (aparece na tela),
    // nós adicionamos a classe CSS 'login-page-body' ao <body> do documento.
    document.body.classList.add('login-page-body');

    // O 'return' de um useEffect é uma "função de limpeza".
    // Ela é executada quando o componente é "desmontado" (quando o usuário navega para outra página).
    return () => {
      // Nós removemos a classe para que as outras páginas não tenham a imagem de fundo.
      document.body.classList.remove('login-page-body');
    };
  }, []); // O array vazio '[]' garante que este efeito rode apenas uma vez (na montagem) e a limpeza uma vez (na desmontagem).

  // --- Funções de Lógica ---
  // Função que é chamada quando o formulário é enviado.
  const handleSubmit = async (event) => {
    event.preventDefault(); // Impede o recarregamento padrão da página.
    setMessage(''); // Limpa mensagens de erro antigas a cada nova tentativa.
    try {
      // Chama a função 'login' do nosso contexto, que lida com a chamada à API.
      const response = await login(username, password);
      // Se a resposta do login (que vem do AuthContext) indicar falha...
      if (!response.sucesso) {
        // ...mostramos a mensagem de erro que o backend nos enviou.
        setMessage(response.mensagem);
      }
    } catch (error) {
      // Captura erros inesperados durante o processo.
      setMessage("Ocorreu um erro inesperado.");
      console.error("Erro no handleSubmit do Login:", error);
    }
  };

  // --- Renderização do Componente (JSX) ---
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