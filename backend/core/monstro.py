# core/monstro.py

# A classe Monstro é o "molde" para criar qualquer inimigo no jogo.
class Monstro:
    """
    Uma classe para representar os inimigos no jogo. Ela armazena os atributos
    de combate de uma criatura.
    """
    # O método __init__ é o construtor, chamado ao criar um novo monstro.
    # Ele recebe todos os status que definem a criatura.
    def __init__(self, nome: str, vida_maxima: int, ataque_bonus: int, dano_dado: str, defesa: int, xp_oferecido: int, ouro_drop: int):
        
        # --- Atributos de Identificação ---
        # O nome do monstro (ex: "Goblin", "Orc").
        self.nome = nome

        # --- Atributos de Combate ---
        # A quantidade máxima de pontos de vida que o monstro pode ter.
        self.vida_maxima = vida_maxima
        # A vida atual do monstro, que começa sempre no máximo.
        self.vida_atual = vida_maxima
        # Um bônus fixo somado à rolagem de ataque (d20) do monstro.
        self.ataque_bonus = ataque_bonus
        # Uma string que representa o dado de dano do monstro (ex: "1d6", "2d8").
        self.dano_dado = dano_dado
        # O valor de "Classe de Armadura" (AC). O jogador precisa rolar um valor igual ou maior para acertar.
        self.defesa = defesa

        # --- Atributos de Recompensa ---
        # A quantidade de pontos de experiência que o monstro concede ao ser derrotado.
        self.xp_oferecido = xp_oferecido
        # A quantidade de ouro que o monstro deixa cair ao ser derrotado.
        self.ouro_drop = ouro_drop