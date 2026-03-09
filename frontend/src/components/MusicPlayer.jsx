// frontend/src/components/MusicPlayer.jsx
import { useState, useEffect, useRef } from 'react';

import song1 from '../music_background/background_song.mp3';
import song2 from '../music_background/background_song2.mp3';
import song3 from '../music_background/background_song3.mp3';

const PLAYLIST = [song1, song2, song3];

function MusicPlayer() {
  const [ativo, setAtivo] = useState(false);
  const [indice, setIndice] = useState(0);
  const audioRef = useRef(null);

  // Inicializa o audio uma vez
  useEffect(() => {
    const audio = new Audio(PLAYLIST[0]);
    audio.volume = 0.35;
    audio.loop = false;
    audioRef.current = audio;

    // Quando uma música termina, passa para a próxima
    const proximaMusica = () => {
      setIndice(prev => {
        const proximo = (prev + 1) % PLAYLIST.length;
        audio.src = PLAYLIST[proximo];
        audio.play().catch(() => {});
        return proximo;
      });
    };

    audio.addEventListener('ended', proximaMusica);

    return () => {
      audio.removeEventListener('ended', proximaMusica);
      audio.pause();
      audioRef.current = null;
    };
  }, []);

  // Liga/desliga conforme estado 'ativo'
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    if (ativo) {
      audio.src = PLAYLIST[indice];
      audio.play().catch(() => {
        // Autoplay bloqueado pelo browser na primeira vez - normal
        setAtivo(false);
      });
    } else {
      audio.pause();
    }
  }, [ativo]);

  const toggleMusica = () => setAtivo(prev => !prev);

  return (
    <button
      onClick={toggleMusica}
      title={ativo ? 'Silenciar música' : 'Tocar música de fundo'}
      style={{
        position: 'fixed',
        top: '12px',
        left: '12px',
        zIndex: 1000,
        width: '42px',
        height: '42px',
        borderRadius: '50%',
        border: `2px solid ${ativo ? '#c59d5f' : '#555'}`,
        background: ativo
          ? 'linear-gradient(135deg, #2a1f0a, #3d2c0f)'
          : 'linear-gradient(135deg, #1a1a1a, #2a2a2a)',
        color: ativo ? '#c59d5f' : '#666',
        fontSize: '1.2rem',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: ativo
          ? '0 0 12px rgba(197,157,95,0.4), inset 0 0 8px rgba(197,157,95,0.1)'
          : '0 2px 8px rgba(0,0,0,0.5)',
        transition: 'all 0.3s ease',
      }}
    >
      {ativo ? '🎵' : '🔇'}
    </button>
  );
}

export default MusicPlayer;