// frontend/src/pages/HomePage.jsx
import { useState, useEffect } from 'react';
import MonsterCard from '../components/MonsterCard';
import GerenciarMonstros from '../components/GerenciarMonstros';
import { useAuth } from '../context/AuthContext';
import bestiaryBg from '../assets/bestiary_background.png';

function HomePage() {
  const { user } = useAuth();
  const [monstros, setMonstros] = useState([]);
  const [reload, setReload] = useState(0);

  useEffect(() => {
    fetch('http://127.0.0.1:5003/api/monstros')
      .then(response => response.json())
      .then(data => setMonstros(data))
      .catch(error => console.error("Erro ao buscar monstros:", error));
  }, [reload]);

  useEffect(() => {
    document.body.style.backgroundImage = `url(${bestiaryBg})`;
    document.body.style.backgroundSize = 'cover';
    document.body.style.backgroundPosition = 'center';
    document.body.style.backgroundAttachment = 'fixed';
    return () => { document.body.style.backgroundImage = ''; };
  }, []);

  return (
    <div>
      <h1>Bestiário da Campanha</h1>

      {/* Painel de criação visível apenas para mestres */}
      {user?.role === 'mestre' && (
        <GerenciarMonstros onMonstroSalvo={() => setReload(r => r + 1)} />
      )}

      <div className="monster-list">
        {monstros.length === 0
          ? <p style={{color:'#c59d5f'}}>Nenhum monstro cadastrado ainda.</p>
          : monstros.map(monstro => <MonsterCard key={monstro.id} monstro={monstro} onDelete={() => setReload(r => r + 1)} />)
        }
      </div>
    </div>
  );
}

export default HomePage;