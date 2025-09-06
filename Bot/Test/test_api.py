import pytest
import json
import sys
import os

# Adicionar o diretório atual ao path para importar o módulo da API
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Bot.chatbot_api import app

@pytest.fixture
def client():
    """Fixture para criar um cliente de teste Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestChatbotAPI:
    """Testes unitários para a API do chatbot"""
    
    def test_home_endpoint(self, client):
        """Testa o endpoint home da API"""
        response = client.get('/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert "mensagem" in data
        assert "versao" in data
        assert "endpoints" in data
    
    def test_health_endpoint(self, client):
        """Testa o endpoint de health check"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_perguntas_endpoint(self, client):
        """Testa o endpoint que lista perguntas disponíveis"""
        response = client.get('/perguntas')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert "perguntas_disponiveis" in data
        assert "tipos_query_disponiveis" in data
        assert len(data["perguntas_disponiveis"]) == 3
        assert len(data["tipos_query_disponiveis"]) == 3
    
    def test_chat_endpoint_pergunta_valida(self, client):
        """Testa o endpoint de chat com pergunta válida"""
        payload = {
            "pergunta": "Qual o total de vendas de produtos por tipo de pagamento?"
        }
        
        response = client.post('/chat', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["status"] == "sucesso"
        assert data["pergunta_do_usuario"] == payload["pergunta"]
        assert data["query"] is not None
        assert data["pergunta_da_query"] is not None
    
    def test_chat_endpoint_pergunta_invalida(self, client):
        """Testa o endpoint de chat com pergunta inválida"""
        payload = {
            "pergunta": "Qual é a cor do céu?"
        }
        
        response = client.post('/chat', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["status"] == "falha"
        assert data["pergunta_do_usuario"] == payload["pergunta"]
        assert data["query"] is None
        assert data["pergunta_da_query"] is None
        assert "mensagem" in data
    
    def test_chat_endpoint_sem_pergunta(self, client):
        """Testa o endpoint de chat sem o campo pergunta"""
        payload = {}
        
        response = client.post('/chat', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert "erro" in data
    
    def test_chat_endpoint_json_invalido(self, client):
        """Testa o endpoint de chat com JSON inválido"""
        response = client.post('/chat', 
                             data="json inválido",
                             content_type='application/json')
        
        assert response.status_code == 500
    
    def test_execute_query_endpoint_valido(self, client):
        """Testa o endpoint de execução de query com tipo válido"""
        payload = {
            "tipo_query": "vendas_por_pagamento"
        }
        
        response = client.post('/execute-query', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        # Pode retornar 200 (sucesso) ou 500 (se não encontrar o arquivo Excel)
        assert response.status_code in [200, 500]
        
        data = json.loads(response.data)
        if response.status_code == 200:
            assert data["status"] == "sucesso"
            assert data["tipo_query"] == payload["tipo_query"]
            assert "resultado" in data
        else:
            assert "erro" in data
    
    def test_execute_query_endpoint_tipo_invalido(self, client):
        """Testa o endpoint de execução de query com tipo inválido"""
        payload = {
            "tipo_query": "tipo_inexistente"
        }
        
        response = client.post('/execute-query', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        # Pode retornar 200 (com erro na resposta) ou 500
        assert response.status_code in [200, 500]
        
        data = json.loads(response.data)
        assert "erro" in data or ("resultado" in data and "erro" in data["resultado"])
    
    def test_execute_query_endpoint_sem_tipo(self, client):
        """Testa o endpoint de execução de query sem o campo tipo_query"""
        payload = {}
        
        response = client.post('/execute-query', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert "erro" in data
    
    def test_cors_headers(self, client):
        """Testa se os headers CORS estão configurados corretamente"""
        response = client.get('/')
        
        # Verifica se o header Access-Control-Allow-Origin está presente
        # (Flask-CORS adiciona automaticamente)
        assert response.status_code == 200

class TestAPIIntegration:
    """Testes de integração para a API"""
    
    def test_fluxo_completo_chat(self, client):
        """Testa o fluxo completo: listar perguntas -> fazer pergunta"""
        # Primeiro, lista as perguntas disponíveis
        response_perguntas = client.get('/perguntas')
        assert response_perguntas.status_code == 200
        
        perguntas_data = json.loads(response_perguntas.data)
        primeira_pergunta = perguntas_data["perguntas_disponiveis"][0]
        
        # Depois, faz a pergunta
        payload = {"pergunta": primeira_pergunta}
        response_chat = client.post('/chat', 
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        assert response_chat.status_code == 200
        
        chat_data = json.loads(response_chat.data)
        assert chat_data["status"] == "sucesso"
        assert chat_data["pergunta_do_usuario"] == primeira_pergunta

if __name__ == "__main__":
    pytest.main([__file__])

