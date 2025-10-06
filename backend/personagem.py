# personagem.py

class Personagem:
    # Adicionamos xp_atual e xp_proximo_nivel ao construtor
    def __init__(self, nome, classe, nivel=1, atributos=None, vida_atual=None, vida_maxima=None, inventario=None, ouro=0, xp_atual=0, xp_proximo_nivel=100):
        self.nome = nome
        self.classe = classe
        self.nivel = nivel
        self.ouro = ouro
        # --- NOVOS ATRIBUTOS DE EXPERIÊNCIA ---
        self.xp_atual = xp_atual
        self.xp_proximo_nivel = xp_proximo_nivel
        
        self.atributos = atributos if atributos is not None else {
            "Força": 10, "Destreza": 10, "Constituição": 10,
            "Inteligência": 10, "Sabedoria": 10, "Carisma": 10
        }
        
        if vida_atual is None or vida_maxima is None:
            mod_constituicao = (self.atributos["Constituição"] - 10) // 2
            self.vida_maxima = 10 + mod_constituicao
            self.vida_atual = self.vida_maxima
        else:
            self.vida_atual = vida_atual
            self.vida_maxima = vida_maxima
            
        self.inventario = inventario if inventario is not None else []

    # --- NOVO MÉTODO PARA GANHAR XP ---
    def ganhar_xp(self, quantidade):
        """Adiciona XP e verifica se o personagem subiu de nível."""
        self.xp_atual += quantidade
        print(f"Você ganhou {quantidade} pontos de experiência!")
        if self.xp_atual >= self.xp_proximo_nivel:
            self.subir_de_nivel()

    # --- NOVO MÉTODO PARA SUBIR DE NÍVEL ---
    def subir_de_nivel(self):
        """Aplica as melhorias de um level up."""
        self.nivel += 1
        xp_excedente = self.xp_atual - self.xp_proximo_nivel
        self.xp_proximo_nivel = int(self.xp_proximo_nivel * 1.5) # Aumenta a dificuldade para o próximo
        self.xp_atual = xp_excedente

        # Aumenta a vida máxima
        aumento_vida = max(1, (self.atributos["Constituição"] - 10) // 2) + 5 # Exemplo de ganho de vida
        self.vida_maxima += aumento_vida
        self.vida_atual = self.vida_maxima # Cura total ao subir de nível!

        print("\n" + "="*20)
        print(f"  PARABÉNS! Você subiu para o Nível {self.nivel}!  ")
        print("="*20)
        print(f"Vida máxima aumentada para {self.vida_maxima}!")

        # Permite ao jogador aumentar um atributo
        print("Escolha um atributo para aumentar em 1 ponto:")
        atributos_lista = list(self.atributos.keys())
        for i, attr in enumerate(atributos_lista):
            print(f"{i + 1}. {attr} ({self.atributos[attr]})")
        
        while True:
            try:
                escolha = int(input("> ")) - 1
                if 0 <= escolha < len(atributos_lista):
                    attr_escolhido = atributos_lista[escolha]
                    self.atributos[attr_escolhido] += 1
                    print(f"{attr_escolhido} aumentado para {self.atributos[attr_escolhido]}!")
                    break
                else:
                    print("Escolha inválida.")
            except ValueError:
                print("Entrada inválida. Digite um número.")
        
        self.mostrar_ficha()
        
    def adicionar_item(self, item): self.inventario.append(item)
    def remover_item(self, item): self.inventario.remove(item)

    def mostrar_ficha(self):
        print("\n--- FICHA DE PERSONAGEM ---")
        print(f"Nome: {self.nome} | Classe: {self.classe} | Nível: {self.nivel}")
        # Mostra a barra de XP
        print(f"XP: {self.xp_atual}/{self.xp_proximo_nivel}")
        print(f"Vida: {self.vida_atual}/{self.vida_maxima} | Ouro: {self.ouro}")
        print("---------------------------")
        print("Atributos:")
        for atributo, valor in self.atributos.items():
            print(f"  {atributo}: {valor}")
        print("---------------------------")
        print("Inventário:")
        print("  (Vazio)" if not self.inventario else "\n".join(f"  - {item}" for item in self.inventario))
        print("---------------------------")