// frontend/src/pages/SalasPage.jsx

// Importa as ferramentas necessárias do React e do React Router.
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
// 1. Importa nosso novo componente de modal customizado.
import PasswordModal from '../components/PasswordModal';

function SalasPage() {
  // --- Estados do Componente ---
  const navigate = useNavigate();
  const { fetchWithAuth } = useAuth();
  
  const [salas, setSalas] = useState([]);
  const [novaSalaNome, setNovaSalaNome] = useState('');
  const [novaSalaSenha, setNovaSalaSenha] = useState('');
  const [mensagem, setMensagem] = useState('');

  // --- Novos estados para controlar o modal ---
  const [isModalOpen, setIsModalOpen] = useState(false); // Controla se o modal está visível.
  const [selectedSala, setSelectedSala] = useState(null); // Guarda a sala que o usuário tentou entrar.
  
  // --- Funções de Lógica ---
  
  // Função para buscar a lista de salas disponíveis na API.
  const buscarSalas = async () => {
    try {
      const response = await fetchWithAuth('http://127.0.0.1:5001/api/salas');
      const data = await response.json();
      if (response.ok) { setSalas(data); } else { setMensagem(data.mensagem || "Erro ao buscar salas."); }
    } catch (error) { setMensagem("Erro de conexão ao buscar salas."); }
  };

  // useEffect para buscar as salas uma vez quando a página carrega.
  useEffect(() => { buscarSalas(); }, []);

  // useEffect para gerenciar o fundo temático da página.
  useEffect(() => {
    document.body.classList.add('salas-page-body');
    return () => { document.body.classList.remove('salas-page-body'); };
  }, []);

  // Função para criar uma nova sala.
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
        buscarSalas();
      }
    } catch (error) { setMensagem("Erro de conexão ao criar sala."); }
  };

  // --- FUNÇÃO ATUALIZADA PARA USAR O MODAL ---
  const handleEntrarSalaClick = (sala) => {
    // Se a sala NÃO tem senha, navega diretamente.
    if (!sala.tem_senha) {
      navigate(`/salas/${sala.id}`);
      return;
    }
    // Se a sala TEM senha, em vez de um prompt, nós guardamos a sala selecionada...
    setSelectedSala(sala);
    // ...e abrimos o nosso modal customizado.
    setIsModalOpen(true);
  };

  // --- NOVA FUNÇÃO PARA PROCESSAR A SENHA DO MODAL ---
  const handleModalSubmit = async (senhaDigitada) => {
    // Se não houver uma sala selecionada, não faz nada (segurança).
    if (!selectedSala) return;

    try {
      // Verifica a senha com o backend.
      const response = await fetchWithAuth('http://127.0.0.1:5001/api/salas/verificar-senha', {
        method: 'POST',
        body: JSON.stringify({ sala_id: selectedSala.id, senha: senhaDigitada }),
      });
      const data = await response.json();

      if (data.sucesso) {
        // Se a senha estiver correta, fecha o modal e navega para a página da sala.
        setIsModalOpen(false);
        navigate(`/salas/${selectedSala.id}`);
      } else {
        // Se estiver incorreta, mostra um alerta para o usuário.
        alert(data.mensagem || "Senha incorreta.");
      }
    } catch (error) {
      alert("Erro de conexão ao verificar a senha.");
    }
  };

  // --- Renderização do Componente (a parte visual) ---
  return (
    <div>
      <h1>Salas de Campanha</h1>

      {/* Seção para Criar uma Nova Sala */}
      <div className="login-container" style={{ maxWidth: '600px', marginBottom: '2rem' }}>
        <h2>Fundar uma Nova Taverna</h2>
        <form onSubmit={handleCriarSala} className="login-form">
          <div className="form-group"><label htmlFor="novaSalaNome">Nome da Campanha</label><input type="text" id="novaSalaNome" value={novaSalaNome} onChange={(e) => setNovaSalaNome(e.target.value)} required /></div>
          <div className="form-group"><label htmlFor="novaSalaSenha">Senha (opcional)</label><input type="password" id="novaSalaSenha" value={novaSalaSenha} onChange={(e) => setNovaSalaSenha(e.target.value)} /></div>
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
                {/* O onClick agora chama nossa nova função que controla o modal */}
                <button 
                  className="edit-button" 
                  onClick={() => handleEntrarSalaClick(sala)}
                >
                  Entrar
                </button>
              </div>
            </div>
          ))
        ) : ( <p>Nenhuma taverna aberta no momento. Que tal criar a sua?</p> )}
      </div>
      
      {/* --- RENDERIZAÇÃO CONDICIONAL DO NOSSO MODAL --- */}
      {/* O modal só é renderizado no HTML se 'isModalOpen' for true. */}
      <PasswordModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)} // Função para fechar o modal.
        onSubmit={handleModalSubmit} // Função para ser chamada quando a senha é confirmada.
      />
    </div>
  );
}

export default SalasPage;