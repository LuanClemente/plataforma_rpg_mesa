// frontend/src/pages/FerrariaArcanaPage.jsx

import React, { useState, useEffect } from 'react';
import api from '../services/api';
import ItemCard from '../components/ItemCard';

function FerrariaArcanaPage() {
    const [itens, setItens] = useState([]);
    const [loading, setLoading] = useState(true);

    // Efeito para gerenciar o fundo da página
    useEffect(() => {
        const classeFundo = 'ferraria-arcana-body';
        document.body.classList.add(classeFundo);

        return () => {
            document.body.classList.remove(classeFundo);
        };
    }, []);

    // Efeito para buscar os itens da API
    useEffect(() => {
        const fetchItens = async () => {
            try {
                const response = await api.get('/itens');
                setItens(response.data);
            } catch (error) {
                console.error("Erro ao forjar a lista de itens:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchItens();
    }, []);

    if (loading) return <div className="loading-screen">Aquecendo a forja...</div>;

    return (
        <div className="fade-in" style={{ padding: '2rem' }}>
            <h1 style={{ textAlign: 'center', fontFamily: 'MedievalSharp, cursive', fontSize: '3rem' }}>Ferraria Arcana</h1>
            <p style={{ textAlign: 'center', marginBottom: '2rem' }}>Os artefatos mais poderosos forjados pelo Mestre.</p>
            <div className="monster-list">
                {itens.map(item => <ItemCard key={item.id} item={item} />)}
            </div>
        </div>
    );
}

export default FerrariaArcanaPage;