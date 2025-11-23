// frontend/src/components/InventarioSala.jsx
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function InventarioSala() {
  const [itens, setItens] = useState([]);
  const [nomeItem, setNomeItem] = useState('');
  const [descricaoItem, setDescricaoItem] = useState('');
  const [mensagem, setMensagem] = useState('');
  
  const { fetchWithAuth } = useAuth();
  const { id: salaId } = useParams();
  
  // Pega o ID da ficha que o jogador escolheu ao entrar na sala.
  const fichaId = sessionStorage.getItem('selectedFichaId');

  // Função para buscar o inventário da sala.
  const buscarInventario = async () => {
    if (!fichaId || !salaId) return;
    try {
      // Passamos a ficha_id como um parâmetro de query na URL.
      const response = await fetchWithAuth(`http://127.0.0.1:5003/api/salas/${salaId}/inventario?ficha_id=${fichaId}`);
      const data = await response.json();
      if (response.ok) {
        setItens(data);
      }
    } catch (error) {
      console.error("Erro ao buscar inventário:", error);
    }
  };

  // Busca o inventário assim que o componente carrega.
  useEffect(() => {
    buscarInventario();
  }, [fichaId, salaId, fetchWithAuth]);

  // Função para adicionar um novo item ao inventário.
  const handleAddItem = async (e) => {
    e.preventDefault();
    if (nomeItem.trim() === '') return;
    
    try {
      const response = await fetchWithAuth(`http://127.0.0.1:5003/api/salas/${salaId}/inventario`, {
        method: 'POST',
        body: JSON.stringify({
          ficha_id: fichaId,
          nome_item: nomeItem,
          descricao: descricaoItem
        })
      });
      const data = await response.json();
      setMensagem(data.mensagem);
      if (response.ok) {
        setNomeItem('');
        setDescricaoItem('');
        buscarInventario(); // Atualiza a lista de itens.
      }
    } catch (error) {
      setMensagem("Erro de conexão ao adicionar item.");
    }
  };
  
  // Função para apagar um item do inventário.
  const handleApagarItem = async (itemId) => {
    if (window.confirm("Descartar este item?")) {
      try {
        const response = await fetchWithAuth(`http://127.0.0.1:5003/api/inventario-sala/${itemId}`, {
          method: 'DELETE',
          body: JSON.stringify({ ficha_id: fichaId }) // Envia o ficha_id para verificação de posse.
        });
        const data = await response.json();
        setMensagem(data.mensagem);
        if (response.ok) {
          buscarInventario(); // Atualiza a lista.
        }
      } catch (error) {
        setMensagem("Erro ao descartar item.");
      }
    }
  };

  return (
    <div className="inventario-container">
      <h2>Bolsa de Itens</h2>
      
      {/* Formulário para adicionar novos itens */}
      <form onSubmit={handleAddItem} className="inventario-form">
        <input 
          type="text" 
          placeholder="Nome do item" 
          value={nomeItem} 
          onChange={(e) => setNomeItem(e.target.value)} 
          required 
        />
        <input 
          type="text" 
          placeholder="Descrição (opcional)" 
          value={descricaoItem} 
          onChange={(e) => setDescricaoItem(e.target.value)} 
        />
        <button type="submit" className="add-item-button">+</button>
      </form>
      {mensagem && <p className="feedback-message" style={{fontSize: '0.9rem'}}>{mensagem}</p>}
      
      {/* Lista de itens no inventário */}
      <div className="inventario-list">
        {itens.length > 0 ? (
          itens.map(item => (
            <div key={item.id} className="inventario-item">
              <div className="item-info">
                <strong>{item.nome_item}</strong>
                <small>{item.descricao}</small>
              </div>
              <button 
                className="delete-item-button"
                onClick={() => handleApagarItem(item.id)}
              >
                X
              </button>
            </div>
          ))
        ) : (
          <p style={{fontSize: '0.9rem', fontStyle: 'italic'}}>Sua bolsa está vazia.</p>
        )}
      </div>
    </div>
  );
}

export default InventarioSala;
