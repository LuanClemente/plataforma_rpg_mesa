# -*- coding: utf-8 -*-
"""
Remove eventlet e corrige async_mode para threading no servidor_api.py.
Execute na raiz do projeto:
  venv\\Scripts\\python.exe fix_eventlet.py
"""
import os, re

CAMINHOS = [
    os.path.join('backend', 'servidor', 'servidor_api.py'),
]

for caminho in CAMINHOS:
    if not os.path.exists(caminho):
        print(f"NAO ENCONTRADO: {caminho}")
        continue

    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    original = c

    # 1. Remover import eventlet e eventlet.monkey_patch
    c = re.sub(r'^import eventlet\s*\n', '', c, flags=re.MULTILINE)
    c = re.sub(r'^eventlet\.monkey_patch\(\)\s*\n', '', c, flags=re.MULTILINE)

    # 2. Trocar async_mode='eventlet' por async_mode='threading'
    c = c.replace("async_mode='eventlet'", "async_mode='threading'")
    c = c.replace('async_mode="eventlet"', "async_mode='threading'")

    # 3. Garantir que socketio.run usa allow_unsafe_werkzeug=True
    c = re.sub(
        r"socketio\.run\(app.*?\)",
        "socketio.run(app, host='0.0.0.0', port=5003, debug=False, allow_unsafe_werkzeug=True)",
        c, flags=re.DOTALL
    )

    if c != original:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"CORRIGIDO: {caminho}")
    else:
        print(f"SEM ALTERACOES (eventlet nao encontrado ou ja corrigido): {caminho}")