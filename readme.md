# 🧙 Plataforma de RPG de Mesa

![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)

Plataforma web **full-stack** desenvolvida em **Python com Flask**, voltada para o gerenciamento de sessões de RPG de mesa, personagens e regras do jogo. 

O projeto nasceu para resolver um "boss" muito comum entre grupos de RPG: a dificuldade de centralizar informações, regras e a progressão dos personagens em um único lugar acessível para o Mestre e os Jogadores.

---

## 📸 Preview da Aplicação

> **Nota:** Adicione as imagens da aplicação rodando aqui. Mostre a tela de login, o dashboard de criação de personagem e a visão do mestre!
> 
> *Exemplo de como adicionar:*
> `![Tela Inicial](./docs/tela-inicial.png)`

---

## 🚀 Funcionalidades
- **Gerenciamento de Sessões:** Controle de campanhas e encontros.
- **Fichas Vivas:** Criação e administração dinâmica de personagens.
- **Compêndio:** Organização de regras, magias e informações do mundo.
- **Multiplayer-Ready:** Estrutura preparada para múltiplos usuários simultâneos (Mestres e Jogadores).

---

## 🛠️ Tecnologias Utilizadas
- **Back-end:** Python, Flask
- **Front-end:** HTML, CSS, JavaScript *(e o framework que você usa no `npm run dev`)*
- **Banco de Dados:** [Escreva aqui, ex: PostgreSQL / SQLite]
- **Infra & Versionamento:** Git, GitHub

---

## 🧠 Arquitetura
A aplicação segue uma arquitetura **full-stack** limpa. O Flask atua no backend lidando com as regras de negócio e a comunicação com o banco de dados. O frontend consome essas informações para fornecer uma interface intuitiva e responsiva. 

Toda a estrutura foi pensada visando **escalabilidade e fácil manutenção**, permitindo a inclusão de novas features sem quebrar o código existente.

---

## ☁️ Deploy
O deploy da aplicação está **em andamento**, com planejamento para hospedagem em nuvem utilizando **PythonAnywhere**.

---

## ▶️ Como Executar o Projeto Localmente

```bash
# 1. Clone o repositório
git clone [https://github.com/LuanClemente/plataforma_rpg_mesa.git](https://github.com/LuanClemente/plataforma_rpg_mesa.git)

# 2. Acesse a pasta do projeto
cd plataforma_rpg_mesa

# 3. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 4. Instale as dependências do Backend
pip install -r backend/requirements.txt

# 5. Execute a API (Backend)
python -m backend.servidor.servidor_api

# 6. Em outro terminal, execute o Frontend
cd frontend
npm run dev
