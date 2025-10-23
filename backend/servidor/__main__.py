# servidor/__main__.py
"""
Este arquivo permite que o pacote 'servidor' seja executável.
Executar `python -m servidor` na pasta `backend` irá rodar este script.
"""
from . import servidor_api

if __name__ == "__main__":
    # Inicia o servidor Flask/SocketIO definido em servidor_api.py
    servidor_api.socketio.run(servidor_api.app, debug=True, port=5001, host='0.0.0.0')