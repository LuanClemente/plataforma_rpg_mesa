# Este arquivo vai definir o "molde" para qualquer personagem do nosso jogo.

class Personagem:
    """
    Esta classe é o molde para criar personagens. Cada personagem criado a partir daqui
    terá as suas próprias informações (nome, classe, etc.).
    """

    # O método __init__ é um método especial chamado "construtor".
    # Ele é executado automaticamente sempre que um novo personagem é criado.
    # 'self' se refere ao próprio objeto que está sendo criado.
    def __init__(self, nome, classe, nivel):
        # Atributos são as variáveis que pertencem ao objeto.
        # Aqui estamos a dizer: "O nome deste personagem será o 'nome' que recebemos".
        self.nome = nome
        self.classe = classe
        self.nivel = nivel
        
        # Vamos guardar os atributos principais num dicionário.
        # Um dicionário é uma estrutura que armazena pares de chave-valor.
        # Por agora, vamos começar com todos os atributos em 10.
        self.atributos = {
            "Força": 10,
            "Destreza": 10,
            "Constituição": 10,
            "Inteligência": 10,
            "Sabedoria": 10,
            "Carisma": 10
        }
        
        # Poderíamos adicionar mais coisas aqui no futuro, como inventário, vida, etc.
        self.vida_atual = 10
        self.vida_maxima = 10

    # Isto é um "método". Um método é uma função que pertence a uma classe.
    # Ele pode aceder e manipular os dados do próprio objeto (usando 'self').
    def mostrar_ficha(self):
        """
        Este método imprime a ficha do personagem no console de forma organizada.
        """
        print("--- FICHA DE PERSONAGEM ---")
        print(f"Nome: {self.nome}")
        print(f"Classe: {self.classe}")
        print(f"Nível: {self.nivel}")
        print("---------------------------")
        print("Atributos:")
        # O loop 'for' vai passar por cada item no nosso dicionário de atributos.
        for atributo, valor in self.atributos.items():
            print(f"  {atributo}: {valor}")
        print("---------------------------")


# --- Exemplo de Utilização ---
# Este bloco de código só será executado quando rodarmos este arquivo diretamente.
# É uma convenção em Python para testes e demonstrações.
if __name__ == "__main__":
    
    # Agora estamos a usar o nosso "molde" (a classe) para criar um personagem real (um objeto).
    # Isto chama o método __init__ e passa os valores para nome, classe e nivel.
    heroi_exemplo = Personagem(nome="Aragorn", classe="Guerreiro", nivel=5)
    
    # Uma vez que o objeto 'heroi_exemplo' foi criado, podemos chamar os seus métodos.
    heroi_exemplo.mostrar_ficha()
    
    print("\n") # Apenas uma linha em branco para separar

    # Podemos criar quantos personagens quisermos a partir do mesmo molde!
    outro_heroi = Personagem(nome="Gandalf", classe="Mago", nivel=10)
    outro_heroi.mostrar_ficha()