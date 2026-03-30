import React, { createContext, useContext, useEffect, useState } from 'react';
import io from 'socket.io-client';

const SocketContext = createContext();

export const useSocket = () => useContext(SocketContext);

export const SocketProvider = ({ children }) => {
    const [socket, setSocket] = useState(null);

    useEffect(() => {
        const newSocket = io('http://localhost:5003', {
            transports: ['websocket', 'polling'],
            path: '/socket.io',
            autoConnect: true,
        });

        newSocket.on('connect', () => console.log('[SocketContext] connected', newSocket.id));
        newSocket.on('connect_error', (err) => console.error('[SocketContext] connect_error', err));
        newSocket.on('disconnect', (reason) => console.log('[SocketContext] disconnect', reason));

        setSocket(newSocket);

        return () => {
            newSocket.off('connect');
            newSocket.off('connect_error');
            newSocket.off('disconnect');
            newSocket.close();
        };
    }, []);

    return (
        <SocketContext.Provider value={socket}>
            {children}
        </SocketContext.Provider>
    );
};