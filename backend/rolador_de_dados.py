# Importa a biblioteca 'random' para gerar números aleatórios.
import random

def rolar_dados(comando):
    """
    Esta função recebe um comando de texto (ex: "2d6") e retorna o resultado da rolagem.
    """
    try:
        # Divide o comando no caractere 'd'. Ex: "2d6" se torna ["2", "6"].
        partes = comando.lower().split('d')

        # Converte a primeira parte para um número inteiro (quantidade de dados).
        quantidade_dados = int(partes[0]) if partes[0] else 1
        
        # Converte a segunda parte para um número inteiro (número de lados).
        numero_lados = int(partes[1])

        # Guarda os resultados individuais.
        rolagens_individuais = []
        
        # Rola cada dado individualmente.
        for _ in range(quantidade_dados):
            rolagem = random.randint(1, numero_lados)
            rolagens_individuais.append(rolagem)
            
        # Retorna a soma total e a lista de rolagens.
        return sum(rolagens_individuais), rolagens_individuais

    except (ValueError, IndexError):
        # Se o comando for inválido, retorna None.
        return None, None

# --- Início do Programa Principal ---

print("--- Bem-vindo à Taverna do Dragão Programador! ---")
print("Use o formato 'XdY' para rolar os dados (ex: 'd20', '2d6', '1d100').")
print("Digite 'sair' a qualquer momento para fechar o programa.")

# Este é o loop principal do jogo. Ele continuará a rodar para sempre até
# que o usuário digite 'sair'.
while True:
    # Pede ao usuário para inserir o comando de rolagem e remove espaços em branco.
    entrada_usuario = input("\nQual dado você quer rolar? ").strip()

    # Verifica se o usuário quer encerrar o programa.
    if entrada_usuario.lower() == 'sair':
        print("Até a próxima aventura!")
        break # O comando 'break' interrompe o loop 'while'.

    # Chama a nossa função para processar o comando do usuário.
    total, rolagens = rolar_dados(entrada_usuario)

    # Verifica se a função retornou um resultado válido.
    if total is not None:
        # Se a rolagem foi válida, mostra o resultado.
        print(f"Resultado de {entrada_usuario}: {total}")
        # Se mais de um dado foi rolado, também mostra os resultados individuais.
        if len(rolagens) > 1:
            print(f"Rolagens individuais: {rolagens}")
    else:
        # Se a função retornou None, significa que o comando era inválido.
        print("Comando inválido. Por favor, use o formato 'XdY' (ex: 'd20' ou '3d8').")