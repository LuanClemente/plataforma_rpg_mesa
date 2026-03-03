// frontend/src/pages/FerrariaArcanaPage.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import ItemCard from '../components/ItemCard';
import GerenciarItens from '../components/GerenciarItens';
import { backgrounds } from '../assets/backgrounds';

function FerrariaArcanaPage() {
    const { user } = useAuth();
    const [itens, setItens] = useState([]);
    const [loading, setLoading] = useState(true);
    const [reload, setReload] = useState(0);

    useEffect(() => {
        document.body.style.backgroundImage = `url(${backgrounds.ferraria})`;
        document.body.style.backgroundSize = 'cover';
        document.body.style.backgroundPosition = 'center';
        document.body.style.backgroundAttachment = 'fixed';
        return () => { document.body.style.backgroundImage = ''; };
    }, []);

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
    }, [reload]);

    if (loading) return <div className="loading-screen">Aquecendo a forja...</div>;

    return (
        <div className="fade-in" style={{ padding: '2rem' }}>
            <h1 style={{ textAlign: 'center' }}>Ferraria Arcana</h1>
            <p style={{ textAlign: 'center', marginBottom: '2rem', color: '#c59d5f' }}>
                Os artefatos mais poderosos forjados pelo Mestre.
            </p>

            {/* Painel de criação visível apenas para mestres */}
            {user?.role === 'mestre' && (
                <GerenciarItens onItemSalvo={() => setReload(r => r + 1)} />
            )}

            <h2>Artefatos Disponíveis</h2>
            <div className="monster-list">
                {itens.length === 0
                    ? <p style={{color:'#c59d5f'}}>Nenhum artefato forjado ainda.</p>
                    : itens.map(item => <ItemCard key={item.id} item={item} />)
                }
            </div>
        </div>
    );
}

export default FerrariaArcanaPage;