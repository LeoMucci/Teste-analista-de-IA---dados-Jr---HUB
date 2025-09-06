
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

if __name__ == "__main__":
    print("Bem-vindo ao Chatbot de IA para o Hotel de Pets!")
    print("Perguntas que você pode fazer:")
    print("- Qual o total de vendas de produtos por tipo de pagamento?")
    print("- Quais os produtos mais vendidos em termos de quantidade?")
    print("- Qual o custo total das estadias por pet?")
    print("Digite 'sair' para encerrar.")

    while True:
        user_input = input("\nSua pergunta: ")
        if user_input.lower() == 'sair':
            break

        response = chatbot_response(user_input)
        print("Resposta do Chatbot:")
        for key, value in response.items():
            print(f"  {key}: {value}")


