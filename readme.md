# 🧙 Plataforma de RPG de Mesa

Plataforma web **full-stack** desenvolvida em **Python com Flask**, voltada para o gerenciamento de sessões de RPG de mesa, personagens e regras do jogo.

O projeto foi criado para resolver um problema comum entre grupos de RPG: a dificuldade de centralizar informações, regras e progressão dos personagens em um único lugar acessível.

---

## 🚀 Funcionalidades
- Gerenciamento de sessões de RPG
- Criação e administração de personagens
- Organização de regras e informações do jogo
- Interface web para interação dos usuários
- Estrutura preparada para múltiplos usuários

---

## 🛠️ Tecnologias Utilizadas
- **Back-end:** Python, Flask
- **Front-end:** HTML, CSS, JavaScript
- **Banco de Dados:** (definir se já estiver usando)
- **Controle de versão:** Git & GitHub

---

## 🧠 Arquitetura
A aplicação segue uma arquitetura **full-stack**, onde o Flask é responsável pelo backend, regras de negócio e comunicação com o banco de dados, enquanto o frontend fornece a interface de interação com o usuário.

O projeto foi estruturado pensando em **escalabilidade e organização**, facilitando a inclusão de novas funcionalidades no futuro.

---

## ☁️ Deploy
O deploy da aplicação está **em andamento**, com planejamento para hospedagem em nuvem utilizando **PythonAnywhere**.

---

## ▶️ Como Executar o Projeto Localmente
```bash
# Clone o repositório
git clone https://github.com/LuanClemente/plataforma_rpg_mesa.git

# Acesse a pasta do projeto
cd plataforma_rpg_mesa

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
flask run