// frontend/src/pages/LoginPage.jsx

// Importa a ferramenta 'useState' do React para gerenciar o estado dos campos do formulário.
import { useState } from 'react';
// Importa o componente 'Link' do React Router para criar links de navegação.
import { Link } from 'react-router-dom';

// Define o componente da página de Login.
function LoginPage() {
  // Cria uma "caixa" (estado) chamada 'username' para guardar o valor do campo de usuário.
  // 'setUsername' é a função que usamos para atualizar esse valor.
  const [username, setUsername] = useState('');
  // Cria outra "caixa" (estado) para guardar o valor do campo de senha.
  const [password, setPassword] = useState('');

  // Esta função será chamada quando o jogador clicar no botão "Entrar".
  const handleSubmit = (event) => {
    // 'event.preventDefault()' impede que a página recarregue, que é o comportamento
    // padrão de um formulário HTML, permitindo que nosso código React controle a ação.
    event.preventDefault(); 
    
    // Por enquanto, como o login ainda não foi implementado no backend,
    // vamos apenas mostrar os dados no console do navegador (F12) e um alerta.
    console.log("Tentativa de login com:");
    console.log("Usuário:", username);
    console.log("Senha:", password);
    alert(`A lógica de login para o usuário ${username} ainda será implementada!`);
  };

  // O 'return' define o que o componente vai renderizar na tela em JSX.
  return (
    // Reutilizamos a classe 'login-container' que já estilizamos no nosso CSS.
    <div className="login-container">
      <h1>Acesso à Fortaleza</h1>
      {/* O evento 'onSubmit' do formulário chama nossa função 'handleSubmit' quando o botão do tipo 'submit' é clicado. */}
      <form onSubmit={handleSubmit} className="login-form">
        <div className="form-group">
          <label htmlFor="username">Nome de Usuário</label>
          {/* Este é um "componente controlado". O valor do input é sempre o que está no nosso estado 'username'. */}
          <input 
            type="text" 
            id="username" 
            value={username}
            // O evento 'onChange' é disparado toda vez que o usuário digita algo.
            // 'e.target.value' contém o texto atual do campo, que usamos para atualizar nosso estado com 'setUsername'.
            onChange={(e) => setUsername(e.target.value)} 
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Palavra-Passe</label>
          <input 
            type="password" 
            id="password" 
            value={password}
            onChange={(e) => setPassword(e.target.value)} 
          />
        </div>
        <button type="submit" className="login-button">Entrar</button>
      </form>

      {/* --- CÓDIGO ADICIONADO --- */}
      {/* Esta seção cria o link para a página de cadastro. */}
      <div className="register-link">
        <p>
          Não tem uma conta? 
          {/* O componente <Link> do React Router cria um link que navega para a rota especificada em 'to' */}
          {/* sem recarregar a página, proporcionando uma experiência de SPA (Single-Page Application). */}
          <Link to="/registrar"> Crie uma agora!</Link>
        </p>
      </div>
    </div>
  );
}

// Exporta o componente para que ele possa ser usado pelo App.jsx.
export default LoginPage;