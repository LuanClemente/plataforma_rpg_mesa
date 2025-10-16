// frontend/src/pages/SalasPage.jsx

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

function SalasPage() {
  // --- Estados do Componente ---
  // Guarda a lista de salas que vem da API.
  const [salas, setSalas] = useState([]);
  // Guarda o nome da nova sala que está sendo criada no formulário.
  const [novaSalaNome, setNovaSalaNome] = useState('');
  // Guarda a senha da nova sala.
  const [novaSalaSenha, setNovaSalaSenha] = useState('');
  // Guarda mensagens de feedback para o usuário.
  const [mensagem, setMensagem] = useState('');
  
  // Pega a nossa função de fetch autenticado do AuthContext.
  const { fetchWithAuth } = useAuth();

  // --- Funções de Lógica ---

  // Função para buscar a lista de salas disponíveis na API.
  const buscarSalas = async () => {
    try {
      const response = await fetchWithAuth('http://127.0.0.1:5001/api/salas');
      const data = await response.json();
      if (response.ok) {
        setSalas(data);
      } else {
        setMensagem(data.mensagem || "Erro ao buscar salas.");
      }
    } catch (error) {
      setMensagem("Erro de conexão ao buscar salas.");
    }
  };

  // useEffect para buscar as salas assim que a página carrega.
  useEffect(() => {
    buscarSalas();
  }, []);

  // useEffect para gerenciar o fundo temático da página.
  useEffect(() => {
    document.body.classList.add('salas-page-body');
    return () => {
      document.body.classList.remove('salas-page-body');
    };
  }, []);

  // Função chamada quando o formulário de "Criar Nova Sala" é enviado.
  const handleCriarSala = async (event) => {
    event.preventDefault(); // Impede o recarregamento da página.
    setMensagem('Criando sala...');

    try {
      // Prepara os dados para enviar à API.
      const payload = {
        nome: novaSalaNome,
        senha: novaSalaSenha, // Envia a senha (pode ser uma string vazia).
      };

      const response = await fetchWithAuth('http://127.0.0.1:5001/api/salas', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      setMensagem(data.mensagem);

      if (response.ok) {
        // Se a sala foi criada com sucesso, limpa os campos do formulário...
        setNovaSalaNome('');
        setNovaSalaSenha('');
        // ...e busca a lista de salas novamente para atualizar a tela!
        buscarSalas();
      }
    } catch (error) {
      setMensagem("Erro de conexão ao criar sala.");
    }
  };

  // --- Renderização do Componente ---
  return (
    <div>
      <h1>Salas de Campanha</h1>

      {/* Seção para Criar uma Nova Sala */}
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
              <p>
                {/* Mostra um cadeado se a sala tiver senha */}
                {sala.tem_senha ? 'Sala Privada  khóa' : 'Sala Pública'}
              </p>
              <div className="card-actions">
                <button 
                  className="edit-button" 
                  onClick={() => alert('A funcionalidade de entrar na sala será implementada com WebSockets!')}
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
    </div>
  );
}

export default SalasPage;