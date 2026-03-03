// frontend/src/components/ChatMessage.jsx
import React from 'react';

// Gera uma cor única e consistente para cada nome de remetente
function corDoRemetente(nome) {
  if (!nome) return '#c59d5f';
  // Sistema: mensagens de sistema em cinza
  if (nome === 'Sistema' || nome === '[Sistema]') return '#888';
  
  let hash = 0;
  for (let i = 0; i < nome.length; i++) {
    hash = nome.charCodeAt(i) + ((hash << 5) - hash);
  }
  // Gera matiz variada, saturação e luminosidade fixas para legibilidade
  const hue = Math.abs(hash) % 360;
  return `hsl(${hue}, 70%, 68%)`;
}

// Extrai o remetente da mensagem (padrão: "[Nome]: mensagem" ou "[Sistema]: ...")
function parsearMensagem(text) {
  if (typeof text !== 'string') return { remetente: null, corpo: text };

  // Padrão: "[Remetente]: mensagem"
  const match = text.match(/^\[([^\]]+)\]:\s*(.*)/s);
  if (match) {
    return { remetente: match[1], corpo: match[2] };
  }
  // Padrão: "--- sistema ---"
  if (text.startsWith('---') || text.startsWith('[Sistema]')) {
    return { remetente: 'Sistema', corpo: text };
  }
  return { remetente: null, corpo: text };
}

// Converte *asteriscos* em negrito
function parseBold(text) {
  if (typeof text !== 'string') return text;
  const parts = text.split(/(\*[^*]+\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('*') && part.endsWith('*')) {
      return <strong key={i} className="chat-bold">{part.slice(1, -1)}</strong>;
    }
    return <span key={i}>{part}</span>;
  });
}

function ChatMessage({ message }) {
  let texto = '';
  if (typeof message === 'string') {
    texto = message;
  } else if (typeof message === 'object' && message !== null) {
    if (message.error) texto = `⚠️ ${message.error}`;
    else if (message.text) texto = message.text;
    else texto = JSON.stringify(message);
  }

  const { remetente, corpo } = parsearMensagem(texto);
  const cor = corDoRemetente(remetente);

  if (remetente) {
    return (
      <p className="chat-message">
        <span style={{ color: cor, fontWeight: 'bold', marginRight: '4px' }}>
          [{remetente}]:
        </span>
        <span className="chat-corpo">{parseBold(corpo)}</span>
      </p>
    );
  }

  return (
    <p className="chat-message chat-message-sistema">
      {parseBold(corpo)}
    </p>
  );
}

export default ChatMessage;