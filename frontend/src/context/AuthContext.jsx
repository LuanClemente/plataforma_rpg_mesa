// frontend/src/context/AuthContext.jsx

// Importa as ferramentas necessárias do React e do React Router.
import { createContext, useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';

// Cria o Contexto (o "molde" do nosso quadro de avisos global).
const AuthContext = createContext(null);

// Cria o componente Provedor, que vai gerenciar o estado de autenticação para toda a aplicação.
export function AuthProvider({ children }) {
  // O estado 'user' guardará a informação do usuário logado.
  // A função dentro do useState é executada apenas na primeira vez que o app carrega.
  const [user, setUser] = useState(() => {
    // Procura por um "crachá" (token) salvo no localStorage do navegador.
    const token = localStorage.getItem('authToken');
    // Se encontrar um token...
    if (token) {
      // ...considera o usuário como logado, armazenando o token no estado.
      return { token: token };
    }
    // Se não encontrar, o usuário começa como deslogado (null).
    return null;
  });

  // Hook do React Router para permitir o redirecionamento de páginas.
  const navigate = useNavigate();

  // Função para realizar o login do usuário.
  const login = async (username, password) => {
    try {
      // Faz a requisição para a API de login.
      const response = await fetch('http://127.0.0.1:5001/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      // Pega a resposta do backend.
      const data = await response.json();

      // Se a resposta indicar sucesso e contiver um token...
      if (data.sucesso && data.token) {
        // 1. GUARDA O TOKEN: Salvamos o token no localStorage para persistir a sessão.
        localStorage.setItem('authToken', data.token);
        // 2. ATUALIZA O ESTADO: "Afixamos o aviso" no nosso estado global.
        setUser({ token: data.token });
        // 3. REDIRECIONA: Leva o usuário para a página principal do app.
        navigate('/home');
      }
      // Retorna os dados (com mensagem de sucesso ou erro) para a LoginPage poder exibir.
      return data;
    } catch (error) {
      console.error("Erro no login:", error);
      return { sucesso: false, mensagem: "Erro de conexão com o servidor." };
    }
  };

  // Função para realizar o logout do usuário.
  const logout = () => {
    // 1. LIMPA O TOKEN: Remove o token do localStorage, encerrando a sessão persistente.
    localStorage.removeItem('authToken');
    // 2. LIMPA O ESTADO: Define o usuário como nulo no nosso estado global.
    setUser(null);
    // 3. REDIRECIONA: Envia o usuário de volta para a página de login.
    navigate('/');
  };

  // --- NOVA FUNÇÃO DE REQUISIÇÃO AUTENTICADA ---
  const fetchWithAuth = async (url, options = {}) => {
    // Pega o token salvo no localStorage.
    const token = localStorage.getItem('authToken');
    
    // Prepara os cabeçalhos da requisição, incluindo o 'Content-Type' e o nosso token.
    const headers = {
      // Mantém quaisquer outros cabeçalhos que a requisição original possa ter.
      ...options.headers,
      'Content-Type': 'application/json',
      // Adicionamos o nosso "crachá" no cabeçalho 'x-access-token', que o nosso backend espera.
      'x-access-token': token,
    };

    // Realiza a requisição fetch com os novos cabeçalhos de autenticação.
    const response = await fetch(url, { ...options, headers });

    // Se a resposta for 401 (Unauthorized), significa que o token é inválido ou expirou.
    // Nesse caso, o melhor a fazer é deslogar o usuário para que ele possa logar novamente.
    if (response.status === 401) {
      logout();
    }
    
    // Retorna a resposta completa da requisição para a função que a chamou.
    return response;
  };

  // O 'value' é o objeto que contém todas as informações e funções que queremos disponibilizar
  // para os componentes da nossa aplicação.
  const value = { user, login, logout, fetchWithAuth };

  // O AuthProvider "envelopa" a aplicação (children) e provê a ela o 'value'.
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Hook customizado que simplifica o acesso ao contexto nos componentes.
// Em vez de 'useContext(AuthContext)', podemos simplesmente usar 'useAuth()'.
export const useAuth = () => {
  return useContext(AuthContext);
};