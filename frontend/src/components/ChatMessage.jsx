// frontend/src/components/ChatMessage.jsx

import React from 'react';

/**
 * Converte um texto com trechos em *asteriscos* para um array de elementos React.
 * Exemplo: "Eu ataco o *dragão* ferozmente!"
 * Resultado: Eu ataco o <strong>dragão</strong> ferozmente!
 */
const parseMessage = (text) => {
  if (typeof text !== 'string') return text; // Segurança extra contra tipos inesperados

  // Divide o texto em partes, separando trechos entre asteriscos
  const parts = text.split(/(\*[^*]+\*)/g);

  return parts.map((part, index) => {
    // Se a parte começa e termina com asterisco, trata como negrito
    if (part.startsWith('*') && part.endsWith('*')) {
      const innerText = part.slice(1, -1); // remove os asteriscos
      return (
        <strong key={index} className="chat-bold">
          {innerText}
        </strong>
      );
    }
    // Trecho normal, sem formatação especial
    return <span key={index}>{part}</span>;
  });
};

/**
 * Componente de exibição individual de mensagens do chat.
 * Pode lidar com:
 * - Strings simples
 * - Objetos com campos 'text', 'error', 'system', etc.
 * - Mensagens com trechos *em negrito*
 */
function ChatMessage({ message }) {
  // Define o conteúdo da mensagem dependendo do formato recebido
  let content = '';

  if (typeof message === 'string') {
    content = message;
  } else if (typeof message === 'object' && message !== null) {
    // Prioridade: erro > texto normal > resultado de dados > mensagem bruta
    if (message.error) {
      content = `⚠️ ${message.error}`;
    } else if (message.text) {
      content = message.text;
    } else if (message.command && message.result !== undefined) {
      content = `🎲 Rolagem ${message.command}: ${message.result}`;
    } else {
      content = JSON.stringify(message);
    }
  }

  return (
    <p className="chat-message">
      {parseMessage(content)}
    </p>
  );
}

export default ChatMessage;
