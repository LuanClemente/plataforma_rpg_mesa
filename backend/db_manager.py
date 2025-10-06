# db_manager.py

import sqlite3
from monstro import Monstro # Precisamos saber como "construir" um monstro

NOME_DB = "campanhas.db"

def buscar_monstro_aleatorio():
    """
    Conecta ao banco de dados, busca um monstro aleatório da tabela 'monstros_base'
    e retorna um objeto Monstro totalmente instanciado.
    """
    try:
        conexao = sqlite3.connect(NOME_DB)
        cursor = conexao.cursor()

        # Esta é a nossa consulta SQL para buscar um monstro aleatório.
        # - SELECT * FROM monstros_base: Seleciona todas as colunas da tabela.
        # - ORDER BY RANDOM(): Embaralha todas as linhas da tabela aleatoriamente.
        # - LIMIT 1: Pega apenas a primeira linha do resultado embaralhado.
        cursor.execute("SELECT * FROM monstros_base ORDER BY RANDOM() LIMIT 1")
        
        # cursor.fetchone() busca apenas um resultado, que é o que queremos.
        dados_monstro = cursor.fetchone()
        
        conexao.close()

        if dados_monstro:
            # Os dados vêm como uma tupla: (id, nome, vida, ataque, dano, defesa, xp, ouro)
            # Vamos "desempacotar" esses dados para criar nosso objeto Monstro.
            # Note que pulamos o índice 0, que é o 'id'.
            monstro_encontrado = Monstro(
                nome=dados_monstro[1],
                vida_maxima=dados_monstro[2],
                ataque_bonus=dados_monstro[3],
                dano_dado=dados_monstro[4],
                defesa=dados_monstro[5],
                xp_oferecido=dados_monstro[6],
                ouro_drop=dados_monstro[7]
            )
            return monstro_encontrado
        else:
            # Caso a tabela de monstros esteja vazia.
            return None
            
    except sqlite3.Error as e:
        print(f"Erro ao buscar monstro no banco de dados: {e}")
        return None