// frontend/src/pages/FichasPage.jsx

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

// --- Constantes de Configuração do Jogo ---
// Define os valores base para os atributos no modo avançado.
const ATRIBUTOS_BASE_AVANCADO = { "Força": 8, "Destreza": 8, "Constituição": 8, "Inteligência": 8, "Sabedoria": 8, "Carisma": 8 };
// Define quantos pontos o jogador pode distribuir.
const PONTOS_INICIAIS = 10;
// Define os atributos padrão para a criação rápida no modo básico.
const ATRIBUTOS_PADRAO_BASICO = { "Força": 10, "Destreza": 10, "Constituição": 10, "Inteligência": 10, "Sabedoria": 10, "Carisma": 10 };
// Lista de todas as perícias disponíveis para escolha (modelo D&D 5e).
const TODAS_AS_PERICIAS = [
  'Acrobacia', 'Arcanismo', 'Atletismo', 'Atuação', 'Enganação', 'Furtividade',
  'História', 'Intimidação', 'Intuição', 'Investigação', 'Lidar com Animais',
  'Medicina', 'Natureza', 'Percepção', 'Persuasão', 'Prestidigitação',
  'Religião', 'Sobrevivência'
];
// Define quantas perícias o jogador pode escolher.
const PERICIAS_A_ESCOLHER = 2;

function FichasPage() {
  // --- Estados do Componente ---
  const [fichas, setFichas] = useState([]); // Guarda a lista de fichas do usuário.
  const [mensagem, setMensagem] = useState(''); // Guarda mensagens de feedback.
  const [modoCriacao, setModoCriacao] = useState(null); // Controla qual formulário mostrar.
  const [step, setStep] = useState(1); // Controla a etapa do formulário avançado.
  // Estado para guardar os dados da ficha sendo criada. Agora inclui os novos campos.
  const [novaFicha, setNovaFicha] = useState({
    nome_personagem: '', classe: '', raca: '', antecedente: '',
    atributos: { ...ATRIBUTOS_BASE_AVANCADO },
    pericias: []
  });
  const [pontosRestantes, setPontosRestantes] = useState(PONTOS_INICIAIS);

  const { fetchWithAuth } = useAuth();

  // Função para buscar as fichas do usuário na API.
  const buscarFichas = async () => {
    try {
      const response = await fetchWithAuth('http://127.0.0.1:5001/api/fichas');
      const data = await response.json();
      if (response.ok) { setFichas(data); } else { setMensagem(data.mensagem || "Erro ao buscar fichas."); }
    } catch (error) { setMensagem("Erro de conexão ao buscar fichas."); }
  };

  // useEffect: Roda a função 'buscarFichas' uma vez, assim que a página carrega.
  useEffect(() => { buscarFichas(); }, []);

  // --- Funções de Controle dos Formulários ---

  // Atualiza o estado da 'novaFicha' quando o usuário digita nos campos de texto.
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNovaFicha(prev => ({ ...prev, [name]: value }));
  };

  // Aumenta ou diminui um atributo no modo avançado.
  const handleAtributoChange = (atributo, valor) => {
    const novoValor = novaFicha.atributos[atributo] + valor;
    if (valor > 0 && pontosRestantes <= 0) return;
    if (novoValor < ATRIBUTOS_BASE_AVANCADO[atributo]) return;
    setNovaFicha(prev => ({ ...prev, atributos: { ...prev.atributos, [atributo]: novoValor } }));
    setPontosRestantes(prev => prev - valor);
  };
  
  // Lida com a seleção de perícias (checkboxes).
  const handlePericiaChange = (pericia) => {
    setNovaFicha(prev => {
      const periciasAtuais = prev.pericias;
      // Se a perícia já estiver selecionada, remove-a (desmarcar).
      if (periciasAtuais.includes(pericia)) {
        return { ...prev, pericias: periciasAtuais.filter(p => p !== pericia) };
      } 
      // Se ainda houver espaço para escolher mais perícias, adiciona-a.
      else if (periciasAtuais.length < PERICIAS_A_ESCOLHER) {
        return { ...prev, pericias: [...periciasAtuais, pericia] };
      }
      // Se o limite já foi atingido, não faz nada.
      return prev;
    });
  };

  // Reseta todo o estado do formulário para o estado inicial.
  const resetarFormulario = () => {
    setModoCriacao(null);
    setStep(1);
    // Garante que os novos campos também sejam resetados.
    setNovaFicha({
      nome_personagem: '', classe: '', raca: '', antecedente: '',
      atributos: { ...ATRIBUTOS_BASE_AVANCADO },
      pericias: []
    });
    setPontosRestantes(PONTOS_INICIAIS);
    setMensagem('');
    buscarFichas(); // Atualiza a lista de fichas na tela.
  };

  // Função central que envia os dados da nova ficha para a API.
  const handleCriarFichaAPI = async (fichaParaEnviar) => {
    setMensagem('Criando ficha...');
    try {
      const response = await fetchWithAuth('http://127.0.0.1:5001/api/fichas', {
        method: 'POST',
        body: JSON.stringify(fichaParaEnviar),
      });
      const data = await response.json();
      setMensagem(data.mensagem);
      if (response.ok) { resetarFormulario(); }
    } catch (error) { setMensagem("Erro de conexão ao criar ficha."); }
  };

  // Função chamada ao submeter o formulário BÁSICO.
  const handleSubmitBasico = (event) => {
    event.preventDefault();
    const fichaParaEnviar = {
      nome_personagem: novaFicha.nome_personagem,
      classe: novaFicha.classe,
      raca: 'N/A', // Envia valores padrão para os novos campos
      antecedente: 'N/A',
      atributos: ATRIBUTOS_PADRAO_BASICO,
      pericias: [],
    };
    handleCriarFichaAPI(fichaParaEnviar);
  };
  
  // Função chamada ao submeter o formulário AVANÇADO.
  const handleSubmitAvancado = (event) => {
    event.preventDefault();
    if (pontosRestantes !== 0) {
      setMensagem(`Você ainda precisa distribuir ${pontosRestantes} pontos!`);
      return;
    }
    if (novaFicha.pericias.length !== PERICIAS_A_ESCOLHER) {
      setMensagem(`Você deve escolher exatamente ${PERICIAS_A_ESCOLHER} perícias.`);
      return;
    }
    handleCriarFichaAPI(novaFicha);
  };

  // --- Renderização do Componente (a parte visual) ---
  return (
    <div>
      <h1>Minhas Fichas</h1>
      
      <div className="login-container" style={{ maxWidth: '600px', marginBottom: '2rem' }}>
        <h2>Criar Nova Ficha</h2>
        
        {!modoCriacao && (
          <div className="mode-selection">
            <p>Como você deseja criar sua ficha?</p>
            <button onClick={() => setModoCriacao('basico')} className="login-button">Modo Básico</button>
            <button onClick={() => setModoCriacao('avancado')} className="login-button">Modo Avançado</button>
          </div>
        )}

        {modoCriacao === 'basico' && (
          <form onSubmit={handleSubmitBasico} className="login-form">
            <div className="form-group"><label>Nome do Personagem</label><input type="text" name="nome_personagem" value={novaFicha.nome_personagem} onChange={handleInputChange} required /></div>
            <div className="form-group"><label>Classe</label><input type="text" name="classe" value={novaFicha.classe} onChange={handleInputChange} required /></div>
            <button type="submit" className="login-button">Criar Ficha Rápida</button>
            <button type="button" className="login-button" style={{backgroundColor: '#555', marginTop: '1rem'}} onClick={resetarFormulario}>Voltar</button>
          </form>
        )}

        {modoCriacao === 'avancado' && (
          <form onSubmit={handleSubmitAvancado} className="login-form">
            {step === 1 && (
              <>
                <h3>Etapa 1: Identidade</h3>
                <div className="form-group"><label>Nome do Personagem</label><input type="text" name="nome_personagem" value={novaFicha.nome_personagem} onChange={handleInputChange} required /></div>
                <div className="form-group"><label>Classe</label><input type="text" name="classe" value={novaFicha.classe} onChange={handleInputChange} required /></div>
                <button type="button" className="login-button" onClick={() => setStep(2)}>Próximo</button>
              </>
            )}
            {step === 2 && (
              <>
                <h3>Etapa 2: Origem</h3>
                <div className="form-group"><label>Raça</label><input type="text" name="raca" value={novaFicha.raca} onChange={handleInputChange} required /></div>
                <div className="form-group"><label>Antecedente</label><input type="text" name="antecedente" value={novaFicha.antecedente} onChange={handleInputChange} required /></div>
                <div style={{display: 'flex', gap: '1rem', marginTop: '1rem'}}><button type="button" className="login-button" style={{backgroundColor: '#555'}} onClick={() => setStep(1)}>Voltar</button><button type="button" className="login-button" onClick={() => setStep(3)}>Próximo</button></div>
              </>
            )}
            {step === 3 && (
              <>
                <h3>Etapa 3: Atributos</h3>
                <p className="feedback-message">Pontos Restantes: {pontosRestantes}</p>
                {Object.keys(novaFicha.atributos).map(attr => (
                  <div key={attr} className="attribute-row"><label>{attr}</label><div><button type="button" onClick={() => handleAtributoChange(attr, -1)}>-</button><span>{novaFicha.atributos[attr]}</span><button type="button" onClick={() => handleAtributoChange(attr, 1)}>+</button></div></div>
                ))}
                <div style={{display: 'flex', gap: '1rem', marginTop: '1rem'}}><button type="button" className="login-button" style={{backgroundColor: '#555'}} onClick={() => setStep(2)}>Voltar</button><button type="button" className="login-button" onClick={() => setStep(4)}>Próximo</button></div>
              </>
            )}
            {step === 4 && (
              <>
                <h3>Etapa 4: Perícias</h3>
                <p>Escolha {PERICIAS_A_ESCOLHER} perícias.</p>
                <div className="skills-grid">
                  {TODAS_AS_PERICIAS.map(pericia => (
                    <div key={pericia} className="skill-checkbox"><input type="checkbox" id={pericia} checked={novaFicha.pericias.includes(pericia)} onChange={() => handlePericiaChange(pericia)} /><label htmlFor={pericia}>{pericia}</label></div>
                  ))}
                </div>
                <div style={{display: 'flex', gap: '1rem', marginTop: '1rem'}}><button type="button" className="login-button" style={{backgroundColor: '#555'}} onClick={() => setStep(3)}>Voltar</button><button type="submit" className="login-button">Criar Personagem</button></div>
              </>
            )}
            <button type="button" className="login-button" style={{backgroundColor: '#555', marginTop: '1rem'}} onClick={resetarFormulario}>Cancelar</button>
          </form>
        )}
        
        {mensagem && <p className="feedback-message">{mensagem}</p>}
      </div>

      <h2>Fichas Salvas</h2>
      <div className="monster-list">
        {fichas.length > 0 ? (
          fichas.map(ficha => (
            <div key={ficha.id} className="monster-card">
              <h2>{ficha.nome_personagem}</h2>
              <p>Classe: {ficha.classe}</p>
              <p>Nível: {ficha.nivel}</p>
            </div>
          ))
        ) : ( <p>Você ainda não tem nenhuma ficha. Crie uma acima!</p> )}
      </div>
    </div>
  );
}

export default FichasPage;