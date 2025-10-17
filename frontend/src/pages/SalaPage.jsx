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
import MestrePanel from '../components/MestrePanel'; // Importa o painel do Mestre.

function SalaPage() {
  // ------------------- ESTADOS & REFS -------------------
  const { id: salaId } = useParams(); // Pega o ID da sala da URL.
  const { fetchWithAuth } = useAuth(); // Função de fetch com autenticação.

  const [messages, setMessages] = useState([]);      // Guarda o histórico e novas mensagens do chat.
  const [newMessage, setNewMessage] = useState('');      // Guarda o texto da caixa de chat.
  const [diceCommand, setDiceCommand] = useState('1d20');  // Guarda o comando de rolagem de dados.
  const [fichaAtiva, setFichaAtiva] = useState(null);      // Guarda os dados da ficha ativa do jogador.
  const [feedback, setFeedback] = useState('');          // Guarda mensagens de feedback (ex: "Ficha salva!").
  const [isMestre, setIsMestre] = useState(false);        // Guarda se o usuário atual é o Mestre da sala.
  
  const socketRef = useRef(null);                   // Mantém a instância do socket viva entre renderizações.

  // ------------------- CONEXÃO SOCKET.IO -------------------
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    const fichaId = sessionStorage.getItem('selectedFichaId');

    if (!fichaId) {
      setMessages(prev => [...prev, 'ERRO: Nenhum personagem foi selecionado. Por favor, volte e entre na sala novamente.']);
      return; // Interrompe a conexão se não houver ficha.
    }
    
    // Conecta-se ao servidor backend via WebSocket.
    const socket = io('http://127.0.0.1:5001');
    socketRef.current = socket;

    // Evento 'connect': Dispara quando a conexão é estabelecida.
    socket.on('connect', () => {
      console.log('✅ Conectado ao servidor WebSocket');
      // Emite o evento 'join_room', enviando o token e o ID da ficha.
      socket.emit('join_room', { token, sala_id: salaId, ficha_id: fichaId });
    });

    // Evento 'chat_history': Ouve pelo histórico enviado pelo servidor.
    socket.on('chat_history', (data) => {
      setMessages(data.historico || []);
    });

    // Evento 'message': Ouve por novas mensagens em tempo real.
    socket.on('message', (data) => {
      setMessages(prev => [...prev, data]);
    });
    
    // Evento 'status_mestre': Ouve pelo "sinal secreto" do servidor.
    socket.on('status_mestre', (data) => {
      console.log('Status de Mestre recebido:', data.isMestre);
      setIsMestre(data.isMestre); // Atualiza o estado para mostrar/esconder o painel do Mestre.
    });

    // Função de Limpeza: É executada quando o usuário sai da página.
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

  // ------------------- FUNÇÕES DE LÓGICA (HANDLERS) -------------------
  const handleSendMessage = (event) => {
    event.preventDefault();
    if (newMessage.trim() === '') return;
    const socket = socketRef.current;
    if (socket) {
      const token = localStorage.getItem('authToken');
      const fichaId = sessionStorage.getItem('selectedFichaId');
      socket.emit('send_message', { token, sala_id: salaId, message: newMessage, ficha_id: fichaId });
      setNewMessage('');
    }
  };

  const handleRollDice = (event) => {
    event.preventDefault();
    if (diceCommand.trim() === '') return;
    const socket = socketRef.current;
    if (socket) {
      const token = localStorage.getItem('authToken');
      const fichaId = sessionStorage.getItem('selectedFichaId');
      socket.emit('roll_dice', { token, sala_id: salaId, command: diceCommand, ficha_id: fichaId });
    }
  };

  // Chamada pelo InGameFicha quando clicamos em + ou - em um atributo.
  const handleAttributeChange = (atributo, delta) => {
    setFichaAtiva(prevFicha => {
      if (!prevFicha) return null;
      const novoValor = (prevFicha.atributos[atributo] || 0) + delta;
      return { ...prevFicha, atributos: { ...prevFicha.atributos, [atributo]: novoValor }};
    });
  };

  // Chamada pelo InGameFicha quando adicionamos uma nova perícia.
  const handleSkillAdd = (novaPericia) => {
    setFichaAtiva(prevFicha => {
      if (!prevFicha || prevFicha.pericias.includes(novaPericia)) return prevFicha;
      return { ...prevFicha, pericias: [...prevFicha.pericias, novaPericia] };
    });
  };

  // Chamada pelo InGameFicha quando clicamos em "Salvar Ficha".
  const handleSaveFicha = async () => {
    if (!fichaAtiva) return;
    setFeedback('Salvando...');
    try {
      const response = await fetchWithAuth(`http://127.0.0.1:5001/api/fichas/${fichaAtiva.id}`, {
        method: 'PUT',
        body: JSON.stringify(fichaAtiva),
      });
      const data = await response.json();
      setFeedback(data.mensagem || 'Ficha salva!');
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
        {/* Renderização Condicional: O Painel do Mestre SÓ aparece se 'isMestre' for true. */}
        {isMestre && <MestrePanel socket={socketRef.current} salaId={salaId} />}
      </div>

      {/* ----------- COLUNA BOLSA DE ITENS ----------- */}
      <div className="sala-coluna-inventario">
        <InventarioSala />
      </div>

      {/* ----------- COLUNA CENTRAL (Ficha e Dados) ----------- */}
      <div className="sala-coluna-ficha">
        <InGameFicha 
          ficha={fichaAtiva} 
          onAttributeChange={handleAttributeChange}
          onSkillAdd={handleSkillAdd}
          onSave={handleSaveFicha}
        />
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