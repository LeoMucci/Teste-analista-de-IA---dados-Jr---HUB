import pytest
import sys
import os

# Adicionar o diretório atual ao path para importar o módulo chatbot
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chatbot import chatbot_response

class TestChatbot:
    """Testes unitários para a função chatbot_response"""
    
    def test_pergunta_valida_vendas_pagamento(self):
        """Testa resposta para pergunta válida sobre vendas por tipo de pagamento"""
        pergunta = "Qual o total de vendas de produtos por tipo de pagamento?"
        resposta = chatbot_response(pergunta)
        
        assert resposta["status"] == "sucesso"
        assert resposta["pergunta_do_usuario"] == pergunta
        assert resposta["query"] is not None
        assert "SELECT" in resposta["query"]
        assert "payment_method_type" in resposta["query"]
        assert resposta["pergunta_da_query"] is not None
    
    def test_pergunta_valida_produtos_vendidos(self):
        """Testa resposta para pergunta válida sobre produtos mais vendidos"""
        pergunta = "Quais os produtos mais vendidos em termos de quantidade?"
        resposta = chatbot_response(pergunta)
        
        assert resposta["status"] == "sucesso"
        assert resposta["pergunta_do_usuario"] == pergunta
        assert resposta["query"] is not None
        assert "SELECT" in resposta["query"]
        assert "product" in resposta["query"]
        assert resposta["pergunta_da_query"] is not None
    
    def test_pergunta_valida_estadias_pet(self):
        """Testa resposta para pergunta válida sobre estadias por pet"""
        pergunta = "Qual o custo total das estadias por pet?"
        resposta = chatbot_response(pergunta)
        
        assert resposta["status"] == "sucesso"
        assert resposta["pergunta_do_usuario"] == pergunta
        assert resposta["query"] is not None
        assert "SELECT" in resposta["query"]
        assert "stay" in resposta["query"]
        assert resposta["pergunta_da_query"] is not None
    
    def test_pergunta_invalida(self):
        """Testa resposta para pergunta inválida"""
        pergunta = "Qual é a cor do céu?"
        resposta = chatbot_response(pergunta)
        
        assert resposta["status"] == "falha"
        assert resposta["pergunta_do_usuario"] == pergunta
        assert resposta["query"] is None
        assert resposta["pergunta_da_query"] is None
        assert "mensagem" in resposta
    
    def test_pergunta_vazia(self):
        """Testa resposta para pergunta vazia"""
        pergunta = ""
        resposta = chatbot_response(pergunta)
        
        assert resposta["status"] == "falha"
        assert resposta["pergunta_do_usuario"] == pergunta
        assert resposta["query"] is None
        assert resposta["pergunta_da_query"] is None
    
    def test_pergunta_case_insensitive(self):
        """Testa se o chatbot é case insensitive"""
        pergunta = "QUAL O TOTAL DE VENDAS DE PRODUTOS POR TIPO DE PAGAMENTO?"
        resposta = chatbot_response(pergunta)
        
        assert resposta["status"] == "sucesso"
        assert resposta["pergunta_do_usuario"] == pergunta
        assert resposta["query"] is not None
    
    def test_pergunta_com_espacos_extras(self):
        """Testa pergunta com espaços extras no início e fim"""
        pergunta = "   Qual o total de vendas de produtos por tipo de pagamento?   "
        resposta = chatbot_response(pergunta)
        
        assert resposta["status"] == "sucesso"
        assert resposta["pergunta_do_usuario"] == pergunta
        assert resposta["query"] is not None
    
    def test_estrutura_resposta_sucesso(self):
        """Testa se a estrutura da resposta de sucesso está correta"""
        pergunta = "Qual o total de vendas de produtos por tipo de pagamento?"
        resposta = chatbot_response(pergunta)
        
        # Verifica se todas as chaves obrigatórias estão presentes
        chaves_obrigatorias = ["pergunta_do_usuario", "query", "pergunta_da_query", "status"]
        for chave in chaves_obrigatorias:
            assert chave in resposta
        
        # Verifica se não há chaves extras inesperadas
        assert len(resposta) == 4
    
    def test_estrutura_resposta_falha(self):
        """Testa se a estrutura da resposta de falha está correta"""
        pergunta = "Pergunta inválida"
        resposta = chatbot_response(pergunta)
        
        # Verifica se todas as chaves obrigatórias estão presentes
        chaves_obrigatorias = ["pergunta_do_usuario", "query", "pergunta_da_query", "status", "mensagem"]
        for chave in chaves_obrigatorias:
            assert chave in resposta
        
        # Verifica se não há chaves extras inesperadas
        assert len(resposta) == 5

if __name__ == "__main__":
    pytest.main([__file__])

