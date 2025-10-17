// frontend/src/components/Anotacoes.jsx

// Importa as ferramentas 'useState' e 'useEffect' do React.
import { useState, useEffect } from 'react';
// Importa o 'useParams' para ler o ID da sala da URL.
import { useParams } from 'react-router-dom';
// Importa o 'useAuth' para usar nossa função de fetch autenticado.
import { useAuth } from '../context/AuthContext';

function Anotacoes() {
  // --- Estados do Componente ---
  const [notas, setNotas] = useState(''); // Guarda o texto das anotações.
  const [status, setStatus] = useState('Pronto.'); // Mostra feedback para o usuário.
  const { fetchWithAuth } = useAuth(); // Nossa função de fetch segura.
  const { id: salaId } = useParams(); // Pega o ID da sala da URL.

  // --- Efeitos do Componente ---

  // Efeito nº 1: Busca as anotações existentes quando o componente carrega.
  useEffect(() => {
    const buscarNotas = async () => {
      setStatus('Carregando...');
      try {
        const response = await fetchWithAuth(`http://127.0.0.1:5001/api/salas/${salaId}/anotacoes`);
        const data = await response.json();
        if (response.ok) {
          setNotas(data.notas); // Preenche o textarea com as notas salvas.
          setStatus('Pronto.');
        } else {
          setStatus('Erro ao carregar.');
        }
      } catch (error) {
        console.error("Erro ao buscar anotações:", error);
        setStatus('Erro de conexão.');
      }
    };
    buscarNotas();
  }, [fetchWithAuth, salaId]); // Roda novamente se a sala ou a função de fetch mudarem.

  // --- Funções de Lógica ---

  // Função que envia as notas atuais para a API para serem salvas.
  const salvarNotas = async () => {
    // Só salva se o status não for "Salvando..." para evitar múltiplas chamadas.
    if (status === 'Salvando...') return; 
    
    setStatus('Salvando...');
    try {
      const response = await fetchWithAuth(`http://127.0.0.1:5001/api/salas/${salaId}/anotacoes`, {
        method: 'PUT',
        body: JSON.stringify({ notas: notas }), // Envia o estado 'notas' atual.
      });
      if (response.ok) {
        setStatus('Salvo!');
        setTimeout(() => setStatus('Pronto.'), 1500); // Volta para "Pronto." após um tempo.
      } else {
        setStatus('Erro ao salvar.');
      }
    } catch (error) {
      console.error("Erro ao salvar anotações:", error);
      setStatus('Erro ao salvar.');
    }
  };

  // --- Renderização do Componente (JSX) ---
  return (
    <div className="anotacoes-container">
      <h2>Anotações da Campanha</h2>
      <textarea
        value={notas}
        // 'onChange' atualiza o estado 'notas' a cada tecla digitada.
        onChange={(e) => {
          // --- CORREÇÃO APLICADA AQUI ---
          // O correto é 'e.target.value' (com 'v' minúsculo).
          setNotas(e.target.value); 
          setStatus('Digitando...'); // Atualiza o status para o usuário.
        }}
        // 'onBlur' é disparado quando o usuário clica FORA do textarea.
        // Esta é a nossa lógica de salvamento confiável.
        onBlur={salvarNotas} 
        placeholder="Anote aqui pistas, nomes de NPCs, ou seu diário de aventura..."
      />
      {/* Exibe o status atual para o usuário. */}
      <div className="anotacoes-status">{status}</div>
    </div>
  );
}

export default Anotacoes;