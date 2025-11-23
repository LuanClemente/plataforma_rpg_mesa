// frontend/src/pages/HomePage.jsx

// Importa as ferramentas 'useState' e 'useEffect' do React.
import { useState, useEffect } from 'react';
// Importa nosso componente reutilizável para exibir cada monstro.
import MonsterCard from '../components/MonsterCard';

// Define o componente da página Home (que funciona como nosso Bestiário).
function HomePage() {
  // Cria uma "caixa" (estado) chamada 'monstros' para guardar a lista de monstros que virá da API.
  // Ela começa como uma lista vazia: [].
  const [monstros, setMonstros] = useState([]);

  // Este primeiro useEffect é responsável por buscar os dados da API.
  useEffect(() => {
    // A função 'fetch' faz a requisição para o nosso backend.
    fetch('http://127.0.0.1:5003/api/monstros')
      // A primeira resposta é o objeto da requisição; usamos .json() para extrair os dados.
      .then(response => response.json())
      // Agora que temos os dados, usamos 'setMonstros' para guardá-los no nosso estado.
      .then(data => setMonstros(data))
      // Se ocorrer um erro de rede, ele será capturado e exibido no console.
      .catch(error => console.error("Erro ao buscar monstros:", error));
  }, []); // O array vazio '[]' garante que este efeito rode apenas uma vez, quando a página carrega.

  // --- LÓGICA ADICIONADA PARA O FUNDO DE IMAGEM ---
  // Este segundo useEffect é responsável por gerenciar o estilo do <body>.
  useEffect(() => {
    // Quando o componente HomePage é "montado" (aparece na tela),
    // nós adicionamos a classe CSS 'bestiary-page-body' ao <body> do documento.
    document.body.classList.add('bestiary-page-body');

    // O 'return' de um useEffect é uma "função de limpeza".
    // Ela é executada quando o componente é "desmontado" (quando o usuário navega para outra página).
    return () => {
      // Nós removemos a classe para que as outras páginas voltem a ter o fundo padrão.
      document.body.classList.remove('bestiary-page-body');
    };
  }, []); // O array vazio também garante que isso só aconteça na montagem e desmontagem.

  // O 'return' define o que o componente vai renderizar na tela em JSX.
  return (
    <div>
      <h1>Bestiário da Campanha</h1>
      <div className="monster-list">
        {/* Usamos o método '.map()' para transformar cada objeto 'monstro' na nossa lista
            em um componente <MonsterCard />. */}
        {monstros.map(monstro => (
          // A propriedade 'key' é essencial para o React otimizar listas.
          // CORREÇÃO: Usar 'monstro.id' é mais seguro e recomendado do que 'monstro.nome'.
          <MonsterCard key={monstro.id} monstro={monstro} />
        ))}
      </div>
    </div>
  );
}

// Exporta o componente para que ele possa ser usado pelo App.jsx.
export default HomePage;
