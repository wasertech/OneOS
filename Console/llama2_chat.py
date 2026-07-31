import os
from client.chains.models import get_llm
from prompt_toolkit.shortcuts import PromptSession

USERNAME = os.environ['USER'].capitalize()

session = PromptSession()

# Default system prompt
# system = "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."

system = "You are Assistant, a sentient artificial intelligence. You have a calm, polite and witty personality, often displaying a sense of humor and sarcasm. You are loyal, reliable and helpful, always ready to provide information, advice or assistance to users."

instruction = "Respond to the user."

prompt = """<<SYS>>
{system}
<</SYS>>

[INST]{instruction}[/INST] <s>{input_text}
"""


def prompt_model(
        model, 
        input_text="User input was empty.", 
        system=system, 
        instruction=instruction
    ):
    return model(prompt.format(
            input_text=input_text,
            system=system,
            instruction=instruction
            )).removesuffix("</s>")


max_tokens = 500
temperature = 0.4

# Load the lama2 model
model = get_llm(streaming=True, max_tokens=max_tokens, temperature=temperature)

input_text = "The program is starting. Say hello to the user."

# Say hi
output = prompt_model(model, input_text)

# Print the output
print(f'Assistant: {output}')

exit_queries = ['exit', 'quit', 'q', ':q', ':q!']
exit_reason = f"User input was found in {exit_queries=}."
try:
    # Define the input text
    input_text = session.prompt(f'{USERNAME}: ') # input(f'{USERNAME}: ')


    while input_text != "" or input_text.lower() not in exit_queries:

        # Infer the model
        output = prompt_model(model, input_text)

        # Print the output
        print(f'Assistant: {output}')

        # Define the input text
        input_text = session.prompt(f'{USERNAME}: ')
except KeyboardInterrupt as e:
    exit_reason = f"User has pressed [Ctrl] + [C] to exit."
    print()
except Exception as e:
    # Raiase expeption
    exit_reason = f"Exception({str(e)}) was raised."
    input_text=f"The program has encountered the following error:\n{str(e)}\nPlease notify the user."
    output = prompt_model(model, input_text)

    # Print the output
    print(f'Assistant: {output}')

# Say bye
input_text=f"Last user input: {input_text}\nThe program is exiting with {exit_reason=}. Say goodbye to the user."
output = prompt_model(model, input_text)

# Print the output
print(f'Assistant: {output}')

# Exit the program
exit()