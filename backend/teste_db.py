# backend/teste_db.py
import sqlite3
import os

print("--- Iniciando Teste de Sanidade do Banco de Dados ---")

try:
    # Vamos tentar criar um banco de dados simples na pasta atual (backend).
    nome_arquivo_teste = "teste.db"
    
    # Se o arquivo já existir de um teste anterior, vamos apagá-lo.
    if os.path.exists(nome_arquivo_teste):
        os.remove(nome_arquivo_teste)
        print(f"Arquivo '{nome_arquivo_teste}' antigo removido.")

    # Tenta conectar (e criar) o novo banco de dados.
    print(f"Tentando criar o arquivo '{nome_arquivo_teste}'...")
    conexao = sqlite3.connect(nome_arquivo_teste)
    
    # Se chegamos aqui, a conexão funcionou!
    print(">>> SUCESSO! Conexão estabelecida e arquivo criado.")
    
    cursor = conexao.cursor()
    
    # Tenta criar uma tabela simples.
    cursor.execute("CREATE TABLE teste (id INTEGER)")
    print(">>> SUCESSO! Tabela de teste criada.")
    
    conexao.commit()
    conexao.close()
    print("Operação concluída com sucesso.")

except Exception as e:
    # Se qualquer um dos passos acima falhar, este bloco será executado.
    print("\n--- OCORREU UM ERRO! ---")
    print(f"Tipo do Erro: {type(e).__name__}")
    print(f"Mensagem: {e}")

print("\n--- Teste de Sanidade Concluído ---")