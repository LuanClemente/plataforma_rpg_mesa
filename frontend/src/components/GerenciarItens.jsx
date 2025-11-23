// frontend/src/components/GerenciarItens.jsx

import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

// Define o estado inicial (em branco) para o formulário de um novo item
const ESTADO_INICIAL_FORMULARIO = {
  nome: '',
  tipo: 'Item', // (ex: Arma, Armadura, Poção, Item)
  descricao: '',
  preco_ouro: 0,
  dano_dado: '',    // (ex: 1d8)
  bonus_ataque: 0,
  efeito: ''       // (ex: +1 DEF)
};

function GerenciarItens() {
  // Pega a função 'fetchWithAuth' do contexto
  const { fetchWithAuth } = useAuth();

  // --- Estados (States) do Componente ---
  const [itens, setItens] = useState([]); // Lista de itens
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState(ESTADO_INICIAL_FORMULARIO);
  
  // Controla se estamos Criando (null) ou Editando (objeto do item)
  const [itemEmEdicao, setItemEmEdicao] = useState(null);

  
  // --- Funções de Busca de Dados (Read) ---
  
  // Função para buscar a lista de itens da API
  const fetchItens = async () => {
    setIsLoading(true);
    try {
      // Rota GET /api/itens é pública
      const response = await fetch('http://127.0.0.1:5003/api/itens');
      if (!response.ok) {
        throw new Error('Falha ao buscar itens');
      }
      const data = await response.json();
      setItens(data); // Salva a lista de itens no estado
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Roda a busca de itens UMA VEZ quando o componente carregar
  useEffect(() => {
    fetchItens();
  }, []);

  
  // --- Funções de Manipulação do Formulário e Modal ---
  
  // Atualiza o formData conforme o Mestre digita
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  // Abre o modal em modo "Criar Novo"
  const handleAbrirModalCriar = () => {
    setItemEmEdicao(null);
    setFormData(ESTADO_INICIAL_FORMULARIO); // Limpa o formulário
    setIsModalOpen(true);
  };

  // Abre o modal em modo "Editar"
  const handleAbrirModalEditar = (item) => {
    setItemEmEdicao(item);
    setFormData(item); // Preenche o formulário com dados do item
    setIsModalOpen(true);
  };

  // Fecha o modal
  const handleFecharModal = () => {
    setIsModalOpen(false);
    setItemEmEdicao(null);
    setFormData(ESTADO_INICIAL_FORMULARIO);
  };

  
  // --- Funções de Ação da API (Create, Update, Delete) ---

  // Função chamada ao enviar o formulário do modal
  const handleSubmitFormulario = async (e) => {
    e.preventDefault();

    const isEditing = itemEmEdicao !== null;
    const url = isEditing 
      ? `http://127.0.0.1:5003/api/itens/${itemEmEdicao.id}` // URL de Update
      : `http://127.0.0.1:5003/api/itens`; // URL de Create
      
    const method = isEditing ? 'PUT' : 'POST';

    try {
      // Usa 'fetchWithAuth' para rotas protegidas
      const response = await fetchWithAuth(url, {
        method: method,
        body: JSON.stringify(formData), 
      });

      const data = await response.json();

      if (!data.sucesso) {
        throw new Error(data.mensagem || 'Falha ao salvar item');
      }

      handleFecharModal(); // Fecha o pop-up
      fetchItens(); // Atualiza a lista na tabela
      
    } catch (err) {
      setError(err.message); 
    }
  };

  // Função para Apagar um item
  const handleApagar = async (itemId) => {
    if (window.confirm("Tem certeza que deseja apagar este item da base de dados?")) {
      try {
        const url = `http://127.0.0.1:5003/api/itens/${itemId}`;
        
        // Usa 'fetchWithAuth' para a rota DELETE
        const response = await fetchWithAuth(url, {
          method: 'DELETE',
        });

        const data = await response.json();

        if (!data.sucesso) {
          throw new Error(data.mensagem || 'Falha ao apagar item');
        }

        fetchItens(); // Atualiza a lista na tabela

      } catch (err) {
        setError(err.message);
      }
    }
  };

  
  // --- Renderização do Componente (JSX) ---

  if (isLoading) return <p>Carregando itens...</p>;
  if (error) return <p style={{ color: 'red' }}>Erro: {error}</p>;

  return (
    <div className="gerenciador-container">
      <h2>Gerenciar Itens</h2>
      <button onClick={handleAbrirModalCriar} className="btn-criar">
        + Criar Novo Item
      </button>

      {/* Tabela com a lista de itens */}
      <table className="mestre-table">
        <thead>
          <tr>
            <th>Nome</th>
            <th>Tipo</th>
            <th>Preço (Ouro)</th>
            <th>Dano</th>
            <th>Efeito</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {itens.map((item) => (
            <tr key={item.id}>
              <td>{item.nome}</td>
              <td>{item.tipo}</td>
              <td>{item.preco_ouro || item.preco}</td> {/* (preco_ouro ou preco) */}
              <td>{item.dano_dado || item.dano}</td> {/* (dano_dado ou dano) */}
              <td>{item.efeito}</td>
              <td>
                <button onClick={() => handleAbrirModalEditar(item)} className="btn-editar">Editar</button>
                <button onClick={() => handleApagar(item.id)} className="btn-apagar">Apagar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* --- O Modal (Pop-up) de Criar/Editar --- */}
      {isModalOpen && (
        <div className="modal-backdrop" onClick={handleFecharModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>{itemEmEdicao ? "Editar Item" : "Criar Novo Item"}</h3>
            
            {/* Formulário de Criação/Edição */}
            <form onSubmit={handleSubmitFormulario} className="mestre-form">
              
              <div className="form-row">
                <div className="form-group" style={{ flex: 2 }}> {/* Campo Nome maior */}
                  <label>Nome:</label>
                  <input type="text" name="nome" value={formData.nome} onChange={handleInputChange} required />
                </div>
                <div className="form-group" style={{ flex: 1 }}> {/* Campo Tipo menor */}
                  <label>Tipo:</label>
                  <input type="text" name="tipo" value={formData.tipo} onChange={handleInputChange} required />
                </div>
              </div>

              <div className="form-group">
                <label>Descrição:</label>
                <input type="text" name="descricao" value={formData.descricao} onChange={handleInputChange} />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Preço (Ouro):</label>
                  <input type="number" name="preco_ouro" value={formData.preco_ouro} onChange={handleInputChange} required />
                </div>
                 <div className="form-group">
                  <label>Bônus Ataque:</label>
                  <input type="number" name="bonus_ataque" value={formData.bonus_ataque} onChange={handleInputChange} />
                </div>
              </div>

              <div className="form-row">
                 <div className="form-group">
                  <label>Dado de Dano:</label>
                  <input type="text" name="dano_dado" value={formData.dano_dado} onChange={handleInputChange} placeholder="ex: 1d8" />
                </div>
                <div className="form-group">
                  <label>Efeito:</label>
                  <input type="text" name="efeito" value={formData.efeito} onChange={handleInputChange} placeholder="ex: +1 DEF" />
                </div>
              </div>

              {/* Botões do formulário */}
              <div className="form-actions">
                <button type="submit" className="btn-salvar">Salvar</button>
                <button type="button" onClick={handleFecharModal} className="btn-cancelar">Cancelar</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default GerenciarItens;
