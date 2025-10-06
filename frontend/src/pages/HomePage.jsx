// frontend/src/pages/HomePage.jsx
import { useState, useEffect } from 'react';
import MonsterCard from '../components/MonsterCard'; // Note o '../' para voltar uma pasta

function HomePage() {
  const [monstros, setMonstros] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:5001/api/monstros')
      .then(response => response.json())
      .then(data => setMonstros(data))
      .catch(error => console.error("Erro ao buscar monstros:", error));
  }, []);

  return (
    <div>
      <h1>Bestiário da Campanha</h1>
      <div className="monster-list">
        {monstros.map(monstro => (
          <MonsterCard key={monstro.nome} monstro={monstro} />
        ))}
      </div>
    </div>
  );
}
export default HomePage;