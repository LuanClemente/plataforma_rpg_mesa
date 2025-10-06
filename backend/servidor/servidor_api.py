# servidor/servidor_api.py

# --- Importações ---
# Importa as classes principais do Flask: Flask para criar o servidor, jsonify para formatar respostas,
# e 'request' para receber os dados enviados pelo frontend (como em um formulário de cadastro).
from flask import Flask, jsonify, request
# Importa o CORS para permitir que nosso frontend (em outro endereço) acesse esta API.
from flask_cors import CORS
# Importa TODAS as funções que nossa API vai precisar do nosso gerenciador de banco de dados.
from database.db_manager import (
    buscar_todos_os_itens, 
    buscar_detalhes_habilidades, 
    buscar_todos_os_monstros,
    registrar_novo_usuario  # A nossa nova função!
)
import os # Importamos 'os' para a lógica de caminho robusto.

# --- Configuração Inicial do Servidor ---

# 1. Lógica de caminho absoluto para garantir que o DB seja encontrado.
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(script_dir, '..')
# Precisamos definir NOME_DB aqui se o db_manager não o fizer de forma global.
# Mas como já corrigimos o db_manager, ele encontrará o DB sozinho.

# 2. Cria a instância ÚNICA da nossa aplicação Flask.
app = Flask(__name__)
# 3. Aplica o CORS a essa instância. Agora, TODAS as rotas que definirmos abaixo terão a permissão CORS.
CORS(app)

# --- Definição dos Endpoints da API (as "Rotas") ---

# --- Endpoints de Busca de Dados (GET) ---

@app.route("/api/monstros", methods=['GET'])
def get_monstros():
    """Endpoint que busca todos os monstros no DB e os retorna como uma lista JSON."""
    # Chama a função centralizada no nosso db_manager para buscar os monstros.
    monstros_db = buscar_todos_os_monstros()
    # Cria uma lista vazia para a nossa resposta formatada.
    lista_de_monstros = []
    # Itera sobre cada tupla de monstro retornada pelo banco de dados.
    for monstro_tupla in monstros_db:
        # Converte a tupla em um dicionário com chaves claras, que o frontend vai entender.
        lista_de_monstros.append({
            "id": monstro_tupla[0],
            "nome": monstro_tupla[1],
            "vida": monstro_tupla[2],
            "ataque_bonus": monstro_tupla[3],
            "dano_dado": monstro_tupla[4],
            "defesa": monstro_tupla[5],
            "xp": monstro_tupla[6],
            "ouro": monstro_tupla[7]
        })
    # 'jsonify' pega nossa lista de dicionários e a transforma em uma resposta JSON válida.
    return jsonify(lista_de_monstros)

@app.route("/api/itens", methods=['GET'])
def get_itens():
    """Endpoint que busca todos os itens no DB e os retorna como uma lista JSON."""
    # Reutiliza a função que já existe no nosso db_manager!
    itens_db = buscar_todos_os_itens()
    lista_de_itens = []
    for item_tupla in itens_db:
        # Converte a tupla em um dicionário.
        lista_de_itens.append({
            "id": item_tupla[0],
            "nome": item_tupla[1],
            "tipo": item_tupla[2],
            "descricao": item_tupla[3],
            "preco": item_tupla[4],
            "dano": item_tupla[5],
            "bonus_ataque": item_tupla[6],
            "efeito": item_tupla[7]
        })
    # Retorna a lista de itens formatada como JSON.
    return jsonify(lista_de_itens)

# (O endpoint de habilidades pode ser melhorado para buscar todas as habilidades, não apenas uma lista fixa)
# Vamos criar a função buscar_todas_as_habilidades no db_manager e usá-la aqui.
# Por agora, manteremos o exemplo.

# --- Endpoint de Ação (POST) ---

@app.route("/api/registrar", methods=['POST'])
def rota_registrar_usuario():
    """
    Endpoint para registrar um novo usuário.
    Espera receber um JSON com 'username' e 'password' no corpo da requisição.
    """
    # 'request.get_json()' pega os dados JSON que o frontend enviou.
    dados = request.get_json()

    # Faz uma verificação de segurança para garantir que os dados necessários foram enviados.
    if not dados or not 'username' in dados or not 'password' in dados:
        # Retorna um erro 400 (Bad Request) se os dados estiverem incompletos, com uma mensagem.
        return jsonify({"sucesso": False, "mensagem": "Dados de usuário ou senha ausentes."}), 400

    # Extrai o nome de usuário e a senha dos dados recebidos.
    username = dados['username']
    password = dados['password']

    # Chama nossa função segura do db_manager para tentar registrar o usuário no banco de dados.
    sucesso = registrar_novo_usuario(username, password)

    # Se a função retornar True, o registro foi um sucesso.
    if sucesso:
        # Retorna uma mensagem de sucesso com o status 201 (Created), que é o padrão para criação de recursos.
        return jsonify({"sucesso": True, "mensagem": "Usuário registrado com sucesso!"}), 201
    # Se retornar False, o usuário provavelmente já existe.
    else:
        # Retorna uma mensagem de erro com o status 409 (Conflict), indicando que o recurso já existe.
        return jsonify({"sucesso": False, "mensagem": "Nome de usuário já está em uso."}), 409

# --- Bloco para Iniciar o Servidor ---

# Este código só executa se o script for chamado diretamente (com 'python -m servidor.servidor_api').
if __name__ == "__main__":
    # O comando 'app.run()' inicia o servidor de desenvolvimento do Flask.
    # 'debug=True' ativa o modo de depuração, que é essencial para o desenvolvimento.
    # 'port=5001' define a porta de rede em que o servidor irá "ouvir" por pedidos.
    app.run(debug=True, port=5001)