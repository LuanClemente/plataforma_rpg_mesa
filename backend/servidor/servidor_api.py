# servidor/servidor_api.py

# --- Importações ---
# Da biblioteca 'functools', importamos 'wraps', uma ferramenta auxiliar para criar decorators.
from functools import wraps
# Do Flask, importamos as classes para criar o servidor, respostas JSON e ler as requisições.
from flask import Flask, jsonify, request
# Do Flask-CORS, importamos a função para habilitar o CORS.
from flask_cors import CORS
# Do nosso gerenciador de banco de dados, importamos TODAS as funções que a API irá utilizar.
from database.db_manager import (
    buscar_todos_os_itens, 
    buscar_detalhes_habilidades, 
    buscar_todos_os_monstros,
    registrar_novo_usuario,
    verificar_login,
    criar_nova_ficha,
    buscar_fichas_por_usuario
)
# Da biblioteca PyJWT, importamos a função principal para codificar e decodificar tokens.
import jwt
# Da biblioteca datetime, importamos as ferramentas para lidar com data e hora.
from datetime import datetime, timedelta, timezone

# --- Configuração Inicial do Servidor ---

# Cria a instância da nossa aplicação Flask.
app = Flask(__name__)
# Adiciona uma "chave secreta" à configuração. Essencial para assinar os tokens JWT de forma segura.
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-forte-e-dificil-de-adivinhar-12345'
# Habilita o CORS para toda a aplicação, permitindo requisições do nosso frontend.
CORS(app)

# --- Decorator de Autenticação (O "Segurança") ---
def token_required(f):
    """Decorator que verifica o token JWT antes de executar uma rota protegida."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({'mensagem': 'Token (crachá) ausente!'}), 401

        try:
            # Tenta decodificar o token. Se falhar, o token é inválido.
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            # Converte o 'sub' (ID do usuário) de volta para um número inteiro.
            current_user_id = int(data['sub'])
        except Exception as e:
            print(f"Erro ao decodificar token: {e}")
            return jsonify({'mensagem': 'Token (crachá) inválido ou expirado!'}), 401
        
        # Passa o ID do usuário logado para a função da rota.
        return f(current_user_id, *args, **kwargs)
    return decorated

# --- Definição dos Endpoints da API (as "Rotas") ---

# --- Endpoints Públicos (GET) ---
@app.route("/api/monstros", methods=['GET'])
def get_monstros():
    """Retorna a lista de todos os monstros da biblioteca."""
    monstros_db = buscar_todos_os_monstros()
    lista_de_monstros = [{'id': m[0], 'nome': m[1], 'vida': m[2], 'ataque_bonus': m[3], 'dano_dado': m[4], 'defesa': m[5], 'xp': m[6], 'ouro': m[7]} for m in monstros_db]
    return jsonify(lista_de_monstros)

@app.route("/api/itens", methods=['GET'])
def get_itens():
    """Retorna a lista de todos os itens da biblioteca."""
    itens_db = buscar_todos_os_itens()
    lista_de_itens = [{'id': i[0], 'nome': i[1], 'tipo': i[2], 'descricao': i[3], 'preco': i[4], 'dano': i[5], 'bonus_ataque': i[6], 'efeito': i[7]} for i in itens_db]
    return jsonify(lista_de_itens)

# --- Endpoints de Autenticação (POST) ---
@app.route("/api/registrar", methods=['POST'])
def rota_registrar_usuario():
    """Recebe dados de novo usuário, chama o db_manager para salvá-lo e retorna o resultado."""
    dados = request.get_json()
    if not dados or 'username' not in dados or 'password' not in dados:
        return jsonify({"sucesso": False, "mensagem": "Dados incompletos."}), 400
    sucesso = registrar_novo_usuario(dados['username'], dados['password'])
    if sucesso:
        return jsonify({"sucesso": True, "mensagem": "Usuário registrado com sucesso!"}), 201
    else:
        return jsonify({"sucesso": False, "mensagem": "Nome de usuário já está em uso."}), 409

@app.route("/api/login", methods=['POST'])
def rota_fazer_login():
    """Recebe credenciais, verifica no DB e retorna um token JWT se forem válidas."""
    dados = request.get_json()
    if not dados or 'username' not in dados or 'password' not in dados:
        return jsonify({"sucesso": False, "mensagem": "Dados ausentes."}), 400
    user_id = verificar_login(dados['username'], dados['password'])
    if user_id:
        token_payload = {
            'sub': str(user_id), 'name': dados['username'],
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({"sucesso": True, "mensagem": "Login bem-sucedido!", "token": token})
    else:
        return jsonify({"sucesso": False, "mensagem": "Nome de usuário ou senha inválidos."}), 401

# --- Endpoints Protegidos para FICHAS (Requerem Token) ---

# --- A ROTA QUE FALTAVA ---
@app.route("/api/fichas", methods=['GET'])
@token_required 
def get_fichas_usuario(current_user_id):
    """Busca e retorna todas as fichas que pertencem ao usuário logado."""
    # O 'current_user_id' é injetado pelo decorator @token_required.
    fichas = buscar_fichas_por_usuario(current_user_id)
    return jsonify(fichas)

@app.route("/api/fichas", methods=['POST'])
@token_required
def post_nova_ficha(current_user_id):
    """Cria uma nova ficha de personagem para o usuário logado."""
    dados = request.get_json()
    if not all(k in dados for k in ['nome_personagem', 'classe', 'raca', 'antecedente', 'atributos', 'pericias']):
        return jsonify({'mensagem': 'Dados da ficha incompletos'}), 400
    
    sucesso = criar_nova_ficha(
        current_user_id, dados['nome_personagem'], dados['classe'],
        dados['raca'], dados['antecedente'], dados['atributos'], dados['pericias']
    )
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Ficha criada com sucesso!'}), 201
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao criar a ficha'}), 500

# --- Bloco para Iniciar o Servidor ---
if __name__ == "__main__":
    app.run(debug=True, port=5001)