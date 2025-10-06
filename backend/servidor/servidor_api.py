# servidor/servidor_api.py

# --- Importações ---
# Importa as classes principais do Flask para criar o servidor e a resposta JSON.
from flask import Flask, jsonify
# Importa o CORS para permitir que nosso frontend (em outro endereço) acesse esta API.
from flask_cors import CORS
# Importa TODAS as funções de busca que nossa API vai precisar do nosso gerenciador de banco de dados.
from database.db_manager import buscar_todos_os_itens, buscar_detalhes_habilidades, buscar_todos_os_monstros

# --- Configuração Inicial do Servidor ---

# 1. Cria a instância ÚNICA da nossa aplicação Flask.
app = Flask(__name__)
# 2. Aplica o CORS a essa instância. Agora, TODAS as rotas que definirmos abaixo terão a permissão CORS.
CORS(app)

# --- Definição dos Endpoints da API (as "Rotas") ---

@app.route("/api/monstros", methods=['GET'])
def get_monstros():
    """
    Endpoint que busca todos os monstros no DB e os retorna como uma lista JSON.
    Acessível via http://127.0.0.1:5001/api/monstros
    """
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
    """
    Endpoint que busca todos os itens no DB e os retorna como uma lista JSON.
    Acessível via http://127.0.0.1:5001/api/itens
    """
    # Reutiliza a função que já existe no nosso db_manager!
    itens_db = buscar_todos_os_itens()
    # Cria uma lista vazia para a resposta.
    lista_de_itens = []
    # Itera sobre cada tupla de item.
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

@app.route("/api/habilidades", methods=['GET'])
def get_habilidades():
    """
    Endpoint que busca todas as habilidades no DB e as retorna como uma lista JSON.
    Acessível via http://127.0.0.1:5001/api/habilidades
    """
    # (Supondo que criamos uma função 'buscar_todas_as_habilidades' no db_manager)
    # Por agora, vamos usar a buscar_detalhes_habilidades com uma lista hipotética para mostrar o padrão.
    # No seu db_manager, você pode criar uma 'buscar_todas_as_habilidades' igual à de itens/monstros.
    habilidades_db = buscar_detalhes_habilidades(["Bola de Fogo", "Toque Curativo", "Ataque Poderoso"]) # Exemplo
    lista_de_habilidades = []
    for hab_tupla in habilidades_db:
        lista_de_habilidades.append({
            "id": hab_tupla[0],
            "nome": hab_tupla[1],
            "descricao": hab_tupla[2],
            "efeito": hab_tupla[3],
            "custo_mana": hab_tupla[4]
        })
    return jsonify(lista_de_habilidades)

# --- Bloco para Iniciar o Servidor ---

# Este código só executa se o script for chamado diretamente (com 'python -m servidor.servidor_api').
if __name__ == "__main__":
    # O comando 'app.run()' inicia o servidor de desenvolvimento do Flask.
    # 'debug=True' ativa o modo de depuração, que é essencial para o desenvolvimento.
    # 'port=5001' define a porta de rede em que o servidor irá "ouvir" por pedidos.
    app.run(debug=True, port=5001)