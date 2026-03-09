// frontend/src/components/ModalConfirm.jsx
import React from 'react';

function ModalConfirm({ titulo, mensagem, confirmLabel, cancelLabel, onConfirm, onCancel, tipo }) {
  const corTitulo = tipo === 'ban' ? '#c04040'
                  : tipo === 'kick' ? '#e0a030'
                  : tipo === 'coroa' ? '#c59d5f'
                  : '#c59d5f';

  const icone = tipo === 'ban' ? '🔨'
              : tipo === 'kick' ? '⚡'
              : tipo === 'coroa' ? '👑'
              : '⚠️';

  return (
    <div style={{
      position: 'fixed', inset: 0,
      background: 'rgba(0,0,0,0.75)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 8000,
      backdropFilter: 'blur(3px)',
    }}>
      <div style={{
        background: 'linear-gradient(160deg, #1e1508 0%, #0f0c06 100%)',
        border: `1px solid ${corTitulo}`,
        borderTop: `3px solid ${corTitulo}`,
        borderRadius: '8px',
        padding: '2rem 2.5rem',
        maxWidth: '420px',
        width: '90%',
        boxShadow: `0 0 40px rgba(0,0,0,0.8), 0 0 20px ${corTitulo}33`,
        textAlign: 'center',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.2rem',
        fontFamily: "'Arial', sans-serif",
      }}>
        {/* Ícone */}
        <div style={{ fontSize: '2.8rem', lineHeight: 1 }}>{icone}</div>

        {/* Título */}
        <h3 style={{
          color: corTitulo,
          fontFamily: "'MedievalSharp', cursive",
          fontSize: '1.3rem',
          margin: 0,
          textShadow: `0 0 12px ${corTitulo}88`,
        }}>
          {titulo}
        </h3>

        {/* Mensagem */}
        <p style={{
          color: '#d0c0a0',
          fontSize: '0.95rem',
          lineHeight: 1.6,
          margin: 0,
          background: 'rgba(197,157,95,0.06)',
          border: '1px solid rgba(197,157,95,0.15)',
          borderRadius: '4px',
          padding: '0.9rem 1rem',
        }}>
          {mensagem}
        </p>

        {/* Botões */}
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          <button
            onClick={onCancel}
            style={{
              flex: 1,
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid #5a4520',
              color: '#a09080',
              fontFamily: "'MedievalSharp', cursive",
              fontSize: '0.85rem',
              padding: '0.55rem 1rem',
              borderRadius: '4px',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseEnter={e => e.target.style.background = 'rgba(255,255,255,0.1)'}
            onMouseLeave={e => e.target.style.background = 'rgba(255,255,255,0.05)'}
          >
            {cancelLabel || 'Cancelar'}
          </button>
          <button
            onClick={onConfirm}
            style={{
              flex: 1,
              background: `linear-gradient(135deg, ${corTitulo}99, ${corTitulo})`,
              border: `1px solid ${corTitulo}`,
              color: tipo === 'coroa' ? '#1a1208' : '#fff',
              fontFamily: "'MedievalSharp', cursive",
              fontSize: '0.85rem',
              fontWeight: 'bold',
              padding: '0.55rem 1rem',
              borderRadius: '4px',
              cursor: 'pointer',
              transition: 'all 0.2s',
              boxShadow: `0 0 12px ${corTitulo}44`,
            }}
            onMouseEnter={e => e.target.style.boxShadow = `0 0 20px ${corTitulo}88`}
            onMouseLeave={e => e.target.style.boxShadow = `0 0 12px ${corTitulo}44`}
          >
            {confirmLabel || 'Confirmar'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ModalConfirm;