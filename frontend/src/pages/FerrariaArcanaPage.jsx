// frontend/src/pages/FerrariaArcanaPage.jsx
import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { backgrounds } from '../assets/backgrounds';

// ─── Avatar por categoria ─────────────────────────────────────────────────────
const CAT_AVATAR = {
  'weapons':            { emoji: '⚔️',  cor: '#c05020' },
  'armor':              { emoji: '🛡️',  cor: '#6080a0' },
  'adventuring gear':   { emoji: '🎒',  cor: '#a07840' },
  'tools':              { emoji: '🔧',  cor: '#808060' },
  'potion':             { emoji: '🧪',  cor: '#60a060' },
  'arcane':             { emoji: '🔮',  cor: '#8060c0' },
  'food, drink':        { emoji: '🍺',  cor: '#c09040' },
  'transportation':     { emoji: '🐴',  cor: '#906040' },
  'services':           { emoji: '📜',  cor: '#808080' },
  'musical':            { emoji: '🎵',  cor: '#c060a0' },
  'jeweler':            { emoji: '💎',  cor: '#40c0c0' },
  'ammunition':         { emoji: '🏹',  cor: '#a06020' },
  'custom':             { emoji: '⚗️',  cor: '#c59d5f' },
  'default':            { emoji: '📦',  cor: '#8b6914' },
};

function getAvatar(categoria) {
  if (!categoria) return CAT_AVATAR.default;
  const c = categoria.toLowerCase();
  for (const key of Object.keys(CAT_AVATAR)) {
    if (key !== 'default' && c.includes(key)) return CAT_AVATAR[key];
  }
  return CAT_AVATAR.default;
}

function formatPreco(v) {
  if (!v && v !== 0) return '—';
  const n = parseFloat(v);
  if (isNaN(n)) return '—';
  if (n === 0) return 'Grátis';
  if (n < 1) return `${Math.round(n * 100)} pp`;
  if (n >= 100) return `${Math.floor(n / 100)} po ${n % 100 > 0 ? `${n % 100} po` : ''}`.trim();
  return `${n} po`;
}

// ─── Card de detalhe (modal) ──────────────────────────────────────────────────
function FichaItem({ item, onClose }) {
  const av = getAvatar(item.categoria || item.tipo);
  return (
    <div style={{
      position:'fixed', inset:0, background:'rgba(0,0,0,0.82)',
      display:'flex', alignItems:'center', justifyContent:'center',
      zIndex:9000, padding:'1rem', backdropFilter:'blur(4px)',
    }} onClick={onClose}>
      <div onClick={e=>e.stopPropagation()} style={{
        background:'linear-gradient(160deg,#1e1810,#0f0c06)',
        border:'2px solid #c59d5f', borderRadius:'8px',
        maxWidth:'480px', width:'100%', maxHeight:'88vh', overflowY:'auto',
        padding:'1.5rem 2rem', color:'#e0d0b0',
        fontFamily:"'Georgia',serif",
        boxShadow:'0 0 60px rgba(0,0,0,0.9), 0 0 30px rgba(197,157,95,0.15)',
        position:'relative',
      }}>
        <button onClick={onClose} style={{
          position:'absolute', top:'0.75rem', right:'1rem',
          background:'none', border:'none', fontSize:'1.3rem',
          cursor:'pointer', color:'#c59d5f',
        }}>✕</button>

        {/* Cabeçalho */}
        <div style={{ display:'flex', alignItems:'center', gap:'1rem', marginBottom:'1rem' }}>
          <div style={{
            width:'56px', height:'56px', borderRadius:'8px', flexShrink:0,
            background:`radial-gradient(circle, ${av.cor}22, ${av.cor}66)`,
            border:`1.5px solid ${av.cor}`,
            display:'flex', alignItems:'center', justifyContent:'center', fontSize:'1.8rem',
          }}>{av.emoji}</div>
          <div>
            <h2 style={{
              fontFamily:"'MedievalSharp',cursive", color:'#c59d5f',
              fontSize:'1.3rem', margin:0,
            }}>{item.nome}</h2>
            <p style={{ color:'#887060', fontSize:'0.82rem', margin:'0.2rem 0 0', fontStyle:'italic' }}>
              {item.categoria}{item.subcategoria && item.subcategoria !== '-' ? ` › ${item.subcategoria}` : ''}
            </p>
          </div>
        </div>

        <hr style={{ border:'none', borderTop:'1px solid #3a2a10', margin:'0.5rem 0 1rem' }} />

        {/* Stats principais */}
        <div style={{
          display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:'0.6rem',
          marginBottom:'1rem',
        }}>
          {[
            ['💰 Preço', formatPreco(item.preco_ouro)],
            ['⚖️ Peso', item.peso && item.peso !== '0' ? `${item.peso} lb` : '—'],
            ['⚔️ Dano', item.dano_dado && item.dano_dado !== '—' ? item.dano_dado : '—'],
          ].map(([label, val]) => (
            <div key={label} style={{
              background:'rgba(197,157,95,0.06)', border:'1px solid rgba(197,157,95,0.15)',
              borderRadius:'4px', padding:'0.5rem', textAlign:'center',
            }}>
              <div style={{ fontSize:'0.72rem', color:'#887060', marginBottom:'0.2rem' }}>{label}</div>
              <div style={{ fontSize:'0.95rem', color:'#e0d0b0', fontWeight:'bold' }}>{val}</div>
            </div>
          ))}
        </div>

        {item.bonus_ataque > 0 && (
          <p style={{ fontSize:'0.88rem', margin:'0.3rem 0' }}>
            <span style={{ color:'#c59d5f' }}>Bônus de Ataque:</span> +{item.bonus_ataque}
          </p>
        )}
        {item.descricao && item.descricao !== '' && (
          <div style={{ marginTop:'0.6rem' }}>
            <p style={{ color:'#c59d5f', fontSize:'0.78rem', textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:'0.3rem' }}>Descrição</p>
            <p style={{ fontSize:'0.88rem', lineHeight:1.6, color:'#c0b090' }}>{item.descricao}</p>
          </div>
        )}
        {item.efeito && item.efeito !== '' && (
          <div style={{ marginTop:'0.6rem' }}>
            <p style={{ color:'#c59d5f', fontSize:'0.78rem', textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:'0.3rem' }}>Efeito</p>
            <p style={{ fontSize:'0.88rem', lineHeight:1.6, color:'#c0b090' }}>{item.efeito}</p>
          </div>
        )}

        <div style={{
          display:'flex', justifyContent:'space-between', alignItems:'center',
          marginTop:'1rem', paddingTop:'0.6rem', borderTop:'1px solid #3a2a10',
          fontSize:'0.78rem',
        }}>
          <span style={{ color:'#666', fontStyle:'italic' }}>{item.fonte || 'Custom'}</span>
          <span style={{
            background: item.oficial ? 'rgba(90,26,26,0.4)' : 'rgba(26,74,42,0.4)',
            border:`1px solid ${item.oficial ? '#8b3030' : '#2d7a4a'}`,
            color: item.oficial ? '#e08080' : '#80c880',
            borderRadius:'10px', padding:'0.15rem 0.6rem',
            fontFamily:"'MedievalSharp',cursive",
          }}>{item.oficial ? '📖 Oficial D&D' : '⚗ Custom'}</span>
        </div>
      </div>
    </div>
  );
}

// ─── Card da lista ────────────────────────────────────────────────────────────
function ItemCard({ item, onClick }) {
  const av = getAvatar(item.categoria || item.tipo);
  return (
    <div onClick={onClick} style={{
      background:'linear-gradient(135deg,rgba(20,14,3,0.94),rgba(30,20,5,0.94))',
      border:'1px solid #3a2a10', borderRadius:'6px',
      padding:'0.55rem 0.9rem', cursor:'pointer',
      transition:'all 0.18s', display:'flex',
      alignItems:'center', gap:'0.8rem',
    }}
      onMouseEnter={e=>{ e.currentTarget.style.borderColor='#c59d5f'; e.currentTarget.style.transform='translateX(3px)'; }}
      onMouseLeave={e=>{ e.currentTarget.style.borderColor='#3a2a10'; e.currentTarget.style.transform='translateX(0)'; }}
    >
      <div style={{
        width:'38px', height:'38px', borderRadius:'6px', flexShrink:0,
        background:`radial-gradient(circle, ${av.cor}22, ${av.cor}55)`,
        border:`1px solid ${av.cor}88`,
        display:'flex', alignItems:'center', justifyContent:'center', fontSize:'1.2rem',
      }}>{av.emoji}</div>

      <div style={{ flex:1, minWidth:0 }}>
        <div style={{
          color:'#e0d0b0', fontFamily:"'MedievalSharp',cursive",
          fontSize:'0.88rem', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis',
        }}>{item.nome}</div>
        <div style={{ color:'#776050', fontSize:'0.73rem', marginTop:'0.1rem' }}>
          {item.categoria || item.tipo}{item.subcategoria && item.subcategoria !== '-' ? ` › ${item.subcategoria}` : ''}
        </div>
      </div>

      <div style={{ display:'flex', alignItems:'center', gap:'0.4rem', flexShrink:0 }}>
        <span style={{
          background:'rgba(197,157,95,0.1)', border:'1px solid rgba(197,157,95,0.2)',
          borderRadius:'3px', padding:'0.1rem 0.4rem',
          color:'#c59d5f', fontSize:'0.72rem', whiteSpace:'nowrap',
        }}>💰 {formatPreco(item.preco_ouro)}</span>
        {item.peso > 0 && (
          <span style={{ color:'#666', fontSize:'0.7rem' }}>⚖️ {item.peso}lb</span>
        )}
        <span style={{
          background: item.oficial ? 'rgba(90,26,26,0.3)' : 'rgba(26,74,42,0.3)',
          border:`1px solid ${item.oficial ? '#8b3030' : '#2d7a4a'}`,
          borderRadius:'10px', padding:'0.1rem 0.45rem',
          color: item.oficial ? '#e08080' : '#80c880', fontSize:'0.68rem',
        }}>{item.oficial ? 'Oficial' : 'Custom'}</span>
      </div>
    </div>
  );
}

// ─── Formulário de criação ────────────────────────────────────────────────────
const CATEGORIAS_PADRAO = ['Adventuring Gear','Armor','Weapons','Tools','Potion','Arcane','Food, Drink, Lodging','Transportation','Services','Musical Instruments','Jewelry'];

function FormCriarItem({ onCriado, fetchWithAuth }) {
  const vazio = {
    nome:'', categoria:'Adventuring Gear', subcategoria:'-',
    preco_ouro:0, peso:0, dano_dado:'—', bonus_ataque:0,
    descricao:'', efeito:'', fonte:'Custom',
  };
  const [form, setForm]   = useState(vazio);
  const [msg, setMsg]     = useState('');
  const [loading, setLoading] = useState(false);
  const [aberto, setAberto]   = useState(false);

  const set = (k,v) => setForm(p=>({...p,[k]:v}));

  const handleSubmit = async () => {
    if (!form.nome.trim()) { setMsg('❌ Nome é obrigatório.'); return; }
    setLoading(true);
    try {
      const r = await fetchWithAuth('http://127.0.0.1:5003/api/itens', {
        method:'POST', body: JSON.stringify({...form, tipo: form.categoria}),
      });
      const data = await r.json();
      if (data.sucesso) {
        setMsg('✅ Item criado!');
        setForm(vazio);
        onCriado();
        setTimeout(()=>setMsg(''), 3000);
      } else {
        setMsg(`❌ ${data.mensagem}`);
      }
    } catch { setMsg('❌ Erro de conexão.'); }
    setLoading(false);
  };

  const f = {
    background:'#1a1208', border:'1px solid #5a4520', color:'#e0d0b0',
    borderRadius:'4px', padding:'0.4rem 0.6rem', fontSize:'0.85rem', width:'100%', boxSizing:'border-box',
  };
  const lbl = { fontSize:'0.73rem', color:'#998060', textTransform:'uppercase', letterSpacing:'0.05em', display:'block', marginBottom:'0.2rem' };

  return (
    <div style={{ background:'rgba(10,8,3,0.9)', border:'1px solid #5a4520', borderRadius:'8px', overflow:'hidden' }}>
      <button onClick={()=>setAberto(a=>!a)} style={{
        width:'100%', background:'linear-gradient(135deg,rgba(30,20,5,0.95),rgba(20,14,3,0.95))',
        border:'none', borderBottom: aberto ? '1px solid #5a4520' : 'none',
        color:'#c59d5f', fontFamily:"'MedievalSharp',cursive",
        fontSize:'1rem', padding:'1rem 1.5rem', cursor:'pointer',
        display:'flex', alignItems:'center', justifyContent:'space-between',
      }}>
        <span>⚗ Criar Novo Item</span>
        <span style={{ fontSize:'0.8rem' }}>{aberto ? '▲' : '▼'}</span>
      </button>

      {aberto && (
        <div style={{ padding:'1.2rem', display:'flex', flexDirection:'column', gap:'0.75rem' }}>

          <div style={{ display:'flex', flexDirection:'column' }}>
            <label style={lbl}>Nome *</label>
            <input value={form.nome} onChange={e=>set('nome',e.target.value)} style={f} placeholder="Ex: Espada Longa +1" />
          </div>

          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.6rem' }}>
            <div style={{ display:'flex', flexDirection:'column' }}>
              <label style={lbl}>Categoria</label>
              <select value={form.categoria} onChange={e=>set('categoria',e.target.value)} style={f}>
                {CATEGORIAS_PADRAO.map(c=><option key={c}>{c}</option>)}
              </select>
            </div>
            <div style={{ display:'flex', flexDirection:'column' }}>
              <label style={lbl}>Subcategoria</label>
              <input value={form.subcategoria} onChange={e=>set('subcategoria',e.target.value)} style={f} placeholder="Ex: Sword, Ammunition..." />
            </div>
          </div>

          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr 1fr', gap:'0.6rem' }}>
            {[['Preço (po)','preco_ouro'],['Peso (lb)','peso'],['Dano','dano_dado'],['Bônus Atq','bonus_ataque']].map(([l,k])=>(
              <div key={k} style={{ display:'flex', flexDirection:'column' }}>
                <label style={lbl}>{l}</label>
                <input value={form[k]} onChange={e=>set(k,e.target.value)} style={f} placeholder={k==='dano_dado'?'Ex: 1d8':'0'} />
              </div>
            ))}
          </div>

          <div style={{ display:'flex', flexDirection:'column' }}>
            <label style={lbl}>Descrição</label>
            <textarea value={form.descricao} onChange={e=>set('descricao',e.target.value)}
              style={{...f, minHeight:'60px', resize:'vertical'}} placeholder="Descrição do item..." />
          </div>

          <div style={{ display:'flex', flexDirection:'column' }}>
            <label style={lbl}>Efeito / Propriedades</label>
            <textarea value={form.efeito} onChange={e=>set('efeito',e.target.value)}
              style={{...f, minHeight:'60px', resize:'vertical'}} placeholder="Ex: Cura 2d4+2 HP ao ser consumido..." />
          </div>

          <div style={{ display:'flex', flexDirection:'column' }}>
            <label style={lbl}>Fonte</label>
            <input value={form.fonte} onChange={e=>set('fonte',e.target.value)} style={f} placeholder="Ex: PHB 2024, Homebrew..." />
          </div>

          {msg && <p style={{ color:msg.startsWith('✅')?'#80c880':'#e08080', fontSize:'0.85rem', margin:0 }}>{msg}</p>}

          <button onClick={handleSubmit} disabled={loading} style={{
            background: loading ? '#3a2a10' : 'linear-gradient(135deg,#8b6914,#c59d5f)',
            border:'1px solid #c59d5f', color: loading?'#888':'#1a1208',
            fontFamily:"'MedievalSharp',cursive", fontSize:'0.95rem', fontWeight:'bold',
            padding:'0.65rem', borderRadius:'4px', cursor:loading?'default':'pointer',
          }}>
            {loading ? 'Criando...' : '⚗ Criar Item'}
          </button>
        </div>
      )}
    </div>
  );
}

// ─── Página principal ─────────────────────────────────────────────────────────
function FerrariaArcanaPage() {
  const { user, fetchWithAuth } = useAuth();
  const [itens, setItens]           = useState([]);
  const [loading, setLoading]       = useState(false);
  const [categorias, setCategorias] = useState([]);
  const [fichaAberta, setFichaAberta] = useState(null);
  const [reload, setReload]         = useState(0);

  const [filtroNome,     setFiltroNome]     = useState('');
  const [filtroOficial,  setFiltroOficial]  = useState('');
  const [filtroCategoria,setFiltroCategoria]= useState('');

  useEffect(() => {
    if (backgrounds?.ferraria) {
      document.body.style.backgroundImage = `url(${backgrounds.ferraria})`;
      document.body.style.backgroundSize  = 'cover';
      document.body.style.backgroundPosition = 'center';
      document.body.style.backgroundAttachment = 'fixed';
    }
    return () => { document.body.style.backgroundImage = ''; };
  }, []);

  useEffect(() => {
    fetch('http://127.0.0.1:5003/api/itens/categorias')
      .then(r=>r.json()).then(setCategorias).catch(()=>{});
  }, []);

  const buscar = useCallback(() => {
    setLoading(true);
    const p = new URLSearchParams();
    if (filtroNome)          p.append('nome', filtroNome);
    if (filtroOficial !== '') p.append('oficial', filtroOficial);
    if (filtroCategoria)     p.append('categoria', filtroCategoria);
    fetch(`http://127.0.0.1:5003/api/itens?${p}`)
      .then(r=>r.json())
      .then(d=>{ setItens(d); setLoading(false); })
      .catch(()=>setLoading(false));
  }, [filtroNome, filtroOficial, filtroCategoria, reload]);

  useEffect(() => { buscar(); }, [buscar]);

  const abrirFicha = async (id) => {
    try {
      const r = await fetch(`http://127.0.0.1:5003/api/itens/${id}`);
      setFichaAberta(await r.json());
    } catch {}
  };

  return (
    <div style={{ minHeight:'100vh', padding:'1.5rem 2rem', fontFamily:"'Georgia',serif" }}>
      {fichaAberta && <FichaItem item={fichaAberta} onClose={()=>setFichaAberta(null)} />}

      <h1 style={{
        fontFamily:"'MedievalSharp',cursive", color:'#c59d5f',
        textAlign:'center', fontSize:'2rem', marginBottom:'0.25rem',
        textShadow:'0 0 20px rgba(197,157,95,0.5)',
      }}>⚒️ Ferraria Arcana</h1>
      <p style={{ textAlign:'center', color:'#777', marginBottom:'1.2rem', fontSize:'0.85rem' }}>
        {itens.length} itens encontrados
      </p>

      {/* Filtros */}
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
          <option value="">📦 Todos os itens</option>
          <option value="1">📖 Oficiais (D&D)</option>
          <option value="0">⚗ Customizados</option>
        </select>
        <select value={filtroCategoria} onChange={e=>setFiltroCategoria(e.target.value)}
          style={{
            flex:1.5, minWidth:'150px', background:'#1a1208', border:'1px solid #5a4520',
            color:'#e0d0b0', borderRadius:'4px', padding:'0.45rem', fontSize:'0.88rem',
          }}>
          <option value="">⚔️ Todas as categorias</option>
          {categorias.map(c=><option key={c} value={c}>{c}</option>)}
        </select>
        {(filtroNome || filtroOficial !== '' || filtroCategoria) && (
          <button onClick={()=>{ setFiltroNome(''); setFiltroOficial(''); setFiltroCategoria(''); }}
            style={{
              background:'rgba(197,157,95,0.08)', border:'1px solid #5a4520',
              color:'#c59d5f', borderRadius:'4px', padding:'0.45rem 1rem',
              cursor:'pointer', fontSize:'0.82rem',
            }}>✕ Limpar</button>
        )}
      </div>

      {/* Layout */}
      <div style={{ display:'grid', gridTemplateColumns:'1fr 400px', gap:'1.5rem', alignItems:'start' }}>

        {/* Lista */}
        <div style={{
          background:'rgba(8,6,2,0.88)', border:'1px solid #3a2a10',
          borderRadius:'8px', maxHeight:'75vh', overflowY:'auto',
        }}>
          {loading ? (
            <p style={{ color:'#777', textAlign:'center', padding:'2rem' }}>⏳ Carregando...</p>
          ) : itens.length === 0 ? (
            <p style={{ color:'#555', textAlign:'center', padding:'2rem', fontStyle:'italic' }}>
              Nenhum item encontrado.
            </p>
          ) : (
            <div style={{ display:'flex', flexDirection:'column', gap:'0.3rem', padding:'0.6rem' }}>
              {itens.map(i=>(
                <ItemCard key={i.id} item={i} onClick={()=>abrirFicha(i.id)} />
              ))}
            </div>
          )}
        </div>

        {/* Coluna direita */}
        <div style={{ display:'flex', flexDirection:'column', gap:'1rem' }}>
          <FormCriarItem onCriado={()=>setReload(r=>r+1)} fetchWithAuth={fetchWithAuth} />

          {/* Legenda de categorias */}
          <div style={{
            background:'rgba(10,8,3,0.85)', border:'1px solid #3a2a10',
            borderRadius:'6px', padding:'0.8rem 1rem',
          }}>
            <p style={{ color:'#c59d5f', fontFamily:"'MedievalSharp',cursive", fontSize:'0.78rem', margin:'0 0 0.5rem', textTransform:'uppercase', letterSpacing:'0.06em' }}>
              Categorias
            </p>
            <div style={{ display:'flex', flexWrap:'wrap', gap:'0.4rem' }}>
              {Object.entries(CAT_AVATAR).filter(([k])=>k!=='default').map(([k,v])=>(
                <span key={k} style={{
                  background:`${v.cor}18`, border:`1px solid ${v.cor}44`,
                  borderRadius:'4px', padding:'0.15rem 0.5rem',
                  fontSize:'0.73rem', color:`${v.cor}`,
                  whiteSpace:'nowrap', cursor:'pointer',
                }}
                  onClick={()=>setFiltroCategoria(k.charAt(0).toUpperCase()+k.slice(1))}
                >{v.emoji} {k.charAt(0).toUpperCase()+k.slice(1)}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FerrariaArcanaPage;