import React, { useState, useEffect, useRef } from 'react';
import { useSocket } from '../context/SocketContext';

const Chat = ({ username, room }) => {
    const socket = useSocket();
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState([]);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        if (!socket) return;

        socket.emit('join_room', { username, room });

        socket.on('message', (data) => {
            setMessages((prev) => [...prev, data]);
        });

        return () => {
            socket.off('message');
        };
    }, [socket, username, room]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const sendMessage = (e) => {
        e.preventDefault();
        if (message.trim() && socket) {
            socket.emit('send_message', { room, message, user: username });
            setMessage('');
        }
    };

    return (
        <div className="chat-container">
            <h2>Chat da Sala: {room}</h2>
            <div className="message-list">
                {messages.map((msg, index) => (
                    <p key={index}>
                        <strong>{msg.user}: </strong>{msg.text || msg.message}
                    </p>
                ))}
                <div ref={messagesEndRef} />
            </div>
            <form className="chat-form" onSubmit={sendMessage}>
                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Digite sua mensagem..."
                />
                <button type="submit">Enviar</button>
            </form>
        </div>
    );
};

export default Chat;
