// frontend/src/components/ItemCard.jsx

function ItemCard({ item }) {
  // Reutilizando a classe 'monster-card' para manter o estilo consistente.
  return (
    <div className="monster-card">
      <h2>{item.nome}</h2>
      <p><strong>Tipo:</strong> {item.tipo}</p>
      <p><strong>Descrição:</strong> {item.descricao}</p>
      {/* No futuro, podemos adicionar mais detalhes como dano, propriedades, etc. */}
    </div>
  );
}

export default ItemCard;