// frontend/src/context/AuthContext.jsx
import { createContext, useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';

// 1. Cria o "molde" do nosso quadro de avisos.
const AuthContext = createContext(null);

// 2. Cria o "Gerenciador do Quadro de Avisos". Este componente irá guardar e gerenciar as informações.
export function AuthProvider({ children }) {
  // O estado 'user' guardará a informação do usuário logado. Começa como nulo.
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  // A função de login agora vai morar aqui!
  const login = async (username, password) => {
    try {
      const response = await fetch('http://127.0.0.1:5001/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();

      if (data.sucesso) {
        // Se o login for um sucesso, "afixamos o aviso": guardamos o nome do usuário no estado.
        setUser({ username: username });
        // E redirecionamos para a home.
        navigate('/home');
      }
      // Retornamos os dados para que a página de login possa exibir a mensagem.
      return data;
    } catch (error) {
      console.error("Erro no login:", error);
      return { sucesso: false, mensagem: "Erro de conexão." };
    }
  };

  // A função de logout também morará aqui.
  const logout = () => {
    // "Limpa o aviso": define o usuário como nulo.
    setUser(null);
    // Envia o usuário de volta para a página de login.
    navigate('/');
  };

  // O 'value' é a informação que estará disponível para todos os componentes.
  const value = { user, login, logout };

  // O AuthProvider "envelopa" outros componentes (children) e provê a eles o 'value'.
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// 3. Cria um "atalho" para que os componentes possam acessar o quadro de avisos facilmente.
export const useAuth = () => {
  return useContext(AuthContext);
};