# 📋 Sistema de Logging - Plataforma RPG

## Estrutura de Logs

```
backend/logs/
├── app.log           (arquivo principal, até 5MB)
├── app.log.1         (backup 1)
├── app.log.2         (backup 2)
└── ... (até 5 backups)
```

## Configuração

### Limite de Tamanho
- **Máximo por arquivo**: 5MB
- **Total de backups**: 5 (mantém histórico de ~25MB)
- **Rotação automática**: Quando atinge 5MB, cria backup e começa novo

## Como Usar

### 1. Importar o logger

```python
from logging_config import logger, log_conexao, log_evento_socket, log_batalha, log_erro, log_debug
```

### 2. Usar as funções específicas

#### Conexão/Desconexão
```python
log_conexao("Cliente conectado", user_id=123, sala_id=1, sid="abc123")
log_conexao("Cliente desconectado", sid="abc123")
```

#### Eventos Socket.IO
```python
log_evento_socket("join_room", sala_id=1, user_id=123, payload_resumo="ficha_id=5")
log_evento_socket("send_message", sala_id=1, user_id=123)
```

#### Batalha
```python
log_batalha("iniciativa", sala_id=1, detalhes="5 monstros, 3 jogadores")
log_batalha("combate", sala_id=1, detalhes="Turno 2, Monstro 1 ataca Jogador 3")
log_batalha("encerrada", sala_id=1, detalhes="Vitória! 3 derrotados, 2 fugiram")
```

#### Erros
```python
log_erro("create_room", user_id=123, sala_id=1, erro_msg="Nome de sala já existe")
log_erro("batalha_iniciar", erro_msg="Exception: monstro_id não encontrado")
```

#### Debug
```python
log_debug("servidor_api", "Enviando batalha_iniciada para sala 1")
```

#### Warning
```python
log_warning("token_required", "Token inválido recebido", user_id=123)
```

## Formato dos Logs

```
2026-03-29 21:26:58 | INFO     | rpg_mesa | handle_connect:1234 | [Conexão] Cliente conectado [User:123] [Sala: 1] [SID:abc123]
2026-03-29 21:27:02 | INFO     | rpg_mesa | handle_batalha_iniciar:5678 | [BATALHA] [Sala:1] [Fase:iniciativa] | 5 monstros, 3 jogadores
2026-03-29 21:27:05 | ERROR    | rpg_mesa | handle_batalha:789 | [ERRO] [batalha_iniciar] [User:1] [Sala:1] | Exception: monstro_id inválido
```

## Visualizando Logs

### Terminal (em tempo real)
```bash
# Linux/Mac
tail -f backend/logs/app.log

# Windows (PowerShell)
Get-Content backend/logs/app.log -Tail 50 -Wait
```

### Arquivo completo
```bash
# Abrir no VS Code (inclui syntax highlighting)
code backend/logs/app.log
```

## Limpeza Manual

Se quiser limpar logs manualmente:

```bash
# Deletar todos os logs
rm backend/logs/*.log*

# Deletar apenas backups (mantém app.log atual)
rm backend/logs/app.log.*
```

## Implementação Gradual

Você pode adicionar logging gradualmente:

### Fase 1: Conexões (já feito)
```python
log_conexao("...", user_id, sala_id, sid)
```

### Fase 2: Socket Events
```python
log_evento_socket("join_room", sala_id, user_id)
log_evento_socket("send_message", sala_id, user_id)
```

### Fase 3: Batalha
```python
log_batalha("iniciativa", sala_id, "...")
log_batalha("combate", sala_id, "...")
```

### Fase 4: Erros (mais importante!)
```python
try:
    ...
except Exception as e:
    log_erro("modulo_name", user_id, sala_id, str(e))
```

## Benefícios

✅ Rastreamento completo de eventos
✅ Identificação rápida de problemas
✅ Histórico crescente (backups)
✅ Sem crescimento infinito (limite automático)
✅ Formato estruturado (fácil de parsear)
✅ Timestamps precisos
✅ Contexto completo (user_id, sala_id, etc)

## Próximas Expansões

- Analytics: parser de logs para gerar estatísticas
- Dashboard: visualização de logs em tempo real
- Alerts: notificação de erros críticos
