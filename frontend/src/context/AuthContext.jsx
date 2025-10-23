// frontend/src/context/AuthContext.jsx

// Importa as ferramentas necessárias do React e do React Router.
import { createContext, useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';

// Cria o Contexto (o "molde" do nosso quadro de avisos global).
const AuthContext = createContext(null);

// --- [NOVA] FUNÇÃO AUXILIAR PARA DECODIFICAR O TOKEN ---
/**
 * Esta função decodifica um token JWT sem precisar de bibliotecas externas.
 * Ela pega a parte do meio (payload), decodifica de Base64 e
 * converte a string JSON em um objeto JavaScript.
 * * ATENÇÃO: Isso NÃO valida a assinatura do token (o backend já fez isso),
 * apenas LÊ os dados que estão dentro dele.
 */
const parseJwt = (token) => {
  try {
    // 1. Divide o token em [header, payload, signature]
    const base64Url = token.split('.')[1]; 
    // 2. Converte o formato Base64URL para Base64 padrão
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/'); 
    // 3. Decodifica de Base64 para uma string JSON
    const jsonPayload = atob(base64); 
    // 4. Converte a string JSON em um objeto
    return JSON.parse(jsonPayload); 
  } catch (e) {
    // Se o token for inválido ou malformado, retorna nulo
    console.error("Erro ao decodificar token:", e);
    return null;
  }
};

// Cria o componente Provedor, que vai gerenciar o estado de autenticação
export function AuthProvider({ children }) {
  
  // O estado 'user' guardará a informação do usuário logado.
  // A função dentro do useState é executada apenas na primeira vez que o app carrega.
  const [user, setUser] = useState(() => {
    
    // Procura por um "crachá" (token) salvo no localStorage do navegador.
    const token = localStorage.getItem('authToken');
    
    // Se não encontrar o token, o usuário está deslogado.
    if (!token) {
      return null;
    }

    // --- [MUDANÇA PRINCIPAL] ---
    // Se encontrar um token, vamos LER o que há dentro dele.
    const userData = parseJwt(token);

    // Se o token for inválido ou expirado...
    // (userData.exp é em segundos, Date.now() é em milissegundos)
    if (!userData || userData.exp * 1000 < Date.now()) {
      // Limpa o token antigo do localStorage
      localStorage.removeItem('authToken');
      // Define o usuário como deslogado
      return null;
    }

    // Se o token for VÁLIDO e NÃO EXPIRADO...
    // Agora o nosso estado 'user' é um objeto completo!
    return {
      token: token,
      role: userData.role,  // <-- O 'role' ('mestre' ou 'player')
      name: userData.name,  // <-- O nome de usuário (ex: 'MrCap')
      id: userData.sub      // <-- O ID do usuário (subject)
    };
    // --- FIM DA MUDANÇA ---
  });

  // Hook do React Router para permitir o redirecionamento de páginas.
  const navigate = useNavigate();

  // Função para realizar o login do usuário.
  const login = async (username, password) => {
    try {
      // Faz a requisição para a API de login.
      // (Seu backend estava na porta 5001, mantive isso)
      const response = await fetch('http://127.0.0.1:5001/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      // Pega a resposta do backend.
      const data = await response.json();

      // --- [MUDANÇA PRINCIPAL] ---
      // Se a resposta indicar sucesso E contiver um token E um role...
      if (data.sucesso && data.token && data.role) {
        
        // 1. GUARDA O TOKEN: Salvamos o token no localStorage
        localStorage.setItem('authToken', data.token);

        // 2. Decodificamos o token para pegar 'name' e 'id'
        const userData = parseJwt(data.token);

        // 3. ATUALIZA O ESTADO: "Afixamos o aviso" no nosso estado global
        //    Agora salvamos o objeto de usuário completo!
        setUser({
          token: data.token,
          role: data.role,     // <-- O 'role' veio da resposta da API
          name: userData.name, // <-- O 'name' veio do token decodificado
          id: userData.sub     // <-- O 'id' veio do token decodificado
        });
        
        // 4. REDIRECIONA: Leva o usuário para a página principal do app.
        navigate('/home');
      }
      // --- FIM DA MUDANÇA ---

      // Retorna os dados (com mensagem de sucesso ou erro) para a LoginPage
      return data;
    } catch (error) {
      console.error("Erro no login:", error);
      return { sucesso: false, mensagem: "Erro de conexão com o servidor." };
    }
  };

  // Função para realizar o logout do usuário.
  const logout = () => {
    // 1. LIMPA O TOKEN: Remove o token do localStorage
    localStorage.removeItem('authToken');
    // 2. LIMPA O ESTADO: Define o usuário como nulo no nosso estado global.
    setUser(null);
    // 3. REDIRECIONA: Envia o usuário de volta para a página de login.
    navigate('/');
  };

  // --- Função de Requisição Autenticada (Sem mudanças) ---
  // Esta função já estava ótima. Ela continuará funcionando perfeitamente.
  const fetchWithAuth = async (url, options = {}) => {
    // Pega o token salvo no localStorage.
    const token = localStorage.getItem('authToken');
    
    // Prepara os cabeçalhos da requisição
    const headers = {
      ...options.headers,
      'Content-Type': 'application/json',
      'x-access-token': token,
    };

    const response = await fetch(url, { ...options, headers });

    // Se o token for inválido ou expirado (401), desloga o usuário.
    if (response.status === 401) {
      logout();
    }
    
    return response;
  };

  // O 'value' é o objeto que contém todas as informações e funções 
  // que queremos disponibilizar para os componentes.
  // O 'user' agora é o objeto completo (ou nulo).
  const value = { user, login, logout, fetchWithAuth };

  // O AuthProvider "envelopa" a aplicação (children) e provê a ela o 'value'.
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Hook customizado que simplifica o acesso ao contexto nos componentes.
// (Sem mudanças, continua perfeito)
export const useAuth = () => {
  return useContext(AuthContext);
};