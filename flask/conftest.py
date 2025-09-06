import pytest
import os
import sys

# Adicionar o diretório atual ao path para importar os módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def pytest_configure(config):
    """Configuração global do pytest"""
    # Configurar variáveis de ambiente para testes
    os.environ['TESTING'] = 'True'

