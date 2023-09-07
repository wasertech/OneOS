import os
from client.chains.models import get_llm
from prompt_toolkit.shortcuts import PromptSession

USERNAME = os.environ['USER']

session = PromptSession()

prompt = """[INST] <<SYS>>
You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
<</SYS>>
{input_text}[/INST]
"""

# Load the lama2 model
model = get_llm(streaming=True, max_tokens=100, temperature=0)

# Say hi
output = model(prompt.format(input_text="The program is starting. Say hello to the user."))

# Print the output
print(f'Assistant: {output}')

# Define the input text
input_text = session.prompt(f'{USERNAME}: ') # input(f'{USERNAME}: ')

while input_text != "" or input_text.lower() not in ['exit', 'quit']:

    # Infer the model
    output = model(prompt.format(input_text=input_text))

    # Print the output
    print(f'Assistant: {output}')

    # Define the input text
    input_text = input(f'{USERNAME}: ')

# Say bye
output = model(prompt.format(input_text="The program is exiting. Say goodbye to the user."))

# Print the output
print(f'Assistant: {output}')

# Exit the program
exit()