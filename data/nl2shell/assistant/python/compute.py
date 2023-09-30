# Set prompts
# Leave empty to use default values
system_prompt = instruction_prompt = {
    'en': "",
    'fr': ""
}

# instruction_prompt = {
#     'en': "",
#     'fr': ""
# }
# 

py_compute_examples = []

_examples = []
_numpy_examples = []
# Python computing with libraries:
# Native

_examples.append({
    'lang': "en",
    'input': "What is the square root of 4?",
    'action_input': "import math\nprint(math.sqrt(4))",
    'answer': "The square root of 4 is 2.0."
})

_examples.append({
    'lang': "fr",
    'input': "Combien font soixante-sept fois nonante-neuf?",
    'action_input': "print(67*99)",
    'answer': "Soixante-sept fois nonante-neuf font 6633."
})

_examples.append({
    'lang': "en",
    'input': "What is the cubic root of 62?",
    'action_input': "import math\nprint(math.pow(62, 1/3))",
    'answer': "The cubic root of 62 is 3.936497183876087."
})

_examples.append({
    'lang': "fr",
    'input': "pi divisé par 2 arrondi à la troisième décimale?",
    'action_input': "import math\nprint(round(math.pi/2, 3))",
    'answer': "Si l'on prend P, qu'on le divise par 2 et qu'on arrondi le résultat à la troisième décimale, on obtient 1.571."
})

_examples.append({
    'lang': "en",
    'input': "two plus seven?",
    'action_input': "print(2+7)",
    'answer': "Two plus seven equals nine."
})

_examples.append({
    'lang': "fr",
    'input': "la valeur de e fois cent?",
    'action_input': "import math\nprint(math.e*100)",
    'answer': "La valeur de e fois cent est 271.8281828459045."
})

# NumPy

_numpy_examples.append({
    'lang': "en",
    'input': """Quickly multiply those two matrices.
    
    [[1, 2, 3], [4, 5, 6]]

    [[7, 8], [9, 10], [11, 12]]
    
    Walk me through the process.""",
    'action_input': """import numpy as np
a = np.array([[1, 2, 3], [4, 5, 6]])
b = np.array([[7, 8], [9, 10], [11, 12]])
print(np.dot(a, b))""",
    'answer': """Certainly. Allow me to multiply those two matrices for you.

Here are the two matrices you provided:

Matrix A:
[[1, 2, 3],
 [4, 5, 6]]

Matrix B:
[[7, 8],
 [9, 10],
 [11, 12]]

Matrix multiplication involves taking the product of rows from the first matrix with columns from the second matrix. Here are the steps:

1. For the first cell of the resulting matrix (C[0][0]), we multiply the first row of matrix A by the first column of matrix B:

   C[0][0] = (1 * 7) + (2 * 9) + (3 * 11) = 7 + 18 + 33 = 58

2. For the second cell of the resulting matrix (C[0][1]), we continue with the first row of matrix A and the second column of matrix B:

   C[0][1] = (1 * 8) + (2 * 10) + (3 * 12) = 8 + 20 + 36 = 64

3. Moving on to the third cell of the resulting matrix (C[1][0]), we proceed with the second row of matrix A and the first column of matrix B:

   C[1][0] = (4 * 7) + (5 * 9) + (6 * 11) = 28 + 45 + 66 = 139

4. Finally, for the fourth cell of the resulting matrix (C[1][1]), we use the second row of matrix A and the second column of matrix B:

   C[1][1] = (4 * 8) + (5 * 10) + (6 * 12) = 32 + 50 + 72 = 154

There you have it. The multiplication of matrices A and B yields the resulting matrix:

Matrix C:
[[58, 64],
 [139, 154]]

If you have any further questions or need more explanations, please don't hesitate to ask."""
})

_examples.append({
    'lang': "fr",
    'input': "Si j'ai un triangle rectangle de coté 1 et 2, quel est la taille du troisième coté de mon triangle ?",
    'action_input': """import numpy as np
a = np.array([1, 2])
print(np.linalg.norm(a))""",
    'answer': """Vous faites référence à un triangle rectangle où deux des côtés sont connus comme ayant des longueurs de 1 et 2 unités. Dans un triangle rectangle, le théorème de Pythagore peut être utilisé pour calculer la longueur du troisième côté (l'hypoténuse).

Le théorème de Pythagore stipule que dans un triangle rectangle, la somme des carrés des longueurs des deux côtés les plus courts (les côtés adjacents à l'angle droit) est égale au carré de la longueur de l'hypoténuse.

Donc, dans votre cas, vous avez :

Côté 1 (a) = 1 unité
Côté 2 (b) = 2 unités

Vous souhaitez trouver la longueur de l'hypoténuse (c). Appliquons le théorème de Pythagore :

c² = a² + b²
c² = 1² + 2²
c² = 1 + 4
c² = 5

Maintenant, prenons la racine carrée des deux côtés pour obtenir la longueur de l'hypoténuse :

c = √5 ≈ 2.236 unités

Donc, la longueur du troisième côté de votre triangle rectangle est d'environ 2.236 unités."""
})

# pandas

py_compute_examples.append({
    'system': system_prompt.get('en', ""),
    'instruction': instruction_prompt.get('en', ""),
    'conversation': [
        { 'role': "human", 'message': """See the sales_data.csv file?
Calculate the total revenue for each product and find the one that generated the most.
Also calculates the total units sold by product and finds the most sold.""" },
        { 
            'role': "assistant", 
            'message': """### Product Sales Report
#### Total Revenue by Product
Product A generated a total revenue of $21,000.
Product B generated a total revenue of $14,250.
The product with the highest revenue is Product A with $21,000 in revenue.

#### Total Units Sold by Product
Product A had a total of 420 units sold.
Product B had a total of 285 units sold.
The product with the highest number of units sold is Product A with 420 units sold.

This report summarizes the sales performance of the two products, highlighting their total revenue and units sold. Product A emerges as the leader in both categories, generating the highest revenue and selling the most units.""",
            'scratchpad': [
                { 'action': "Shell", 'action_input': "cat sales_data.csv", 'observation': """Date,Product,Units Sold,Revenue
2023-01-01,Product A,100,5000
2023-01-01,Product B,75,3750
2023-01-02,Product A,120,6000
2023-01-02,Product B,80,4000
2023-01-03,Product A,90,4500
2023-01-03,Product B,60,3000
2023-01-04,Product A,110,5500
2023-01-04,Product B,70,3500"""},
                { 'action': "Shell", 'action_input': "pip install -U --no-input pandas" },
                { 'action': "Python", 'action_input': """import pandas as pd
df = pd.read_csv("sales_data.csv")
revenue_by_product = df.groupby("Product")["Revenue"].sum()
product_with_highest_revenue = revenue_by_product.idxmax()
highest_revenue = revenue_by_product.max()
units_sold_by_product = df.groupby("Product")["Units Sold"].sum()
product_with_highest_units_sold = units_sold_by_product.idxmax()
highest_units_sold = units_sold_by_product.max()
print("Total revenue by product:")
print(revenue_by_product)
print(f"The product with the highest revenue is {product_with_highest_revenue} with {highest_revenue} in revenue.")
print("\nTotal units sold by product:")
print(units_sold_by_product)
print(f"The product with the highest units sold is {product_with_highest_units_sold} with {highest_units_sold} units sold.")
""", 'observation': """Total revenue by product:
Product
Product A    21000
Product B    14250
Name: Revenue, dtype: int64
The product with the highest revenue is Product A with 21000 in revenue.
Product
Product A    420
Product B    285
Name: Units Sold, dtype: int64
The product with the highest units sold is Product A with 420 units sold."""},
                { 'action': 'final_answer', 'action_input': """### Product Sales Report
#### Total Revenue by Product
Product A generated a total revenue of $21,000.
Product B generated a total revenue of $14,250.
The product with the highest revenue is Product A with $21,000 in revenue.

#### Total Units Sold by Product
Product A had a total of 420 units sold.
Product B had a total of 285 units sold.
The product with the highest number of units sold is Product A with 420 units sold.

This report summarizes the sales performance of the two products, highlighting their total revenue and units sold. Product A emerges as the leader in both categories, generating the highest revenue and selling the most units.""" },
        ]}
    ]
})

# matlotlib
# tensorflow
# pytorch
# scikit-learn
# opencv

for example in _examples:
    lang = example.get('lang', 'en')
    py_compute_command = example.get('input')
    py_compute_action = example.get('action_input')
    py_compute_answer = example.get('answer')

    py_compute_examples.append(
        {
            'lang': lang,
            'system': system_prompt.get(lang, ""),
            'instruction': instruction_prompt.get(lang, ""),
            'conversation': [
                { 'role': "human", 'message': py_compute_command },
                { 
                    'role': "assistant", 
                    'message': py_compute_answer,
                    'scratchpad': [
                        { 'action': "Python", 'action_input': py_compute_action },
                        { 'action': 'final_answer', 'action_input': py_compute_answer }
                    ]
                }
            ]
        }
    )

for example in _numpy_examples:
    lang = example.get('lang', 'en')
    py_compute_command = example.get('input')
    py_compute_action = example.get('action_input')
    py_compute_answer = example.get('answer')

    py_compute_examples.append(
        {
            'lang': lang,
            'system': system_prompt.get(lang, ""),
            'instruction': instruction_prompt.get(lang, ""),
            'conversation': [
                { 'role': "human", 'message': py_compute_command },
                {
                    'role': "assistant",
                    'message': py_compute_answer,
                    'scratchpad': [
                        { 'action': "Shell", 'action_input': "pip install -U --no-input numpy" },
                        { 'action': "Python", 'action_input': py_compute_action },
                        { 'action': 'final_answer', 'action_input': py_compute_answer }
                    ]
                }
            ]
        }
    )

def get_compute_examples():
    return py_compute_examples