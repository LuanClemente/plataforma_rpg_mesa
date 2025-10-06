# gerenciador_de_personagens.py
import json, os
from personagem import Personagem

PASTA_SAVES = "personagens_salvos"

def salvar_personagem(personagem):
    dados_para_salvar = {
        "nome": personagem.nome, "classe": personagem.classe, "nivel": personagem.nivel,
        "atributos": personagem.atributos, "vida_atual": personagem.vida_atual,
        "vida_maxima": personagem.vida_maxima, "inventario": personagem.inventario,
        "ouro": personagem.ouro,
        "xp_atual": personagem.xp_atual,                   # NOVO
        "xp_proximo_nivel": personagem.xp_proximo_nivel,   # NOVO
    }
    caminho_arquivo = os.path.join(PASTA_SAVES, f"{personagem.nome}.json")
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados_para_salvar, f, indent=4, ensure_ascii=False)
    print(f"Personagem {personagem.nome} salvo com sucesso!")

def carregar_personagem(nome_personagem):
    caminho_arquivo = os.path.join(PASTA_SAVES, f"{nome_personagem}.json")
    if not os.path.exists(caminho_arquivo): return None
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados_carregados = json.load(f)
    personagem_carregado = Personagem(
        nome=dados_carregados["nome"], classe=dados_carregados["classe"],
        nivel=dados_carregados["nivel"], atributos=dados_carregados["atributos"],
        vida_atual=dados_carregados["vida_atual"], vida_maxima=dados_carregados["vida_maxima"],
        inventario=dados_carregados.get("inventario", []), ouro=dados_carregados.get("ouro", 0),
        xp_atual=dados_carregados.get("xp_atual", 0),                   # NOVO
        xp_proximo_nivel=dados_carregados.get("xp_proximo_nivel", 100) # NOVO
    )
    print(f"Personagem {personagem_carregado.nome} carregado com sucesso!")
    return personagem_carregado