import React, { useState, useEffect } from 'react';

const BestiarioPage = () => {
  const [monstros, setMonstros] = useState([]);

  useEffect(() => {
    // Adiciona a classe de fundo específica desta página (definida no CSS)
    document.body.classList.add('bestiario-page-body');

    // Busca os dados da API do backend
    fetch('http://localhost:5003/api/monstros')
      .then(response => response.json())
      .then(data => setMonstros(data))
      .catch(error => console.error('Erro ao buscar monstros:', error));

    // Remove a classe ao sair da página para não afetar outras telas
    return () => {
      document.body.classList.remove('bestiario-page-body');
    };
  }, []);

  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>Bestiário</h1>
      <div className="monster-list">
        {monstros.map((monstro) => (
          <div key={monstro.id} className="monster-card">
            <h2>{monstro.nome}</h2>
            <p><strong>HP:</strong> {monstro.vida_maxima}</p>
            <p><strong>ATK:</strong> +{monstro.ataque_bonus}</p>
            <p><strong>Dano:</strong> {monstro.dano_dado}</p>
            <p><strong>DEF:</strong> {monstro.defesa}</p>
            <p><strong>XP:</strong> {monstro.xp_oferecido}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BestiarioPage;