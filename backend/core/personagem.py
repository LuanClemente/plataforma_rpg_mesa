# core/personagem.py

# A classe Personagem é o "molde" ou a "planta" para criar qualquer personagem jogável.
# Ela centraliza todos os dados e ações que um personagem pode ter.
class Personagem:
    # O método __init__ é o "construtor" da classe. Ele é chamado sempre que um novo personagem é criado.
    # Ele recebe todos os dados iniciais do personagem. Parâmetros com '=' têm um valor padrão.
    def __init__(self, nome, classe, nivel=1, atributos=None, vida_atual=None, vida_maxima=None, 
                 inventario=None, ouro=0, xp_atual=0, xp_proximo_nivel=100, 
                 mana_atual=None, mana_maxima=None, habilidades=None):
        
        # --- Atributos Básicos ---
        self.nome = nome                  # O nome do personagem, definido na criação.
        self.classe = classe              # A classe do personagem (Guerreiro, Mago, etc.).
        self.nivel = nivel                # O nível atual do personagem.
        self.ouro = ouro                  # A quantidade de moedas de ouro que o personagem possui.

        # --- Atributos de Progressão ---
        self.xp_atual = xp_atual          # Pontos de experiência acumulados no nível atual.
        self.xp_proximo_nivel = xp_proximo_nivel # Total de XP necessário para o próximo nível.

        # --- Atributos de Combate (Dicionário) ---
        # Se 'atributos' não for fornecido ao criar o personagem (None), cria um dicionário padrão.
        self.atributos = atributos if atributos is not None else {
            "Força": 10, "Destreza": 10, "Constituição": 10,
            "Inteligência": 10, "Sabedoria": 10, "Carisma": 10
        }

        # --- Pontos de Vida (HP) ---
        # Se a vida não for fornecida (ao criar um novo personagem), calcula-a com base na Constituição.
        if vida_atual is None or vida_maxima is None:
            # Calcula o bônus de Constituição: (valor - 10) / 2.
            mod_constituicao = (self.atributos["Constituição"] - 10) // 2
            # Define a vida máxima com base numa fórmula (ex: 10 + bônus).
            self.vida_maxima = 10 + mod_constituicao
            # Um personagem novo sempre começa com a vida cheia.
            self.vida_atual = self.vida_maxima
        # Se a vida for fornecida (ao carregar um jogo salvo), usa os valores recebidos.
        else:
            self.vida_atual = vida_atual
            self.vida_maxima = vida_maxima

        # --- Pontos de Mana (MP) ---
        # Lógica similar à da vida, mas baseada em Inteligência.
        if mana_atual is None or mana_maxima is None:
            # Calcula o bônus de Inteligência.
            mod_inteligencia = (self.atributos["Inteligência"] - 10) // 2
            # Define a mana máxima com base numa fórmula (ex: 10 + dobro do bônus).
            self.mana_maxima = max(0, 10 + (mod_inteligencia * 2))
            # Começa com a mana cheia.
            self.mana_atual = self.mana_maxima
        # Se a mana for fornecida, usa os valores recebidos.
        else:
            self.mana_atual = mana_atual
            self.mana_maxima = mana_maxima

        # --- Inventário e Habilidades (Listas) ---
        # Se o inventário não for fornecido, começa com uma lista vazia.
        self.inventario = inventario if inventario is not None else []
        # Se as habilidades não forem fornecidas, começa com uma lista vazia.
        self.habilidades = habilidades if habilidades is not None else []

    # --- Métodos de Ação e Gerenciamento ---

    def ganhar_xp(self, quantidade):
        """Este método adiciona XP ao personagem e verifica se ele subiu de nível."""
        # Aumenta o XP atual com a quantidade recebida.
        self.xp_atual += quantidade
        # Informa ao jogador sobre o ganho de XP.
        print(f"Você ganhou {quantidade} pontos de experiência!")
        # Se o XP atual atingir ou ultrapassar o necessário para o próximo nível...
        if self.xp_atual >= self.xp_proximo_nivel:
            # ...chama o método que cuida do processo de subir de nível.
            self.subir_de_nivel()

    def subir_de_nivel(self):
        """Este método aplica todas as melhorias quando o personagem sobe de nível."""
        # Aumenta o contador de nível em 1.
        self.nivel += 1
        # Calcula o XP que "sobrou" após subir de nível.
        xp_excedente = self.xp_atual - self.xp_proximo_nivel
        # Define a nova meta de XP para o próximo nível (ex: 50% a mais).
        self.xp_proximo_nivel = int(self.xp_proximo_nivel * 1.5)
        # O XP atual começa com o valor excedente do nível anterior.
        self.xp_atual = xp_excedente

        # Aumenta a vida máxima do personagem.
        aumento_vida = max(1, (self.atributos["Constituição"] - 10) // 2) + 5
        self.vida_maxima += aumento_vida
        # Ao subir de nível, o personagem é totalmente curado.
        self.vida_atual = self.vida_maxima

        # Imprime uma mensagem de celebração para o jogador.
        print("\n" + "="*42)
        print(f"  PARABÉNS! Você subiu para o Nível {self.nivel}!  ")
        print("="*42)
        print(f"Vida máxima aumentada para {self.vida_maxima}!")

        # Loop interativo para o jogador escolher um atributo para melhorar.
        print("Escolha um atributo para aumentar em 1 ponto:")
        # Pega a lista de nomes dos atributos.
        atributos_lista = list(self.atributos.keys())
        # Exibe os atributos numerados para facilitar a escolha.
        for i, attr in enumerate(atributos_lista):
            print(f"{i + 1}. {attr} ({self.atributos[attr]})")
        
        # O loop continua até que o jogador faça uma escolha válida.
        while True:
            try:
                # Pede ao jogador para digitar um número.
                escolha = int(input("> ")) - 1 # Subtrai 1 para alinhar com o índice da lista (que começa em 0).
                # Verifica se o número escolhido é um índice válido.
                if 0 <= escolha < len(atributos_lista):
                    # Pega o nome do atributo escolhido.
                    attr_escolhido = atributos_lista[escolha]
                    # Aumenta o valor do atributo em 1.
                    self.atributos[attr_escolhido] += 1
                    # Informa a mudança ao jogador.
                    print(f"{attr_escolhido} aumentado para {self.atributos[attr_escolhido]}!")
                    # Interrompe o loop de escolha.
                    break
                else:
                    # Informa se o número estiver fora do intervalo.
                    print("Escolha inválida.")
            except ValueError:
                # Informa se o jogador digitar algo que não seja um número.
                print("Entrada inválida. Digite um número.")

    def adicionar_item(self, item):
        """Adiciona um item (string) à lista de inventário."""
        self.inventario.append(item)
        # Não imprimimos nada aqui para não poluir a tela (a loja já informa).

    def remover_item(self, item):
        """Remove um item do inventário, se ele existir."""
        # Verifica se o item está na lista antes de tentar removê-lo.
        if item in self.inventario:
            # Remove a primeira ocorrência do item.
            self.inventario.remove(item)
        else:
            # Informa caso o item não seja encontrado (prevenção de erros).
            print(f"Tentativa de remover item não existente: {item}")
    
    def curar(self, quantidade):
        """Aumenta a vida atual do personagem, sem ultrapassar a vida máxima."""
        # Adiciona a quantidade de cura à vida atual.
        self.vida_atual += quantidade
        # Se a vida passar do máximo, define-a como o máximo.
        if self.vida_atual > self.vida_maxima:
            self.vida_atual = self.vida_maxima
        # Informa ao jogador sobre a cura.
        print(f"Você se curou em {quantidade} pontos de vida! Vida atual: {self.vida_atual}/{self.vida_maxima}")

    def mostrar_ficha(self):
        """Imprime no console uma visualização completa e organizada da ficha do personagem."""
        # Cabeçalho da ficha.
        print("\n--- FICHA DE PERSONAGEM ---")
        # Linha com informações básicas.
        print(f"Nome: {self.nome} | Classe: {self.classe} | Nível: {self.nivel}")
        # Linha de progressão.
        print(f"XP: {self.xp_atual}/{self.xp_proximo_nivel}")
        # Linha de recursos (HP, MP, Ouro).
        print(f"Vida: {self.vida_atual}/{self.vida_maxima} | Mana: {self.mana_atual}/{self.mana_maxima} | Ouro: {self.ouro}")
        # Divisor visual.
        print("---------------------------")
        # Seção de atributos.
        print("Atributos:")
        # Itera sobre o dicionário de atributos para imprimir cada um.
        for atributo, valor in self.atributos.items():
            print(f"  {atributo}: {valor}")
        # Divisor visual.
        print("---------------------------")
        # Seção de inventário.
        print("Inventário:")
        # Se a lista de inventário estiver vazia, imprime "(Vazio)".
        if not self.inventario:
            print("  (Vazio)")
        # Se não, itera sobre a lista e imprime cada item.
        else:
            for item in self.inventario:
                print(f"  - {item}")
        # Divisor visual.
        print("---------------------------")