// frontend/src/components/MonsterCard.jsx

// Este é um componente funcional em React. Ele é literalmente uma função JavaScript.
// Ele recebe 'props' (propriedades) como argumento. Aqui, estamos desestruturando para pegar a propriedade 'monstro' diretamente.
function MonsterCard({ monstro }) {
  // O 'return' define o que o componente vai renderizar na tela (seu JSX).
  return (
    // Usamos 'className' em vez de 'class' para definir classes de CSS em JSX.
    <div className="monster-card">
      {/* Exibimos o nome do monstro que recebemos via props */}
      <h2>{monstro.nome}</h2>
      {/* Exibimos os outros status do monstro */}
      <p>Vida: {monstro.vida}</p>
      <p>Defesa: {monstro.defesa}</p>
      <p>XP: {monstro.xp}</p>
    </div>
  );
}

// Exportamos o componente para que possamos importá-lo e usá-lo em outros arquivos, como o App.jsx.
export default MonsterCard;