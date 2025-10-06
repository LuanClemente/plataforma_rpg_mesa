# saves/saves_manager.py

# Importa a biblioteca 'json' para trabalhar com o formato de dados JSON.
import json
# Importa a biblioteca 'os' para interagir com o sistema operacional, como criar pastas e verificar caminhos.
import os
# Importa a classe 'Personagem' do nosso pacote 'core' para que possamos criar um objeto dela ao carregar.
from core.personagem import Personagem

# Define o caminho relativo para a pasta onde os arquivos de save dos personagens serão guardados.
# A partir da raiz do 'backend', ele entrará em 'saves' e depois em 'personagens_salvos'.
PASTA_SAVES = "saves/personagens_salvos"

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
    # Esta é a etapa de "serialização": transformar um objeto complexo em uma estrutura de dados simples.
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
    # 'os.path.join' é a forma mais segura de construir caminhos de arquivo, funcionando em qualquer sistema operacional.
    caminho_arquivo = os.path.join(PASTA_SAVES, f"{personagem.nome}.json")

    # O bloco 'with open(...)' abre o arquivo e garante que ele seja fechado automaticamente no final.
    # 'w' significa que abrimos o arquivo em modo de escrita (write), apagando qualquer conteúdo anterior.
    # 'encoding='utf-8'' garante que caracteres especiais (como acentos) sejam salvos corretamente.
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        # 'json.dump()' é a função que efetivamente escreve o dicionário no arquivo em formato JSON.
        # 'indent=4' formata o arquivo JSON de forma legível para humanos, com 4 espaços de indentação.
        # 'ensure_ascii=False' também ajuda na codificação correta de caracteres especiais.
        json.dump(dados_para_salvar, f, indent=4, ensure_ascii=False)
    
    # Informa ao usuário que o processo foi concluído com sucesso.
    print(f"Personagem {personagem.nome} salvo com sucesso!")

def carregar_personagem(nome_personagem: str):
    """
    Esta função recebe o nome de um personagem, procura pelo arquivo .json correspondente,
    lê os dados e os usa para criar e retornar um novo objeto Personagem.
    """
    # Monta o caminho completo para o arquivo de save do personagem solicitado.
    caminho_arquivo = os.path.join(PASTA_SAVES, f"{nome_personagem}.json")

    # Verifica se o arquivo de save realmente existe no caminho especificado.
    if not os.path.exists(caminho_arquivo):
        # Se não existir, informa o usuário e retorna 'None' para indicar que o personagem não foi encontrado.
        print("Arquivo de personagem não encontrado.")
        return None

    # Abre o arquivo em modo de leitura ('r' de read).
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        # 'json.load()' lê o conteúdo do arquivo JSON e o converte de volta para um dicionário Python.
        dados_carregados = json.load(f)

    # Esta é a etapa de "desserialização": usar o dicionário de dados simples para reconstruir nosso objeto complexo.
    # Chamamos o construtor da classe Personagem, passando cada valor do dicionário para o parâmetro correspondente.
    personagem_carregado = Personagem(
        nome=dados_carregados["nome"],
        classe=dados_carregados["classe"],
        nivel=dados_carregados["nivel"],
        atributos=dados_carregados["atributos"],
        vida_atual=dados_carregados["vida_atual"],
        vida_maxima=dados_carregados["vida_maxima"],
        # O método .get(chave, valor_padrao) é usado para retrocompatibilidade.
        # Ele tenta pegar o valor da chave 'inventario'. Se não encontrar (em um save antigo),
        # ele usa o valor padrão (uma lista vazia []), em vez de dar um erro.
        inventario=dados_carregados.get("inventario", []),
        ouro=dados_carregados.get("ouro", 0),
        xp_atual=dados_carregados.get("xp_atual", 0),
        xp_proximo_nivel=dados_carregados.get("xp_proximo_nivel", 100),
        mana_atual=dados_carregados.get("mana_atual", 10),
        mana_maxima=dados_carregados.get("mana_maxima", 10),
        habilidades=dados_carregados.get("habilidades", [])
    )
    
    # Informa ao usuário que o personagem foi carregado.
    print(f"Personagem {personagem_carregado.nome} carregado com sucesso!")
    # Retorna o objeto Personagem recém-criado, pronto para ser usado no jogo.
    return personagem_carregado