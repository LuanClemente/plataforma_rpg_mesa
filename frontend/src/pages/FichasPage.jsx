// frontend/src/pages/FichasPage.jsx
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

function FichasPage() {
  // Estados para guardar a lista de fichas, e os dados do novo formulário.
  const [fichas, setFichas] = useState([]);
  const [nomePersonagem, setNomePersonagem] = useState('');
  const [classe, setClasse] = useState('');
  const [mensagem, setMensagem] = useState('');

  // Pegamos nossa nova função de fetch autenticado do contexto.
  const { fetchWithAuth } = useAuth();

  // Função para buscar as fichas do usuário na API.
  const buscarFichas = async () => {
    try {
      const response = await fetchWithAuth('http://127.0.0.1:5001/api/fichas');
      const data = await response.json();
      if (response.ok) {
        setFichas(data);
      } else {
        setMensagem(data.mensagem || "Erro ao buscar fichas.");
      }
    } catch (error) {
      setMensagem("Erro de conexão ao buscar fichas.");
    }
  };

  // useEffect para buscar as fichas assim que a página carrega.
  useEffect(() => {
    buscarFichas();
  }, []); // O array vazio garante que isso rode só uma vez.

  // Função para lidar com a criação de uma nova ficha.
  const handleCriarFicha = async (event) => {
    event.preventDefault();
    setMensagem('');
    try {
      const response = await fetchWithAuth('http://127.0.0.1:5001/api/fichas', {
        method: 'POST',
        body: JSON.stringify({ nome_personagem: nomePersonagem, classe: classe }),
      });
      const data = await response.json();
      setMensagem(data.mensagem);

      if (response.ok) {
        // Se a ficha foi criada, limpa os campos e busca a lista de fichas atualizada.
        setNomePersonagem('');
        setClasse('');
        buscarFichas(); // Atualiza a lista de fichas na tela!
      }
    } catch (error) {
      setMensagem("Erro de conexão ao criar ficha.");
    }
  };

  return (
    <div>
      <h1>Minhas Fichas</h1>

      {/* Formulário para criar nova ficha */}
      <div className="login-container" style={{ maxWidth: '600px', marginBottom: '2rem' }}>
        <h2>Criar Nova Ficha</h2>
        <form onSubmit={handleCriarFicha} className="login-form">
          <div className="form-group">
            <label htmlFor="nomePersonagem">Nome do Personagem</label>
            <input type="text" id="nomePersonagem" value={nomePersonagem} onChange={(e) => setNomePersonagem(e.target.value)} required />
          </div>
          <div className="form-group">
            <label htmlFor="classe">Classe</label>
            <input type="text" id="classe" value={classe} onChange={(e) => setClasse(e.target.value)} required />
          </div>
          <button type="submit" className="login-button">Criar Personagem</button>
        </form>
        {mensagem && <p className="feedback-message">{mensagem}</p>}
      </div>

      {/* Lista de fichas existentes */}
      <h2>Fichas Salvas</h2>
      <div className="monster-list"> {/* Reutilizando o estilo da lista de monstros */}
        {fichas.length > 0 ? (
          fichas.map(ficha => (
            <div key={ficha.id} className="monster-card"> {/* Reutilizando o estilo das cartas */}
              <h2>{ficha.nome_personagem}</h2>
              <p>Classe: {ficha.classe}</p>
              <p>Nível: {ficha.nivel}</p>
            </div>
          ))
        ) : (
          <p>Você ainda não tem nenhuma ficha. Crie uma acima!</p>
        )}
      </div>
    </div>
  );
}

export default FichasPage;