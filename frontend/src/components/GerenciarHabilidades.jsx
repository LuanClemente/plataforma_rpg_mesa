// frontend/src/components/GerenciarHabilidades.jsx

import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

// Define o estado inicial (em branco) para o formulário de uma nova habilidade
const ESTADO_INICIAL_FORMULARIO = {
  nome: '',
  descricao: '',
  efeito: '',
  custo_mana: 0,
};

function GerenciarHabilidades() {
  // Pega a função 'fetchWithAuth' do contexto
  const { fetchWithAuth } = useAuth();

  // --- Estados (States) do Componente ---
  const [habilidades, setHabilidades] = useState([]); // Lista de habilidades
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState(ESTADO_INICIAL_FORMULARIO);
  
  // Controla se estamos Criando (null) ou Editando (objeto da habilidade)
  const [habilidadeEmEdicao, setHabilidadeEmEdicao] = useState(null);

  
  // --- Funções de Busca de Dados (Read) ---
  
  // Função para buscar a lista de habilidades da API
  const fetchHabilidades = async () => {
    setIsLoading(true);
    try {
      // ATENÇÃO: A rota GET /api/habilidades ainda não existe publicamente.
      // Vamos usar a rota de Itens como placeholder por enquanto.
      // TODO: Criar a rota GET /api/habilidades no backend (servidor_api.py)
      
      // *** Início do Bloco Provisório ***
      // Esta rota (GET /api/itens) é só para o componente não quebrar
      // Nossos botões de Criar, Editar e Apagar (que usam /api/habilidades) VÃO FUNCIONAR!
      const response = await fetch('http://127.0.0.1:5001/api/itens'); 
      if (!response.ok) {
        throw new Error('Falha ao buscar dados (rota de habilidades pendente)');
      }
      // setHabilidades([]); // Quando a rota /api/habilidades existir, use esta linha
      // *** Fim do Bloco Provisório ***

      // (Quando a rota GET /api/habilidades existir, descomente esta parte)
      /*
      const response = await fetch('http://127.0.0.1:5001/api/habilidades');
      if (!response.ok) {
        throw new Error('Falha ao buscar habilidades');
      }
      const data = await response.json();
      setHabilidades(data); 
      */
      
      setHabilidades([]); // Define como vazio por enquanto
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Roda a busca UMA VEZ quando o componente carregar
  useEffect(() => {
    fetchHabilidades();
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
    setHabilidadeEmEdicao(null);
    setFormData(ESTADO_INICIAL_FORMULARIO); // Limpa o formulário
    setIsModalOpen(true);
  };

  // Abre o modal em modo "Editar"
  const handleAbrirModalEditar = (habilidade) => {
    setHabilidadeEmEdicao(habilidade);
    setFormData(habilidade); // Preenche o formulário
    setIsModalOpen(true);
  };

  // Fecha o modal
  const handleFecharModal = () => {
    setIsModalOpen(false);
    setHabilidadeEmEdicao(null);
    setFormData(ESTADO_INICIAL_FORMULARIO);
  };

  
  // --- Funções de Ação da API (Create, Update, Delete) ---

  // Função chamada ao enviar o formulário do modal
  const handleSubmitFormulario = async (e) => {
    e.preventDefault();

    const isEditing = habilidadeEmEdicao !== null;
    const url = isEditing 
      ? `http://127.0.0.1:5001/api/habilidades/${habilidadeEmEdicao.id}` // URL de Update
      : `http://127.0.0.1:5001/api/habilidades`; // URL de Create
      
    const method = isEditing ? 'PUT' : 'POST';

    try {
      // Usa 'fetchWithAuth' para rotas protegidas
      const response = await fetchWithAuth(url, {
        method: method,
        body: JSON.stringify(formData), 
      });

      const data = await response.json();

      if (!data.sucesso) {
        throw new Error(data.mensagem || 'Falha ao salvar habilidade');
      }

      handleFecharModal(); // Fecha o pop-up
      fetchHabilidades(); // Atualiza a lista na tabela
      
    } catch (err) {
      setError(err.message); 
    }
  };

  // Função para Apagar uma habilidade
  const handleApagar = async (habilidadeId) => {
    if (window.confirm("Tem certeza que deseja apagar esta habilidade da base de dados?")) {
      try {
        const url = `http://127.0.0.1:5001/api/habilidades/${habilidadeId}`;
        
        // Usa 'fetchWithAuth' para a rota DELETE
        const response = await fetchWithAuth(url, {
          method: 'DELETE',
        });

        const data = await response.json();

        if (!data.sucesso) {
          throw new Error(data.mensagem || 'Falha ao apagar habilidade');
        }

        fetchHabilidades(); // Atualiza a lista na tabela

      } catch (err) {
        setError(err.message);
      }
    }
  };

  
  // --- Renderização do Componente (JSX) ---

  if (isLoading) return <p>Carregando habilidades...</p>;
  // Não mostre o erro "pendente" se for só isso
  if (error && !error.includes('pendente')) {
     return <p style={{ color: 'red' }}>Erro: {error}</p>;
  }


  return (
    <div className="gerenciador-container">
      <h2>Gerenciar Habilidades</h2>
      <button onClick={handleAbrirModalCriar} className="btn-criar">
        + Criar Nova Habilidade
      </button>

      {/* Tabela com a lista de habilidades */}
      <table className="mestre-table">
        <thead>
          <tr>
            <th>Nome</th>
            <th>Efeito</th>
            <th>Custo (Mana)</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {/* Se a lista estiver vazia, mostre uma mensagem */}
          {habilidades.length === 0 ? (
            <tr>
              <td colSpan="4">Nenhuma habilidade encontrada. (A rota GET /api/habilidades precisa ser criada no backend)</td>
            </tr>
          ) : (
            habilidades.map((habilidade) => (
              <tr key={habilidade.id}>
                <td>{habilidade.nome}</td>
                <td>{habilidade.efeito}</td>
                <td>{habilidade.custo_mana}</td>
                <td>
                  <button onClick={() => handleAbrirModalEditar(habilidade)} className="btn-editar">Editar</button>
                  <button onClick={() => handleApagar(habilidade.id)} className="btn-apagar">Apagar</button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>

      {/* --- O Modal (Pop-up) de Criar/Editar --- */}
      {isModalOpen && (
        <div className="modal-backdrop" onClick={handleFecharModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>{habilidadeEmEdicao ? "Editar Habilidade" : "Criar Nova Habilidade"}</h3>
            
            {/* Formulário de Criação/Edição */}
            <form onSubmit={handleSubmitFormulario} className="mestre-form">
              
              <div className="form-group">
                <label>Nome:</label>
                <input type="text" name="nome" value={formData.nome} onChange={handleInputChange} required />
              </div>

              <div className="form-group">
                <label>Descrição:</label>
                <input type="text" name="descricao" value={formData.descricao} onChange={handleInputChange} />
              </div>
              
              <div className="form-group">
                <label>Efeito (Obrigatório):</label>
                <input type="text" name="efeito" value={formData.efeito} onChange={handleInputChange} required />
              </div>

              <div className="form-group">
                <label>Custo de Mana:</label>
                <input type="number" name="custo_mana" value={formData.custo_mana} onChange={handleInputChange} />
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

export default GerenciarHabilidades;