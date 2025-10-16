# saves/saves_manager.py

# Importa a biblioteca 'json' para trabalhar com o formato de dados JSON.
import json
# Importa a biblioteca 'os' para interagir com o sistema operacional (pastas e caminhos).
import os

# --- CORREÇÃO DE IMPORTAÇÃO ---
# Alteramos a importação de relativa ('core.') para absoluta ('backend.core.')
# para garantir que o módulo seja encontrado quando executamos o servidor da raiz do projeto.
from backend.core.personagem import Personagem

# --- LÓGICA DE CAMINHO ABSOLUTO E ROBUSTA ---
# Descobre o caminho absoluto para a pasta onde este script está localizado (a pasta 'saves').
script_dir = os.path.dirname(os.path.abspath(__file__))
# Constrói o caminho para a subpasta 'personagens_salvos' dentro da pasta 'saves'.
# Este caminho será sempre correto.
PASTA_SAVES = os.path.join(script_dir, 'personagens_salvos')

def salvar_personagem(personagem: Personagem):
    """
    Esta função recebe um objeto Personagem, converte seus dados para o formato JSON
    e os salva em um arquivo .json no disco.
    """
    # Verifica se a pasta de saves já existe.
    if not os.path.exists(PASTA_SAVES):
        # Se não existir, o comando 'os.makedirs()' a cria.
        os.makedirs(PASTA_SAVES)

    # Cria um dicionário Python contendo todos os atributos do objeto personagem que queremos salvar.
    dados_para_salvar = {
        "nome": personagem.nome,
        "classe": personagem.classe,
        "nivel": personagem.nivel,
        "atributos": personagem.atributos,
        "vida_atual": personagem.vida_atual,
        "vida_maxima": personagem.vida_maxima,
        "inventario": personagem.inventario,
        "ouro": personagem.ouro,
        "xp_atual": personagem.xp_atual,
        "xp_proximo_nivel": personagem.xp_proximo_nivel,
        "mana_atual": personagem.mana_atual,
        "mana_maxima": personagem.mana_maxima,
        "habilidades": personagem.habilidades,
    }

    # Monta o nome do arquivo de save usando o nome do personagem (ex: "Aragorn.json").
    caminho_arquivo = os.path.join(PASTA_SAVES, f"{personagem.nome}.json")

    # O bloco 'with open(...)' abre o arquivo e garante que ele seja fechado automaticamente.
    # 'w' = modo de escrita (sobrescreve o arquivo se ele existir).
    # 'encoding='utf-8'' garante que caracteres especiais sejam salvos corretamente.
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        # 'json.dump()' escreve o dicionário no arquivo em formato JSON.
        # 'indent=4' formata o JSON de forma legível.
        json.dump(dados_para_salvar, f, indent=4, ensure_ascii=False)
    
    print(f"Personagem {personagem.nome} salvo com sucesso!")

def carregar_personagem(nome_personagem: str):
    """
    Esta função recebe o nome de um personagem, procura pelo arquivo .json correspondente,
    lê os dados e os usa para criar e retornar um novo objeto Personagem.
    """
    # Monta o caminho completo para o arquivo de save.
    caminho_arquivo = os.path.join(PASTA_SAVES, f"{nome_personagem}.json")

    # Verifica se o arquivo de save realmente existe.
    if not os.path.exists(caminho_arquivo):
        print("Arquivo de personagem não encontrado.")
        return None # Retorna None se não encontrar.

    # Abre o arquivo em modo de leitura ('r').
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        # 'json.load()' lê o arquivo JSON e o converte de volta para um dicionário Python.
        dados_carregados = json.load(f)

    # Desserialização: recria o objeto Personagem a partir do dicionário.
    personagem_carregado = Personagem(
        nome=dados_carregados["nome"],
        classe=dados_carregados["classe"],
        nivel=dados_carregados["nivel"],
        atributos=dados_carregados["atributos"],
        vida_atual=dados_carregados["vida_atual"],
        vida_maxima=dados_carregados["vida_maxima"],
        # O método .get(chave, valor_padrao) é usado para retrocompatibilidade.
        # Se um save antigo não tiver a chave 'inventario', ele usa uma lista vazia '[]' como padrão.
        inventario=dados_carregados.get("inventario", []),
        ouro=dados_carregados.get("ouro", 0),
        xp_atual=dados_carregados.get("xp_atual", 0),
        xp_proximo_nivel=dados_carregados.get("xp_proximo_nivel", 100),
        mana_atual=dados_carregados.get("mana_atual", 10),
        mana_maxima=dados_carregados.get("mana_maxima", 10),
        habilidades=dados_carregados.get("habilidades", [])
    )
    
    print(f"Personagem {personagem_carregado.nome} carregado com sucesso!")
    # Retorna o objeto Personagem recém-criado, pronto para ser usado no jogo.
    return personagem_carregado