# servidor/servidor_api.py

# Importa as classes 'Flask' (para criar o servidor) e 'jsonify' (para formatar nossas respostas em JSON) da biblioteca Flask.
from flask import Flask, jsonify
# Importa as funções que já criamos para buscar informações no nosso banco de dados.
# Graças à nossa estrutura e à execução com '-m', o Python sabe onde encontrar o pacote 'database'.
from database.db_manager import buscar_todos_os_itens, buscar_detalhes_habilidades

# Precisamos adicionar a função para buscar monstros ao db_manager ou recriá-la aqui. Vamos adicioná-la ao db_manager para manter o padrão.
# (Supondo que adicionamos 'buscar_todos_os_monstros' ao db_manager de forma similar a 'buscar_todos_os_itens')
# Por enquanto, vamos importar uma função hipotética que faremos a seguir.
from database.db_manager import buscar_todos_os_itens # Vamos usar esta como base

# --- Criação do Servidor ---

# Cria uma instância da aplicação Flask. A variável '__name__' ajuda o Flask a se localizar no projeto.
app = Flask(__name__)

# --- Definição dos Endpoints da API (as "rotas" ou "URLs") ---

# O decorator '@app.route(...)' associa uma URL a uma função Python.
# Quando um navegador ou frontend acessa "/api/monstros", a função 'get_monstros' é executada.
# 'methods=['GET']' especifica que esta rota responde a requisições de busca de dados (GET).
@app.route("/api/monstros", methods=['GET'])
def get_monstros():
    """
    Este endpoint busca todos os monstros do banco de dados e os retorna como JSON.
    """
    # (Para este exemplo funcionar, precisamos adicionar a função buscar_todos_os_monstros ao db_manager.py)
    # Por enquanto, vamos escrever a lógica aqui para ser claro.
    import sqlite3
    # O caminho precisa ser relativo à raiz do backend, de onde o servidor é executado.
    conexao = sqlite3.connect("database/campanhas.db")
    cursor = conexao.cursor()
    # Seleciona apenas os campos que o frontend pode precisar, para não expor dados a mais.
    cursor.execute("SELECT nome, vida_maxima, defesa, xp_oferecido FROM monstros_base ORDER BY nome")
    # Pega todos os resultados.
    monstros_db = cursor.fetchall()
    conexao.close()
    
    # Converte a lista de tuplas do banco de dados em uma lista de dicionários.
    # Dicionários são mais fáceis de ler e usar no frontend ("chave": "valor").
    lista_de_monstros = []
    # Itera sobre cada monstro retornado pelo banco de dados.
    for monstro_tupla in monstros_db:
        # Cria um dicionário para cada monstro com chaves claras.
        lista_de_monstros.append({
            "nome": monstro_tupla[0],
            "vida": monstro_tupla[1],
            "defesa": monstro_tupla[2],
            "xp": monstro_tupla[3]
        })

    # 'jsonify' é a função do Flask que converte nossa lista de dicionários Python
    # para o formato JSON padrão da web, preparando a resposta para o frontend.
    return jsonify(lista_de_monstros)

@app.route("/api/itens", methods=['GET'])
def get_itens():
    """
    Este endpoint busca todos os itens do banco de dados e os retorna como JSON.
    """
    # Reutiliza a função que já criamos e testamos no nosso db_manager!
    itens_db = buscar_todos_os_itens()
    # Cria uma lista vazia para a nossa resposta formatada.
    lista_de_itens = []
    # Itera sobre cada tupla de item retornada pelo banco de dados.
    for item_tupla in itens_db:
        # Converte a tupla em um dicionário com chaves descritivas.
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
    # Converte a lista de dicionários de itens para JSON e a envia como resposta.
    return jsonify(lista_de_itens)

# --- Bloco para Iniciar o Servidor ---

# Este código só executa se o script for chamado diretamente (python -m servidor.servidor_api)
if __name__ == "__main__":
    # O comando 'app.run()' inicia o servidor de desenvolvimento do Flask.
    # 'debug=True' é uma ferramenta poderosa para desenvolvimento:
    # 1. Reinicia o servidor automaticamente a cada alteração no código.
    # 2. Mostra erros detalhados diretamente no navegador, facilitando a depuração.
    # 'port=5001' define a porta de rede em que o servidor irá "ouvir" por pedidos.
    app.run(debug=True, port=5001)