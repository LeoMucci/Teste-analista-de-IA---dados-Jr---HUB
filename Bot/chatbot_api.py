from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

# Função do chatbot (importada do arquivo original)
def chatbot_response(user_question):
    responses = {
        "qual o total de vendas de produtos por tipo de pagamento?": {
            "query": "SELECT pmt.nome AS tipo_pagamento, SUM(p.total_value) AS total_vendas FROM purchase AS p JOIN payment_method_type AS pmt ON p.payment_method = pmt.payment_method_type_id GROUP BY pmt.nome ORDER BY total_vendas DESC;",
            "pergunta_da_query": "Qual o total de vendas de produtos agrupado por tipo de pagamento?"
        },
        "quais os produtos mais vendidos em termos de quantidade?": {
            "query": "SELECT prod.name AS nome_produto, SUM(p.quantity) AS quantidade_vendida FROM purchase AS p JOIN product AS prod ON p.product_id = prod.product_id GROUP BY prod.name ORDER BY quantidade_vendida DESC;",
            "pergunta_da_query": "Quais produtos tiveram a maior quantidade vendida?"
        },
        "qual o custo total das estadias por pet?": {
            "query": "SELECT pet.name AS nome_pet, SUM(s.stay_cost) AS custo_total_estadia FROM stay AS s JOIN pet ON s.pet_id = pet.pet_id GROUP BY pet.name ORDER BY custo_total_estadia DESC;",
            "pergunta_da_query": "Qual o custo acumulado das estadias para cada pet?"
        }
    }

    normalized_question = user_question.lower().strip()

    if normalized_question in responses:
        response_data = responses[normalized_question]
        return {
            "pergunta_do_usuario": user_question,
            "query": response_data["query"],
            "pergunta_da_query": response_data["pergunta_da_query"],
            "status": "sucesso"
        }
    else:
        return {
            "pergunta_do_usuario": user_question,
            "query": None,
            "pergunta_da_query": None,
            "status": "falha",
            "mensagem": "Não foi possível encontrar uma resposta para esta pergunta."
        }

# Função para executar queries simuladas usando pandas
def execute_query_simulation(query_type):
    try:
        # Caminho para o arquivo Excel
        excel_file = 'flask/Conjuntodedados.xlsx'
        
        if not os.path.exists(excel_file):
            return {"erro": "Arquivo de dados não encontrado"}
        
        xls = pd.ExcelFile(excel_file)
        
        # Carregar os DataFrames necessários
        pet_df = pd.read_excel(xls, 'pet')
        stay_df = pd.read_excel(xls, 'stay')
        product_df = pd.read_excel(xls, 'product')
        purchase_df = pd.read_excel(xls, 'purchase')
        payment_method_type_df = pd.read_excel(xls, 'payment_method_type')
        
        if query_type == "vendas_por_pagamento":
            merged_purchase_payment = pd.merge(purchase_df, payment_method_type_df, 
                                             left_on='payment_method', 
                                             right_on='payment_method_type_id', 
                                             how='left')
            result = merged_purchase_payment.groupby('nome')['total_value'].sum().sort_values(ascending=False)
            return result.to_dict()
            
        elif query_type == "produtos_mais_vendidos":
            merged_purchase_product = pd.merge(purchase_df, product_df, 
                                             left_on='product_id', 
                                             right_on='product_id', 
                                             how='left')
            result = merged_purchase_product.groupby('name')['quantity'].sum().sort_values(ascending=False)
            return result.to_dict()
            
        elif query_type == "estadias_por_pet":
            merged_stay_pet = pd.merge(stay_df, pet_df, 
                                     left_on='pet_id', 
                                     right_on='pet_id', 
                                     how='left')
            result = merged_stay_pet.groupby('name')['stay_cost'].sum().sort_values(ascending=False)
            return result.to_dict()
            
        else:
            return {"erro": "Tipo de query não reconhecido"}
            
    except Exception as e:
        return {"erro": f"Erro ao executar query: {str(e)}"}

# Rotas da API

@app.route('/', methods=['GET'])
def home():
    """Rota inicial da API"""
    return jsonify({
        "mensagem": "API do Chatbot para Hotel de Pets",
        "versao": "1.0",
        "endpoints": {
            "/chat": "POST - Enviar pergunta para o chatbot",
            "/execute-query": "POST - Executar query simulada",
            "/perguntas": "GET - Listar perguntas disponíveis",
            "/health": "GET - Verificar status da API"
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint principal do chatbot"""
    try:
        data = request.get_json()
        
        if not data or 'pergunta' not in data:
            return jsonify({
                "erro": "Campo 'pergunta' é obrigatório"
            }), 400
        
        user_question = data['pergunta']
        response = chatbot_response(user_question)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "erro": f"Erro interno do servidor: {str(e)}"
        }), 500

@app.route('/execute-query', methods=['POST'])
def execute_query():
    """Endpoint para executar queries simuladas e retornar dados"""
    try:
        data = request.get_json()
        
        if not data or 'tipo_query' not in data:
            return jsonify({
                "erro": "Campo 'tipo_query' é obrigatório"
            }), 400
        
        query_type = data['tipo_query']
        result = execute_query_simulation(query_type)
        
        return jsonify({
            "tipo_query": query_type,
            "resultado": result,
            "status": "sucesso"
        })
        
    except Exception as e:
        return jsonify({
            "erro": f"Erro ao executar query: {str(e)}"
        }), 500

@app.route('/perguntas', methods=['GET'])
def list_questions():
    """Endpoint para listar perguntas disponíveis"""
    perguntas = [
        "Qual o total de vendas de produtos por tipo de pagamento?",
        "Quais os produtos mais vendidos em termos de quantidade?",
        "Qual o custo total das estadias por pet?"
    ]
    
    tipos_query = [
        "vendas_por_pagamento",
        "produtos_mais_vendidos", 
        "estadias_por_pet"
    ]
    
    return jsonify({
        "perguntas_disponiveis": perguntas,
        "tipos_query_disponiveis": tipos_query
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar o status da API"""
    return jsonify({
        "status": "healthy",
        "timestamp": pd.Timestamp.now().isoformat()
    })

if __name__ == '__main__':
    # Configuração para desenvolvimento
    app.run(host='0.0.0.0', port=5000, debug=True)

