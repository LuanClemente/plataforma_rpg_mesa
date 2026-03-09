// frontend/src/pages/HomePage.jsx
import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import bestiaryBg from '../assets/bestiary_background.png';

// ─── Avatar por tipo de criatura ─────────────────────────────────────────────
const TIPO_AVATAR = {
  dragon:      { emoji: '🐉', cor: '#c05020' },
  undead:      { emoji: '💀', cor: '#8080a0' },
  humanoid:    { emoji: '🧝', cor: '#80a060' },
  beast:       { emoji: '🐺', cor: '#a07040' },
  demon:       { emoji: '😈', cor: '#9020a0' },
  devil:       { emoji: '👿', cor: '#a02020' },
  fey:         { emoji: '🧚', cor: '#80c0c0' },
  giant:       { emoji: '👹', cor: '#806040' },
  elemental:   { emoji: '🌊', cor: '#4080c0' },
  fiend:       { emoji: '🔥', cor: '#c04020' },
  celestial:   { emoji: '✨', cor: '#c0c020' },
  construct:   { emoji: '⚙️', cor: '#607080' },
  monstrosity: { emoji: '👾', cor: '#806080' },
  ooze:        { emoji: '🫧', cor: '#40a040' },
  plant:       { emoji: '🌿', cor: '#408040' },
  aberration:  { emoji: '🦑', cor: '#6040a0' },
  swarm:       { emoji: '🐝', cor: '#a0a020' },
  default:     { emoji: '⚔️', cor: '#8b6914' },
};

function getAvatar(tipo) {
  if (!tipo) return TIPO_AVATAR.default;
  const t = tipo.toLowerCase();
  for (const key of Object.keys(TIPO_AVATAR)) {
    if (t.includes(key)) return TIPO_AVATAR[key];
  }
  return TIPO_AVATAR.default;
}

function crLabel(cr) {
  if (!cr || cr === '0' || cr === '0.0') return '0';
  const n = parseFloat(cr);
  if (n === 0.125) return '1/8';
  if (n === 0.25)  return '1/4';
  if (n === 0.5)   return '1/2';
  return String(n % 1 === 0 ? Math.floor(n) : n);
}

function modStr(val) {
  const mod = Math.floor((parseInt(val || 10) - 10) / 2);
  return mod >= 0 ? `+${mod}` : `${mod}`;
}

// ─── Ficha D&D modal ──────────────────────────────────────────────────────────
function FichaMonstro({ m, onClose }) {
  const av = getAvatar(m.tipo);
  const attrs = [
    { label:'FOR', val: m.for_attr },
    { label:'DES', val: m.des_attr },
    { label:'CON', val: m.con_attr },
    { label:'INT', val: m.intel_attr },
    { label:'SAB', val: m.sab_attr },
    { label:'CAR', val: m.car_attr },
  ];
  return (
    <div style={{
      position:'fixed', inset:0, background:'rgba(0,0,0,0.82)',
      display:'flex', alignItems:'center', justifyContent:'center',
      zIndex:9000, padding:'1rem', backdropFilter:'blur(4px)',
    }} onClick={onClose}>
      <div onClick={e=>e.stopPropagation()} style={{
        background:'linear-gradient(160deg,#f5e6c8,#ede0c0)',
        border:'3px solid #8b6914', borderRadius:'8px',
        maxWidth:'580px', width:'100%', maxHeight:'92vh', overflowY:'auto',
        padding:'1.5rem 2rem', color:'#2a1f08', fontFamily:"'Georgia',serif",
        boxShadow:'0 0 60px rgba(0,0,0,0.8)', position:'relative',
      }}>
        <button onClick={onClose} style={{
          position:'absolute', top:'0.75rem', right:'1rem',
          background:'none', border:'none', fontSize:'1.4rem', cursor:'pointer', color:'#8b6914',
        }}>✕</button>

        {/* Topo: avatar + nome */}
        <div style={{ display:'flex', alignItems:'center', gap:'1rem', marginBottom:'0.8rem' }}>
          <div style={{
            width:'64px', height:'64px', borderRadius:'50%', flexShrink:0,
            background:`radial-gradient(circle, ${av.cor}33, ${av.cor}88)`,
            border:`2px solid ${av.cor}`,
            display:'flex', alignItems:'center', justifyContent:'center', fontSize:'2rem',
          }}>{av.emoji}</div>
          <div>
            <h2 style={{ fontFamily:"'MedievalSharp',cursive", color:'#5a1a1a', fontSize:'1.5rem', margin:0 }}>{m.nome}</h2>
            <p style={{ fontStyle:'italic', color:'#5a3a10', margin:0, fontSize:'0.88rem' }}>
              {m.tamanho} {m.tipo}{m.alinhamento && m.alinhamento!=='—' ? `, ${m.alinhamento}` : ''}
            </p>
          </div>
        </div>

        <hr style={{ border:'none', borderTop:'2px solid #8b6914', margin:'0.5rem 0' }} />

        <div style={{ fontSize:'0.9rem', lineHeight:1.7 }}>
          <p style={{margin:'0.1rem 0'}}><strong>Classe de Armadura</strong> {m.ca || m.defesa}</p>
          <p style={{margin:'0.1rem 0'}}><strong>Pontos de Vida</strong> {m.vida_maxima}</p>
          <p style={{margin:'0.1rem 0'}}><strong>Deslocamento</strong> {m.deslocamento || '30 ft.'}</p>
        </div>

        <hr style={{ border:'none', borderTop:'1px solid #c8a96e', margin:'0.6rem 0' }} />

        {/* Atributos */}
        <div style={{
          display:'grid', gridTemplateColumns:'repeat(6,1fr)',
          gap:'0.4rem', textAlign:'center', margin:'0.5rem 0 0.8rem',
        }}>
          {attrs.map(a=>(
            <div key={a.label} style={{
              background:'rgba(139,105,20,0.1)', borderRadius:'4px', padding:'0.3rem',
            }}>
              <div style={{ fontWeight:'bold', fontSize:'0.75rem', color:'#5a1a1a' }}>{a.label}</div>
              <div style={{ fontSize:'1.05rem', fontWeight:'bold' }}>{a.val||10}</div>
              <div style={{ fontSize:'0.8rem', color:'#5a3a10' }}>({modStr(a.val)})</div>
            </div>
          ))}
        </div>

        <hr style={{ border:'none', borderTop:'1px solid #c8a96e', margin:'0.4rem 0' }} />

        <div style={{ fontSize:'0.88rem', lineHeight:1.7 }}>
          {m.saving_throws && m.saving_throws!=='' && <p style={{margin:'0.1rem 0'}}><strong>Testes de Resistência</strong> {m.saving_throws}</p>}
          {m.skills        && m.skills!==''        && <p style={{margin:'0.1rem 0'}}><strong>Perícias</strong> {m.skills}</p>}
          {m.resistencias  && m.resistencias!==''  && <p style={{margin:'0.1rem 0'}}><strong>Resistências/Imunidades</strong> {m.resistencias}</p>}
          {m.sentidos      && m.sentidos!=='Normal' && <p style={{margin:'0.1rem 0'}}><strong>Sentidos</strong> {m.sentidos}</p>}
          {m.idiomas       && m.idiomas!=='—'       && <p style={{margin:'0.1rem 0'}}><strong>Idiomas</strong> {m.idiomas}</p>}
        </div>

        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginTop:'0.6rem', fontSize:'0.88rem' }}>
          <span><strong>Nível de Desafio</strong> {crLabel(m.cr)}</span>
          <span style={{
            background: m.oficial ? '#5a1a1a' : '#1a4a2a',
            color:'#f5e6c8', borderRadius:'12px', padding:'0.2rem 0.8rem',
            fontSize:'0.78rem', fontFamily:"'MedievalSharp',cursive",
          }}>{m.oficial ? '📖 Oficial D&D' : '⚗ Customizada'}</span>
        </div>

        {m.habilidades && m.habilidades!=='' && (
          <div style={{ marginTop:'0.8rem', borderTop:'1px solid #c8a96e', paddingTop:'0.6rem' }}>
            <strong style={{ fontSize:'0.9rem', color:'#5a1a1a' }}>Habilidades Especiais</strong>
            <p style={{ margin:'0.3rem 0', fontSize:'0.85rem', lineHeight:1.5 }}>{m.habilidades}</p>
          </div>
        )}

        {m.fonte && (
          <p style={{ marginTop:'0.8rem', fontSize:'0.75rem', color:'#999', fontStyle:'italic', textAlign:'right' }}>
            Fonte: {m.fonte}
          </p>
        )}
      </div>
    </div>
  );
}

// ─── Card da lista ────────────────────────────────────────────────────────────
function MonstroCard({ m, onClick }) {
  const av = getAvatar(m.tipo);
  return (
    <div onClick={onClick} style={{
      background:'linear-gradient(135deg,rgba(20,14,3,0.94),rgba(30,20,5,0.94))',
      border:'1px solid #3a2a10', borderRadius:'6px',
      padding:'0.6rem 0.9rem', cursor:'pointer',
      transition:'all 0.18s', display:'flex',
      alignItems:'center', gap:'0.85rem',
    }}
      onMouseEnter={e=>{ e.currentTarget.style.borderColor='#c59d5f'; e.currentTarget.style.transform='translateX(3px)'; }}
      onMouseLeave={e=>{ e.currentTarget.style.borderColor='#3a2a10'; e.currentTarget.style.transform='translateX(0)'; }}
    >
      {/* Avatar */}
      <div style={{
        width:'42px', height:'42px', borderRadius:'50%', flexShrink:0,
        background:`radial-gradient(circle, ${av.cor}22, ${av.cor}55)`,
        border:`1px solid ${av.cor}88`,
        display:'flex', alignItems:'center', justifyContent:'center',
        fontSize:'1.3rem',
      }}>{av.emoji}</div>

      {/* Info */}
      <div style={{ flex:1, minWidth:0 }}>
        <div style={{
          color:'#e0d0b0', fontFamily:"'MedievalSharp',cursive",
          fontSize:'0.92rem', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis',
        }}>{m.nome}</div>
        <div style={{ color:'#887060', fontSize:'0.76rem', marginTop:'0.1rem' }}>
          {m.tamanho} {m.tipo}
        </div>
      </div>

      {/* Tags */}
      <div style={{ display:'flex', alignItems:'center', gap:'0.4rem', flexShrink:0 }}>
        <span style={{
          background:'rgba(197,157,95,0.1)', border:'1px solid rgba(197,157,95,0.25)',
          borderRadius:'3px', padding:'0.1rem 0.4rem',
          color:'#c59d5f', fontSize:'0.72rem',
        }}>ND {crLabel(m.cr)}</span>
        <span style={{
          background: m.oficial ? 'rgba(90,26,26,0.35)' : 'rgba(26,74,42,0.35)',
          border:`1px solid ${m.oficial ? '#8b3030' : '#2d7a4a'}`,
          borderRadius:'10px', padding:'0.1rem 0.5rem',
          color: m.oficial ? '#e08080' : '#80c880',
          fontSize:'0.7rem',
        }}>{m.oficial ? 'Oficial' : 'Custom'}</span>
        <span style={{ color:'#666', fontSize:'0.76rem' }}>❤ {m.vida_maxima}</span>
      </div>
    </div>
  );
}

// ─── Formulário de criação ────────────────────────────────────────────────────
const TAMANHOS = ['Tiny','Small','Medium','Large','Huge','Gargantuan'];
const TIPOS_PADRAO = ['Aberration','Beast','Celestial','Construct','Dragon','Elemental','Fey','Fiend','Giant','Humanoid','Monstrosity','Ooze','Plant','Undead'];
const ALINHAMENTOS = ['LG','NG','CG','LN','TN','CN','LE','NE','CE','Unaligned','ANY','—'];

function FormCriarMonstro({ onCriado, fetchWithAuth }) {
  const campoVazio = {
    nome:'', tamanho:'Medium', tipo:'Humanoid', alinhamento:'TN',
    ca:10, vida_maxima:10, deslocamento:'30',
    for_attr:10, des_attr:10, con_attr:10, intel_attr:10, sab_attr:10, car_attr:10,
    saving_throws:'', skills:'', resistencias:'', sentidos:'Normal', idiomas:'Common',
    cr:'1', habilidades:'', fonte:'Custom',
    ataque_bonus:0, dano_dado:'1d6', xp_oferecido:0, ouro_drop:0,
  };
  const [form, setForm] = useState(campoVazio);
  const [msg, setMsg] = useState('');
  const [loading, setLoading] = useState(false);
  const [aberto, setAberto] = useState(false);

  const set = (k, v) => setForm(p => ({ ...p, [k]: v }));

  const handleSubmit = async () => {
    if (!form.nome.trim()) { setMsg('❌ Nome é obrigatório.'); return; }
    setLoading(true);
    try {
      const r = await fetchWithAuth('http://127.0.0.1:5003/api/monstros', {
        method:'POST', body: JSON.stringify(form),
      });
      const data = await r.json();
      if (data.sucesso) {
        setMsg('✅ Criatura criada!');
        setForm(campoVazio);
        onCriado();
        setTimeout(() => setMsg(''), 3000);
      } else {
        setMsg(`❌ ${data.mensagem}`);
      }
    } catch { setMsg('❌ Erro de conexão.'); }
    setLoading(false);
  };

  const fieldStyle = {
    background:'#1a1208', border:'1px solid #5a4520', color:'#e0d0b0',
    borderRadius:'4px', padding:'0.4rem 0.6rem', fontSize:'0.85rem', width:'100%',
    boxSizing:'border-box',
  };
  const labelStyle = { fontSize:'0.75rem', color:'#998060', textTransform:'uppercase', letterSpacing:'0.05em', display:'block', marginBottom:'0.2rem' };
  const groupStyle = { display:'flex', flexDirection:'column' };

  return (
    <div style={{
      background:'rgba(10,8,3,0.9)', border:'1px solid #5a4520',
      borderRadius:'8px', overflow:'hidden',
    }}>
      {/* Header clicável */}
      <button onClick={() => setAberto(a=>!a)} style={{
        width:'100%', background:'linear-gradient(135deg,rgba(30,20,5,0.95),rgba(20,14,3,0.95))',
        border:'none', borderBottom: aberto ? '1px solid #5a4520' : 'none',
        color:'#c59d5f', fontFamily:"'MedievalSharp',cursive",
        fontSize:'1rem', padding:'1rem 1.5rem', cursor:'pointer',
        display:'flex', alignItems:'center', justifyContent:'space-between',
        transition:'background 0.2s',
      }}>
        <span>⚗ Criar Nova Criatura</span>
        <span style={{ fontSize:'0.8rem' }}>{aberto ? '▲' : '▼'}</span>
      </button>

      {aberto && (
        <div style={{ padding:'1.2rem', display:'flex', flexDirection:'column', gap:'0.8rem' }}>

          {/* Nome */}
          <div style={groupStyle}>
            <label style={labelStyle}>Nome *</label>
            <input value={form.nome} onChange={e=>set('nome',e.target.value)} style={fieldStyle} placeholder="Ex: Dracolich Ancião" />
          </div>

          {/* Tamanho / Tipo / Alinhamento */}
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:'0.6rem' }}>
            <div style={groupStyle}>
              <label style={labelStyle}>Tamanho</label>
              <select value={form.tamanho} onChange={e=>set('tamanho',e.target.value)} style={fieldStyle}>
                {TAMANHOS.map(t=><option key={t}>{t}</option>)}
              </select>
            </div>
            <div style={groupStyle}>
              <label style={labelStyle}>Tipo</label>
              <select value={form.tipo} onChange={e=>set('tipo',e.target.value)} style={fieldStyle}>
                {TIPOS_PADRAO.map(t=><option key={t}>{t}</option>)}
              </select>
            </div>
            <div style={groupStyle}>
              <label style={labelStyle}>Alinhamento</label>
              <select value={form.alinhamento} onChange={e=>set('alinhamento',e.target.value)} style={fieldStyle}>
                {ALINHAMENTOS.map(a=><option key={a}>{a}</option>)}
              </select>
            </div>
          </div>

          {/* CA / HP / Deslocamento / ND */}
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr 1fr', gap:'0.6rem' }}>
            {[['CA','ca'],['HP','vida_maxima'],['Deslocamento','deslocamento'],['ND (CR)','cr']].map(([l,k])=>(
              <div key={k} style={groupStyle}>
                <label style={labelStyle}>{l}</label>
                <input value={form[k]} onChange={e=>set(k, e.target.value)} style={fieldStyle} />
              </div>
            ))}
          </div>

          {/* Atributos */}
          <div>
            <label style={{...labelStyle, marginBottom:'0.4rem'}}>Atributos</label>
            <div style={{ display:'grid', gridTemplateColumns:'repeat(6,1fr)', gap:'0.5rem', textAlign:'center' }}>
              {[['FOR','for_attr'],['DES','des_attr'],['CON','con_attr'],['INT','intel_attr'],['SAB','sab_attr'],['CAR','car_attr']].map(([l,k])=>(
                <div key={k}>
                  <div style={{ fontSize:'0.72rem', color:'#c59d5f', marginBottom:'0.2rem' }}>{l}</div>
                  <input type="number" value={form[k]} onChange={e=>set(k,parseInt(e.target.value)||10)}
                    style={{...fieldStyle, textAlign:'center', padding:'0.3rem'}} min="1" max="30" />
                  <div style={{ fontSize:'0.7rem', color:'#666', marginTop:'0.1rem' }}>({modStr(form[k])})</div>
                </div>
              ))}
            </div>
          </div>

          {/* Saving throws / Skills */}
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.6rem' }}>
            <div style={groupStyle}>
              <label style={labelStyle}>Testes de Resistência</label>
              <input value={form.saving_throws} onChange={e=>set('saving_throws',e.target.value)} style={fieldStyle} placeholder="Ex: CON, WIS" />
            </div>
            <div style={groupStyle}>
              <label style={labelStyle}>Perícias</label>
              <input value={form.skills} onChange={e=>set('skills',e.target.value)} style={fieldStyle} placeholder="Ex: Perception, Stealth" />
            </div>
          </div>

          {/* Resistências / Sentidos / Idiomas */}
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:'0.6rem' }}>
            <div style={groupStyle}>
              <label style={labelStyle}>Resistências</label>
              <input value={form.resistencias} onChange={e=>set('resistencias',e.target.value)} style={fieldStyle} placeholder="Ex: Fire, Poison" />
            </div>
            <div style={groupStyle}>
              <label style={labelStyle}>Sentidos</label>
              <input value={form.sentidos} onChange={e=>set('sentidos',e.target.value)} style={fieldStyle} placeholder="Ex: Darkvision 60" />
            </div>
            <div style={groupStyle}>
              <label style={labelStyle}>Idiomas</label>
              <input value={form.idiomas} onChange={e=>set('idiomas',e.target.value)} style={fieldStyle} placeholder="Ex: Common, Draconic" />
            </div>
          </div>

          {/* Habilidades especiais */}
          <div style={groupStyle}>
            <label style={labelStyle}>Habilidades Especiais</label>
            <textarea value={form.habilidades} onChange={e=>set('habilidades',e.target.value)}
              style={{...fieldStyle, minHeight:'70px', resize:'vertical'}}
              placeholder="Ex: Breath Weapon (Recharge 5-6): ..." />
          </div>

          {/* Fonte */}
          <div style={groupStyle}>
            <label style={labelStyle}>Fonte / Livro</label>
            <input value={form.fonte} onChange={e=>set('fonte',e.target.value)} style={fieldStyle} placeholder="Ex: Homebrew, Livro customizado..." />
          </div>

          {msg && <p style={{ color: msg.startsWith('✅') ? '#80c880' : '#e08080', fontSize:'0.85rem', margin:0 }}>{msg}</p>}

          <button onClick={handleSubmit} disabled={loading} style={{
            background: loading ? '#3a2a10' : 'linear-gradient(135deg,#8b6914,#c59d5f)',
            border:'1px solid #c59d5f', color: loading ? '#888' : '#1a1208',
            fontFamily:"'MedievalSharp',cursive", fontSize:'0.95rem', fontWeight:'bold',
            padding:'0.65rem', borderRadius:'4px', cursor: loading ? 'default' : 'pointer',
            transition:'all 0.2s',
          }}>
            {loading ? 'Criando...' : '⚗ Criar Criatura'}
          </button>
        </div>
      )}
    </div>
  );
}

// ─── Página principal ─────────────────────────────────────────────────────────
function HomePage() {
  const { user, fetchWithAuth } = useAuth();
  const [monstros, setMonstros]     = useState([]);
  const [loading, setLoading]       = useState(false);
  const [tipos, setTipos]           = useState([]);
  const [fichaAberta, setFichaAberta] = useState(null);
  const [reload, setReload]         = useState(0);

  const [filtroNome,    setFiltroNome]    = useState('');
  const [filtroOficial, setFiltroOficial] = useState('');
  const [filtroTipo,    setFiltroTipo]    = useState('');

  useEffect(() => {
    document.body.style.backgroundImage = `url(${bestiaryBg})`;
    document.body.style.backgroundSize  = 'cover';
    document.body.style.backgroundPosition = 'center';
    document.body.style.backgroundAttachment = 'fixed';
    return () => { document.body.style.backgroundImage = ''; };
  }, []);

  useEffect(() => {
    fetch('http://127.0.0.1:5003/api/monstros/tipos')
      .then(r=>r.json()).then(setTipos).catch(()=>{});
  }, []);

  const buscar = useCallback(() => {
    setLoading(true);
    const p = new URLSearchParams();
    if (filtroNome)         p.append('nome', filtroNome);
    if (filtroOficial!=='') p.append('oficial', filtroOficial);
    if (filtroTipo)         p.append('tipo', filtroTipo);
    fetch(`http://127.0.0.1:5003/api/monstros?${p}`)
      .then(r=>r.json())
      .then(d=>{ setMonstros(d); setLoading(false); })
      .catch(()=>setLoading(false));
  }, [filtroNome, filtroOficial, filtroTipo, reload]);

  useEffect(() => { buscar(); }, [buscar]);

  const abrirFicha = async (id) => {
    try {
      const r = await fetch(`http://127.0.0.1:5003/api/monstros/${id}`);
      setFichaAberta(await r.json());
    } catch {}
  };

  return (
    <div style={{ minHeight:'100vh', padding:'1.5rem 2rem', fontFamily:"'Georgia',serif" }}>
      {fichaAberta && <FichaMonstro m={fichaAberta} onClose={()=>setFichaAberta(null)} />}

      <h1 style={{
        fontFamily:"'MedievalSharp',cursive", color:'#c59d5f',
        textAlign:'center', fontSize:'2rem', marginBottom:'0.25rem',
        textShadow:'0 0 20px rgba(197,157,95,0.5)',
      }}>📖 Bestiário</h1>
      <p style={{ textAlign:'center', color:'#777', marginBottom:'1.2rem', fontSize:'0.85rem' }}>
        {monstros.length} criaturas encontradas
      </p>

      {/* ── Filtros ── */}
      <div style={{
        display:'flex', gap:'0.75rem', flexWrap:'wrap', marginBottom:'1.2rem',
        background:'rgba(12,9,3,0.88)', border:'1px solid #5a4520',
        borderRadius:'6px', padding:'0.85rem 1rem',
      }}>
        <input value={filtroNome} onChange={e=>setFiltroNome(e.target.value)}
          placeholder="🔍 Buscar por nome..."
          style={{
            flex:3, minWidth:'150px', background:'#1a1208', border:'1px solid #5a4520',
            color:'#e0d0b0', borderRadius:'4px', padding:'0.45rem 0.75rem', fontSize:'0.88rem',
          }} />
        <select value={filtroOficial} onChange={e=>setFiltroOficial(e.target.value)}
          style={{
            flex:1.5, minWidth:'150px', background:'#1a1208', border:'1px solid #5a4520',
            color:'#e0d0b0', borderRadius:'4px', padding:'0.45rem', fontSize:'0.88rem',
          }}>
          <option value="">📚 Todas as criaturas</option>
          <option value="1">📖 Oficiais (D&D)</option>
          <option value="0">⚗ Customizadas</option>
        </select>
        <select value={filtroTipo} onChange={e=>setFiltroTipo(e.target.value)}
          style={{
            flex:1.5, minWidth:'150px', background:'#1a1208', border:'1px solid #5a4520',
            color:'#e0d0b0', borderRadius:'4px', padding:'0.45rem', fontSize:'0.88rem',
          }}>
          <option value="">🐉 Todos os tipos</option>
          {tipos.map(t=><option key={t} value={t}>{t}</option>)}
        </select>
        {(filtroNome || filtroOficial!=='' || filtroTipo) && (
          <button onClick={()=>{ setFiltroNome(''); setFiltroOficial(''); setFiltroTipo(''); }}
            style={{
              background:'rgba(197,157,95,0.08)', border:'1px solid #5a4520',
              color:'#c59d5f', borderRadius:'4px', padding:'0.45rem 1rem',
              cursor:'pointer', fontSize:'0.82rem',
            }}>✕ Limpar</button>
        )}
      </div>

      {/* ── Layout principal ── */}
      <div style={{ display:'grid', gridTemplateColumns:'1fr 400px', gap:'1.5rem', alignItems:'start' }}>

        {/* Lista */}
        <div style={{
          background:'rgba(8,6,2,0.88)', border:'1px solid #3a2a10',
          borderRadius:'8px', maxHeight:'75vh', overflowY:'auto',
        }}>
          {loading ? (
            <p style={{ color:'#777', textAlign:'center', padding:'2rem' }}>⏳ Carregando...</p>
          ) : monstros.length === 0 ? (
            <p style={{ color:'#555', textAlign:'center', padding:'2rem', fontStyle:'italic' }}>
              Nenhuma criatura encontrada.
            </p>
          ) : (
            <div style={{ display:'flex', flexDirection:'column', gap:'0.3rem', padding:'0.6rem' }}>
              {monstros.map(m=>(
                <MonstroCard key={m.id} m={m} onClick={()=>abrirFicha(m.id)} />
              ))}
            </div>
          )}
        </div>

        {/* Coluna direita: criar criatura */}
        <div style={{ display:'flex', flexDirection:'column', gap:'1rem' }}>
          <FormCriarMonstro onCriado={()=>setReload(r=>r+1)} fetchWithAuth={fetchWithAuth} />

          {/* Legenda de avatares */}
          <div style={{
            background:'rgba(10,8,3,0.85)', border:'1px solid #3a2a10',
            borderRadius:'6px', padding:'0.8rem 1rem',
          }}>
            <p style={{ color:'#c59d5f', fontFamily:"'MedievalSharp',cursive", fontSize:'0.78rem', margin:'0 0 0.5rem', textTransform:'uppercase', letterSpacing:'0.06em' }}>
              Tipos de Criaturas
            </p>
            <div style={{ display:'flex', flexWrap:'wrap', gap:'0.4rem' }}>
              {Object.entries(TIPO_AVATAR).filter(([k])=>k!=='default').map(([k,v])=>(
                <span key={k} style={{
                  background:`${v.cor}18`, border:`1px solid ${v.cor}44`,
                  borderRadius:'4px', padding:'0.15rem 0.5rem',
                  fontSize:'0.75rem', color:`${v.cor}`,
                  whiteSpace:'nowrap',
                }}>{v.emoji} {k.charAt(0).toUpperCase()+k.slice(1)}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;