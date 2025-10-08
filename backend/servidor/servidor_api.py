# servidor/servidor_api.py

# --- Importações ---
# Importa a biblioteca 'functools' para usar o decorador 'wraps'
from functools import wraps
# Importa as classes principais do Flask: Flask, jsonify e request.
from flask import Flask, jsonify, request
# Importa o CORS para permitir a comunicação entre o frontend e o backend.
from flask_cors import CORS
# Importa TODAS as funções que nossa API vai precisar do nosso gerenciador de banco de dados.
from database.db_manager import (
    buscar_todos_os_itens, 
    buscar_detalhes_habilidades, 
    buscar_todos_os_monstros,
    registrar_novo_usuario,
    verificar_login
)
# Importa a biblioteca 'jwt' para criar nossos tokens de autenticação.
import jwt
# Importa as bibliotecas 'datetime' para definir o tempo de expiração do token.
from datetime import datetime, timedelta, timezone

# --- Configuração Inicial do Servidor ---

# Cria a instância da nossa aplicação Flask.
app = Flask(__name__)
# Adiciona uma "chave secreta" à configuração do app. É essencial para assinar os tokens de forma segura.
# Mude esta string para qualquer outra coisa complexa e secreta.
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-forte-e-dificil-de-adivinhar-12345'
# Aplica o CORS à nossa aplicação.
CORS(app)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Verifica se o 'x-access-token' (nosso crachá) está no cabeçalho da requisição.
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({'mensagem': 'Crachá de acesso (token) ausente!'}), 401

        try:
            # Tenta decodificar o token usando nossa chave secreta.
            # Isso verifica a validade e a assinatura do crachá.
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            # Passamos os dados do usuário decodificado para a rota.
            current_user_id = data['sub']
        except:
            return jsonify({'mensagem': 'Crachá de acesso (token) inválido!'}), 401
        
        # Se tudo estiver certo, executa a rota original.
        return f(current_user_id, *args, **kwargs)
    return decorated
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

# (Este endpoint pode ser melhorado no futuro)
@app.route("/api/habilidades", methods=['GET'])
def get_habilidades():
    """Endpoint de exemplo que busca algumas habilidades no DB."""
    habilidades_db = buscar_detalhes_habilidades(["Bola de Fogo", "Toque Curativo"])
    lista_de_habilidades = []
    for hab_tupla in habilidades_db:
        lista_de_habilidades.append({
            "id": hab_tupla[0], "nome": hab_tupla[1], "descricao": hab_tupla[2],
            "efeito": hab_tupla[3], "custo_mana": hab_tupla[4]
        })
    return jsonify(lista_de_habilidades)


@app.route("/api/fichas", methods=['GET'])
@token_required # <-- Nosso "segurança" está na porta deste endpoint!
def get_fichas_usuario(current_user_id):
    """Busca e retorna todas as fichas do usuário logado."""
    # O 'current_user_id' é fornecido pelo nosso sentinela @token_required.
    fichas = buscar_fichas_por_usuario(current_user_id)
    return jsonify(fichas)

@app.route("/api/fichas", methods=['POST'])
@token_required # <-- O segurança também está aqui!
def post_nova_ficha(current_user_id):
    """Cria uma nova ficha para o usuário logado."""
    dados = request.get_json()
    if not dados or 'nome_personagem' not in dados or 'classe' not in dados:
        return jsonify({'mensagem': 'Dados da ficha incompletos'}), 400

    # Por enquanto, vamos usar atributos padrão.
    atributos_padrao = {
        "Força": 10, "Destreza": 10, "Constituição": 10,
        "Inteligência": 10, "Sabedoria": 10, "Carisma": 10
    }
    
    sucesso = criar_nova_ficha(
        current_user_id, 
        dados['nome_personagem'], 
        dados['classe'], 
        atributos_padrao
    )

    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Ficha criada com sucesso!'}), 201
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao criar a ficha'}), 500


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

# --- ROTA DE LOGIN ATUALIZADA COM GERAÇÃO DE TOKEN ---
@app.route("/api/login", methods=['POST'])
def rota_fazer_login():
    """Endpoint para autenticar um usuário e retornar um token JWT."""
    dados = request.get_json()
    if not dados or 'username' not in dados or 'password' not in dados:
        return jsonify({"sucesso": False, "mensagem": "Dados de usuário ou senha ausentes."}), 400

    username = dados['username']
    password = dados['password']

    # A função 'verificar_login' agora retorna o ID do usuário em caso de sucesso, ou None.
    user_id = verificar_login(username, password)

    # Verifica se o login foi válido (se recebemos um user_id).
    if user_id:
        # Se o login for válido, vamos criar o "crachá" (token).
        # O 'payload' são as informações que queremos guardar dentro do token.
        token_payload = {
            'sub': user_id,  # 'sub' (subject) é o padrão para guardar o ID do usuário.
            'name': username,
            'iat': datetime.now(timezone.utc), # 'iat' (issued at) marca quando o token foi criado.
            'exp': datetime.now(timezone.utc) + timedelta(hours=24) # 'exp' (expiration) define a validade (ex: 24 horas).
        }
        # Codifica o payload usando nossa chave secreta para gerar o token final.
        token = jwt.encode(
            token_payload, 
            app.config['SECRET_KEY'], 
            algorithm='HS256'
        )
        
        # Envia a resposta de sucesso, incluindo o token.
        return jsonify({"sucesso": True, "mensagem": "Login bem-sucedido!", "token": token})
    else:
        # Se o login for inválido, retorna um erro 401 (Unauthorized).
        return jsonify({"sucesso": False, "mensagem": "Nome de usuário ou senha inválidos."}), 401

# --- Bloco para Iniciar o Servidor ---

if __name__ == "__main__":
    # Inicia o servidor de desenvolvimento do Flask.
    app.run(debug=True, port=5001)