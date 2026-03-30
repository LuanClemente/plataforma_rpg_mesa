// frontend/src/pages/EsconderijoPage.jsx
import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { backgrounds } from '../assets/backgrounds';

const API = 'http://127.0.0.1:5003';

// ── Helpers ───────────────────────────────────────────────────────────────────
const TONS = ['Épico','Sombrio','Humorístico','Misterioso','Horror','Aventura','Político'];
const STATUS_EVENTO = { futuro:'🔮 Futuro', em_andamento:'⚡ Em andamento', concluido:'✅ Concluído' };
const STATUS_QUEST  = { ativa:'⚔️ Ativa', concluida:'✅ Concluída', falhou:'💀 Falhou', oculta:'🔒 Oculta' };
const ALINHAMENTOS  = ['Leal e Bom','Neutro e Bom','Caótico e Bom','Leal e Neutro','Neutro','Caótico e Neutro','Leal e Mau','Neutro e Mau','Caótico e Mau'];

function VisToggle({ visivel, onChange }) {
  return (
    <button onClick={() => onChange(!visivel)} title={visivel ? 'Visível para players' : 'Oculto'} style={{
      background: visivel ? 'rgba(80,180,80,0.2)' : 'rgba(80,80,80,0.2)',
      border: `1px solid ${visivel ? '#60c060' : '#555'}`,
      color: visivel ? '#80c880' : '#777',
      borderRadius: '4px', padding: '0.2rem 0.5rem',
      cursor: 'pointer', fontSize: '0.78rem', whiteSpace: 'nowrap',
    }}>
      {visivel ? '👁 Visível' : '🔒 Oculto'}
    </button>
  );
}

const estilo = {
  input: {
    background: '#1a1208', border: '1px solid #5a4520', color: '#e0d0b0',
    borderRadius: '4px', padding: '0.4rem 0.6rem', fontSize: '0.85rem',
    width: '100%', boxSizing: 'border-box',
  },
  textarea: {
    background: '#1a1208', border: '1px solid #5a4520', color: '#e0d0b0',
    borderRadius: '4px', padding: '0.4rem 0.6rem', fontSize: '0.85rem',
    width: '100%', boxSizing: 'border-box', resize: 'vertical', minHeight: '70px',
  },
  label: {
    fontSize: '0.7rem', color: '#998060', textTransform: 'uppercase',
    letterSpacing: '0.05em', display: 'block', marginBottom: '0.2rem',
  },
  card: {
    background: 'rgba(15,10,2,0.92)', border: '1px solid #3a2a10',
    borderRadius: '8px', padding: '1rem',
  },
  btnPrimario: {
    background: 'linear-gradient(135deg,#8b6914,#c59d5f)',
    border: 'none', color: '#1a1208', fontFamily: "'MedievalSharp',cursive",
    fontWeight: 'bold', padding: '0.5rem 1.2rem', borderRadius: '4px',
    cursor: 'pointer', fontSize: '0.85rem',
  },
  btnPerigo: {
    background: 'rgba(139,30,30,0.2)', border: '1px solid #8b3030',
    color: '#e08080', borderRadius: '4px', padding: '0.3rem 0.7rem',
    cursor: 'pointer', fontSize: '0.78rem',
  },
  btnSecundario: {
    background: 'rgba(197,157,95,0.08)', border: '1px solid #5a4520',
    color: '#c59d5f', borderRadius: '4px', padding: '0.3rem 0.7rem',
    cursor: 'pointer', fontSize: '0.78rem',
  },
};

// ── Seção Campanha ────────────────────────────────────────────────────────────
function SecaoCampanha({ campanha, fetchWithAuth, onAtualizado }) {
  const [form, setForm] = useState({ ...campanha });
  const [salvando, setSalvando] = useState(false);
  const set = (k, v) => setForm(p => ({ ...p, [k]: v }));

  const salvar = async () => {
    setSalvando(true);
    await fetchWithAuth(`${API}/api/campanhas/${campanha.id}`, {
      method: 'PUT', body: JSON.stringify(form),
    });
    setSalvando(false);
    onAtualizado();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.7rem' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '0.6rem' }}>
        <div><label style={estilo.label}>Nome da Campanha</label>
          <input value={form.nome} onChange={e => set('nome', e.target.value)} style={estilo.input} /></div>
        <div><label style={estilo.label}>Sistema</label>
          <input value={form.sistema} onChange={e => set('sistema', e.target.value)} style={estilo.input} /></div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.6rem' }}>
        <div><label style={estilo.label}>Tom</label>
          <select value={form.tom} onChange={e => set('tom', e.target.value)} style={estilo.input}>
            {TONS.map(t => <option key={t}>{t}</option>)}
          </select></div>
        <div><label style={estilo.label}>Nível Mínimo</label>
          <input type="number" min="1" max="20" value={form.nivel_min} onChange={e => set('nivel_min', e.target.value)} style={estilo.input} /></div>
        <div><label style={estilo.label}>Nível Máximo</label>
          <input type="number" min="1" max="20" value={form.nivel_max} onChange={e => set('nivel_max', e.target.value)} style={estilo.input} /></div>
      </div>
      <div><label style={estilo.label}>Descrição (pública)</label>
        <textarea value={form.descricao} onChange={e => set('descricao', e.target.value)} style={{ ...estilo.textarea, minHeight: '60px' }} /></div>
      <div><label style={estilo.label}>História / Lore (privado)</label>
        <textarea value={form.historia} onChange={e => set('historia', e.target.value)} style={{ ...estilo.textarea, minHeight: '120px' }} /></div>
      <button onClick={salvar} disabled={salvando} style={estilo.btnPrimario}>
        {salvando ? 'Salvando...' : '💾 Salvar Campanha'}
      </button>
    </div>
  );
}

// ── Lista genérica com form inline ───────────────────────────────────────────
function ListaSecao({ itens, renderItem, renderForm, onCreate, titulo, btnLabel }) {
  const [criando, setCriando] = useState(false);
  const [editandoId, setEditandoId] = useState(null);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <button onClick={() => { setCriando(true); setEditandoId(null); }} style={estilo.btnPrimario}>
          {btnLabel}
        </button>
      </div>

      {criando && (
        <div style={{ ...estilo.card, border: '1px solid #c59d5f' }}>
          {renderForm(null, () => { setCriando(false); onCreate(); }, () => setCriando(false))}
        </div>
      )}

      {itens.length === 0 && !criando && (
        <p style={{ color: '#555', fontStyle: 'italic', textAlign: 'center', padding: '1.5rem' }}>
          Nenhum {titulo.toLowerCase()} criado ainda.
        </p>
      )}

      {itens.map(item => (
        <div key={item.id} style={{ ...estilo.card }}>
          {editandoId === item.id
            ? renderForm(item, () => { setEditandoId(null); onCreate(); }, () => setEditandoId(null))
            : renderItem(item, () => setEditandoId(item.id))
          }
        </div>
      ))}
    </div>
  );
}

// ── Mapa ──────────────────────────────────────────────────────────────────────
function SecaoMapas({ cid, fetchWithAuth }) {
  const [mapas, setMapas] = useState([]);
  const fileRef = useRef(null);
  const buscar = () => fetchWithAuth(`${API}/api/campanhas/${cid}/mapas`).then(r => r.json()).then(setMapas).catch(() => {});
  useEffect(() => { buscar(); }, [cid]);

  const toggle = async (id, v) => {
    await fetchWithAuth(`${API}/api/campanhas/${cid}/mapas/${id}/toggle`, { method: 'PATCH', body: JSON.stringify({ visivel: v }) });
    buscar();
  };
  const deletar = async (id) => {
    if (!window.confirm('Deletar mapa?')) return;
    await fetchWithAuth(`${API}/api/campanhas/${cid}/mapas/${id}`, { method: 'DELETE' });
    buscar();
  };

  const FormMapa = ({ item, onSalvo, onCancelar }) => {
    const [f, setF] = useState({ nome: item?.nome || '', descricao: item?.descricao || '', imagem_data: item?.imagem_data || '' });
    const set = (k, v) => setF(p => ({ ...p, [k]: v }));
    const handleFile = (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = ev => set('imagem_data', ev.target.result);
      reader.readAsDataURL(file);
    };
    const salvar = async () => {
      const url    = item ? `${API}/api/campanhas/${cid}/mapas/${item.id}` : `${API}/api/campanhas/${cid}/mapas`;
      const method = item ? 'PUT' : 'POST';
      await fetchWithAuth(url, { method, body: JSON.stringify(f) });
      onSalvo();
    };
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
          <div><label style={estilo.label}>Nome</label><input value={f.nome} onChange={e => set('nome', e.target.value)} style={estilo.input} /></div>
          <div><label style={estilo.label}>Descrição</label><input value={f.descricao} onChange={e => set('descricao', e.target.value)} style={estilo.input} /></div>
        </div>
        <div>
          <label style={estilo.label}>Imagem do Mapa</label>
          <input ref={fileRef} type="file" accept="image/*" onChange={handleFile} style={{ display: 'none' }} />
          <button onClick={() => fileRef.current?.click()} style={{ ...estilo.btnSecundario, marginBottom: '0.4rem' }}>📁 Escolher imagem</button>
          {f.imagem_data && <img src={f.imagem_data} alt="preview" style={{ width: '100%', maxHeight: '200px', objectFit: 'contain', borderRadius: '4px', border: '1px solid #5a4520' }} />}
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button onClick={onCancelar} style={estilo.btnSecundario}>Cancelar</button>
          <button onClick={salvar} style={estilo.btnPrimario}>💾 Salvar</button>
        </div>
      </div>
    );
  };

  return (
    <ListaSecao itens={mapas} titulo="Mapa" btnLabel="🗺 + Novo Mapa" onCreate={buscar}
      renderItem={(m, editar) => (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
            <div>
              <div style={{ color: '#c59d5f', fontFamily: "'MedievalSharp',cursive", fontSize: '0.9rem' }}>{m.nome}</div>
              {m.descricao && <div style={{ color: '#776050', fontSize: '0.78rem' }}>{m.descricao}</div>}
            </div>
            <div style={{ display: 'flex', gap: '0.4rem' }}>
              <VisToggle visivel={!!m.visivel} onChange={v => toggle(m.id, v)} />
              <button onClick={editar} style={estilo.btnSecundario}>✏️</button>
              <button onClick={() => deletar(m.id)} style={estilo.btnPerigo}>🗑️</button>
            </div>
          </div>
          {m.imagem_data && <img src={m.imagem_data} alt={m.nome} style={{ width: '100%', maxHeight: '300px', objectFit: 'contain', borderRadius: '6px', border: '1px solid #3a2a10' }} />}
        </div>
      )}
      renderForm={(item, onSalvo, onCancelar) => <FormMapa item={item} onSalvo={onSalvo} onCancelar={onCancelar} />}
    />
  );
}

// ── Eventos ───────────────────────────────────────────────────────────────────
function SecaoEventos({ cid, fetchWithAuth }) {
  const [eventos, setEventos] = useState([]);
  const buscar = () => fetchWithAuth(`${API}/api/campanhas/${cid}/eventos`).then(r => r.json()).then(setEventos).catch(() => {});
  useEffect(() => { buscar(); }, [cid]);

  const toggle = async (id, v) => { await fetchWithAuth(`${API}/api/campanhas/${cid}/eventos/${id}/toggle`, { method: 'PATCH', body: JSON.stringify({ visivel: v }) }); buscar(); };
  const deletar = async (id) => { if (!window.confirm('Deletar evento?')) return; await fetchWithAuth(`${API}/api/campanhas/${cid}/eventos/${id}`, { method: 'DELETE' }); buscar(); };

  const FormEvento = ({ item, onSalvo, onCancelar }) => {
    const [f, setF] = useState({ titulo: item?.titulo || '', descricao_pub: item?.descricao_pub || '', descricao_priv: item?.descricao_priv || '', status: item?.status || 'futuro', ordem: item?.ordem || 0 });
    const set = (k, v) => setF(p => ({ ...p, [k]: v }));
    const salvar = async () => {
      const url = item ? `${API}/api/campanhas/${cid}/eventos/${item.id}` : `${API}/api/campanhas/${cid}/eventos`;
      await fetchWithAuth(url, { method: item ? 'PUT' : 'POST', body: JSON.stringify(f) });
      onSalvo();
    };
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 80px', gap: '0.5rem' }}>
          <div><label style={estilo.label}>Título</label><input value={f.titulo} onChange={e => set('titulo', e.target.value)} style={estilo.input} /></div>
          <div><label style={estilo.label}>Status</label>
            <select value={f.status} onChange={e => set('status', e.target.value)} style={estilo.input}>
              {Object.entries(STATUS_EVENTO).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </div>
          <div><label style={estilo.label}>Ordem</label><input type="number" value={f.ordem} onChange={e => set('ordem', e.target.value)} style={estilo.input} /></div>
        </div>
        <div><label style={estilo.label}>👁 Descrição Pública (players veem)</label><textarea value={f.descricao_pub} onChange={e => set('descricao_pub', e.target.value)} style={estilo.textarea} /></div>
        <div><label style={estilo.label}>🔒 Detalhes Privados (só mestre)</label><textarea value={f.descricao_priv} onChange={e => set('descricao_priv', e.target.value)} style={estilo.textarea} /></div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button onClick={onCancelar} style={estilo.btnSecundario}>Cancelar</button>
          <button onClick={salvar} style={estilo.btnPrimario}>💾 Salvar</button>
        </div>
      </div>
    );
  };

  const statusCor = { futuro: '#8090c0', em_andamento: '#c59d5f', concluido: '#80c880' };

  return (
    <ListaSecao itens={[...eventos].sort((a, b) => a.ordem - b.ordem)} titulo="Evento" btnLabel="📅 + Novo Evento" onCreate={buscar}
      renderItem={(e, editar) => (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <span style={{ color: statusCor[e.status] || '#888', fontSize: '0.8rem' }}>{STATUS_EVENTO[e.status]}</span>
              <span style={{ color: '#c59d5f', fontFamily: "'MedievalSharp',cursive" }}>{e.titulo}</span>
            </div>
            <div style={{ display: 'flex', gap: '0.4rem' }}>
              <VisToggle visivel={!!e.visivel} onChange={v => toggle(e.id, v)} />
              <button onClick={editar} style={estilo.btnSecundario}>✏️</button>
              <button onClick={() => deletar(e.id)} style={estilo.btnPerigo}>🗑️</button>
            </div>
          </div>
          {e.descricao_pub && <p style={{ color: '#a09070', fontSize: '0.82rem', margin: '0.3rem 0 0' }}>👁 {e.descricao_pub}</p>}
          {e.descricao_priv && <p style={{ color: '#666', fontSize: '0.78rem', margin: '0.2rem 0 0', fontStyle: 'italic' }}>🔒 {e.descricao_priv}</p>}
        </div>
      )}
      renderForm={(item, onSalvo, onCancelar) => <FormEvento item={item} onSalvo={onSalvo} onCancelar={onCancelar} />}
    />
  );
}

// ── NPCs ──────────────────────────────────────────────────────────────────────
function SecaoNPCs({ cid, fetchWithAuth }) {
  const [npcs, setNpcs] = useState([]);
  const buscar = () => fetchWithAuth(`${API}/api/campanhas/${cid}/npcs`).then(r => r.json()).then(setNpcs).catch(() => {});
  useEffect(() => { buscar(); }, [cid]);

  const toggle = async (id, v) => { await fetchWithAuth(`${API}/api/campanhas/${cid}/npcs/${id}/toggle`, { method: 'PATCH', body: JSON.stringify({ visivel: v }) }); buscar(); };
  const deletar = async (id) => { if (!window.confirm('Deletar NPC?')) return; await fetchWithAuth(`${API}/api/campanhas/${cid}/npcs/${id}`, { method: 'DELETE' }); buscar(); };

  const FormNPC = ({ item, onSalvo, onCancelar }) => {
    const [f, setF] = useState({ nome: item?.nome || '', papel: item?.papel || '', alinhamento: item?.alinhamento || '', local: item?.local || '', descricao_pub: item?.descricao_pub || '', descricao_priv: item?.descricao_priv || '' });
    const set = (k, v) => setF(p => ({ ...p, [k]: v }));
    const salvar = async () => {
      const url = item ? `${API}/api/campanhas/${cid}/npcs/${item.id}` : `${API}/api/campanhas/${cid}/npcs`;
      await fetchWithAuth(url, { method: item ? 'PUT' : 'POST', body: JSON.stringify(f) });
      onSalvo();
    };
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '0.5rem' }}>
          {[['Nome', 'nome'], ['Papel', 'papel'], ['Local', 'local']].map(([l, k]) => (
            <div key={k}><label style={estilo.label}>{l}</label><input value={f[k]} onChange={e => set(k, e.target.value)} style={estilo.input} /></div>
          ))}
          <div><label style={estilo.label}>Alinhamento</label>
            <select value={f.alinhamento} onChange={e => set('alinhamento', e.target.value)} style={estilo.input}>
              <option value="">—</option>
              {ALINHAMENTOS.map(a => <option key={a}>{a}</option>)}
            </select>
          </div>
        </div>
        <div><label style={estilo.label}>👁 Descrição Pública</label><textarea value={f.descricao_pub} onChange={e => set('descricao_pub', e.target.value)} style={estilo.textarea} /></div>
        <div><label style={estilo.label}>🔒 Segredos / Notas Privadas</label><textarea value={f.descricao_priv} onChange={e => set('descricao_priv', e.target.value)} style={estilo.textarea} /></div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button onClick={onCancelar} style={estilo.btnSecundario}>Cancelar</button>
          <button onClick={salvar} style={estilo.btnPrimario}>💾 Salvar</button>
        </div>
      </div>
    );
  };

  return (
    <ListaSecao itens={npcs} titulo="NPC" btnLabel="👥 + Novo NPC" onCreate={buscar}
      renderItem={(n, editar) => (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <span style={{ color: '#c59d5f', fontFamily: "'MedievalSharp',cursive", marginRight: '0.5rem' }}>{n.nome}</span>
              {n.papel && <span style={{ color: '#887060', fontSize: '0.78rem' }}>{n.papel}</span>}
              {n.alinhamento && <span style={{ color: '#666', fontSize: '0.75rem', marginLeft: '0.5rem' }}>· {n.alinhamento}</span>}
              {n.local && <span style={{ color: '#666', fontSize: '0.75rem', marginLeft: '0.5rem' }}>📍 {n.local}</span>}
            </div>
            <div style={{ display: 'flex', gap: '0.4rem' }}>
              <VisToggle visivel={!!n.visivel} onChange={v => toggle(n.id, v)} />
              <button onClick={editar} style={estilo.btnSecundario}>✏️</button>
              <button onClick={() => deletar(n.id)} style={estilo.btnPerigo}>🗑️</button>
            </div>
          </div>
          {n.descricao_pub && <p style={{ color: '#a09070', fontSize: '0.82rem', margin: '0.3rem 0 0' }}>👁 {n.descricao_pub}</p>}
          {n.descricao_priv && <p style={{ color: '#666', fontSize: '0.78rem', margin: '0.2rem 0 0', fontStyle: 'italic' }}>🔒 {n.descricao_priv}</p>}
        </div>
      )}
      renderForm={(item, onSalvo, onCancelar) => <FormNPC item={item} onSalvo={onSalvo} onCancelar={onCancelar} />}
    />
  );
}

// ── Quests ────────────────────────────────────────────────────────────────────
function SecaoQuests({ cid, fetchWithAuth }) {
  const [quests, setQuests] = useState([]);
  const buscar = () => fetchWithAuth(`${API}/api/campanhas/${cid}/quests`).then(r => r.json()).then(setQuests).catch(() => {});
  useEffect(() => { buscar(); }, [cid]);

  const toggle = async (id, v) => { await fetchWithAuth(`${API}/api/campanhas/${cid}/quests/${id}/toggle`, { method: 'PATCH', body: JSON.stringify({ visivel: v }) }); buscar(); };
  const deletar = async (id) => { if (!window.confirm('Deletar quest?')) return; await fetchWithAuth(`${API}/api/campanhas/${cid}/quests/${id}`, { method: 'DELETE' }); buscar(); };
  const mudarStatus = async (id, status) => { await fetchWithAuth(`${API}/api/campanhas/${cid}/quests/${id}`, { method: 'PUT', body: JSON.stringify({ status }) }); buscar(); };

  const FormQuest = ({ item, onSalvo, onCancelar }) => {
    const [f, setF] = useState({ titulo: item?.titulo || '', objetivo_pub: item?.objetivo_pub || '', detalhes_priv: item?.detalhes_priv || '', recompensa_pub: item?.recompensa_pub || '', recompensa_priv: item?.recompensa_priv || '', local_priv: item?.local_priv || '', status: item?.status || 'ativa' });
    const set = (k, v) => setF(p => ({ ...p, [k]: v }));
    const salvar = async () => {
      const url = item ? `${API}/api/campanhas/${cid}/quests/${item.id}` : `${API}/api/campanhas/${cid}/quests`;
      await fetchWithAuth(url, { method: item ? 'PUT' : 'POST', body: JSON.stringify(f) });
      onSalvo();
    };
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '0.5rem' }}>
          <div><label style={estilo.label}>Título</label><input value={f.titulo} onChange={e => set('titulo', e.target.value)} style={estilo.input} /></div>
          <div><label style={estilo.label}>Status</label>
            <select value={f.status} onChange={e => set('status', e.target.value)} style={estilo.input}>
              {Object.entries(STATUS_QUEST).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </div>
        </div>
        <div><label style={estilo.label}>👁 Objetivo (players veem)</label><textarea value={f.objetivo_pub} onChange={e => set('objetivo_pub', e.target.value)} style={estilo.textarea} /></div>
        <div><label style={estilo.label}>🔒 Detalhes Privados</label><textarea value={f.detalhes_priv} onChange={e => set('detalhes_priv', e.target.value)} style={estilo.textarea} /></div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem' }}>
          <div><label style={estilo.label}>👁 Recompensa Pública</label><input value={f.recompensa_pub} onChange={e => set('recompensa_pub', e.target.value)} style={estilo.input} /></div>
          <div><label style={estilo.label}>🔒 Recompensa Privada</label><input value={f.recompensa_priv} onChange={e => set('recompensa_priv', e.target.value)} style={estilo.input} /></div>
          <div><label style={estilo.label}>🔒 Localização (privado)</label><input value={f.local_priv} onChange={e => set('local_priv', e.target.value)} style={estilo.input} /></div>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button onClick={onCancelar} style={estilo.btnSecundario}>Cancelar</button>
          <button onClick={salvar} style={estilo.btnPrimario}>💾 Salvar</button>
        </div>
      </div>
    );
  };

  const statusCor = { ativa: '#c59d5f', concluida: '#80c880', falhou: '#e08080', oculta: '#666' };

  return (
    <ListaSecao itens={quests} titulo="Quest" btnLabel="🎯 + Nova Quest" onCreate={buscar}
      renderItem={(q, editar) => (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ color: statusCor[q.status], fontSize: '0.78rem' }}>{STATUS_QUEST[q.status]}</span>
              <span style={{ color: '#c59d5f', fontFamily: "'MedievalSharp',cursive" }}>{q.titulo}</span>
            </div>
            <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
              <select value={q.status} onChange={e => mudarStatus(q.id, e.target.value)}
                style={{ ...estilo.input, width: 'auto', fontSize: '0.72rem', padding: '0.2rem 0.3rem' }}>
                {Object.entries(STATUS_QUEST).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
              <VisToggle visivel={!!q.visivel} onChange={v => toggle(q.id, v)} />
              <button onClick={editar} style={estilo.btnSecundario}>✏️</button>
              <button onClick={() => deletar(q.id)} style={estilo.btnPerigo}>🗑️</button>
            </div>
          </div>
          {q.objetivo_pub && <p style={{ color: '#a09070', fontSize: '0.82rem', margin: '0.3rem 0 0' }}>🎯 {q.objetivo_pub}</p>}
          {q.recompensa_pub && <p style={{ color: '#80c880', fontSize: '0.78rem', margin: '0.15rem 0 0' }}>💰 {q.recompensa_pub}</p>}
          {q.detalhes_priv && <p style={{ color: '#666', fontSize: '0.75rem', margin: '0.15rem 0 0', fontStyle: 'italic' }}>🔒 {q.detalhes_priv}</p>}
        </div>
      )}
      renderForm={(item, onSalvo, onCancelar) => <FormQuest item={item} onSalvo={onSalvo} onCancelar={onCancelar} />}
    />
  );
}

// ── Anotações ────────────────────────────────────────────────────────────────
function SecaoAnotacoes({ cid, fetchWithAuth }) {
  const [anotacoes, setAnotacoes] = useState([]);
  const buscar = () => fetchWithAuth(`${API}/api/campanhas/${cid}/anotacoes`).then(r => r.json()).then(setAnotacoes).catch(() => {});
  useEffect(() => { buscar(); }, [cid]);

  const toggle = async (id, v) => { await fetchWithAuth(`${API}/api/campanhas/${cid}/anotacoes/${id}/toggle`, { method: 'PATCH', body: JSON.stringify({ visivel: v }) }); buscar(); };
  const deletar = async (id) => { if (!window.confirm('Deletar anotação?')) return; await fetchWithAuth(`${API}/api/campanhas/${cid}/anotacoes/${id}`, { method: 'DELETE' }); buscar(); };

  const FormAnotacao = ({ item, onSalvo, onCancelar }) => {
    const [f, setF] = useState({ titulo: item?.titulo || '', conteudo: item?.conteudo || '' });
    const set = (k, v) => setF(p => ({ ...p, [k]: v }));
    const salvar = async () => {
      const url = item ? `${API}/api/campanhas/${cid}/anotacoes/${item.id}` : `${API}/api/campanhas/${cid}/anotacoes`;
      await fetchWithAuth(url, { method: item ? 'PUT' : 'POST', body: JSON.stringify(f) });
      onSalvo();
    };
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <div><label style={estilo.label}>Título</label><input value={f.titulo} onChange={e => set('titulo', e.target.value)} style={estilo.input} /></div>
        <div><label style={estilo.label}>Conteúdo</label><textarea value={f.conteudo} onChange={e => set('conteudo', e.target.value)} style={{ ...estilo.textarea, minHeight: '100px' }} /></div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button onClick={onCancelar} style={estilo.btnSecundario}>Cancelar</button>
          <button onClick={salvar} style={estilo.btnPrimario}>💾 Salvar</button>
        </div>
      </div>
    );
  };

  return (
    <ListaSecao itens={anotacoes} titulo="Anotação" btnLabel="📝 + Nova Anotação" onCreate={buscar}
      renderItem={(a, editar) => (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: '#c59d5f', fontFamily: "'MedievalSharp',cursive" }}>{a.titulo}</span>
            <div style={{ display: 'flex', gap: '0.4rem' }}>
              <VisToggle visivel={!!a.visivel} onChange={v => toggle(a.id, v)} />
              <button onClick={editar} style={estilo.btnSecundario}>✏️</button>
              <button onClick={() => deletar(a.id)} style={estilo.btnPerigo}>🗑️</button>
            </div>
          </div>
          {a.conteudo && <p style={{ color: '#a09070', fontSize: '0.82rem', margin: '0.3rem 0 0', whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>{a.conteudo}</p>}
        </div>
      )}
      renderForm={(item, onSalvo, onCancelar) => <FormAnotacao item={item} onSalvo={onSalvo} onCancelar={onCancelar} />}
    />
  );
}

// ── PÁGINA PRINCIPAL ──────────────────────────────────────────────────────────
const ABAS = [
  { id: 'campanha', label: '📖 Campanha', icone: '📖' },
  { id: 'mapas',    label: '🗺 Mapas',    icone: '🗺' },
  { id: 'eventos',  label: '📅 Eventos',  icone: '📅' },
  { id: 'npcs',     label: '👥 NPCs',     icone: '👥' },
  { id: 'quests',   label: '🎯 Quests',   icone: '🎯' },
  { id: 'notas',    label: '📝 Anotações',icone: '📝' },
];

export default function EsconderijoPage() {
  const { fetchWithAuth } = useAuth();
  const [campanhas,   setCampanhas]   = useState([]);
  const [campanhaAtiva, setCampanhaAtiva] = useState(null);
  const [abaAtiva,    setAbaAtiva]    = useState('campanha');
  const [criandoNova, setCriandoNova] = useState(false);
  const [nomeNova,    setNomeNova]    = useState('');
  const [loading,     setLoading]     = useState(true);

  useEffect(() => {
    if (backgrounds?.mestre) {
      document.body.style.backgroundImage    = `url(${backgrounds.mestre})`;
      document.body.style.backgroundSize     = 'cover';
      document.body.style.backgroundPosition = 'center';
      document.body.style.backgroundAttachment = 'fixed';
    }
    return () => { document.body.style.backgroundImage = ''; };
  }, []);

  const buscarCampanhas = async () => {
    setLoading(true);
    try {
      const r = await fetchWithAuth(`${API}/api/campanhas`);
      const data = await r.json();
      setCampanhas(data);
      if (!campanhaAtiva && data.length > 0) setCampanhaAtiva(data[0]);
    } catch {}
    setLoading(false);
  };
  useEffect(() => { buscarCampanhas(); }, []);

  const criarCampanha = async () => {
    if (!nomeNova.trim()) return;
    const r = await fetchWithAuth(`${API}/api/campanhas`, { method: 'POST', body: JSON.stringify({ nome: nomeNova }) });
    const data = await r.json();
    if (data.sucesso) {
      setCriandoNova(false);
      setNomeNova('');
      await buscarCampanhas();
      setCampanhaAtiva(data.campanha);
    }
  };

  const deletarCampanha = async (id) => {
    if (!window.confirm('Deletar esta campanha e todo seu conteúdo? Esta ação não pode ser desfeita.')) return;
    await fetchWithAuth(`${API}/api/campanhas/${id}`, { method: 'DELETE' });
    await buscarCampanhas();
    setCampanhaAtiva(null);
  };

  return (
    <div style={{ minHeight: '100vh', fontFamily: "'Georgia',serif", display: 'flex', flexDirection: 'column' }}>

      {/* Header */}
      <div style={{
        background: 'linear-gradient(180deg,rgba(20,14,3,0.97),rgba(12,8,2,0.97))',
        borderBottom: '2px solid #c59d5f', padding: '1rem 2rem',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <h1 style={{ fontFamily: "'MedievalSharp',cursive", color: '#c59d5f', margin: 0, fontSize: '1.5rem', textShadow: '0 0 20px rgba(197,157,95,0.4)' }}>
          🏰 Esconderijo do Mestre
        </h1>
        <button onClick={() => setCriandoNova(true)} style={estilo.btnPrimario}>
          + Nova Campanha
        </button>
      </div>

      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>

        {/* Sidebar: lista de campanhas */}
        <div style={{
          width: '240px', flexShrink: 0,
          background: 'rgba(8,6,2,0.95)', borderRight: '1px solid #3a2a10',
          display: 'flex', flexDirection: 'column', overflowY: 'auto',
        }}>
          <p style={{ color: '#776050', fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', padding: '0.8rem 1rem 0.3rem', margin: 0 }}>
            Minhas Campanhas
          </p>

          {criandoNova && (
            <div style={{ padding: '0.5rem 0.8rem', borderBottom: '1px solid #3a2a10' }}>
              <input value={nomeNova} onChange={e => setNomeNova(e.target.value)}
                placeholder="Nome da campanha..."
                style={{ ...estilo.input, marginBottom: '0.4rem' }}
                onKeyDown={e => e.key === 'Enter' && criarCampanha()}
                autoFocus
              />
              <div style={{ display: 'flex', gap: '0.4rem' }}>
                <button onClick={() => setCriandoNova(false)} style={{ ...estilo.btnSecundario, flex: 1 }}>✕</button>
                <button onClick={criarCampanha} style={{ ...estilo.btnPrimario, flex: 2, padding: '0.3rem' }}>Criar</button>
              </div>
            </div>
          )}

          {loading ? (
            <p style={{ color: '#555', padding: '1rem', fontSize: '0.82rem' }}>Carregando...</p>
          ) : campanhas.length === 0 ? (
            <p style={{ color: '#444', padding: '1rem', fontSize: '0.82rem', fontStyle: 'italic' }}>Nenhuma campanha ainda.</p>
          ) : (
            campanhas.map(c => (
              <div key={c.id}
                onClick={() => { setCampanhaAtiva(c); setAbaAtiva('campanha'); }}
                style={{
                  padding: '0.7rem 1rem', cursor: 'pointer',
                  background: campanhaAtiva?.id === c.id ? 'rgba(197,157,95,0.12)' : 'transparent',
                  borderLeft: `3px solid ${campanhaAtiva?.id === c.id ? '#c59d5f' : 'transparent'}`,
                  borderBottom: '1px solid #1a1208', transition: 'all 0.15s',
                }}
              >
                <div style={{ color: campanhaAtiva?.id === c.id ? '#c59d5f' : '#a09070', fontFamily: "'MedievalSharp',cursive", fontSize: '0.85rem', marginBottom: '0.15rem' }}>
                  {c.nome}
                </div>
                <div style={{ fontSize: '0.7rem', color: '#556', display: 'flex', justifyContent: 'space-between' }}>
                  <span>{c.tom} · {c.sistema}</span>
                  <button onClick={e => { e.stopPropagation(); deletarCampanha(c.id); }}
                    style={{ background: 'none', border: 'none', color: '#664', cursor: 'pointer', fontSize: '0.75rem', padding: 0 }}>🗑</button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Conteúdo principal */}
        {!campanhaAtiva ? (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#444', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ fontSize: '4rem' }}>🏰</div>
            <p style={{ fontFamily: "'MedievalSharp',cursive", color: '#5a4520', fontSize: '1.1rem' }}>
              Selecione ou crie uma campanha
            </p>
          </div>
        ) : (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

            {/* Abas */}
            <div style={{
              display: 'flex', background: 'rgba(10,8,3,0.95)',
              borderBottom: '1px solid #3a2a10', padding: '0 1rem', flexShrink: 0,
            }}>
              {ABAS.map(aba => (
                <button key={aba.id} onClick={() => setAbaAtiva(aba.id)} style={{
                  background: 'none', border: 'none',
                  borderBottom: `2px solid ${abaAtiva === aba.id ? '#c59d5f' : 'transparent'}`,
                  color: abaAtiva === aba.id ? '#c59d5f' : '#665040',
                  fontFamily: "'MedievalSharp',cursive", fontSize: '0.82rem',
                  padding: '0.7rem 1rem', cursor: 'pointer', whiteSpace: 'nowrap',
                  transition: 'all 0.15s',
                }}>
                  {aba.label}
                </button>
              ))}
            </div>

            {/* Conteúdo da aba */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem 2rem' }}>
              {abaAtiva === 'campanha' && (
                <SecaoCampanha campanha={campanhaAtiva} fetchWithAuth={fetchWithAuth} onAtualizado={buscarCampanhas} />
              )}
              {abaAtiva === 'mapas'   && <SecaoMapas    cid={campanhaAtiva.id} fetchWithAuth={fetchWithAuth} />}
              {abaAtiva === 'eventos' && <SecaoEventos  cid={campanhaAtiva.id} fetchWithAuth={fetchWithAuth} />}
              {abaAtiva === 'npcs'    && <SecaoNPCs     cid={campanhaAtiva.id} fetchWithAuth={fetchWithAuth} />}
              {abaAtiva === 'quests'  && <SecaoQuests   cid={campanhaAtiva.id} fetchWithAuth={fetchWithAuth} />}
              {abaAtiva === 'notas'   && <SecaoAnotacoes cid={campanhaAtiva.id} fetchWithAuth={fetchWithAuth} />}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}