// frontend/src/components/MestrePanel.jsx
import React, { useState, useEffect } from 'react';

function MestrePanel({ socket, salaId, jogadores }) {
  // --- XP ---
  const [xpAmount, setXpAmount] = useState(100);
  const [targetFichaId, setTargetFichaId] = useState('all');
  const [msgXp, setMsgXp] = useState('');

  // --- Passar Coroa ---
  const [coronaAlvo, setCoronaAlvo] = useState('');
  const [msgCorona, setMsgCorona] = useState('');

  // --- Dar Item ---
  const [itensDisp, setItensDisp] = useState([]);
  const [itemSelecionado, setItemSelecionado] = useState('');
  const [itemAlvo, setItemAlvo] = useState('');
  const [msgItem, setMsgItem] = useState('');

  const jogadores_players = jogadores.filter(j => j.role === 'player');

  // Buscar itens da Ferraria Arcana para o select
  useEffect(() => {
    fetch('http://127.0.0.1:5003/api/itens')
      .then(r => r.json())
      .then(data => {
        setItensDisp(data);
        if (data.length > 0) setItemSelecionado(data[0].nome);
      })
      .catch(() => {});
  }, []);

  // Inicializar alvos quando jogadores mudarem
  useEffect(() => {
    if (jogadores_players.length > 0) {
      if (!coronaAlvo) setCoronaAlvo(jogadores_players[0].ficha_id);
      if (!itemAlvo) setItemAlvo(jogadores_players[0].ficha_id);
    }
  }, [jogadores]);

  // Feedback temporário
  const feedback = (setter, msg, delay = 3000) => {
    setter(msg);
    setTimeout(() => setter(''), delay);
  };

  const handleDarXp = () => {
    if (!socket || !salaId || xpAmount <= 0) {
      feedback(setMsgXp, '❌ Conexão perdida ou XP inválido.');
      return;
    }
    const token = localStorage.getItem('authToken');
    socket.emit('mestre_dar_xp', {
      token, sala_id: salaId,
      alvo_id: targetFichaId,
      quantidade: parseInt(xpAmount, 10),
    });
    feedback(setMsgXp, `✅ ${xpAmount} XP distribuído!`);
  };

  const handlePassarCoroa = () => {
    if (!socket || !coronaAlvo) {
      feedback(setMsgCorona, '❌ Selecione um jogador.');
      return;
    }
    if (!window.confirm('Tem certeza? Você deixará de ser Mestre!')) return;
    const token = localStorage.getItem('authToken');
    socket.emit('mestre_passar_coroa', {
      token, sala_id: salaId,
      alvo_ficha_id: coronaAlvo,
    });
    feedback(setMsgCorona, '👑 Coroa transferida!');
  };

  const handleDarItem = () => {
    if (!socket || !itemSelecionado || !itemAlvo) {
      feedback(setMsgItem, '❌ Selecione item e jogador.');
      return;
    }
    const token = localStorage.getItem('authToken');
    const item = itensDisp.find(i => i.nome === itemSelecionado);
    socket.emit('mestre_dar_item', {
      token, sala_id: salaId,
      alvo_ficha_id: itemAlvo,
      nome_item: item?.nome || itemSelecionado,
      descricao_item: item?.descricao || '',
    });
    feedback(setMsgItem, `✅ "${itemSelecionado}" enviado!`);
  };

  return (
    <div className="mestre-panel-container">

      {/* ---- XP ---- */}
      <div className="mestre-secao">
        <span className="mestre-secao-titulo">⭐ Distribuir XP</span>
        <div className="mestre-secao-controles">
          <div className="mestre-campo">
            <label>Quantidade</label>
            <input type="number" value={xpAmount}
              onChange={e => setXpAmount(e.target.value)}
              style={{ width: '90px' }} />
          </div>
          <div className="mestre-campo">
            <label>Alvo</label>
            <select value={targetFichaId} onChange={e => setTargetFichaId(e.target.value)}>
              <option value="all">— Todos —</option>
              {jogadores_players.map(j => (
                <option key={j.ficha_id} value={j.ficha_id}>{j.nome_personagem}</option>
              ))}
            </select>
          </div>
          <button onClick={handleDarXp} className="mestre-btn-acao">Dar XP</button>
        </div>
        {msgXp && <span className="mestre-feedback">{msgXp}</span>}
      </div>

      {/* ---- DAR ITEM ---- */}
      <div className="mestre-secao">
        <span className="mestre-secao-titulo">🎁 Dar Item</span>
        <div className="mestre-secao-controles">
          <div className="mestre-campo">
            <label>Item</label>
            <select value={itemSelecionado} onChange={e => setItemSelecionado(e.target.value)}>
              {itensDisp.length === 0
                ? <option value="">Nenhum item cadastrado</option>
                : itensDisp.map(i => (
                    <option key={i.id} value={i.nome}>{i.nome}</option>
                  ))
              }
            </select>
          </div>
          <div className="mestre-campo">
            <label>Para</label>
            <select value={itemAlvo} onChange={e => setItemAlvo(e.target.value)}>
              {jogadores_players.length === 0
                ? <option value="">Sem jogadores</option>
                : jogadores_players.map(j => (
                    <option key={j.ficha_id} value={j.ficha_id}>{j.nome_personagem}</option>
                  ))
              }
            </select>
          </div>
          <button onClick={handleDarItem} className="mestre-btn-acao">Dar Item</button>
        </div>
        {msgItem && <span className="mestre-feedback">{msgItem}</span>}
      </div>

      {/* ---- PASSAR COROA ---- */}
      <div className="mestre-secao">
        <span className="mestre-secao-titulo">👑 Passar Coroa</span>
        <div className="mestre-secao-controles">
          <div className="mestre-campo">
            <label>Novo Mestre</label>
            <select value={coronaAlvo} onChange={e => setCoronaAlvo(e.target.value)}>
              {jogadores_players.length === 0
                ? <option value="">Sem jogadores</option>
                : jogadores_players.map(j => (
                    <option key={j.ficha_id} value={j.ficha_id}>{j.nome_personagem}</option>
                  ))
              }
            </select>
          </div>
          <button onClick={handlePassarCoroa}
            className="mestre-btn-acao"
            style={{ background: 'linear-gradient(135deg, #6b3a3a, #9e5050)', borderColor: '#9e5050' }}>
            Transferir
          </button>
        </div>
        {msgCorona && <span className="mestre-feedback">{msgCorona}</span>}
      </div>

      {/* ---- JOGADORES ---- */}
      <div className="mestre-secao">
        <span className="mestre-secao-titulo">👥 Online ({jogadores_players.length})</span>
        <div className="mestre-jogadores-lista">
          {jogadores_players.length === 0
            ? <span style={{ color: '#777', fontSize: '0.85rem' }}>Nenhum jogador</span>
            : jogadores_players.map((j, i) => (
                <span key={i} className="mestre-jogador-tag">⚔ {j.nome_personagem}</span>
              ))
          }
        </div>
      </div>

    </div>
  );
}

export default MestrePanel;