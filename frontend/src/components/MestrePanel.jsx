// frontend/src/components/MestrePanel.jsx
import React, { useState, useEffect } from 'react';
import ModalConfirm from './ModalConfirm';

function MestrePanel({ socket, salaId, jogadores }) {
  const [xpAmount, setXpAmount]           = useState(100);
  const [targetXp, setTargetXp]           = useState('all');
  const [itemSelecionado, setItemSelecionado] = useState('');
  const [itemAlvo, setItemAlvo]           = useState('');
  const [coronaAlvo, setCoronaAlvo]       = useState('');
  const [itensDisp, setItensDisp]         = useState([]);
  const [feedback, setFeedback]           = useState({});

  const players = jogadores.filter(j => j.role === 'player');

  // Estado do modal de confirmação customizado
  const [modal, setModal] = useState(null); // { titulo, mensagem, tipo, confirmLabel, onConfirm }

  const confirmar = (config) => setModal(config);
  const fecharModal = () => setModal(null);

  useEffect(() => {
    fetch('http://127.0.0.1:5003/api/itens')
      .then(r => r.json())
      .then(data => { setItensDisp(data); if (data[0]) setItemSelecionado(data[0].nome); })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (players.length > 0) {
      if (!itemAlvo)    setItemAlvo(String(players[0].ficha_id));
      if (!coronaAlvo)  setCoronaAlvo(String(players[0].ficha_id));
    }
  }, [jogadores]);

  const fb = (key, msg) => {
    setFeedback(p => ({ ...p, [key]: msg }));
    setTimeout(() => setFeedback(p => ({ ...p, [key]: '' })), 3000);
  };

  const token = () => localStorage.getItem('authToken');

  const handleXp = () => {
    if (!socket || xpAmount <= 0) return fb('xp', '❌ XP inválido');
    socket.emit('mestre_dar_xp', { token: token(), sala_id: salaId, alvo_id: targetXp, quantidade: parseInt(xpAmount) });
    fb('xp', `✅ ${xpAmount} XP enviado!`);
  };

  const handleItem = () => {
    if (!socket || !itemSelecionado || !itemAlvo) return fb('item', '❌ Selecione item e jogador');
    const item = itensDisp.find(i => i.nome === itemSelecionado);
    socket.emit('mestre_dar_item', { token: token(), sala_id: salaId, alvo_ficha_id: itemAlvo, nome_item: item?.nome || itemSelecionado, descricao_item: item?.descricao || '' });
    fb('item', `✅ "${itemSelecionado}" enviado!`);
  };

  const handleCoroa = () => {
    if (!socket || !coronaAlvo) return fb('coroa', '❌ Selecione jogador');
    const nomeAlvo = players.find(j => String(j.ficha_id) === String(coronaAlvo))?.nome_personagem || 'jogador';
    confirmar({
      tipo: 'coroa',
      titulo: 'Passar a Coroa',
      mensagem: `Deseja transferir o cargo de Mestre para ${nomeAlvo}? Você se tornará um jogador comum.`,
      confirmLabel: '👑 Confirmar',
      onConfirm: () => {
        socket.emit('mestre_passar_coroa', { token: token(), sala_id: salaId, alvo_ficha_id: coronaAlvo });
        fb('coroa', '👑 Coroa transferida!');
        fecharModal();
      }
    });
  };

  const handleKick = (fichaId, nome) => {
    confirmar({
      tipo: 'kick',
      titulo: 'Expulsar Jogador',
      mensagem: `Deseja expulsar ${nome} da sala? Ele poderá entrar novamente.`,
      confirmLabel: '⚡ Expulsar',
      onConfirm: () => {
        socket.emit('mestre_kickar', { token: token(), sala_id: salaId, alvo_ficha_id: fichaId });
        fecharModal();
      }
    });
  };

  const handleBan = (fichaId, nome) => {
    confirmar({
      tipo: 'ban',
      titulo: 'Banir Jogador',
      mensagem: `Tem certeza que deseja banir ${nome} permanentemente desta sala? Esta ação não pode ser desfeita!`,
      confirmLabel: '🔨 Banir',
      onConfirm: () => {
        socket.emit('mestre_banir', { token: token(), sala_id: salaId, alvo_ficha_id: fichaId });
        fecharModal();
      }
    });
  };

  return (
    <>
    {modal && (
      <ModalConfirm
        titulo={modal.titulo}
        mensagem={modal.mensagem}
        tipo={modal.tipo}
        confirmLabel={modal.confirmLabel}
        cancelLabel="Cancelar"
        onConfirm={modal.onConfirm}
        onCancel={fecharModal}
      />
    )}
    <div className="mestre-panel-container">

      {/* ====== LINHA PRINCIPAL: XP | ITEM | COROA lado a lado ====== */}
      <div className="mestre-linha-controles">

        {/* XP */}
        <div className="mestre-bloco">
          <span className="mestre-bloco-titulo">⭐ XP</span>
          <div className="mestre-bloco-row">
            <input type="number" value={xpAmount} onChange={e => setXpAmount(e.target.value)}
              className="mestre-input-sm" style={{ width: '70px' }} placeholder="XP" />
            <select value={targetXp} onChange={e => setTargetXp(e.target.value)} className="mestre-select-sm">
              <option value="all">Todos</option>
              {players.map(j => <option key={j.ficha_id} value={j.ficha_id}>{j.nome_personagem}</option>)}
            </select>
            <button onClick={handleXp} className="mestre-btn">Dar</button>
          </div>
          {feedback.xp && <span className="mestre-fb">{feedback.xp}</span>}
        </div>

        <div className="mestre-divisor">⚔</div>

        {/* ITEM */}
        <div className="mestre-bloco">
          <span className="mestre-bloco-titulo">🎁 Item</span>
          <div className="mestre-bloco-row">
            <select value={itemSelecionado} onChange={e => setItemSelecionado(e.target.value)} className="mestre-select-sm">
              {itensDisp.length === 0
                ? <option value="">Sem itens</option>
                : itensDisp.map(i => <option key={i.id} value={i.nome}>{i.nome}</option>)}
            </select>
            <select value={itemAlvo} onChange={e => setItemAlvo(e.target.value)} className="mestre-select-sm">
              {players.length === 0
                ? <option value="">Sem jogadores</option>
                : players.map(j => <option key={j.ficha_id} value={j.ficha_id}>{j.nome_personagem}</option>)}
            </select>
            <button onClick={handleItem} className="mestre-btn">Dar</button>
          </div>
          {feedback.item && <span className="mestre-fb">{feedback.item}</span>}
        </div>

        <div className="mestre-divisor">⚔</div>

        {/* COROA */}
        <div className="mestre-bloco">
          <span className="mestre-bloco-titulo">👑 Coroa</span>
          <div className="mestre-bloco-row">
            <select value={coronaAlvo} onChange={e => setCoronaAlvo(e.target.value)} className="mestre-select-sm">
              {players.length === 0
                ? <option value="">Sem jogadores</option>
                : players.map(j => <option key={j.ficha_id} value={j.ficha_id}>{j.nome_personagem}</option>)}
            </select>
            <button onClick={handleCoroa} className="mestre-btn mestre-btn-danger">Passar</button>
          </div>
          {feedback.coroa && <span className="mestre-fb">{feedback.coroa}</span>}
        </div>

        <div className="mestre-divisor">⚔</div>

        {/* JOGADORES ONLINE + KICK/BAN */}
        <div className="mestre-bloco mestre-bloco-jogadores">
          <span className="mestre-bloco-titulo">👥 Online ({players.length})</span>
          <div className="mestre-jogadores-inline">
            {players.length === 0
              ? <span className="mestre-sem-jogadores">Nenhum jogador</span>
              : players.map((j, i) => (
                  <div key={i} className="mestre-jogador-row">
                    <span className="mestre-jogador-nome">⚔ {j.nome_personagem}</span>
                    <button onClick={() => handleKick(j.ficha_id, j.nome_personagem)} className="mestre-btn-kick" title="Expulsar">⚡</button>
                    <button onClick={() => handleBan(j.ficha_id, j.nome_personagem)} className="mestre-btn-ban" title="Banir">🔨</button>
                  </div>
                ))
            }
          </div>
        </div>

      </div>
    </div>
    </>
  );
}

export default MestrePanel;