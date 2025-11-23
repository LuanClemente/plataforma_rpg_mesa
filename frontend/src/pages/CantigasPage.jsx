import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

function CantigasPage() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const [stats, setStats] = useState(null);
    const [historico, setHistorico] = useState([]);
    const [loading, setLoading] = useState(true);

    // Estados para formulário de credenciais
    const [novoNome, setNovoNome] = useState('');
    const [novaSenha, setNovaSenha] = useState('');
    const [msgCredenciais, setMsgCredenciais] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [statsRes, histRes] = await Promise.all([
                    api.get('/cantigas/dados'),
                    api.get('/cantigas/historico')
                ]);
                setStats(statsRes.data);
                setHistorico(histRes.data);
            } catch (error) {
                console.error("Erro ao carregar dados:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const handleUpdateCredenciais = async (e) => {
        e.preventDefault();
        if (!novoNome && !novaSenha) return;

        try {
            await api.put('/usuario/credenciais', {
                novo_nome: novoNome,
                nova_senha: novaSenha
            });
            setMsgCredenciais('Dados atualizados com sucesso! Faça login novamente.');
            setTimeout(logout, 2000); // Desloga para forçar novo login com novos dados
        } catch (error) {
            setMsgCredenciais('Erro ao atualizar. Nome pode já estar em uso.');
        }
    };

    const formatarTempo = (segundos) => {
        const horas = Math.floor(segundos / 3600);
        const minutos = Math.floor((segundos % 3600) / 60);
        return `${horas}h ${minutos}m`;
    };

    if (loading) return <div className="loading-screen">Afinando o alaúde...</div>;

    return (
        <div className="cantigas-container fade-in">
            <header className="cantigas-header">
                <h1>Cantigas do Aventureiro</h1>
                <p className="subtitle">Onde suas lendas são imortalizadas.</p>
            </header>

            <div className="cantigas-grid">
                {/* Coluna da Esquerda: Stats e Histórico */}
                <div className="cantigas-left">

                    {/* Card de Estatísticas */}
                    <div className="cantigas-card stats-card">
                        <h2>Sua Lenda</h2>
                        <div className="stats-row">
                            <div className="stat-item">
                                <span className="stat-value">{formatarTempo(stats?.tempo_aventura_segundos || 0)}</span>
                                <span className="stat-label">Tempo em Aventura</span>
                            </div>
                            <div className="stat-item">
                                <span className="stat-value">{stats?.total_fichas || 0}</span>
                                <span className="stat-label">Fichas Criadas</span>
                            </div>
                            <div className="stat-item">
                                <span className="stat-value">{stats?.total_salas_visitadas || 0}</span>
                                <span className="stat-label">Salas Exploradas</span>
                            </div>
                        </div>
                    </div>

                    {/* Card de Histórico (Correr para a Aventura) */}
                    <div className="cantigas-card history-card">
                        <h2>Últimas Aventuras</h2>
                        {historico.length === 0 ? (
                            <p className="empty-msg">Você ainda não iniciou sua jornada.</p>
                        ) : (
                            <ul className="history-list">
                                {historico.map((item, index) => (
                                    <li key={index} className="history-item">
                                        <div className="history-info">
                                            <strong>{item.sala_nome}</strong>
                                            <span>como {item.ficha_nome || 'Mestre'}</span>
                                        </div>
                                        <button
                                            className="btn-adventure"
                                            onClick={() => navigate(`/salas/${item.sala_id}`)}
                                        >
                                            Correr para a Aventura ⚔️
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                </div>

                {/* Coluna da Direita: Configurações e Doação */}
                <div className="cantigas-right">

                    {/* Card de Configurações */}
                    <div className="cantigas-card settings-card">
                        <h2>Configurações de Identidade</h2>
                        <form onSubmit={handleUpdateCredenciais}>
                            <div className="form-group">
                                <label>Novo Nome de Viajante</label>
                                <input
                                    type="text"
                                    value={novoNome}
                                    onChange={(e) => setNovoNome(e.target.value)}
                                    placeholder="Deixe vazio para manter"
                                />
                            </div>
                            <div className="form-group">
                                <label>Nova Palavra-Passe</label>
                                <input
                                    type="password"
                                    value={novaSenha}
                                    onChange={(e) => setNovaSenha(e.target.value)}
                                    placeholder="Deixe vazio para manter"
                                />
                            </div>
                            <button type="submit" className="btn-save">Atualizar Identidade</button>
                            {msgCredenciais && <p className="form-msg">{msgCredenciais}</p>}
                        </form>
                    </div>

                    {/* Card de Doação (O Bardo Precisa Comer) */}
                    <div className="cantigas-card donation-card">
                        <h2>Oferenda ao Criador</h2>
                        <p className="donation-text">
                            "Ó nobre viajante! Se esta plataforma está te trazendo um pouco de alegria, saiba que ela é feita por uma só pessoa,
                            que não passa de um simples plebeu que dorme em seleiros em troca de trabalhos manuais, mas faz tudo com zelo e principalmente de forma gratuita.
                            Considerando isso, se possível, deixe uma moeda de ouro, prata ou bronze (ou seja, um PIX) para que o plebeu programador possa
                            continuar codando e pagando a taverna (servidor). Continue sua nobre aventura, e cuidado! Pois eu costumava ser aventureiro igual a você, até que levei uma flechada no joelho, e hoje sou CLT. Que os dados sempre rolem 20 para você!"
                        </p>
                        <div className="qr-code-placeholder">
                            <img
                                src="/qrcode-pix.png"
                                alt="QR Code PIX"
                                style={{
                                    width: '200px',
                                    height: '200px',
                                    border: '2px dashed #8b7355',
                                    borderRadius: '8px',
                                    backgroundColor: 'white',
                                    padding: '8px'
                                }}
                            />
                        </div>
                        <p className="heartfelt-msg">
                            De coração, obrigado por trazer seus mundos para esta plataforma. <br />
                            ~ O Desenvolvedor Solitário
                        </p>
                    </div>

                </div>
            </div>
        </div>
    );
}

export default CantigasPage;
