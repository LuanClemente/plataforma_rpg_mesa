// frontend/src/pages/SalaPage.jsx

// Importa as ferramentas necessárias do React e de bibliotecas externas.
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom'; // Para ler parâmetros da URL, como o ID da sala.
import io from 'socket.io-client'; // A biblioteca cliente para se comunicar via WebSockets.
import { useAuth } from '../context/AuthContext'; // Para pegar o token de autenticação.

function SalaPage() {
  // --- Estados do Componente ---
  // O hook 'useParams' extrai o parâmetro 'id' da URL (ex: de /salas/1, o id será "1").
  const { id: salaId } = useParams();
  // Estado para guardar a lista de mensagens do chat e eventos da sala.
  const [messages, setMessages] = useState([]);
  
  // --- Efeitos do Componente (Lifecycle) ---

  // Este useEffect gerencia a conexão WebSocket. Ele é o coração da comunicação em tempo real.
  useEffect(() => {
    // Pega o token de autenticação salvo no localStorage do navegador.
    const token = localStorage.getItem('authToken');

    // 1. Estabelece a conexão com nosso servidor backend na porta 5001.
    const socket = io('http://127.0.0.1:5001');

    // 2. Define um "ouvinte" para o evento 'connect'.
    // Este evento é disparado automaticamente pela biblioteca quando a conexão é bem-sucedida.
    socket.on('connect', () => {
      console.log('Conectado ao servidor WebSocket!');
      // Assim que conectado, envia (emite) o evento 'join_room' para o backend.
      // Junto, enviamos nosso "crachá" (token) e o ID da sala que queremos entrar.
      socket.emit('join_room', { token: token, sala_id: salaId });
    });

    // 3. Define um "ouvinte" para o evento 'message'.
    // Este é o evento padrão que o 'send()' do backend utiliza. Qualquer mensagem enviada pelo servidor
    // para esta sala será recebida aqui.
    socket.on('message', (data) => {
      // Adiciona a nova mensagem recebida à nossa lista de mensagens na tela.
      setMessages(prevMessages => [...prevMessages, data]);
    });

    // 4. A função de limpeza (return) é executada quando o componente é "desmontado" (quando o jogador sai da página).
    return () => {
      console.log('Desconectando do servidor WebSocket...');
      // Encerra a conexão WebSocket para economizar recursos do servidor e do cliente.
      socket.disconnect();
    };
  }, [salaId]); // A lista de dependências '[salaId]' diz ao React para rodar este efeito novamente se a URL da sala mudar.

  // Este useEffect gerencia o fundo temático da página.
  useEffect(() => {
    // Adiciona a classe CSS 'sala-page-body' ao <body> do documento.
    document.body.classList.add('sala-page-body');
    // A função de limpeza remove a classe quando o usuário navega para outra página.
    return () => {
      document.body.classList.remove('sala-page-body');
    };
  }, []); // O array vazio '[]' garante que o efeito só rode na montagem e desmontagem.

  // --- Renderização do Componente ---
  return (
    <div>
      <h1>Sala de Campanha: {salaId}</h1>
      <div className="chat-container">
        <h2>Diário da Aventura</h2>
        <div className="message-list">
          {/* Mapeia e exibe cada mensagem recebida do servidor. */}
          {messages.map((msg, index) => (
            // A 'key' é importante para o React otimizar a renderização de listas.
            // Verificamos se a mensagem é um objeto de erro ou um texto simples.
            <p key={index}>{typeof msg === 'object' ? msg.error : msg}</p>
          ))}
        </div>
        {/* No futuro, aqui teremos o campo para o jogador digitar e enviar mensagens. */}
      </div>
    </div>
  );
}

export default SalaPage;