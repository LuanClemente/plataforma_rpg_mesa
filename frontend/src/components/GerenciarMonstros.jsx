// frontend/src/components/GerenciarMonstros.jsx

import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

// Define o estado inicial (em branco) para o formulário de um novo monstro
const ESTADO_INICIAL_FORMULARIO = {
  nome: '',
  vida_maxima: 10,
  ataque_bonus: 0,
  dano_dado: '1d6',
  defesa: 10,
  xp_oferecido: 50,
  ouro_drop: 10,
};

function GerenciarMonstros() {
  // Pega a função 'fetchWithAuth' do contexto para fazermos chamadas protegidas
  const { fetchWithAuth } = useAuth();

  // --- Estados (States) do Componente ---
  
  // Armazena a lista de monstros que vem do backend
  const [monstros, setMonstros] = useState([]);
  
  // Controla se a página está carregando os dados
  const [isLoading, setIsLoading] = useState(true);
  
  // Armazena mensagens de erro, se houver
  const [error, setError] = useState(null);
  
  // Controla a visibilidade do modal (pop-up) de criar/editar
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Armazena os dados do monstro que está sendo editado ou criado
  const [formData, setFormData] = useState(ESTADO_INICIAL_FORMULARIO);
  
  // Se 'monstroEmEdicao' for nulo, o modal está em modo "Criar".
  // Se tiver um objeto de monstro, está em modo "Editar".
  const [monstroEmEdicao, setMonstroEmEdicao] = useState(null);

  
  // --- Funções de Busca de Dados (Read) ---
  
  // Função para buscar a lista de monstros da API
  const fetchMonstros = async () => {
    setIsLoading(true); // Começa o carregamento
    try {
      // Usamos 'fetch' normal aqui, pois a rota GET é pública (Bestiário)
      // (Se a sua rota GET /api/monstros for protegida, troque 'fetch' por 'fetchWithAuth')
      const response = await fetch('http://127.0.0.1:5003/api/monstros');
      if (!response.ok) {
        throw new Error('Falha ao buscar monstros');
      }
      const data = await response.json();
      setMonstros(data); // Salva a lista de monstros no estado
      setError(null); // Limpa erros antigos
    } catch (err) {
      setError(err.message); // Salva a mensagem de erro no estado
    } finally {
      setIsLoading(false); // Termina o carregamento (com sucesso ou erro)
    }
  };

  // 'useEffect' para rodar a função 'fetchMonstros' UMA VEZ quando o componente carregar
  useEffect(() => {
    fetchMonstros();
  }, []); // O array vazio [] garante que isso só rode no "mount" (carregamento)

  
  // --- Funções de Manipulação do Formulário e Modal ---
  
  // Atualiza o estado 'formData' conforme o usuário digita nos inputs
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  // Abre o modal em modo "Criar Novo"
  const handleAbrirModalCriar = () => {
    setMonstroEmEdicao(null); // Garante que não estamos editando
    setFormData(ESTADO_INICIAL_FORMULARIO); // Limpa o formulário
    setIsModalOpen(true); // Abre o pop-up
  };

  // Abre o modal em modo "Editar"
  const handleAbrirModalEditar = (monstro) => {
    setMonstroEmEdicao(monstro); // Define qual monstro estamos editando
    setFormData(monstro); // Preenche o formulário com os dados dele
    setIsModalOpen(true); // Abre o pop-up
  };

  // Fecha o modal e reseta tudo
  const handleFecharModal = () => {
    setIsModalOpen(false);
    setMonstroEmEdicao(null);
    setFormData(ESTADO_INICIAL_FORMULARIO);
  };

  
  // --- Funções de Ação da API (Create, Update, Delete) ---

  // Função chamada quando o formulário do modal é enviado
  const handleSubmitFormulario = async (e) => {
    e.preventDefault(); // Impede o recarregamento da página

    // Define a URL e o Método baseado se estamos editando ou criando
    const isEditing = monstroEmEdicao !== null;
    const url = isEditing 
      ? `http://127.0.0.1:5003/api/monstros/${monstroEmEdicao.id}` // URL de Update
      : `http://127.0.0.1:5003/api/monstros`; // URL de Create
      
    const method = isEditing ? 'PUT' : 'POST';

    try {
      // Usamos 'fetchWithAuth' pois Criar e Editar são rotas protegidas de Mestre
      const response = await fetchWithAuth(url, {
        method: method,
        body: JSON.stringify(formData), // Envia os dados do formulário como JSON
      });

      const data = await response.json();

      if (!data.sucesso) {
        // Se a API retornar um erro (ex: nome duplicado)
        throw new Error(data.mensagem || 'Falha ao salvar monstro');
      }

      // Se deu tudo certo:
      handleFecharModal(); // Fecha o pop-up
      fetchMonstros(); // Re-busca a lista de monstros para mostrar o item novo/atualizado
      
    } catch (err) {
      setError(err.message); // Mostra o erro no topo da página
      // (Poderíamos ter um estado de erro só para o modal também)
    }
  };

  // Função para Apagar um monstro
  const handleApagar = async (monstroId) => {
    // Pede confirmação antes de apagar
    if (window.confirm("Tem certeza que deseja apagar este monstro da base de dados?")) {
      try {
        const url = `http://127.0.0.1:5003/api/monstros/${monstroId}`;
        
        // Usa 'fetchWithAuth' pois Apagar é uma rota protegida
        const response = await fetchWithAuth(url, {
          method: 'DELETE',
        });

        const data = await response.json();

        if (!data.sucesso) {
          throw new Error(data.mensagem || 'Falha ao apagar monstro');
        }

        // Se deu certo, re-busca a lista de monstros para remover o item apagado
        fetchMonstros();

      } catch (err) {
        setError(err.message);
      }
    }
  };

  
  // --- Renderização do Componente (JSX) ---

  // Mostra mensagens de Carregamento ou Erro
  if (isLoading) return <p>Carregando monstros...</p>;
  if (error) return <p style={{ color: 'red' }}>Erro: {error}</p>;

  return (
    <div className="gerenciador-container">
      <h2>Gerenciar Monstros</h2>
      <button onClick={handleAbrirModalCriar} className="btn-criar">
        + Criar Novo Monstro
      </button>

      {/* Tabela com a lista de monstros */}
      <table className="mestre-table">
        <thead>
          <tr>
            <th>Nome</th>
            <th>Vida</th>
            <th>Defesa</th>
            <th>XP</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {monstros.map((monstro) => (
            <tr key={monstro.id}>
              <td>{monstro.nome}</td>
              <td>{monstro.vida || monstro.vida_maxima}</td> {/* (vida ou vida_maxima) */}
              <td>{monstro.defesa}</td>
              <td>{monstro.xp || monstro.xp_oferecido}</td> {/* (xp ou xp_oferecido) */}
              <td>
                <button onClick={() => handleAbrirModalEditar(monstro)} className="btn-editar">Editar</button>
                <button onClick={() => handleApagar(monstro.id)} className="btn-apagar">Apagar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* --- O Modal (Pop-up) de Criar/Editar --- */}
      {/* Ele só é renderizado se 'isModalOpen' for true */}
      {isModalOpen && (
        // O fundo escurecido
        <div className="modal-backdrop" onClick={handleFecharModal}>
          {/* O conteúdo do modal (parar a propagação do clique) */}
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>{monstroEmEdicao ? "Editar Monstro" : "Criar Novo Monstro"}</h3>
            
            {/* Formulário de Criação/Edição */}
            <form onSubmit={handleSubmitFormulario} className="mestre-form">
              {/* Agrupador de Campos */}
              <div className="form-group">
                <label>Nome:</label>
                <input type="text" name="nome" value={formData.nome} onChange={handleInputChange} required />
              </div>
              
              {/* Agrupador de Campos em linha */}
              <div className="form-row">
                <div className="form-group">
                  <label>Vida Máxima:</label>
                  <input type="number" name="vida_maxima" value={formData.vida_maxima} onChange={handleInputChange} />
                </div>
                <div className="form-group">
                  <label>Defesa (CA):</label>
                  <input type="number" name="defesa" value={formData.defesa} onChange={handleInputChange} />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Bônus de Ataque:</label>
                  <input type="number" name="ataque_bonus" value={formData.ataque_bonus} onChange={handleInputChange} />
                </div>
                <div className="form-group">
                  <label>Dado de Dano:</label>
                  <input type="text" name="dano_dado" value={formData.dano_dado} onChange={handleInputChange} />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>XP Oferecido:</label>
                  <input type="number" name="xp_oferecido" value={formData.xp_oferecido} onChange={handleInputChange} />
                </div>
                <div className="form-group">
                  <label>Ouro (Drop):</label>
                  <input type="number" name="ouro_drop" value={formData.ouro_drop} onChange={handleInputChange} />
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

export default GerenciarMonstros;
