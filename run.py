import sys
import os

# Adicionar o diretório src ao PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.game.main import main

if __name__ == '__main__':
    main() 