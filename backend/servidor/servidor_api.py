# servidor/servidor_api.py

# --- Importações ---
# Importa as classes principais do Flask: Flask, jsonify e request.
from flask import Flask, jsonify, request
# Importa o CORS para permitir a comunicação entre o frontend e o backend.
from flask_cors import CORS
# Importa TODAS as funções que nossa API vai precisar do nosso gerenciador de banco de dados em um único import.
from database.db_manager import (
    buscar_todos_os_itens, 
    buscar_detalhes_habilidades, 
    buscar_todos_os_monstros,
    registrar_novo_usuario,
    verificar_login
)

# --- Configuração Inicial do Servidor ---

# Cria a instância da nossa aplicação Flask.
app = Flask(__name__)
# Aplica o CORS à nossa aplicação, permitindo que o frontend (em outra porta) faça requisições.
CORS(app)

# --- Definição dos Endpoints da API (as "Rotas") ---

# --- Endpoints de Busca de Dados (GET) ---

@app.route("/api/monstros", methods=['GET'])
def get_monstros():
    """Endpoint que busca todos os monstros no DB e os retorna como uma lista JSON."""
    monstros_db = buscar_todos_os_monstros()
    lista_de_monstros = []
    for monstro_tupla in monstros_db:
        lista_de_monstros.append({
            "id": monstro_tupla[0], "nome": monstro_tupla[1],
            "vida": monstro_tupla[2], "ataque_bonus": monstro_tupla[3],
            "dano_dado": monstro_tupla[4], "defesa": monstro_tupla[5],
            "xp": monstro_tupla[6], "ouro": monstro_tupla[7]
        })
    return jsonify(lista_de_monstros)

@app.route("/api/itens", methods=['GET'])
def get_itens():
    """Endpoint que busca todos os itens no DB e os retorna como uma lista JSON."""
    itens_db = buscar_todos_os_itens()
    lista_de_itens = []
    for item_tupla in itens_db:
        lista_de_itens.append({
            "id": item_tupla[0], "nome": item_tupla[1], "tipo": item_tupla[2],
            "descricao": item_tupla[3], "preco": item_tupla[4], "dano": item_tupla[5],
            "bonus_ataque": item_tupla[6], "efeito": item_tupla[7]
        })
    return jsonify(lista_de_itens)

# (Este endpoint de habilidades pode ser melhorado no futuro para buscar todas as habilidades do DB)
@app.route("/api/habilidades", methods=['GET'])
def get_habilidades():
    """Endpoint de exemplo que busca algumas habilidades no DB."""
    # O ideal seria criar 'buscar_todas_as_habilidades' no db_manager.
    habilidades_db = buscar_detalhes_habilidades(["Bola de Fogo", "Toque Curativo"])
    lista_de_habilidades = []
    for hab_tupla in habilidades_db:
        lista_de_habilidades.append({
            "id": hab_tupla[0], "nome": hab_tupla[1], "descricao": hab_tupla[2],
            "efeito": hab_tupla[3], "custo_mana": hab_tupla[4]
        })
    return jsonify(lista_de_habilidades)


# --- Endpoints de Ação (POST) ---

@app.route("/api/registrar", methods=['POST'])
def rota_registrar_usuario():
    """Endpoint para registrar um novo usuário."""
    dados = request.get_json()
    if not dados or 'username' not in dados or 'password' not in dados:
        return jsonify({"sucesso": False, "mensagem": "Dados incompletos."}), 400
    
    sucesso = registrar_novo_usuario(dados['username'], dados['password'])

    if sucesso:
        return jsonify({"sucesso": True, "mensagem": "Usuário registrado com sucesso!"}), 201
    else:
        return jsonify({"sucesso": False, "mensagem": "Nome de usuário já está em uso."}), 409

# ROTA DE LOGIN MOVIDA PARA O LUGAR CORRETO
@app.route("/api/login", methods=['POST'])
def rota_fazer_login():
    """Endpoint para autenticar um usuário."""
    dados = request.get_json()

    if not dados or 'username' not in dados or 'password' not in dados:
        return jsonify({"sucesso": False, "mensagem": "Dados de usuário ou senha ausentes."}), 400

    username = dados['username']
    password = dados['password']

    login_valido = verificar_login(username, password)

    if login_valido:
        return jsonify({"sucesso": True, "mensagem": "Login bem-sucedido!"})
    else:
        return jsonify({"sucesso": False, "mensagem": "Nome de usuário ou senha inválidos."}), 401

# --- Bloco para Iniciar o Servidor ---

# Este código deve ser a ÚLTIMA coisa no seu arquivo.
if __name__ == "__main__":
    # O comando 'app.run()' inicia o servidor de desenvolvimento do Flask.
    app.run(debug=True, port=5001)