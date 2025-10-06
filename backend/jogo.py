# --- Importando as nossas ferramentas ---
# Do arquivo personagem.py, estamos a importar a classe Personagem.
from personagem import Personagem
# Do arquivo rolador_de_dados.py, estamos a importar a função rolar_dados.
from rolador_de_dados import rolar_dados

def calcular_modificador(valor_atributo):
    """
    Calcula o modificador de um atributo seguindo a regra do D&D 5e.
    Fórmula: (valor - 10) / 2, arredondado para baixo.
    """
    return (valor_atributo - 10) // 2

# --- Configuração Inicial do Jogo ---
print("--- Aventura a postos! ---")

# Criamos o nosso herói para esta sessão de jogo.
jogador = Personagem(nome="Kael", classe="Ladino", nivel=3)

# Alteramos um atributo para o nosso teste ficar mais interessante.
jogador.atributos["Destreza"] = 16 

# --- Loop Principal do Jogo ---
while True:
    print("\n--- O que você deseja fazer? ---")
    print("1. Fazer um teste de Destreza")
    print("2. Ver a ficha do personagem")
    print("Digite 'sair' para terminar a aventura.")

    escolha = input("> ").strip()

    if escolha == '1':
        # Pega o valor do atributo 'Destreza' do nosso jogador.
        valor_destreza = jogador.atributos["Destreza"]
        
        # Calcula o modificador correspondente.
        modificador = calcular_modificador(valor_destreza)
        
        # Rola um d20 usando a nossa função importada.
        # O '_' é para ignorar o segundo valor retornado (a lista de rolagens).
        resultado_dado, _ = rolar_dados("d20")
        
        # Soma o resultado do dado com o modificador.
        total_teste = resultado_dado + modificador
        
        print("\n--- Teste de Destreza ---")
        print(f"Rolagem do d20: {resultado_dado}")
        print(f"Modificador de Destreza ({valor_destreza}): +{modificador}")
        print(f"Resultado Total: {total_teste}")

    elif escolha == '2':
        # Chama o método do próprio objeto para mostrar a sua ficha.
        jogador.mostrar_ficha()
        
    elif escolha.lower() == 'sair':
        print("A sua jornada termina aqui... por enquanto.")
        break # Encerra o loop e o programa.
        
    else:
        print("Comando desconhecido, nobre aventureiro.")