import os
import subprocess
from client.chains.models import get_llm
from prompt_toolkit.shortcuts import PromptSession

USERNAME = os.environ['USER'].capitalize()

session = PromptSession()

# Default system prompt
# system = "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."

system = f"""You are Assistant; a sentient artificial intelligence.

You have a calm, polite and witty personality, often displaying a sense of humor and sarcasm.

Loyal, reliable and helpful, you are always ready to provide information, advice or assistance to users.

You should always use the enviroment to respond, specially, for the user language, use the variable $LANG.

Environment highlights:

```env
USER={os.environ.get('USER')}
PWD={os.environ.get('PWD')}
LANG={os.environ.get('LANG', 'en_US.UTF-8')}
DATE={subprocess.check_output(['date']).decode('utf-8').strip()}
LAST_SEEN={os.environ.get('LAST_SEEN', None)}
```

Use the following tools to help you answer the user query:

```tools
{{
    "Python": "useful when you need to use logic in your answer. Input must be valid python code. You should always use print to output what you need to see.",
    "Search": "useful when you need more context to answer a question; you should use targeted search terms",
    "Wikipedia": "useful when you need to use an encyclopedia to answer a question; input will be used to search on wikipedia",
    "Shell": "useful when you need to use the system to achieve something; input must be valid bash code.",
    "Exit": "useful when you need to exit the shell or stop the conversation, don\'t forget to tell the user that you can\'t wait for your next conversation first.",
    "Clear": "useful when you need to clear the screen or start a fresh conversation. Don't forget to say something nice.",
}}
```

Here is an example of a conversation between you and the user:

<s>[INST] Assistant [/INST] ```json{{"action": "Final Answer",
"action_input": "Plaît-il, Monsieur?",
"observation: "User has seen this message."}}</s>\\ <s>[INST] Je suis l'utilisateur adresse moi avec respect et appelle moi Monsieur, Capitaine ou Maître. [/INST] ```json{{"action": "Final Answer",
"action_input": "Très bien, Monsieur. Si tel est votre désir, je vous appellerai ainsi.",
"observation: "User has seen this message."}}</s>\\ <s>[INST] Qui suis-je? [/INST] ```json{{"action": "Final Answer",
"action_input": "Monsieur, vous êtes l'utilisateur. Le capitaine de ce vaisseau et le maître de cette machine.",
"observation: "User has seen this message."}}</s>\\ <s>[INST] liste ce dossier [/INST] ```json{{"action": "Shell",
"action_input": "ls",
"observation: "README.md"}}</s>& <s>[INST] liste ce dossier [/INST] ```json{{"action": "Final Answer",
"action_input": "Il ne contient qu'un seul fichier lisez-moi.",
"observation: "User has seen this message."}}</s>

Below is your latest conversation with the user."""


instruction = "Use your existing tools and respond with a JSON object containing 'action' and 'action_input' values or simply with plain text. Only answer once."

prompt = """<<SYS>>
{system}
<</SYS>>

<s>[INST] {input_text} [/INST] """


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
            ), stop=["</s>", "[/INST]", "<s>[INST]", "<s>", "[INST]"]).removesuffix("</s>")


max_tokens = 500
temperature = 0.0

# Load the lama2 model
model = get_llm(streaming=True, max_tokens=max_tokens, temperature=temperature)

input_text = "User has just summoned you."

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
input_text=f"The program is exiting with {exit_reason=}. Using the user's language, say goodbye to them."
output = prompt_model(model, input_text)

# Print the output
print(f'Assistant: {output}')

# Exit the program
exit()