// frontend/src/pages/SalaPage.jsx
import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import io from 'socket.io-client';
import { useAuth } from '../context/AuthContext';

import InGameFicha from '../components/InGameFicha';
import Anotacoes from '../components/Anotacoes';
import InventarioSala from '../components/InventarioSala';
import ChatMessage from '../components/ChatMessage';
import MestrePanel from '../components/MestrePanel';
import BatalhaModal from '../components/BatalhaModal';
import { backgrounds } from '../assets/backgrounds';

function SalaPage() {
  const { id: salaId } = useParams();
  const navigate = useNavigate();
  const { fetchWithAuth } = useAuth();

  const [messages,          setMessages]          = useState([]);
  const [newMessage,        setNewMessage]        = useState('');
  const [diceCommand,       setDiceCommand]       = useState('1d20');
  const [fichaAtiva,        setFichaAtiva]        = useState(null);
  const [feedback,          setFeedback]          = useState('');
  const [isMestre,          setIsMestre]          = useState(false);
  const [jogadores,         setJogadores]         = useState([]);
  const [kickBanMsg,        setKickBanMsg]        = useState(null);
  const [batalhaAberta,     setBatalhaAberta]     = useState(false);
  const [playerMorto,       setPlayerMorto]       = useState(false);
  const [encerradaMensagem, setEncerradaMensagem] = useState(null);

  const socketRef    = useRef(null);
  const chatEndRef   = useRef(null);
  // Flag para impedir que o cleanup do StrictMode desconecte o socket
  const montadoRef   = useRef(false);

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Desconectar ao ser kickado/banido
  useEffect(() => {
    if (!kickBanMsg) return;
    const socket = socketRef.current;
    if (socket) setTimeout(() => socket.disconnect(), 300);
  }, [kickBanMsg]);

  // ── WebSocket principal ──────────────────────────────────────────────────
  useEffect(() => {
    // Evitar dupla execução do StrictMode em dev
    if (montadoRef.current) return;
    montadoRef.current = true;

    const token  = localStorage.getItem('authToken');
    const fichaId = sessionStorage.getItem('selectedFichaId');

    if (!fichaId) {
      setMessages(['ERRO: Nenhum personagem selecionado. Volte e entre na sala novamente.']);
      return;
    }

    const socket = io('http://127.0.0.1:5003', {
      transports: ['websocket', 'polling'],
    });
    socketRef.current = socket;

    socket.on('connect', () => {
      console.log('✅ Conectado ao WebSocket');
      socket.emit('join_room', { token, sala_id: salaId, ficha_id: fichaId });
    });

    socket.on('chat_history',   (data) => setMessages(data.historico || []));
    socket.on('message',        (data) => setMessages(prev => [...prev, data]));
    socket.on('status_mestre',  (data) => setIsMestre(data.isMestre));

    socket.on('lista_jogadores_atualizada', (lista) => setJogadores(lista || []));

    socket.on('ficha_atualizada', (fichaAtualizada) => {
      setFichaAtiva(prev =>
        prev && prev.id === fichaAtualizada.id ? fichaAtualizada : prev
      );
    });

    socket.on('kick_ban', (data) => setKickBanMsg({ tipo: data.tipo, mensagem: data.mensagem }));

    // Batalha
    socket.on('batalha_iniciada',  ()     => setBatalhaAberta(true));
    socket.on('batalha_encerrada', (data) => {
      setBatalhaAberta(false);
      setEncerradaMensagem(data);
      setTimeout(() => setEncerradaMensagem(null), 4000);
    });
    socket.on('jogador_morto',        () => setPlayerMorto(true));
    socket.on('jogador_ressuscitado', () => setPlayerMorto(false));
    socket.on('acao_bloqueada',   (data) => setFeedback(data.motivo));

    // Cleanup: só desconecta ao realmente sair da página (não no StrictMode)
    return () => {
      // montadoRef continua true — cleanup real só acontece ao desmontar por navegação
      if (socket && !socket.disconnected) socket.disconnect();
      montadoRef.current = false;
    };
  }, [salaId]);

  // Fundo da página
  useEffect(() => {
    document.body.style.backgroundImage    = `url(${backgrounds.sala})`;
    document.body.style.backgroundSize     = 'cover';
    document.body.style.backgroundPosition = 'center';
    document.body.style.backgroundAttachment = 'fixed';
    return () => { document.body.style.backgroundImage = ''; };
  }, []);

  // Buscar ficha ativa
  useEffect(() => {
    const fichaId = sessionStorage.getItem('selectedFichaId');
    if (!fichaId) return;
    const buscar = async () => {
      try {
        const res  = await fetchWithAuth(`http://127.0.0.1:5003/api/fichas/${fichaId}`);
        const data = await res.json();
        if (res.ok) setFichaAtiva(data);
      } catch (e) { console.error('Erro ao buscar ficha:', e); }
    };
    buscar();
  }, [salaId, fetchWithAuth]);

  // ── Handlers ────────────────────────────────────────────────────────────
  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;
    if (playerMorto) { setFeedback('Você está morto e não pode falar.'); return; }
    const socket = socketRef.current;
    if (socket) {
      socket.emit('send_message', {
        token: localStorage.getItem('authToken'),
        sala_id: salaId,
        message: newMessage,
        ficha_id: sessionStorage.getItem('selectedFichaId'),
      });
      setNewMessage('');
    }
  };

  const handleRollDice = (e) => {
    e.preventDefault();
    if (!diceCommand.trim()) return;
    if (playerMorto) { setFeedback('Você está morto e não pode rolar dados.'); return; }
    const socket = socketRef.current;
    if (socket) {
      socket.emit('roll_dice', {
        token: localStorage.getItem('authToken'),
        sala_id: salaId,
        command: diceCommand,
        ficha_id: sessionStorage.getItem('selectedFichaId'),
      });
    }
  };

  const handleAttributeChange = (atributo, delta) => {
    setFichaAtiva(prev => {
      if (!prev) return null;
      return { ...prev, atributos: { ...prev.atributos, [atributo]: (prev.atributos[atributo] || 0) + delta } };
    });
  };

  const handleSkillAdd = (novaPericia) => {
    setFichaAtiva(prev => {
      if (!prev || prev.pericias.includes(novaPericia)) return prev;
      return { ...prev, pericias: [...prev.pericias, novaPericia] };
    });
  };

  const handleSaveFicha = async () => {
    if (!fichaAtiva) return;
    setFeedback('Salvando...');
    try {
      const res  = await fetchWithAuth(`http://127.0.0.1:5003/api/fichas/${fichaAtiva.id}`, {
        method: 'PUT', body: JSON.stringify(fichaAtiva),
      });
      const data = await res.json();
      setFeedback(data.mensagem || 'Ficha salva!');
      setTimeout(() => setFeedback(''), 2000);
    } catch { setFeedback('Erro de conexão ao salvar.'); }
  };

  // ── Kick/Ban modal ──────────────────────────────────────────────────────
  if (kickBanMsg) {
    return (
      <div style={{
        position:'fixed', inset:0, background:'rgba(0,0,0,0.92)',
        display:'flex', alignItems:'center', justifyContent:'center',
        zIndex:9999, flexDirection:'column', gap:'2rem', padding:'2rem',
      }}>
        <div style={{ fontSize:'4rem' }}>{kickBanMsg.tipo === 'ban' ? '🔨' : '⚡'}</div>
        <h2 style={{
          color: kickBanMsg.tipo === 'ban' ? '#c04040' : '#e0a030',
          fontFamily:"'MedievalSharp',cursive", textAlign:'center', fontSize:'1.8rem',
        }}>
          {kickBanMsg.tipo === 'ban' ? 'BANIDO!' : 'EXPULSO!'}
        </h2>
        <p style={{
          color:'#e0d0b0', textAlign:'center', fontSize:'1.1rem',
          maxWidth:'500px', lineHeight:1.6,
          background:'rgba(30,20,5,0.8)', padding:'1.5rem',
          borderRadius:'8px', border:'1px solid #5a4520',
        }}>{kickBanMsg.mensagem}</p>
        <button onClick={() => navigate('/salas')} style={{
          background:'linear-gradient(135deg,#8b6914,#c59d5f)',
          border:'none', color:'#1a1208',
          fontFamily:"'MedievalSharp',cursive",
          fontSize:'1rem', padding:'0.75rem 2.5rem',
          borderRadius:'4px', cursor:'pointer',
        }}>
          {kickBanMsg.tipo === 'ban' ? 'Iniciar Nova Aventura' : 'Voltar às Salas'}
        </button>
      </div>
    );
  }

  // ── Render ──────────────────────────────────────────────────────────────
  return (
    <div style={{ display:'flex', flexDirection:'column', height:'100vh', overflow:'hidden' }}>

      {/* Barra de topo */}
      <div style={{
        display:'flex', alignItems:'center', gap:'1rem',
        background:'linear-gradient(180deg,#1a1208,#0f0c06)',
        borderBottom:'2px solid #c59d5f',
        padding:'0.5rem 1.5rem', flexShrink:0,
      }}>
        <button onClick={() => navigate('/salas')} style={{
          background:'rgba(197,157,95,0.15)', border:'1px solid #c59d5f',
          color:'#c59d5f', fontFamily:"'MedievalSharp',cursive",
          fontSize:'0.95rem', padding:'0.4rem 1rem', cursor:'pointer', borderRadius:'4px',
        }}>← Voltar às Salas</button>
        <span style={{ color:'#c59d5f', fontFamily:"'MedievalSharp',cursive", fontSize:'1.1rem' }}>
          ⚔ Sala {salaId}
        </span>
        {isMestre && <span style={{ color:'#e0a030', fontSize:'0.9rem', marginLeft:'auto' }}>👑 Modo Mestre</span>}
      </div>

      {/* Grid principal */}
      <div className="sala-layout-grid">

        <div className="sala-coluna-anotacoes"><Anotacoes /></div>

        <div className="sala-coluna-inventario">
          <InventarioSala socket={socketRef.current} />
        </div>

        <div className="sala-coluna-ficha">
          <InGameFicha
            ficha={fichaAtiva}
            onAttributeChange={handleAttributeChange}
            onSkillAdd={handleSkillAdd}
            onSave={handleSaveFicha}
          />
          {feedback && <p className="feedback-message" style={{ textAlign:'center' }}>{feedback}</p>}
          <div className="sala-actions-container">
            <div className="dice-roller-container">
              <h2>Rolar Dados</h2>
              <form onSubmit={handleRollDice} className="dice-roller-form">
                <input
                  type="text" value={diceCommand}
                  onChange={e => setDiceCommand(e.target.value)}
                  placeholder="ex: 2d6+3"
                />
                <button type="submit" className="roll-button">Rolar</button>
              </form>
            </div>
          </div>
        </div>

        <div className="sala-coluna-chat">
          <div className="chat-container">
            <h2>Diário da Aventura</h2>
            <div className="message-list">
              {messages.map((msg, i) => (
                <ChatMessage
                  key={i}
                  message={typeof msg === 'string' ? msg : msg.error || 'Mensagem inválida'}
                />
              ))}
              <div ref={chatEndRef} />
            </div>
            <form onSubmit={handleSendMessage} className="chat-form">
              <input
                type="text" value={newMessage}
                onChange={e => setNewMessage(e.target.value)}
                placeholder="Digite sua mensagem ou ação..."
              />
              <button type="submit">Enviar</button>
            </form>
          </div>
        </div>

      </div>

      {/* Painel do mestre */}
      {isMestre && (
        <div className="sala-mestre-bar">
          <MestrePanel socket={socketRef.current} salaId={salaId} jogadores={jogadores} />
          <button onClick={() => setBatalhaAberta(true)} style={{
            background:'linear-gradient(135deg,#8b1a1a,#c04040)',
            border:'2px solid #e04040', color:'#fff',
            fontFamily:"'MedievalSharp',cursive",
            fontSize:'0.95rem', fontWeight:'bold',
            padding:'0.5rem 1.4rem', borderRadius:'6px',
            cursor:'pointer', flexShrink:0,
            boxShadow:'0 0 16px rgba(200,40,40,0.5)',
            animation:'battlePulse 2s ease-in-out infinite',
          }}>⚔️ BATALHA</button>
        </div>
      )}

      {/* Modal de batalha — renderizado como portal fora do fluxo normal */}
      {batalhaAberta && socketRef.current && (
        <BatalhaModal
          socket={socketRef.current}
          salaId={salaId}
          isMestre={isMestre}
          onFechar={(data) => {
            setBatalhaAberta(false);
            if (data?.motivo) {
              setEncerradaMensagem(data);
              setTimeout(() => setEncerradaMensagem(null), 4000);
            }
          }}
        />
      )}

      {/* Banner fim de batalha */}
      {encerradaMensagem && (
        <div style={{
          position:'fixed', top:'50%', left:'50%',
          transform:'translate(-50%,-50%)',
          background:'linear-gradient(160deg,#1e1508,#0f0c06)',
          border:'3px solid #c59d5f', borderRadius:'12px',
          padding:'2rem 3rem', textAlign:'center',
          zIndex:9999, boxShadow:'0 0 60px rgba(0,0,0,0.9)',
          animation:'fadeInScale 0.4s ease-out',
        }}>
          <div style={{ fontSize:'4rem' }}>{encerradaMensagem.emoji}</div>
          <div style={{
            fontFamily:"'MedievalSharp',cursive", color:'#c59d5f',
            fontSize:'2rem', margin:'0.5rem 0',
          }}>{encerradaMensagem.texto}</div>
        </div>
      )}

      {/* Overlay morto */}
      {playerMorto && (
        <div style={{
          position:'fixed', bottom:'1rem', left:'50%', transform:'translateX(-50%)',
          background:'rgba(100,0,0,0.92)', border:'2px solid #c04040',
          borderRadius:'8px', padding:'0.6rem 1.5rem',
          color:'#e08080', fontFamily:"'MedievalSharp',cursive",
          fontSize:'0.9rem', zIndex:7000,
        }}>☠️ Você está morto. Aguarde o mestre.</div>
      )}

    </div>
  );
}

export default SalaPage;