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
  // Pega a função 'fetchWithAuth' do contexto (usada para POST, PUT, DELETE)
  const { fetchWithAuth } = useAuth();

  // --- Estados (States) do Componente (sem alterações) ---
  const [habilidades, setHabilidades] = useState([]); 
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState(ESTADO_INICIAL_FORMULARIO);
  const [habilidadeEmEdicao, setHabilidadeEmEdicao] = useState(null);

  
  // --- Funções de Busca de Dados (Read) ---
  
  // Função para buscar a lista de habilidades da API
  const fetchHabilidades = async () => {
    // Log para indicar início da busca
    console.log("GerenciarHabilidades: Buscando lista de habilidades...");
    setIsLoading(true); // Inicia o estado de carregamento
    try {
      // --- [CORREÇÃO APLICADA AQUI] ---
      // Agora chamamos a rota GET /api/habilidades que criamos no backend.
      // Esta rota é pública, então usamos 'fetch' normal.
      const response = await fetch('http://127.0.0.1:5001/api/habilidades'); 
      
      // Verifica se a resposta da rede foi bem-sucedida
      if (!response.ok) {
        throw new Error('Falha ao buscar habilidades do servidor');
      }
      
      // Converte a resposta JSON em um array de objetos JavaScript
      const data = await response.json();
      
      // Salva a lista de habilidades recebida no estado do componente
      setHabilidades(data); 
      setError(null); // Limpa qualquer erro anterior
      console.log("GerenciarHabilidades: Habilidades carregadas:", data);
      // --- FIM DA CORREÇÃO ---
      
    } catch (err) {
      // Se ocorrer um erro durante a busca ou processamento
      console.error("GerenciarHabilidades: Erro ao buscar:", err);
      setError(err.message); // Salva a mensagem de erro no estado
      setHabilidades([]); // Garante que a lista fique vazia em caso de erro
    } finally {
      // Executa sempre, independentemente de sucesso ou erro
      setIsLoading(false); // Finaliza o estado de carregamento
    }
  };

  // useEffect para chamar fetchHabilidades() UMA VEZ quando o componente monta
  useEffect(() => {
    fetchHabilidades();
  }, []); // O array vazio [] garante que rode só uma vez

  
  // --- Funções de Manipulação do Formulário e Modal (sem alterações) ---
  const handleInputChange = (e) => { /* ... */ };
  const handleAbrirModalCriar = () => { /* ... */ };
  const handleAbrirModalEditar = (habilidade) => { /* ... */ };
  const handleFecharModal = () => { /* ... */ };
  const handleSubmitFormulario = async (e) => { /* ... */ };
  const handleApagar = async (habilidadeId) => { /* ... */ };

  
  // --- Renderização do Componente (JSX) ---

  // Mostra mensagem de carregamento enquanto busca os dados
  if (isLoading) return <p>Carregando habilidades...</p>;
  // Mostra mensagem de erro se a busca falhar
  if (error) return <p style={{ color: 'red' }}>Erro: {error}</p>; 


  return (
    <div className="gerenciador-container">
      {/* Título da Seção */}
      <h2>Gerenciar Habilidades</h2>
      {/* Botão para abrir o modal de criação */}
      <button onClick={handleAbrirModalCriar} className="btn-criar">
        + Criar Nova Habilidade
      </button>

      {/* Tabela para exibir a lista de habilidades */}
      <table className="mestre-table">
        {/* Cabeçalho da tabela */}
        <thead>
          <tr>
            <th>Nome</th>
            <th>Efeito</th>
            <th>Custo (Mana)</th>
            <th>Ações</th>
          </tr>
        </thead>
        {/* Corpo da tabela */}
        <tbody>
          {/* --- [MENSAGEM ATUALIZADA AQUI] --- */}
          {/* Verifica se a lista de habilidades está vazia */}
          {habilidades.length === 0 ? (
            // Se vazia, mostra uma única linha com a mensagem
            <tr>
              <td colSpan="4">Nenhuma habilidade encontrada na base de dados.</td>
            </tr>
          ) : (
            // Se não estiver vazia, mapeia cada habilidade para uma linha da tabela
            habilidades.map((habilidade) => (
              <tr key={habilidade.id}> {/* Usa o ID como chave única */}
                <td>{habilidade.nome}</td> {/* Coluna Nome */}
                <td>{habilidade.efeito}</td> {/* Coluna Efeito */}
                <td>{habilidade.custo_mana}</td> {/* Coluna Custo */}
                <td> {/* Coluna Ações com botões Editar e Apagar */}
                  <button onClick={() => handleAbrirModalEditar(habilidade)} className="btn-editar">Editar</button>
                  <button onClick={() => handleApagar(habilidade.id)} className="btn-apagar">Apagar</button>
                </td>
              </tr>
            ))
          )}
          {/* --- FIM DA ATUALIZAÇÃO --- */}
        </tbody>
      </table>

      {/* --- O Modal (Pop-up) de Criar/Editar (sem alterações no JSX) --- */}
      {/* Condicionalmente renderiza o modal se isModalOpen for true */}
      {isModalOpen && (
        <div className="modal-backdrop" onClick={handleFecharModal}> 
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>{habilidadeEmEdicao ? "Editar Habilidade" : "Criar Nova Habilidade"}</h3>
            <form onSubmit={handleSubmitFormulario} className="mestre-form">
              {/* Campos do formulário: Nome, Descrição, Efeito, Custo Mana */}
              <div className="form-group"> <label>Nome:</label> <input type="text" name="nome" value={formData.nome} onChange={handleInputChange} required /> </div>
              <div className="form-group"> <label>Descrição:</label> <input type="text" name="descricao" value={formData.descricao} onChange={handleInputChange} /> </div>
              <div className="form-group"> <label>Efeito (Obrigatório):</label> <input type="text" name="efeito" value={formData.efeito} onChange={handleInputChange} required /> </div>
              <div className="form-group"> <label>Custo de Mana:</label> <input type="number" name="custo_mana" value={formData.custo_mana} onChange={handleInputChange} /> </div>
              {/* Botões Salvar e Cancelar */}
              <div className="form-actions"> <button type="submit" className="btn-salvar">Salvar</button> <button type="button" onClick={handleFecharModal} className="btn-cancelar">Cancelar</button> </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default GerenciarHabilidades;