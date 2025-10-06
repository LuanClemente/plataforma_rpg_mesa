// frontend/src/App.jsx

import { useState, useEffect } from 'react'
// 1. Importamos nosso novo componente! O caminho é relativo a este arquivo.
import MonsterCard from './components/MonsterCard'

function App() {
  const [monstros, setMonstros] = useState([])

  useEffect(() => {
    // A lógica para buscar os dados na API continua a mesma.
    fetch('http://127.0.0.1:5001/api/monstros')
      .then(response => response.json())
      .then(data => setMonstros(data))
      .catch(error => console.error("Erro ao buscar monstros:", error));
  }, [])

  return (
    // Adicionamos uma div principal com uma classe para estilização.
    <div className="app-container">
      <h1>Bestiário da Campanha</h1>
      {/* Um container para organizar nossas cartas de monstros. */}
      <div className="monster-list">
        {/* Em vez de criar um <li>, agora criamos um componente <MonsterCard> para cada monstro. */}
        {monstros.map(monstro => (
          // Passamos os dados do monstro atual para o componente através da prop 'monstro'.
          // A 'key' continua sendo essencial para o React.
          <MonsterCard key={monstro.nome} monstro={monstro} />
        ))}
      </div>
    </div>
  )
}

export default App