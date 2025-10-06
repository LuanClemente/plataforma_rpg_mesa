# backend/servidor/servidor_api.py

# Importa a classe Flask para criar nosso servidor e 'jsonify' para formatar nossa resposta em JSON.
from flask import Flask, jsonify
# Importa a biblioteca para interagir com o banco de dados.
import sqlite3

# --- Caminho do Banco de Dados ---
# Como vamos executar o comando a partir da pasta 'backend', o caminho para o DB continua sendo este.
# O Python usará a pasta 'backend' como ponto de partida para encontrar 'database/campanhas.db'.
NOME_DB = "database/campanhas.db"

# Cria uma instância da aplicação Flask. '__name__' é uma variável especial do Python que ajuda o Flask a se localizar.
app = Flask(__name__)

# --- Funções Auxiliares para o Banco de Dados ---
# Para manter este arquivo limpo, estamos recriando a função aqui, mas o ideal
# seria importar do db_manager. Com o '-m', o import original 'from database.db_manager...' funcionaria!
# Vamos usar o import correto para seguir as boas práticas.
from database.db_manager import buscar_todos_os_itens # Importando corretamente

def buscar_todos_os_monstros():
    """Função para buscar todos os monstros (exemplo para a API)."""
    try:
        # Conecta ao banco de dados usando o caminho definido.
        conexao = sqlite3.connect(NOME_DB)
        # Cria um cursor.
        cursor = conexao.cursor()
        # Executa a consulta SQL para selecionar alguns campos de todos os monstros.
        cursor.execute("SELECT nome, vida_maxima, defesa, xp_oferecido FROM monstros_base ORDER BY nome")
        # Pega todos os resultados.
        monstros_db = cursor.fetchall()
        # Fecha a conexão.
        conexao.close()
        
        # Cria uma lista vazia para armazenar os monstros formatados.
        lista_de_monstros = []
        # Itera sobre cada tupla de monstro retornada pelo banco de dados.
        for monstro_tupla in monstros_db:
            # Converte a tupla em um dicionário, que é um formato mais amigável para JSON.
            lista_de_monstros.append({
                "nome": monstro_tupla[0],
                "vida": monstro_tupla[1],
                "defesa": monstro_tupla[2],
                "xp": monstro_tupla[3]
            })
        # Retorna a lista de dicionários.
        return lista_de_monstros
    except Exception as e:
        # Em caso de erro, imprime o erro e retorna uma lista vazia.
        print(f"Erro ao buscar monstros: {e}")
        return []

# --- Definição dos Endpoints da API ---

# O decorator '@app.route(...)' define uma URL para a nossa API.
# 'methods=['GET']' especifica que esta URL responde a requisições do tipo GET (buscar dados).
@app.route("/api/monstros", methods=['GET'])
def get_monstros():
    """Endpoint que retorna a lista de todos os monstros em formato JSON."""
    # Chama nossa função auxiliar para buscar os dados no DB.
    monstros = buscar_todos_os_monstros()
    # 'jsonify' pega a nossa lista Python e a converte para o formato JSON, que o frontend entenderá.
    return jsonify(monstros)

@app.route("/api/itens", methods=['GET'])
def get_itens():
    """Endpoint que retorna a lista de todos os itens em formato JSON."""
    # Reutiliza a função que já existe no nosso db_manager!
    itens_db = buscar_todos_os_itens()
    lista_de_itens = []
    # Itera sobre os itens do DB para formatá-los.
    for item_tupla in itens_db:
        lista_de_itens.append({
            "nome": item_tupla[1],
            "tipo": item_tupla[2],
            "descricao": item_tupla[3],
            "preco": item_tupla[4]
        })
    # Retorna a lista de itens formatada como JSON.
    return jsonify(lista_de_itens)

# --- Bloco para Iniciar o Servidor ---

# Este código só executa se o script for chamado diretamente (não se for importado).
if __name__ == "__main__":
    # O comando 'app.run()' inicia o servidor Flask.
    # 'debug=True' ativa o modo de depuração, que reinicia o servidor automaticamente
    # a cada alteração no código e mostra erros detalhados no navegador.
    app.run(debug=True, port=5001) # Usando a porta 5001 para evitar conflitos