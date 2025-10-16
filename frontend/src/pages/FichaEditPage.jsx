// frontend/src/pages/FichaEditPage.jsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function FichaEditPage() {
  const { id } = useParams(); 
  const navigate = useNavigate();
  const { fetchWithAuth } = useAuth();

  const [ficha, setFicha] = useState(null);
  const [mensagem, setMensagem] = useState('');

  // useEffect para buscar os dados da ficha na API.
  useEffect(() => {
    const buscarFicha = async () => {
      try {
        const response = await fetchWithAuth(`http://127.0.0.1:5001/api/fichas/${id}`);
        const data = await response.json();
        if (response.ok) {
          setFicha(data);
        } else {
          setMensagem(data.mensagem || "Erro ao buscar dados da ficha.");
        }
      } catch (error) {
        setMensagem("Erro de conexão.");
      }
    };
    buscarFicha();
  }, [id, fetchWithAuth]);

  // --- NOVO CÓDIGO ADICIONADO ---
  // Este useEffect é responsável por gerenciar o estilo do <body>.
  useEffect(() => {
    // Adiciona a classe quando o componente FichaEditPage é montado.
    document.body.classList.add('edit-ficha-page-body');
    // A função de limpeza remove a classe quando o componente é desmontado.
    return () => {
      document.body.classList.remove('edit-ficha-page-body');
    };
  }, []); // O array vazio garante que o efeito só rode na montagem e desmontagem.

  // Função para lidar com mudanças nos inputs do formulário.
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFicha(prev => ({ ...prev, [name]: value }));
  };
  
  // Função para salvar as alterações.
  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await fetchWithAuth(`http://127.0.0.1:5001/api/fichas/${id}`, {
        method: 'PUT',
        body: JSON.stringify(ficha),
      });
      const data = await response.json();
      setMensagem(data.mensagem);
      if (response.ok) {
        setTimeout(() => navigate('/fichas'), 1500);
      }
    } catch (error) {
      setMensagem("Erro de conexão ao salvar.");
    }
  };

  // Se a ficha ainda não foi carregada, mostra uma mensagem de "Carregando...".
  if (!ficha) {
    return <div>Carregando ficha...</div>;
  }

  // O JSX do formulário (sem alterações na estrutura).
  return (
    <div className="login-container" style={{ maxWidth: '600px' }}>
      <h1>Editando: {ficha.nome_personagem}</h1>
      <form onSubmit={handleSubmit} className="login-form">
        <div className="form-group">
          <label>Nome do Personagem</label>
          <input type="text" name="nome_personagem" value={ficha.nome_personagem} onChange={handleInputChange} required />
        </div>
        <div className="form-group">
          <label>Classe</label>
          <input type="text" name="classe" value={ficha.classe} onChange={handleInputChange} required />
        </div>
        <div className="form-group">
          <label>Raça</label>
          <input type="text" name="raca" value={ficha.raca} onChange={handleInputChange} required />
        </div>
        <div className="form-group">
          <label>Antecedente</label>
          <input type="text" name="antecedente" value={ficha.antecedente} onChange={handleInputChange} required />
        </div>
        <div className="form-group">
          <label>Nível</label>
          <input type="number" name="nivel" value={ficha.nivel} onChange={handleInputChange} required />
        </div>
        {/* A edição de atributos e perícias pode ser adicionada aqui no futuro */}
        
        <button type="submit" className="login-button">Salvar Alterações</button>
        <button type="button" className="login-button" style={{backgroundColor: '#555', marginTop: '1rem'}} onClick={() => navigate('/fichas')}>Cancelar</button>
      </form>
      {mensagem && <p className="feedback-message">{mensagem}</p>}
    </div>
  );
}

export default FichaEditPage;