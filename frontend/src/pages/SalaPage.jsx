// frontend/src/pages/SalaPage.jsx

// Importa as ferramentas necessárias do React e de bibliotecas externas.
import { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom'; // Para ler o ID da sala da URL.
import io from 'socket.io-client'; // A biblioteca cliente para se comunicar via WebSockets.
import { useAuth } from '../context/AuthContext'; // Importa o hook para usar o fetchWithAuth.

// Importa os componentes filhos que esta página irá renderizar.
import InGameFicha from '../components/InGameFicha';
import Anotacoes from '../components/Anotacoes';
import InventarioSala from '../components/InventarioSala';
import ChatMessage from '../components/ChatMessage';

function SalaPage() {
  // ------------------- ESTADOS & REFS -------------------
  const { id: salaId } = useParams();
  const { fetchWithAuth } = useAuth(); // Função de fetch com autenticação.

  const [messages, setMessages] = useState([]);      // Histórico e novas mensagens do chat.
  const [newMessage, setNewMessage] = useState('');      // Texto digitado no chat.
  const [diceCommand, setDiceCommand] = useState('1d20');  // Comando de rolagem de dados.
  const [fichaAtiva, setFichaAtiva] = useState(null);      // Dados da ficha ativa do jogador.
  const [feedback, setFeedback] = useState('');          // NOVO: Mensagem de feedback para o salvamento da ficha.
  const socketRef = useRef(null);                   // Mantém a instância do socket viva.

  // ------------------- CONEXÃO SOCKET.IO -------------------
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    const fichaId = sessionStorage.getItem('selectedFichaId');
    if (!fichaId) {
      setMessages(prev => [...prev, 'ERRO: Nenhum personagem foi selecionado.']);
      return;
    }
    
    const socket = io('http://127.0.0.1:5001');
    socketRef.current = socket;

    socket.on('connect', () => {
      console.log('✅ Conectado ao servidor WebSocket');
      socket.emit('join_room', { token, sala_id: salaId, ficha_id: fichaId });
    });

    socket.on('chat_history', (data) => {
      setMessages(data.historico || []);
    });

    socket.on('message', (data) => {
      setMessages(prev => [...prev, data]);
    });

    return () => {
      console.log('🔌 Desconectando do WebSocket...');
      socket.disconnect();
    };
  }, [salaId]); // Dependência: reconecta se o ID da sala na URL mudar.

  // ------------------- APLICA FUNDO TEMÁTICO -------------------
  useEffect(() => {
    document.body.classList.add('sala-page-body');
    return () => {
      document.body.classList.remove('sala-page-body');
    };
  }, []); // O array vazio garante que rode apenas uma vez.

  // ------------------- BUSCA A FICHA ATIVA -------------------
  useEffect(() => {
    const fichaId = sessionStorage.getItem('selectedFichaId');
    if (!fichaId) return;

    const buscarFicha = async () => {
      try {
        const response = await fetchWithAuth(`http://127.0.0.1:5001/api/fichas/${fichaId}`);
        const data = await response.json();
        if (response.ok) {
          setFichaAtiva(data);
        } else {
          console.error('Erro ao carregar ficha:', data.mensagem);
        }
      } catch (error) {
        console.error('Erro ao buscar ficha ativa:', error);
      }
    };
    buscarFicha();
  }, [salaId, fetchWithAuth]); // Roda se a sala (ou a função de fetch) mudar.

  // ------------------- ENVIO DE MENSAGEM -------------------
  const handleSendMessage = (event) => {
    event.preventDefault();
    if (newMessage.trim() === '') return;
    const socket = socketRef.current;
    if (socket) {
      const token = localStorage.getItem('authToken');
      const fichaId = sessionStorage.getItem('selectedFichaId');
      socket.emit('send_message', {
        token, sala_id: salaId, message: newMessage, ficha_id: fichaId
      });
      setNewMessage('');
    }
  };

  // ------------------- ROLAGEM DE DADOS -------------------
  const handleRollDice = (event) => {
    event.preventDefault();
    if (diceCommand.trim() === '') return;
    const socket = socketRef.current;
    if (socket) {
      const token = localStorage.getItem('authToken');
      const fichaId = sessionStorage.getItem('selectedFichaId');
      socket.emit('roll_dice', {
        token, sala_id: salaId, command: diceCommand, ficha_id: fichaId
      });
    }
  };

  // --- NOVAS FUNÇÕES PARA EDIÇÃO DA FICHA ATIVA ---

  // Chamada pelo componente InGameFicha quando clicamos em + ou - em um atributo.
  const handleAttributeChange = (atributo, delta) => {
    // Atualiza o estado 'fichaAtiva' localmente no React.
    setFichaAtiva(prevFicha => {
      if (!prevFicha) return null; // Segurança
      const novoValor = (prevFicha.atributos[atributo] || 0) + delta;
      return {
        ...prevFicha, // Copia todos os dados da ficha
        atributos: {
          ...prevFicha.atributos, // Copia todos os outros atributos
          [atributo]: novoValor // Atualiza o atributo específico
        }
      };
    });
  };

  // Chamada pelo InGameFicha quando adicionamos uma nova perícia.
  const handleSkillAdd = (novaPericia) => {
    setFichaAtiva(prevFicha => {
      if (!prevFicha || prevFicha.pericias.includes(novaPericia)) {
        return prevFicha; // Não faz nada se a perícia já existir.
      }
      return {
        ...prevFicha,
        pericias: [...prevFicha.pericias, novaPericia] // Adiciona a nova perícia à lista.
      };
    });
  };

  // Chamada pelo InGameFicha quando clicamos em "Salvar Ficha".
  const handleSaveFicha = async () => {
    if (!fichaAtiva) return; // Segurança
    setFeedback('Salvando...');
    try {
      // Usa nossa rota PUT que já existe no backend!
      const response = await fetchWithAuth(`http://127.0.0.1:5001/api/fichas/${fichaAtiva.id}`, {
        method: 'PUT',
        body: JSON.stringify(fichaAtiva), // Envia o objeto 'fichaAtiva' inteiro e atualizado.
      });
      const data = await response.json();
      if (response.ok) {
        setFeedback('Ficha salva com sucesso!');
      } else {
        setFeedback(data.mensagem || 'Erro ao salvar.');
      }
      // Limpa a mensagem de feedback após 2 segundos.
      setTimeout(() => setFeedback(''), 2000);
    } catch (error) {
      setFeedback('Erro de conexão ao salvar.');
    }
  };

  // ------------------- RENDERIZAÇÃO -------------------
  return (
    <div className="sala-layout-grid">
      
      {/* ----------- COLUNA ESQUERDA (Anotações) ----------- */}
      <div className="sala-coluna-anotacoes">
        <Anotacoes />
      </div>

      {/* ----------- COLUNA BOLSA DE ITENS ----------- */}
      <div className="sala-coluna-inventario">
        <InventarioSala />
      </div>

      {/* ----------- COLUNA CENTRAL (Ficha e Dados) ----------- */}
      <div className="sala-coluna-ficha">
        {/* Passamos as novas funções como 'props' para o componente da ficha */}
        <InGameFicha 
          ficha={fichaAtiva} 
          onAttributeChange={handleAttributeChange}
          onSkillAdd={handleSkillAdd}
          onSave={handleSaveFicha}
        />
        {/* Exibe o feedback de salvamento */}
        {feedback && <p className="feedback-message" style={{textAlign: 'center'}}>{feedback}</p>}

        <div className="sala-actions-container">
          <div className="dice-roller-container">
            <h2>Rolar Dados</h2>
            <form onSubmit={handleRollDice} className="dice-roller-form">
              <input
                type="text"
                value={diceCommand}
                onChange={(e) => setDiceCommand(e.target.value)}
                placeholder="ex: 2d6+3"
              />
              <button type="submit" className="roll-button">Rolar</button>
            </form>
          </div>
        </div>
      </div>

      {/* ----------- COLUNA DIREITA (CHAT) ----------- */}
      <div className="sala-coluna-chat">
        <div className="chat-container">
          <h2>Diário da Aventura</h2>
          <div className="message-list">
            {messages.map((msg, index) => (
              <ChatMessage
                key={index}
                message={typeof msg === 'string' ? msg : msg.error || 'Mensagem inválida'}
              />
            ))}
          </div>
          <form onSubmit={handleSendMessage} className="chat-form">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Digite sua mensagem ou ação..."
            />
            <button type="submit">Enviar</button>
          </form>
        </div>
      </div>
      
    </div>
  );
}

export default SalaPage;