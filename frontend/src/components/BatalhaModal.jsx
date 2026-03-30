// frontend/src/components/BatalhaModal.jsx
import { useState, useEffect, useRef } from 'react';

// ── Avatares por tipo ────────────────────────────────────────────────────────
const TIPO_AVATAR = {
  dragon:'🐉', undead:'💀', humanoid:'🧝', beast:'🐺', demon:'😈',
  devil:'👿', fey:'🧚', giant:'👹', elemental:'🌊', fiend:'🔥',
  celestial:'✨', construct:'⚙️', monstrosity:'👾', ooze:'🫧',
  plant:'🌿', aberration:'🦑', default:'👹',
};
function getEmoji(tipo) {
  if (!tipo) return TIPO_AVATAR.default;
  const t = tipo.toLowerCase();
  for (const k of Object.keys(TIPO_AVATAR))
    if (k !== 'default' && t.includes(k)) return TIPO_AVATAR[k];
  return TIPO_AVATAR.default;
}

// ── Sons ────────────────────────────────────────────────────────────────────
function playSound(tipo) {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain); gain.connect(ctx.destination);
    if (tipo === 'hit') {
      osc.frequency.setValueAtTime(150, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(50, ctx.currentTime + 0.15);
      gain.gain.setValueAtTime(0.4, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.15);
      osc.start(); osc.stop(ctx.currentTime + 0.15);
    } else if (tipo === 'cura') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(440, ctx.currentTime);
      osc.frequency.setValueAtTime(660, ctx.currentTime + 0.1);
      gain.gain.setValueAtTime(0.2, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
      osc.start(); osc.stop(ctx.currentTime + 0.3);
    }
  } catch {}
}

// ── POW aleatório ────────────────────────────────────────────────────────────
const POWS = ['POW!', 'SLASH!', 'BOOM!', 'CRACK!', 'SMASH!', 'HIT!'];
const getPow = () => POWS[Math.floor(Math.random() * POWS.length)];

// ── Rolador de dados local ───────────────────────────────────────────────────
function rolarDado(lados) {
  return Math.floor(Math.random() * lados) + 1;
}
function parsearERotar(expr) {
  // Ex: "2d6" → rola 2d6, "1d6+1d10" → soma ambos
  let total = 0;
  let partes = [];
  const grupos = expr.toLowerCase().split('+');
  for (const g of grupos) {
    const m = g.trim().match(/^(\d+)?d(\d+)$/);
    if (m) {
      const qtd = parseInt(m[1] || '1');
      const lados = parseInt(m[2]);
      let soma = 0;
      for (let i = 0; i < qtd; i++) {
        const r = rolarDado(lados);
        soma += r;
        partes.push(`d${lados}=${r}`);
      }
      total += soma;
    }
  }
  return { total, str: partes.join(' + ') };
}

// ── Card participante ────────────────────────────────────────────────────────
function CardParticipante({ p, isMonstro, isMestre, emTurno, selecionado, onClick, flashando, movendo }) {
  const statusCor = {
    vivo: '#80c880', caido: '#e0a030', morto: '#c04040',
    derrotado: '#c04040', fugiu: '#888',
  }[p.status] || '#888';

  const fora = ['morto','derrotado','fugiu'].includes(p.status);

  return (
    <div
      onClick={!fora ? onClick : undefined}
      style={{
        background: selecionado ? 'rgba(197,157,95,0.25)'
          : emTurno ? 'rgba(60,180,60,0.15)' : 'rgba(15,10,2,0.92)',
        border: selecionado ? '2px solid #c59d5f'
          : emTurno ? '2px solid #60c060' : '1px solid #3a2a10',
        borderRadius: '10px',
        padding: '0.7rem 0.6rem',
        textAlign: 'center',
        cursor: onClick && !fora ? 'pointer' : 'default',
        opacity: fora ? 0.3 : 1,
        minWidth: isMonstro ? '110px' : '100px',
        maxWidth: isMonstro ? '130px' : '120px',
        position: 'relative',
        transition: 'border-color 0.15s',
        transform: movendo ? (isMonstro ? 'translateX(-25px) scale(1.1)' : 'translateX(25px) scale(1.1)') : 'none',
        filter: flashando ? 'brightness(2.5) saturate(4)' : 'none',
      }}
    >
      {emTurno && !fora && (
        <div style={{
          position: 'absolute', top: '-12px', left: '50%', transform: 'translateX(-50%)',
          background: '#60c060', color: '#050', fontSize: '0.6rem',
          fontFamily: "'MedievalSharp',cursive", padding: '0.1rem 0.5rem',
          borderRadius: '4px', whiteSpace: 'nowrap', zIndex: 2,
        }}>SEU TURNO</div>
      )}
      {p.iniciativa > 0 && (
        <div style={{
          position: 'absolute', top: '4px', right: '4px',
          background: 'rgba(197,157,95,0.85)', color: '#1a1208',
          width: '20px', height: '20px', borderRadius: '50%',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '0.65rem', fontWeight: 'bold',
        }}>{p.iniciativa}</div>
      )}
      <div style={{ fontSize: isMonstro ? '2.8rem' : '2.2rem', lineHeight: 1 }}>
        {isMonstro ? getEmoji(p.tipo) : '🧙'}
      </div>
      <div style={{
        color: '#e0d0b0', fontFamily: "'MedievalSharp',cursive",
        fontSize: '0.72rem', marginTop: '0.35rem',
        overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
      }}>{p.nome}</div>
      <div style={{ fontSize: '0.7rem', color: statusCor, marginTop: '0.15rem' }}>
        {p.status === 'vivo' && !isMonstro && `❤ ${p.hp_atual}`}
        {p.status === 'vivo' && isMonstro && !isMestre && `CA ${p.ca}`}
        {p.status === 'vivo' && isMonstro && isMestre && `❤ ${p.hp_atual}/${p.hp_max}`}
        {p.status === 'caido' && '💛 Caído'}
        {p.status === 'morto' && '☠️ Morto'}
        {p.status === 'derrotado' && '💥 Derrotado'}
        {p.status === 'fugiu' && '💨 Fugiu'}
      </div>
    </div>
  );
}

// ── Seletor de monstros ──────────────────────────────────────────────────────
function SeletorMonstros({ onConfirmar, onCancelar }) {
  const [busca, setBusca]           = useState('');
  const [resultados, setResultados] = useState([]);
  const [selecionados, setSelecionados] = useState([]);
  const [carregando, setCarregando] = useState(false);

  useEffect(() => {
    if (!busca.trim()) { setResultados([]); return; }
    setCarregando(true);
    fetch(`http://127.0.0.1:5003/api/monstros?nome=${encodeURIComponent(busca)}`)
      .then(r => r.json())
      .then(d => { setResultados(d.slice(0,10)); setCarregando(false); })
      .catch(() => setCarregando(false));
  }, [busca]);

  const toggle = (m) => setSelecionados(prev =>
    prev.find(x => x.id === m.id) ? prev.filter(x => x.id !== m.id) : [...prev, m]
  );

  const f = {
    background:'#1a1208', border:'1px solid #5a4520', color:'#e0d0b0',
    borderRadius:'4px', padding:'0.4rem 0.6rem', fontSize:'0.85rem',
    width:'100%', boxSizing:'border-box',
  };

  return (
    <div style={{
      position:'fixed', inset:0, background:'rgba(0,0,0,0.88)',
      display:'flex', alignItems:'center', justifyContent:'center',
      zIndex:9600, backdropFilter:'blur(5px)',
    }}>
      <div style={{
        background:'linear-gradient(160deg,#1e1508,#0f0c06)',
        border:'2px solid #c59d5f', borderRadius:'10px',
        width:'520px', maxHeight:'80vh', overflowY:'auto',
        padding:'1.5rem', color:'#e0d0b0',
      }}>
        <h2 style={{ fontFamily:"'MedievalSharp',cursive", color:'#c59d5f', margin:'0 0 1rem' }}>
          ⚔️ Iniciar Batalha
        </h2>
        <p style={{ color:'#887060', fontSize:'0.82rem', margin:'0 0 1rem' }}>
          Busque e selecione os monstros que vão entrar em combate.
        </p>

        <input value={busca} onChange={e => setBusca(e.target.value)}
          placeholder="🔍 Nome do monstro (ex: Dragon, Goblin...)"
          style={f} autoFocus />

        {carregando && <p style={{ color:'#666', fontSize:'0.8rem', margin:'0.4rem 0' }}>Buscando...</p>}

        {resultados.length > 0 && (
          <div style={{
            border:'1px solid #3a2a10', borderRadius:'4px',
            maxHeight:'200px', overflowY:'auto', marginTop:'0.4rem',
          }}>
            {resultados.map(m => (
              <div key={m.id} onClick={() => toggle(m)} style={{
                padding:'0.45rem 0.8rem', cursor:'pointer',
                background: selecionados.find(x=>x.id===m.id) ? 'rgba(197,157,95,0.18)' : 'transparent',
                borderBottom:'1px solid #2a1a08',
                display:'flex', justifyContent:'space-between', alignItems:'center',
                transition:'background 0.12s',
              }}>
                <span style={{ fontSize:'0.85rem' }}>{getEmoji(m.tipo)} {m.nome}</span>
                <span style={{ fontSize:'0.72rem', color:'#666' }}>
                  {m.tipo} · HP {m.vida_maxima} · CA {m.ca || m.defesa}
                </span>
              </div>
            ))}
          </div>
        )}

        {selecionados.length > 0 && (
          <div style={{ marginTop:'0.8rem' }}>
            <p style={{ fontSize:'0.75rem', color:'#998060', margin:'0 0 0.4rem' }}>SELECIONADOS</p>
            <div style={{ display:'flex', flexWrap:'wrap', gap:'0.4rem' }}>
              {selecionados.map(m => (
                <span key={m.id} onClick={() => toggle(m)} style={{
                  background:'rgba(192,80,32,0.3)', border:'1px solid #c05020',
                  borderRadius:'20px', padding:'0.2rem 0.7rem',
                  fontSize:'0.8rem', cursor:'pointer', color:'#e0a080',
                }}>{getEmoji(m.tipo)} {m.nome} ✕</span>
              ))}
            </div>
          </div>
        )}

        <div style={{ display:'flex', gap:'0.75rem', marginTop:'1.2rem' }}>
          <button onClick={onCancelar} style={{
            flex:1, background:'rgba(255,255,255,0.04)', border:'1px solid #5a4520',
            color:'#a09080', fontFamily:"'MedievalSharp',cursive",
            padding:'0.6rem', borderRadius:'4px', cursor:'pointer',
          }}>Cancelar</button>
          <button
            disabled={!selecionados.length}
            onClick={() => selecionados.length && onConfirmar(selecionados)}
            style={{
              flex:2,
              background: selecionados.length ? 'linear-gradient(135deg,#8b1a1a,#c04040)' : '#3a2a10',
              border:`1px solid ${selecionados.length ? '#c04040' : '#3a2a10'}`,
              color: selecionados.length ? '#fff' : '#666',
              fontFamily:"'MedievalSharp',cursive", fontWeight:'bold',
              padding:'0.6rem', borderRadius:'4px', cursor: selecionados.length ? 'pointer' : 'default',
              fontSize:'1rem',
            }}>
            ⚔️ INICIAR {selecionados.length > 0 ? `(${selecionados.length} inimigo${selecionados.length>1?'s':''})` : ''}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── MODAL PRINCIPAL ──────────────────────────────────────────────────────────
export default function BatalhaModal({ socket, salaId, isMestre, onFechar }) {
  const token = localStorage.getItem('authToken');
  const emit = (ev, payload) => socket?.emit(ev, { token, sala_id: salaId, ...payload });

  // Decodifica user_id do token (sub)
  const [meuUserId, setMeuUserId] = useState(null);
  const [meuFichaId, setMeuFichaId] = useState(null);
  useEffect(() => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      setMeuUserId(String(payload.sub || ''));
    } catch {}
  }, [token]);

  const [batalha,       setBatalha]       = useState(null); // público
  const [batalhaMestre, setBatalhaMestre] = useState(null); // com HP monstros
  const [mostrarSeletor, setMostrarSeletor] = useState(false);

  // Quando batalha chegar, descobrir meu ficha_id pelo sid (que vem do socket)
  useEffect(() => {
    if (!batalha || !socket) return;
    // O backend inclui o sid em cada jogador; encontrar o meu pelo socket.id
    const mySid = socket.id;
    const eu = batalha.jogadores?.find(j => j.sid === mySid);
    if (eu) setMeuFichaId(eu.ficha_id);
  }, [batalha, socket]);
  const [pow,           setPow]           = useState(null);
  const [flashAlvo,     setFlashAlvo]     = useState(null);

  useEffect(() => {
    console.log('[BatalhaModal] mount', { isMestre });
  }, []);

  useEffect(() => {
    console.log('[BatalhaModal] isMestre changed', isMestre);
    setMostrarSeletor(isMestre);
  }, [isMestre]);

  useEffect(() => {
    console.log('[BatalhaModal] mount', { isMestre, mostrarSeletor });
  }, []);

  const [movendo,       setMovendo]       = useState(null);
  const [alvoSelecionado, setAlvoSelecionado] = useState(null);
  const [encerrarMenu,  setEncerrarMenu]  = useState(false);
  const [erroMsg,       setErroMsg]       = useState('');
  const [dadoEscolhido, setDadoEscolhido] = useState('1d6');
  const [curaInput,     setCuraInput]     = useState('');
  const [curaAlvo,      setCuraAlvo]      = useState('');
  const logRef = useRef(null);

  // ── Listeners ──
  useEffect(() => {
    if (!socket) return;
    const onIniciada = (data) => {
      console.log('[BatalhaModal] batalha_iniciada', data);
      setBatalha(data.batalha);
      if (isMestre) setBatalhaMestre(data.batalha_mestre);
      setMostrarSeletor(false);
    };
    const onAtualizada = (data) => {
      setBatalha(data.batalha);
      if (isMestre) setBatalhaMestre(data.batalha_mestre);
      if (data.efeito) triggerEfeito(data.efeito);
    };
    const onEncerrada = (data) => {
      setBatalha(null); setBatalhaMestre(null);
      onFechar(data);
    };
    const onErro = (data) => {
      setErroMsg(data.mensagem);
      setTimeout(() => setErroMsg(''), 3000);
    };
    socket.on('batalha_iniciada',   onIniciada);
    socket.on('batalha_atualizada', onAtualizada);
    socket.on('batalha_encerrada',  onEncerrada);
    socket.on('batalha_erro',       onErro);
    return () => {
      socket.off('batalha_iniciada',   onIniciada);
      socket.off('batalha_atualizada', onAtualizada);
      socket.off('batalha_encerrada',  onEncerrada);
      socket.off('batalha_erro',       onErro);
    };
  }, [socket, isMestre]);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [batalha?.log]);

  // ── Efeitos visuais ──
  const triggerEfeito = ({ tipo, atacante, alvo, dano }) => {
    if (tipo !== 'ataque') return;
    playSound('hit');
    setMovendo(atacante);
    setTimeout(() => setMovendo(null), 500);
    setFlashAlvo(alvo);
    setTimeout(() => setFlashAlvo(null), 450);
    setPow({ texto: getPow(), x: 25 + Math.random()*50, y: 15 + Math.random()*40 });
    setTimeout(() => setPow(null), 900);
  };

  // ── Helpers ──
  const iniciarBatalha = (monstros) => {
    emit('batalha_iniciar', { monstros_ids: monstros.map(m => m.id), acoes_padrao: 1, acoes_individuais: {} });
  };

  // Estado mesclado (mestre vê HP real dos monstros)
  const b = batalha ? {
    ...batalha,
    monstros: batalha.monstros.map((m, i) => ({
      ...m,
      ...(isMestre && batalhaMestre?.monstros?.[i] ? {
        hp_atual: batalhaMestre.monstros[i].hp_atual,
        hp_max:   batalhaMestre.monstros[i].hp_max,
      } : {}),
    })),
  } : null;

  const ativos = b ? b.turno_ordem.filter(p => {
    if (b.monstros.find(m => m.id === p.id && m.status !== 'vivo')) return false;
    if (b.jogadores.find(j => j.ficha_id === p.id && j.status === 'morto')) return false;
    return true;
  }) : [];

  const turnoAtual   = ativos[b?.turno_atual % Math.max(ativos.length, 1)];
  const ehMeuTurno   = !isMestre && turnoAtual?.id === meuFichaId;
  const subFase      = b?.sub_fase;
  const dadoDano     = b?.dado_dano_atual;
  const alvoIdDano   = b?.alvo_dano_atual;

  // ── Ações do player ──
  const handleRolarIniciativa = () => {
    const v = rolarDado(20);
    emit('batalha_player_iniciativa', { valor: v });
  };

  const handleD20Acerto = () => {
    const v = rolarDado(20);
    emit('batalha_d20_acerto', { valor: v });
  };

  const handleRolarDano = () => {
    if (!dadoDano) return;
    const { total, str } = parsearERotar(dadoDano);
    emit('batalha_roll_dano', { valor: total, rolagem_str: str });
  };

  // ── Ações do mestre ──
  const handleMestreEscolheDado = () => {
    if (!alvoSelecionado) { setErroMsg('Selecione o alvo primeiro!'); return; }
    emit('batalha_mestre_escolhe_dado', { dado: dadoEscolhido, alvo_id: alvoSelecionado });
    setAlvoSelecionado(null);
  };

  const handleMestreAtacaPlayer = () => {
    // Mestre ataca diretamente (monstro → player) sem rolagem do player
    if (!alvoSelecionado) { setErroMsg('Selecione o alvo!'); return; }
    const { total, str } = parsearERotar(dadoEscolhido);
    const monstroTurno = b?.monstros.find(m => m.id === turnoAtual?.id);
    if (!monstroTurno) return;
    emit('batalha_atacar', {
      atacante_id: monstroTurno.id,
      alvo_id: alvoSelecionado,
      dano: total,
      rolagem: str,
    });
    setAlvoSelecionado(null);
  };

  const handleCurar = () => {
    if (!curaAlvo || !curaInput) return;
    emit('batalha_curar', { alvo_id: curaAlvo, cura: parseInt(curaInput)||1 });
    playSound('cura');
    setCuraInput(''); setCuraAlvo('');
  };

  const fInput = {
    background:'#1a1208', border:'1px solid #5a4520', color:'#e0d0b0',
    borderRadius:'4px', padding:'0.35rem 0.5rem', fontSize:'0.82rem',
  };

  const btnBase = (cor='#c59d5f', disabled=false) => ({
    background: disabled ? '#2a1a08' : `rgba(${cor},0.2)`,
    border: `1px solid ${disabled ? '#3a2a10' : cor}`,
    color: disabled ? '#555' : cor,
    fontFamily:"'MedievalSharp',cursive",
    padding:'0.45rem 0.9rem', borderRadius:'5px',
    cursor: disabled ? 'default' : 'pointer', fontSize:'0.82rem',
  });

  const isTurnoMonstro = turnoAtual && b?.monstros.find(m => m.id === turnoAtual.id && m.status === 'vivo');

  return (
    <div style={{
      position:'fixed', inset:0, zIndex:8500,
      background:'rgba(0,0,0,0.93)', backdropFilter:'blur(6px)',
      display:'flex', flexDirection:'column', fontFamily:"'Georgia',serif",
    }}>
      {/* ── HEADER (sempre visível) ── */}
      <div style={{
        background:'linear-gradient(180deg,#1a0808,#100505)',
        borderBottom:'2px solid #c04040', padding:'0.55rem 1.5rem',
        display:'flex', alignItems:'center', gap:'1rem', flexShrink:0,
      }}>
        <span style={{ fontSize:'1.4rem' }}>⚔️</span>
        <h2 style={{
          margin:0, flex:1, fontFamily:"'MedievalSharp',cursive",
          color:'#e04040', fontSize:'1.1rem',
          textShadow:'0 0 12px rgba(220,60,60,0.5)',
        }}>
          {mostrarSeletor ? 'BATALHA — Configurar Inimigos' : (
            <>
              BATALHA
              {b?.fase === 'iniciativa' && ' — Rolagem de Iniciativa'}
              {b?.fase === 'combate' && turnoAtual && ` — Turno de ${turnoAtual.nome}`}
            </>
          )}
        </h2>

        {mostrarSeletor && isMestre && (
          <button onClick={onFechar} style={{
            background:'rgba(255,255,255,0.05)', border:'1px solid #5a4520',
            color:'#a09080', fontFamily:"'MedievalSharp',cursive",
            padding:'0.35rem 0.9rem', borderRadius:'4px', cursor:'pointer', fontSize:'0.82rem',
          }}>✕ Cancelar</button>
        )}
        {b && isMestre && (
          <div style={{ display:'flex', gap:'0.5rem', alignItems:'center' }}>
            {b.fase === 'combate' && (
              <button onClick={() => emit('batalha_proximo_turno', {})} style={{
                background:'rgba(60,160,60,0.2)', border:'1px solid #60c060',
                color:'#60c060', fontFamily:"'MedievalSharp',cursive",
                padding:'0.35rem 0.9rem', borderRadius:'4px', cursor:'pointer', fontSize:'0.82rem',
              }}>▶ Próximo Turno</button>
            )}
            {b.fase === 'iniciativa' && (
              <button onClick={() => emit('batalha_comecar_combate', {})} style={{
                background:'rgba(197,157,95,0.2)', border:'1px solid #c59d5f',
                color:'#c59d5f', fontFamily:"'MedievalSharp',cursive",
                padding:'0.35rem 0.9rem', borderRadius:'4px', cursor:'pointer', fontSize:'0.82rem',
              }}>🎲 Começar Combate</button>
            )}
            <div style={{ position:'relative' }}>
              <button onClick={() => setEncerrarMenu(e=>!e)} style={{
                background:'rgba(192,64,64,0.2)', border:'1px solid #c04040',
                color:'#e04040', fontFamily:"'MedievalSharp',cursive",
                padding:'0.35rem 0.9rem', borderRadius:'4px', cursor:'pointer', fontSize:'0.82rem',
              }}>🏳️ Encerrar ▾</button>
              {encerrarMenu && (
                <div style={{
                  position:'absolute', top:'110%', right:0,
                  background:'#1a0808', border:'1px solid #c04040',
                  borderRadius:'6px', overflow:'hidden', minWidth:'160px', zIndex:100,
                }}>
                  {[['vitoria','🏆 Vitória!','#80c880'],['derrota','💀 Derrota...','#e04040'],['encerrada','🏳️ Encerrar','#888']].map(([m,l,cor])=>(
                    <button key={m} onClick={()=>{ emit('batalha_encerrar',{motivo:m}); setEncerrarMenu(false); }} style={{
                      display:'block', width:'100%', background:'none', border:'none',
                      color:cor, padding:'0.6rem 1rem', cursor:'pointer',
                      textAlign:'left', fontSize:'0.85rem',
                      fontFamily:"'MedievalSharp',cursive",
                      borderBottom:'1px solid #3a1010',
                    }}>{l}</button>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Seletor de monstros (overlay interno) */}
      {mostrarSeletor && isMestre && (
        <div style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center', position:'relative' }}>
          <SeletorMonstros onConfirmar={iniciarBatalha} onCancelar={onFechar} />
        </div>
      )}

      {/* Arena e painel só aparecem após batalha iniciada */}
      {b && !mostrarSeletor && (
        <div style={{ flex:1, display:'flex', overflow:'hidden' }}>

          {/* ══ ARENA ══ */}
          <div style={{
            flex:1, display:'flex', flexDirection:'column',
            padding:'1.2rem 1.5rem', overflow:'hidden', position:'relative',
          }}>
            {/* POW */}
            {pow && (
              <div style={{
                position:'absolute', left:`${pow.x}%`, top:`${pow.y}%`,
                fontSize:'2.8rem', fontFamily:"'MedievalSharp',cursive",
                color:'#ffe000', textShadow:'0 0 20px #ff8800, 2px 2px 0 #000',
                zIndex:200, pointerEvents:'none',
                animation:'powAnim 0.9s ease-out forwards',
              }}>{pow.texto}</div>
            )}

            {/* Erro */}
            {erroMsg && (
              <div style={{
                position:'absolute', top:'0.5rem', left:'50%', transform:'translateX(-50%)',
                background:'rgba(180,30,30,0.9)', border:'1px solid #c04040',
                borderRadius:'6px', padding:'0.4rem 1rem',
                color:'#ffaaaa', fontSize:'0.85rem', zIndex:300,
              }}>{erroMsg}</div>
            )}

            {/* ─ Layout horizontal: Monstros | VS | Players ─ */}
            <div style={{
              flex:1, display:'flex', alignItems:'center',
              justifyContent:'center', gap:'0',
            }}>

              {/* ── LADO ESQUERDO: Monstros ── */}
              <div style={{
                flex:1, display:'flex', flexWrap:'wrap',
                alignContent:'center', justifyContent:'flex-end',
                gap:'0.8rem', padding:'0 1.5rem 0 0',
              }}>
                {b.monstros.map(m => (
                  <CardParticipante
                    key={m.id} p={m} isMonstro isMestre={isMestre}
                    emTurno={turnoAtual?.id === m.id}
                    selecionado={alvoSelecionado === m.id}
                    flashando={flashAlvo === m.id}
                    movendo={movendo === m.id}
                    onClick={isMestre ? () => setAlvoSelecionado(alvoSelecionado === m.id ? null : m.id) : undefined}
                  />
                ))}
              </div>

              {/* ── VS CENTRAL ── */}
              <div style={{
                display:'flex', flexDirection:'column', alignItems:'center',
                flexShrink:0, padding:'0 1rem',
              }}>
                <div style={{
                  fontSize:'2.5rem',
                  textShadow:'0 0 20px rgba(200,40,40,0.7)',
                  animation:'vsPulse 1.8s ease-in-out infinite',
                }}>⚔️</div>
                <div style={{
                  fontFamily:"'MedievalSharp',cursive", color:'#c04040',
                  fontSize:'1.8rem', lineHeight:1,
                  textShadow:'0 0 15px rgba(200,40,40,0.6)',
                  animation:'vsPulse 1.8s ease-in-out infinite',
                }}>VS</div>
                <div style={{ fontSize:'2.5rem', textShadow:'0 0 20px rgba(200,40,40,0.7)', animation:'vsPulse 1.8s ease-in-out infinite' }}>⚔️</div>
              </div>

              {/* ── LADO DIREITO: Players ── */}
              <div style={{
                flex:1, display:'flex', flexWrap:'wrap',
                alignContent:'center', justifyContent:'flex-start',
                gap:'0.8rem', padding:'0 0 0 1.5rem',
              }}>
                {b.jogadores.map(j => (
                  <CardParticipante
                    key={j.ficha_id} p={j} isMonstro={false} isMestre={isMestre}
                    emTurno={turnoAtual?.id === j.ficha_id}
                    selecionado={alvoSelecionado === j.ficha_id}
                    flashando={flashAlvo === j.ficha_id}
                    movendo={movendo === j.ficha_id}
                    onClick={isMestre ? () => setAlvoSelecionado(alvoSelecionado===j.ficha_id ? null : j.ficha_id) : undefined}
                  />
                ))}
              </div>
            </div>

            {/* ─ Fase Iniciativa ─ */}
            {b.fase === 'iniciativa' && (
              <div style={{
                background:'rgba(12,9,3,0.95)', border:'1px solid #5a4520',
                borderRadius:'8px', padding:'1rem 1.2rem', marginTop:'1rem', flexShrink:0,
              }}>
                {isMestre ? (
                  <>
                    <p style={{ color:'#c59d5f', fontFamily:"'MedievalSharp',cursive", margin:'0 0 0.6rem', fontSize:'0.9rem' }}>
                      🎲 Aguardando rolagens de iniciativa (1d20)...
                    </p>
                    <p style={{ color:'#776050', fontSize:'0.8rem', margin:'0 0 0.8rem' }}>
                      Os players rolam automaticamente. Defina abaixo a iniciativa dos monstros:
                    </p>
                    <div style={{ display:'flex', flexWrap:'wrap', gap:'0.8rem', marginBottom:'0.7rem' }}>
                      {b.monstros.filter(m=>m.status==='vivo').map(m => (
                        <div key={m.id} style={{ display:'flex', alignItems:'center', gap:'0.5rem' }}>
                          <span style={{ fontSize:'0.8rem', color:'#c0a080' }}>{getEmoji(m.tipo)} {m.nome}</span>
                          <input type="number" min="1" max="30"
                            placeholder="d20"
                            onChange={e => emit('batalha_set_iniciativa', { pid: m.id, valor: parseInt(e.target.value)||0 })}
                            style={{...fInput, width:'55px', textAlign:'center'}}
                          />
                        </div>
                      ))}
                    </div>
                    <div style={{ fontSize:'0.78rem', color:'#556' }}>
                      {b.jogadores.map(j => (
                        <span key={j.ficha_id} style={{ marginRight:'1rem' }}>
                          {j.nome}: {j.iniciativa > 0 ? `✅ ${j.iniciativa}` : '⏳ aguardando...'}
                        </span>
                      ))}
                    </div>
                  </>
                ) : (
                  <div style={{ textAlign:'center' }}>
                    {meuFichaId && b.jogadores.find(j=>j.ficha_id===meuFichaId)?.iniciativa > 0 ? (
                      <p style={{ color:'#80c880', fontFamily:"'MedievalSharp',cursive", margin:0 }}>
                        ✅ Iniciativa registrada: {b.jogadores.find(j=>j.ficha_id===meuFichaId)?.iniciativa}
                        <br/><span style={{ fontSize:'0.8rem', color:'#666' }}>Aguardando os outros jogadores...</span>
                      </p>
                    ) : (
                      <>
                        <p style={{ color:'#c59d5f', fontFamily:"'MedievalSharp',cursive", margin:'0 0 0.8rem' }}>
                          🎲 Role seu D20 de Iniciativa!
                        </p>
                        <button onClick={handleRolarIniciativa} style={{
                          background:'linear-gradient(135deg,#8b6914,#c59d5f)',
                          border:'none', color:'#1a1208',
                          fontFamily:"'MedievalSharp',cursive", fontWeight:'bold',
                          padding:'0.7rem 2rem', borderRadius:'6px', cursor:'pointer',
                          fontSize:'1.1rem',
                          boxShadow:'0 0 20px rgba(197,157,95,0.4)',
                        }}>🎲 Rolar 1D20</button>
                      </>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* ─ Fase Combate: ações do player ─ */}
            {b.fase === 'combate' && !isMestre && (
              <div style={{
                background:'rgba(12,9,3,0.95)', border:`1px solid ${ehMeuTurno ? '#c59d5f' : '#3a2a10'}`,
                borderRadius:'8px', padding:'0.8rem 1.2rem', marginTop:'1rem', flexShrink:0,
                transition:'border-color 0.3s',
              }}>
                {!ehMeuTurno ? (
                  <p style={{ color:'#556', textAlign:'center', margin:0, fontStyle:'italic', fontSize:'0.85rem' }}>
                    Aguardando seu turno... (turno de {turnoAtual?.nome || '?'})
                  </p>
                ) : subFase === null || subFase === undefined ? (
                  <div style={{ textAlign:'center' }}>
                    <p style={{ color:'#c59d5f', fontFamily:"'MedievalSharp',cursive", margin:'0 0 0.7rem' }}>
                      ⚔️ É seu turno! Role o D20 para acertar!
                    </p>
                    <button onClick={handleD20Acerto} style={{
                      background:'linear-gradient(135deg,#8b1a1a,#c04040)',
                      border:'none', color:'#fff',
                      fontFamily:"'MedievalSharp',cursive", fontWeight:'bold',
                      padding:'0.65rem 2rem', borderRadius:'6px', cursor:'pointer', fontSize:'1.05rem',
                      boxShadow:'0 0 18px rgba(200,40,40,0.4)',
                    }}>🎲 Rolar D20 — Acerto</button>
                  </div>
                ) : subFase === 'aguardando_dado_dano' ? (
                  <p style={{ color:'#e0a030', textAlign:'center', margin:0, fontFamily:"'MedievalSharp',cursive" }}>
                    🎯 D20: {b.d20_acerto_atual} — Aguardando o mestre escolher o dado de dano...
                  </p>
                ) : subFase === 'aguardando_roll_dano' ? (
                  <div style={{ textAlign:'center' }}>
                    <p style={{ color:'#80c880', fontFamily:"'MedievalSharp',cursive", margin:'0 0 0.7rem' }}>
                      🎲 Mestre escolheu <strong style={{ color:'#c59d5f' }}>{dadoDano}</strong>! Role o dado de dano!
                    </p>
                    <button onClick={handleRolarDano} style={{
                      background:'linear-gradient(135deg,#1a6b1a,#40c040)',
                      border:'none', color:'#fff',
                      fontFamily:"'MedievalSharp',cursive", fontWeight:'bold',
                      padding:'0.65rem 2rem', borderRadius:'6px', cursor:'pointer', fontSize:'1.05rem',
                      boxShadow:'0 0 18px rgba(40,200,40,0.4)',
                    }}>🎲 Rolar {dadoDano}</button>
                  </div>
                ) : null}
              </div>
            )}
          </div>

          {/* ══ PAINEL LATERAL ══ */}
          <div style={{
            width:'300px', flexShrink:0, display:'flex', flexDirection:'column',
            borderLeft:'1px solid #3a2a10', background:'rgba(6,5,2,0.97)',
          }}>
            {/* Log */}
            <p style={{ color:'#c59d5f', fontFamily:"'MedievalSharp',cursive", fontSize:'0.75rem', margin:'0.6rem 0.8rem 0.3rem', textTransform:'uppercase', letterSpacing:'0.08em' }}>
              📜 Registro de Batalha
            </p>
            <div ref={logRef} style={{
              flex:1, overflowY:'auto', padding:'0 0.8rem 0.5rem',
              display:'flex', flexDirection:'column', gap:'0.2rem',
            }}>
              {(b.log||[]).map((l,i) => (
                <p key={i} style={{
                  margin:0, fontSize:'0.78rem', lineHeight:1.5,
                  color: l.includes('⚔️')||l.includes('🎲') ? '#c0b090'
                       : l.includes('💥')||l.includes('derrotado') ? '#e07050'
                       : l.includes('💚') ? '#70c870'
                       : l.includes('☠️')||l.includes('morreu')||l.includes('caiu') ? '#e04040'
                       : l.includes('🔄') ? '#7090c0'
                       : '#777',
                  borderLeft: l.includes('⚔️') ? '2px solid rgba(197,157,95,0.25)' : 'none',
                  paddingLeft: l.includes('⚔️') ? '6px' : '0',
                }}>{l}</p>
              ))}
            </div>

            {/* ─ Controles do Mestre ─ */}
            {isMestre && b.fase === 'combate' && (
              <div style={{ borderTop:'1px solid #3a2a10', padding:'0.7rem', flexShrink:0 }}>

                {/* Turno monstro: mestre ataca */}
                {isTurnoMonstro && (
                  <div style={{ marginBottom:'0.7rem' }}>
                    <p style={{ color:'#e04040', fontSize:'0.72rem', textTransform:'uppercase', margin:'0 0 0.4rem', fontFamily:"'MedievalSharp',cursive" }}>
                      👾 Ataque do Monstro
                    </p>
                    <p style={{ color:'#666', fontSize:'0.72rem', margin:'0 0 0.35rem' }}>
                      Selecione o alvo clicando nele na arena:
                      {alvoSelecionado && <span style={{ color:'#c59d5f' }}> {b.jogadores.find(j=>j.ficha_id===alvoSelecionado)?.nome || alvoSelecionado}</span>}
                    </p>
                    <div style={{ display:'flex', gap:'0.4rem', marginBottom:'0.4rem' }}>
                      <select value={dadoEscolhido} onChange={e=>setDadoEscolhido(e.target.value)}
                        style={{...fInput, flex:1}}>
                        {['1d4','1d6','1d8','1d10','1d12','1d20','2d6','2d8','1d6+1d4','1d8+1d6'].map(d=>(
                          <option key={d} value={d}>{d}</option>
                        ))}
                      </select>
                      <button onClick={handleMestreAtacaPlayer} disabled={!alvoSelecionado} style={{
                        ...btnBase('#e04040', !alvoSelecionado),
                        padding:'0.35rem 0.7rem',
                      }}>⚔️ Atacar</button>
                    </div>
                  </div>
                )}

                {/* Turno player: mestre escolhe dado de dano */}
                {!isTurnoMonstro && (
                  <div style={{ marginBottom:'0.7rem' }}>
                    <p style={{ color:'#c59d5f', fontSize:'0.72rem', textTransform:'uppercase', margin:'0 0 0.4rem', fontFamily:"'MedievalSharp',cursive" }}>
                      🎯 Dado de Dano do Player
                    </p>
                    {subFase === 'aguardando_dado_dano' ? (
                      <>
                        <p style={{ color:'#80c880', fontSize:'0.78rem', margin:'0 0 0.4rem' }}>
                          D20: {b.d20_acerto_atual} — Selecione alvo e dado:
                        </p>
                        <p style={{ color:'#666', fontSize:'0.72rem', margin:'0 0 0.3rem' }}>
                          Alvo: {alvoSelecionado
                            ? (b.monstros.find(m=>m.id===alvoSelecionado)?.nome || alvoSelecionado)
                            : 'clique na arena...'}
                        </p>
                        <div style={{ display:'flex', gap:'0.4rem' }}>
                          <select value={dadoEscolhido} onChange={e=>setDadoEscolhido(e.target.value)}
                            style={{...fInput, flex:1}}>
                            {['1d4','1d6','1d8','1d10','1d12','1d20','2d6','2d8','1d6+1d4','1d8+1d6'].map(d=>(
                              <option key={d} value={d}>{d}</option>
                            ))}
                          </select>
                          <button onClick={handleMestreEscolheDado} disabled={!alvoSelecionado} style={{
                            ...btnBase('#c59d5f', !alvoSelecionado),
                            padding:'0.35rem 0.7rem',
                          }}>✓</button>
                        </div>
                      </>
                    ) : subFase === 'aguardando_roll_dano' ? (
                      <p style={{ color:'#80c880', fontSize:'0.8rem', margin:0 }}>
                        ⏳ Aguardando o player rolar {dadoDano}...
                      </p>
                    ) : subFase === null || !subFase ? (
                      <p style={{ color:'#555', fontSize:'0.78rem', margin:0, fontStyle:'italic' }}>
                        Aguardando o player rolar D20...
                      </p>
                    ) : null}
                  </div>
                )}

                {/* Curar */}
                <div style={{ marginBottom:'0.7rem' }}>
                  <p style={{ color:'#70c870', fontSize:'0.72rem', textTransform:'uppercase', margin:'0 0 0.35rem', fontFamily:"'MedievalSharp',cursive" }}>
                    💚 Curar Jogador
                  </p>
                  <div style={{ display:'flex', gap:'0.4rem' }}>
                    <select value={curaAlvo} onChange={e=>setCuraAlvo(e.target.value)}
                      style={{...fInput, flex:2}}>
                      <option value="">Jogador...</option>
                      {b.jogadores.filter(j=>j.status!=='morto').map(j=>(
                        <option key={j.ficha_id} value={j.ficha_id}>{j.nome}</option>
                      ))}
                    </select>
                    <input type="number" value={curaInput} onChange={e=>setCuraInput(e.target.value)}
                      placeholder="HP" style={{...fInput, width:'50px'}} />
                    <button onClick={handleCurar} disabled={!curaAlvo||!curaInput} style={{
                      ...btnBase('#70c870', !curaAlvo||!curaInput),
                      padding:'0.35rem 0.5rem',
                    }}>💚</button>
                  </div>
                </div>

                {/* Status jogadores */}
                <div style={{ marginBottom:'0.5rem' }}>
                  <p style={{ color:'#e0a030', fontSize:'0.72rem', textTransform:'uppercase', margin:'0 0 0.35rem', fontFamily:"'MedievalSharp',cursive" }}>
                    👤 Status Aventureiros
                  </p>
                  {b.jogadores.map(j => (
                    <div key={j.ficha_id} style={{ display:'flex', alignItems:'center', gap:'0.4rem', marginBottom:'0.25rem' }}>
                      <span style={{ flex:1, fontSize:'0.75rem', color:'#c0b090', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
                        {j.nome}
                      </span>
                      <select value={j.status}
                        onChange={e => emit('batalha_status_jogador', { alvo_id: j.ficha_id, status: e.target.value })}
                        style={{...fInput, fontSize:'0.7rem', padding:'0.15rem 0.3rem'}}>
                        <option value="vivo">Vivo</option>
                        <option value="caido">Caído</option>
                        <option value="morto">Morto</option>
                      </select>
                    </div>
                  ))}
                </div>

                {/* Status monstros */}
                <div>
                  <p style={{ color:'#e04040', fontSize:'0.72rem', textTransform:'uppercase', margin:'0 0 0.35rem', fontFamily:"'MedievalSharp',cursive" }}>
                    👾 Status Inimigos
                  </p>
                  {b.monstros.map(m => (
                    <div key={m.id} style={{ display:'flex', alignItems:'center', gap:'0.4rem', marginBottom:'0.25rem' }}>
                      <span style={{ flex:1, fontSize:'0.75rem', color:'#c0a0a0', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
                        {getEmoji(m.tipo)} {m.nome}
                        {isMestre && ` (${batalhaMestre?.monstros?.find(x=>x.id===m.id)?.hp_atual ?? '?'} HP)`}
                      </span>
                      {m.status === 'vivo' ? (
                        <select defaultValue="" onChange={e => e.target.value && emit('batalha_status_monstro', { monstro_id: m.id, status: e.target.value })}
                          style={{...fInput, fontSize:'0.7rem', padding:'0.15rem 0.3rem'}}>
                          <option value="">Ação</option>
                          <option value="derrotado">💥 Derrotado</option>
                          <option value="fugiu">💨 Fugiu</option>
                        </select>
                      ) : (
                        <span style={{ fontSize:'0.7rem', color: m.status==='derrotado'?'#e04040':'#888' }}>
                          {m.status==='derrotado'?'💥':'💨'} {m.status}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <style>{`
        @keyframes powAnim {
          0%   { opacity:1; transform: scale(0.5) rotate(-12deg); }
          45%  { opacity:1; transform: scale(1.5) rotate(6deg); }
          100% { opacity:0; transform: scale(1.2) rotate(0deg) translateY(-25px); }
        }
        @keyframes vsPulse {
          0%,100% { opacity:0.8; text-shadow: 0 0 15px rgba(200,40,40,0.6); }
          50%     { opacity:1;   text-shadow: 0 0 28px rgba(200,40,40,1); }
        }
      `}</style>
    </div>
  );
}