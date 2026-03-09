// frontend/src/pages/SalaPage.jsx

// Importa as ferramentas necessárias do React e de bibliotecas externas.
import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom'; // Para ler o ID da sala da URL.
import io from 'socket.io-client'; // A biblioteca cliente para se comunicar via WebSockets.
import { useAuth } from '../context/AuthContext'; // Importa o hook para usar o fetchWithAuth.

// Importa os componentes filhos que esta página irá renderizar.
import InGameFicha from '../components/InGameFicha';
import Anotacoes from '../components/Anotacoes';
import InventarioSala from '../components/InventarioSala';
import ChatMessage from '../components/ChatMessage';
import MestrePanel from '../components/MestrePanel';
import { backgrounds } from '../assets/backgrounds'; // Importa o painel do Mestre.

function SalaPage() {
  // ------------------- ESTADOS & REFS -------------------
  const { id: salaId } = useParams();
  const navigate = useNavigate(); // Pega o ID da sala da URL (ex: /salas/1).
  const { fetchWithAuth } = useAuth(); // Função de fetch com autenticação.

  const [messages, setMessages] = useState([]);      // Guarda o histórico e novas mensagens do chat.
  const [newMessage, setNewMessage] = useState('');      // Guarda o texto da caixa de chat.
  const [diceCommand, setDiceCommand] = useState('1d20');  // Guarda o comando de rolagem de dados.
  const [fichaAtiva, setFichaAtiva] = useState(null);      // Guarda os dados da ficha ativa do jogador.
  const [feedback, setFeedback] = useState('');          // Guarda mensagens de feedback (ex: "Ficha salva!").
  const [isMestre, setIsMestre] = useState(false);        // Guarda se o usuário atual é o Mestre da sala.
  const [jogadores, setJogadores] = useState([]);
  const [kickBanMsg, setKickBanMsg] = useState(null); // { tipo, mensagem }      // Guarda a lista de jogadores na sala.
  
  const socketRef = useRef(null);
  const chatEndRef = useRef(null); // ref para auto-scroll                   // Mantém a instância do socket viva entre renderizações.


  // Auto-scroll: rola o chat para baixo sempre que chegar nova mensagem
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  // Quando for kickado/banido: desconecta o socket após o estado ser atualizado
  useEffect(() => {
    if (!kickBanMsg) return;
    const socket = socketRef.current;
    if (socket) {
      setTimeout(() => socket.disconnect(), 300); // pequeno delay para o React renderizar o modal
    }
  }, [kickBanMsg]);


  // ------------------- EFEITOS (LIFECYCLE) -------------------

  // useEffect principal: Gerencia a conexão WebSocket.
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    const fichaId = sessionStorage.getItem('selectedFichaId');

    if (!fichaId) {
      setMessages(prev => [...prev, 'ERRO: Nenhum personagem foi selecionado. Por favor, volte e entre na sala novamente.']);
      return; // Interrompe a conexão se não houver ficha.
    }
    
    // Conecta-se ao servidor backend via WebSocket.
    const socket = io('http://127.0.0.1:5003');
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

    // Evento 'lista_jogadores_atualizada': Ouve pela lista de jogadores.
    socket.on('lista_jogadores_atualizada', (jogadores) => {
      console.log('Lista de jogadores recebida:', jogadores);
      // O backend envia a lista direto, não um objeto {jogadores: ...}
      setJogadores(jogadores || []);
    });

    // Evento 'ficha_atualizada': Ouve por atualizações de ficha (ex: XP).
    socket.on('ficha_atualizada', (fichaAtualizada) => {
      // Verifica se a ficha atualizada é a do jogador atual.
      // Usamos 'prevFicha' para garantir que estamos comparando com o estado mais recente.
      setFichaAtiva(prevFicha => {
        if (prevFicha && prevFicha.id === fichaAtualizada.id) {
          console.log('Ficha ativa foi atualizada pelo servidor:', fichaAtualizada);
          return fichaAtualizada; // Atualiza o estado local com os novos dados.
        }
        return prevFicha; // Mantém a ficha atual se o ID não corresponder.
      });
    });

    // Evento 'kick_ban': Mestre expulsou ou baniu este jogador
    socket.on('kick_ban', (data) => {
      console.log('⚡ kick_ban recebido:', data);
      setKickBanMsg({ tipo: data.tipo, mensagem: data.mensagem });
      // Não desconectar aqui — o useEffect abaixo cuida disso
    });

    // Função de Limpeza: É executada quando o usuário sai da página.
    return () => {
      console.log('🔌 Desconectando do WebSocket...');
      socket.disconnect();
    };
  }, [salaId]); // Dependência: reconecta se o ID da sala na URL mudar.

  // useEffect para gerenciar o fundo temático da página.
  useEffect(() => {
    document.body.style.backgroundImage = `url(${backgrounds.sala})`;
    document.body.style.backgroundSize = 'cover';
    document.body.style.backgroundPosition = 'center';
    document.body.style.backgroundAttachment = 'fixed';;
    return () => {
      document.body.style.backgroundImage = '';;
    };
  }, []); // O array vazio garante que rode apenas uma vez.

  // useEffect para buscar os dados da ficha ativa.
  useEffect(() => {
    const fichaId = sessionStorage.getItem('selectedFichaId');
    if (!fichaId) return;

    const buscarFicha = async () => {
      try {
        const response = await fetchWithAuth(`http://127.0.0.1:5003/api/fichas/${fichaId}`);
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
  
  // Função para ENVIAR MENSAGEM DE CHAT.
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

  // Função para ROLAR DADOS.
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
      const response = await fetchWithAuth(`http://127.0.0.1:5003/api/fichas/${fichaAtiva.id}`, {
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


  // Modal de kick/ban — ao fechar, redireciona para /salas
  if (kickBanMsg) {
    return (
      <div style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.92)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 9999, flexDirection: 'column', gap: '2rem', padding: '2rem'
      }}>
        <div style={{ fontSize: '4rem' }}>{kickBanMsg.tipo === 'ban' ? '🔨' : '⚡'}</div>
        <h2 style={{
          color: kickBanMsg.tipo === 'ban' ? '#c04040' : '#e0a030',
          fontFamily: "'MedievalSharp', cursive",
          textAlign: 'center', fontSize: '1.8rem',
          textShadow: '0 0 20px currentColor'
        }}>
          {kickBanMsg.tipo === 'ban' ? 'BANIDO!' : 'EXPULSO!'}
        </h2>
        <p style={{
          color: '#e0d0b0', textAlign: 'center', fontSize: '1.1rem',
          maxWidth: '500px', lineHeight: 1.6,
          background: 'rgba(30,20,5,0.8)', padding: '1.5rem',
          borderRadius: '8px', border: '1px solid #5a4520'
        }}>
          {kickBanMsg.mensagem}
        </p>
        <button
          onClick={() => navigate('/salas')}
          style={{
            background: 'linear-gradient(135deg, #8b6914, #c59d5f)',
            border: 'none', color: '#1a1208',
            fontFamily: "'MedievalSharp', cursive",
            fontSize: '1rem', padding: '0.75rem 2.5rem',
            borderRadius: '4px', cursor: 'pointer',
            boxShadow: '0 0 20px rgba(197,157,95,0.4)'
          }}
        >
          {kickBanMsg.tipo === 'ban' ? 'Iniciar Nova Aventura' : 'Voltar às Salas'}
        </button>
      </div>
    );
  }

  // ------------------- RENDERIZAÇÃO -------------------
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      {/* Barra de topo com navegação */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '1rem',
        background: 'linear-gradient(180deg, #1a1208 0%, #0f0c06 100%)',
        borderBottom: '2px solid #c59d5f',
        padding: '0.5rem 1.5rem', flexShrink: 0
      }}>
        <button
          onClick={() => navigate('/salas')}
          style={{
            background: 'rgba(197,157,95,0.15)', border: '1px solid #c59d5f',
            color: '#c59d5f', fontFamily: "'MedievalSharp', cursive",
            fontSize: '0.95rem', padding: '0.4rem 1rem', cursor: 'pointer',
            borderRadius: '4px', transition: 'background 0.2s'
          }}
          onMouseEnter={e => e.target.style.background='rgba(197,157,95,0.3)'}
          onMouseLeave={e => e.target.style.background='rgba(197,157,95,0.15)'}
        >
          ← Voltar às Salas
        </button>
        <span style={{ color: '#c59d5f', fontFamily: "'MedievalSharp', cursive", fontSize: '1.1rem' }}>
          ⚔ Sala {salaId}
        </span>
        {isMestre && <span style={{ color: '#e0a030', fontSize: '0.9rem', marginLeft: 'auto' }}>👑 Modo Mestre</span>}
      </div>
    {/* ===== ÁREA PRINCIPAL: 4 colunas ===== */}
    <div className="sala-layout-grid">
      
      {/* ----------- COLUNA ESQUERDA: Anotações (tamanho igual ao chat) ----------- */}
      <div className="sala-coluna-anotacoes">
        <Anotacoes />
      </div>

      {/* ----------- COLUNA BOLSA DE ITENS ----------- */}
      <div className="sala-coluna-inventario">
        <InventarioSala socket={socketRef.current} />
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
            <div ref={chatEndRef} />
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

    {/* ===== PAINEL DO MESTRE: faixa inferior larga ===== */}
    {isMestre && (
      <div className="sala-mestre-bar">
        <MestrePanel 
          socket={socketRef.current} 
          salaId={salaId} 
          jogadores={jogadores} 
        />
      </div>
    )}

    </div>
  );
}

export default SalaPage;