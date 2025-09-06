import pandas as pd

excel_file = 'flask/Conjuntodedados.xlsx'
xls = pd.ExcelFile(excel_file)

# Carregar os DataFrames
pet_df = pd.read_excel(xls, 'pet')
stay_df = pd.read_excel(xls, 'stay')
product_df = pd.read_excel(xls, 'product')
purchase_df = pd.read_excel(xls, 'purchase')
payment_method_type_df = pd.read_excel(xls, 'payment_method_type')

print("\n--- Simulação da Query 1: Total de vendas de produtos por tipo de pagamento ---")
merged_purchase_payment = pd.merge(purchase_df, payment_method_type_df, left_on='payment_method', right_on='payment_method_type_id', how='left')
payment_sales = merged_purchase_payment.groupby('nome')['total_value'].sum().sort_values(ascending=False)
print(payment_sales)

print("\n--- Simulação da Query 2: Produtos mais vendidos em termos de quantidade ---")
merged_purchase_product = pd.merge(purchase_df, product_df, left_on='product_id', right_on='product_id', how='left')
product_quantity = merged_purchase_product.groupby('name')['quantity'].sum().sort_values(ascending=False)
print(product_quantity)

print("\n--- Simulação da Query 3: Custo total das estadias por pet ---")
merged_stay_pet = pd.merge(stay_df, pet_df, left_on='pet_id', right_on='pet_id', how='left')
pet_stay_cost = merged_stay_pet.groupby('name')['stay_cost'].sum().sort_values(ascending=False)
print(pet_stay_cost)

