// frontend/src/pages/SalasPage.jsx

// Importa as ferramentas necessárias do React e do React Router.
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
// Importa nossos componentes de modal.
import PasswordModal from '../components/PasswordModal';
import CharacterSelectionModal from '../components/CharacterSelectionModal';

function SalasPage() {
  // --- Estados do Componente ---
  const navigate = useNavigate();
  const { fetchWithAuth } = useAuth();
  
  const [salas, setSalas] = useState([]); // Guarda a lista de salas.
  const [fichas, setFichas] = useState([]); // Guarda a lista de fichas do usuário.
  const [novaSalaNome, setNovaSalaNome] = useState(''); // Controla o campo de nome da nova sala.
  const [novaSalaSenha, setNovaSalaSenha] = useState(''); // Controla o campo de senha da nova sala.
  const [mensagem, setMensagem] = useState(''); // Guarda mensagens de feedback.

  // Estados para controlar os modais.
  const [isCharModalOpen, setIsCharModalOpen] = useState(false);
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [selectedSala, setSelectedSala] = useState(null);

  // --- Funções de Lógica ---
  
  // useEffect para buscar os dados iniciais (salas e fichas) quando a página carrega.
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [salasRes, fichasRes] = await Promise.all([
          fetchWithAuth('http://127.0.0.1:5001/api/salas'),
          fetchWithAuth('http://127.0.0.1:5001/api/fichas')
        ]);
        if (salasRes.ok) setSalas(await salasRes.json());
        if (fichasRes.ok) setFichas(await fichasRes.json());
      } catch (error) {
        setMensagem("Erro de conexão ao carregar dados da página.");
      }
    };
    fetchData();
  }, [fetchWithAuth]);

  // useEffect para gerenciar o fundo temático da página.
  useEffect(() => {
    document.body.classList.add('salas-page-body');
    return () => { document.body.classList.remove('salas-page-body'); };
  }, []);

  // Função para criar uma nova sala, chamada pelo formulário.
  const handleCriarSala = async (event) => {
    event.preventDefault();
    setMensagem('Criando sala...');
    try {
      const response = await fetchWithAuth('http://127.0.0.1:5001/api/salas', {
        method: 'POST',
        body: JSON.stringify({ nome: novaSalaNome, senha: novaSalaSenha }),
      });
      const data = await response.json();
      setMensagem(data.mensagem);
      if (response.ok) {
        setNovaSalaNome('');
        setNovaSalaSenha('');
        // Após criar, busca a lista de salas novamente para atualizar a tela.
        const salasRes = await fetchWithAuth('http://127.0.0.1:5001/api/salas');
        if (salasRes.ok) setSalas(await salasRes.json());
      }
    } catch (error) { setMensagem("Erro de conexão ao criar sala."); }
  };

  // --- FLUXO PARA ENTRAR NA SALA ---

  // 1. Chamado ao clicar no botão "Entrar". Abre o modal de seleção de personagem.
  const handleEntrarSalaClick = (sala) => {
    setSelectedSala(sala);
    setIsCharModalOpen(true);
  };

  // 2. Chamado QUANDO um personagem é selecionado no modal.
  const handleCharacterSelect = (ficha) => {
    setIsCharModalOpen(false);
    sessionStorage.setItem('selectedFichaId', ficha.id);

    if (selectedSala.tem_senha) {
      setIsPasswordModalOpen(true); // Se a sala tem senha, abre o modal de senha.
    } else {
      navigate(`/salas/${selectedSala.id}`); // Se for pública, entra direto.
    }
  };

  // 3. Chamado QUANDO a senha é submetida no modal de senha.
  const handlePasswordSubmit = async (senhaDigitada) => {
    if (!selectedSala) return;
    try {
      const response = await fetchWithAuth('http://127.0.0.1:5001/api/salas/verificar-senha', {
        method: 'POST',
        body: JSON.stringify({ sala_id: selectedSala.id, senha: senhaDigitada }),
      });
      const data = await response.json();
      if (data.sucesso) {
        setIsPasswordModalOpen(false);
        navigate(`/salas/${selectedSala.id}`);
      } else {
        alert(data.mensagem || "Senha incorreta.");
      }
    } catch (error) {
      alert("Erro de conexão ao verificar a senha.");
    }
  };

  // --- Renderização do Componente ---
  return (
    <div>
      <h1>Salas de Campanha</h1>

      {/* --- SEÇÃO PARA CRIAR UMA NOVA SALA (RE-ADICIONADA) --- */}
      <div className="login-container" style={{ maxWidth: '600px', marginBottom: '2rem' }}>
        <h2>Fundar uma Nova Taverna</h2>
        <form onSubmit={handleCriarSala} className="login-form">
          <div className="form-group">
            <label htmlFor="novaSalaNome">Nome da Campanha</label>
            <input 
              type="text" 
              id="novaSalaNome" 
              value={novaSalaNome}
              onChange={(e) => setNovaSalaNome(e.target.value)}
              required 
            />
          </div>
          <div className="form-group">
            <label htmlFor="novaSalaSenha">Senha (opcional)</label>
            <input 
              type="password" 
              id="novaSalaSenha" 
              value={novaSalaSenha}
              onChange={(e) => setNovaSalaSenha(e.target.value)}
            />
          </div>
          <button type="submit" className="login-button">Criar Sala</button>
        </form>
        {mensagem && <p className="feedback-message">{mensagem}</p>}
      </div>

      {/* Seção para Listar as Salas Disponíveis */}
      <h2>Tavernas Abertas</h2>
      <div className="monster-list">
        {salas.length > 0 ? (
          salas.map(sala => (
            <div key={sala.id} className="monster-card">
              <h3>{sala.nome}</h3>
              <p>Mestre: {sala.mestre_nome}</p>
              <p>{sala.tem_senha ? 'Sala Privada 🔒' : 'Sala Pública'}</p>
              <div className="card-actions">
                <button 
                  className="edit-button" 
                  onClick={() => handleEntrarSalaClick(sala)}
                >
                  Entrar
                </button>
              </div>
            </div>
          ))
        ) : (
          <p>Nenhuma taverna aberta no momento. Que tal criar a sua?</p>
        )}
      </div>
      
      {/* Renderização condicional dos nossos modais */}
      <CharacterSelectionModal
        isOpen={isCharModalOpen}
        onClose={() => setIsCharModalOpen(false)}
        fichas={fichas}
        onSelect={handleCharacterSelect}
      />
      
      <PasswordModal
        isOpen={isPasswordModalOpen}
        onClose={() => setIsPasswordModalOpen(false)}
        onSubmit={handlePasswordSubmit}
      />
    </div>
  );
}

export default SalasPage;