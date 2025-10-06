# core/rolador_de_dados.py

# Importa a biblioteca 'random', que é a ferramenta padrão do Python para gerar números aleatórios.
import random

def rolar_dados(comando: str):
    """
    Esta função recebe um comando de texto no formato 'NdY' (ex: "2d6", "d20")
    e retorna a soma total da rolagem e uma lista com os resultados individuais.
    """
    # O bloco 'try...except' lida com possíveis erros se o comando for mal formatado (ex: "banana").
    try:
        # Converte o comando para minúsculas e o divide no caractere 'd'.
        # Ex: "2d6" se torna uma lista ["2", "6"]. "d20" se torna ["", "20"].
        partes = comando.lower().split('d')

        # Pega a primeira parte (quantidade de dados).
        # 'if partes[0]' verifica se a primeira parte não está vazia.
        # Se estiver vazia (como em "d20"), a quantidade de dados é 1.
        # Senão, converte a primeira parte (ex: "2") para um número inteiro.
        quantidade_dados = int(partes[0]) if partes[0] else 1
        
        # Pega a segunda parte (número de lados do dado) e a converte para um número inteiro.
        numero_lados = int(partes[1])

        # Cria uma lista vazia para guardar os resultados de cada rolagem individual.
        rolagens_individuais = []
        
        # Este 'for' loop vai se repetir 'quantidade_dados' vezes.
        # O '_' é uma convenção em Python para uma variável que não vamos usar.
        for _ in range(quantidade_dados):
            # 'random.randint(A, B)' gera um número inteiro aleatório entre A e B (inclusivo).
            # Simulando a rolagem de um único dado.
            rolagem = random.randint(1, numero_lados)
            # Adiciona o resultado desta rolagem à nossa lista de resultados.
            rolagens_individuais.append(rolagem)
            
        # 'sum()' é uma função do Python que soma todos os números de uma lista.
        # Retorna a soma total e a lista de rolagens para possível exibição detalhada.
        return sum(rolagens_individuais), rolagens_individuais

    # Se ocorrer um erro durante a conversão para 'int' (ValueError) ou ao acessar partes[1] (IndexError)...
    except (ValueError, IndexError):
        # ...significa que o comando era inválido.
        # Informa o erro no console para ajudar a depurar.
        print(f"ERRO: Comando de rolagem de dados inválido: '{comando}'")
        # Retorna 0 e uma lista vazia como um resultado de falha seguro.
        return 0, []