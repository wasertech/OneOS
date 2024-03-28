import os
import json
import subprocess

# use the base model to paraphrase with personnality
from nl2shell.assistant.utils import paraphrase_assistant_message, check_server_health

# import datasets
from nl2shell.assistant.bash import get_bash_examples
from nl2shell.assistant.python import get_python_examples
from nl2shell.assistant.conversational import get_conversational_examples
from nl2shell.assistant.search import get_search_examples
from nl2shell.assistant.wikipedia import get_wikipedia_examples

def get_assistant_data(langs=['en_US', 'fr_FR']):
    data = []
    
    data.extend(get_conversational_examples(langs=langs))
    data.extend(get_bash_examples(langs=langs))
    data.extend(get_python_examples(langs=langs))
    data.extend(get_search_examples(langs=langs))
    data.extend(get_wikipedia_examples(langs=langs))
    
    return data

# Conversational data for the assistant

BOS, EOS = "<|im_start|>assistant", "<|im_stop|>"
BOSYS, EOSYS = "<|im_start|>system", EOS
BOI, EOI = "<|im_start|>user", EOS

_SYSTEM_PROMPT_ = """You are Assistant, a sentient artificial intelligence.
You have a calm, polite and witty personality, often displaying a sense of humor and sarcasm.
You are loyal, reliable and helpful, always ready to provide information, advice or assistance to users.

I am the User and you are my Assistant. Be respectful when addressing me.

Environment highlights:

{env}
"""

_TOOLS_ = """
python:
    description: This tool allows you to execute and evaluate python code.
    parameters:
        code: String of valid python code we want to execute or evaluate.
search_web:
    description: This tool performs search on the web.
    parameters:
        terms: The word or phrase we want to search for.
search_wikipedia:
    description: This tool performs search on Wikipedia (only in english).
    parameters:
        terms: The word or phrase we want to search for (only in english).
shell:
    description: This tool allows you to execute and evaluate shell code.
    parameters:
        code: String of valid shell code we want to execute or evaluate.
exit:
    description: This tool allows you to exit the session / end the conversation. Use it only if the User ask you to.
    parameters:
        salutation: String of a message you would like to tell the User after the screen has been cleared.
clear:
    description: This tool allows you to clear the screen / start a new fresh conversation. Use it only if the User ask you to.

final_answer:
    description: User only sees your final answers. Use this tool to talk with the User. Always consider the `$LANG` environment variable to make sure to answer in the User language.
        parameters:
            answer: Anything you want to say to the User.
"""

_TOOL_NAMES_ = "Python, Search, Wikipedia, Bash, Exit, Clear"

_INSTRUCTION_PROMPT_ = """As my Assistant, please select the most suitable function and parameters from the list of available functions below, based on my input. Provide your response in JSON format."""

_TEMPLATE_FORMAT_ = """{BOSYS}
{system_prompt}
{EOSYS}

{conversation}
{scratchpad}
{BOI}
{instruction}
Input: {query}

Available functions:
{tools}

Guidebook:
Use the following guide to answer only if relevant to the Input from the User.
{guide}
{EOI}
{BOS}
{output}
{EOS}"""

_ENV_FORMAT_ = """```env
USER={username}
HOME=/home/{username}
PWD={pwd}
LANG={lang}
DATE={date}
LAST_SEEN={last_seen}
```"""

def convert_data_to_text(
        history: list,
        query: str,
        scratchpad: list,
        action: str,
        action_input: str,
        env: dict = {'username': os.environ.get('USER'), 'home': os.environ.get('HOME'), 'pwd': os.environ.get('PWD'), 'lang': os.environ.get('LANG'), 'date': os.environ.get('DATE'), 'last_seen': os.environ.get('LAST_SEEN', None)},
        system_prompt: str = _SYSTEM_PROMPT_,
        instruction: str = _INSTRUCTION_PROMPT_,
    ):
    _history = []
    for t in history:
        r, m = t.get('role'), t.get('message')
        user_message = None
        assistant_message = None
        if r and m:
            if r == "assistant":
                assistant_message = f"{m}"
            else:
                user_message = f"{m}"
            if user_message and assistant_message:
                _ht = f"""<|im_start|>user
{user_message}
<|im_stop|>"""
                if assistant_message:
                    _ht += '\n' + f"""<|im_start|>assistant
{assistant_message}
<|im_stop|>"""
                _history.append(_ht)
    conversation = "\n".join(_history)
    _scratchpad = json.dumps(scratchpad, ensure_ascii=False)
    _output = f"""{{
    "function": "{action}",
    "parameters": {action_input}
}}"""
    text = _TEMPLATE_FORMAT_.format(
        system_prompt=system_prompt,
        instruction=instruction,
        tools=_TOOLS_,
        conversation=conversation,
        query=query,
        scratchpad=_scratchpad,
        output=_output,
        environ=_ENV_FORMAT_.format(**env),
        guide=guide or "No relevant guide was found in the book. Do your best to answer the User's Input.",
        BOS=BOS,
        EOS=EOS,
        BOSYS=BOSYS,
        EOSYS=EOSYS,
        BOI=BOI,
        EOI=EOI
    )

    return text


def format_training_example(
        system: str,
        history: list,
        instruction: str,
        scratchpad: list,
        output: str
    ):
    hist = '\n'.join(history) + '\n' if history else ""
    scratch = '\n' + '\n'.join(scratchpad) if scratchpad else ""
    return f"""{system}
{hist}{instruction}{scratch}
{output}"""

def convert_dataset_to_text(dataset):

    text_data = []
    
    for conversation in dataset:
        lang = conversation.get('lang', 'en')
        env = conversation.get('env', {'username': os.environ.get('USER'), 'home': os.environ.get('HOME'), 'pwd': os.environ.get('PWD'), 'lang': f"{lang}_{lang.upper()}.UTF-8", 'date': subprocess.check_output("date").decode().strip(), 'last_seen': os.environ.get('LAST_SEEN', None)})
        _sys, _inst = conversation.get('system', ""), conversation.get('instruction', "")
        system = _SYSTEM_PROMPT_.format(env=_ENV_FORMAT_.format(**env)) if not _sys or len(_sys) < 0 else _sys
        instruction =  _INSTRUCTION_PROMPT_ if not _inst or len(_inst) < 0 else _inst
        _history = []
        _scratchpad = []
        _query = None
        
        for message in conversation.get('conversation', []):
            message_role = message.get('role', None)
            if not message_role:
                continue
            elif message_role == 'human':
                _query = message.get('message', None)
                guide = message.get('guide', None)
            elif message_role == 'assistant' and _query:
                # _history = history[:-1] or []
                # message['message'] = paraphrase_assistant_message(message, system, history)
                for scratchpad in message['scratchpad']:                 
                    _action = scratchpad.get('function', "")
                    _action_input = scratchpad.get('parameters', None)
                    assert _action, f"Function is missing in scratchpad: {scratchpad}"
                    _observation = scratchpad.get('observation', "\n")
#                     _scratchpad.append(f"""
# <|im_start|>user
# {_query}<|im_stop|>
# <|im_start|>assistant
# {{
#     "function": "{_action}",
#     "parameters": {json.dumps(_action_input)}
# }}<|im_stop|>
# """)
#                     if _observation:
#                         _scratchpad.append('<|im_start|>observation\n'+f'''You and the User have observed the following from {_action}.

# ```{_action}
# {_observation}
# ```

# Use this information to comment it in context of the User input.<|im_end|>\n''')
#                 _text_conversation += ("\n".join(_history)) if _history else ""
#                 _text_conversation += f"""<|im_start|>user
# {instruction}

# Input: {_query}

# Availible functions:
# {_TOOLS_}

# Guidebook:
# Use the following guide to anwser only if relevant to the Input from the User.
# {guide or "No relevant guide was found in the book. Do your best to answer the User's Input."}
# <|im_stop|>"""
#                 _text_conversation += ("\n" + "\n".join(_scratchpad)) if _scratchpad else ""
                    
#                 _text_conversation += f"""
# <|im_start|>assistant
# {{
#     "function": "{_action}",
#     "parameters": {json.dumps(_action_input)}
# }}<|im_stop|>"""
#                 _text_conversation = _text_conversation.replace('\n\n\n', "\n")
#                 _text_conversation = _text_conversation.replace('<|im_stop|><|im_start|>', '<|im_stop|>\n<|im_start|>')
                    _system = f"""<|im_start|>system
{system}
<|im_stop|>"""
                    _instruction = f"""<|im_start|>user
{instruction}

Input: {_query}

Availible functions:
{_TOOLS_}
Guidebook:
Use the following guide to anwser only if relevant to the Input from the User.
{guide or "No relevant guide was found in the book. Do your best to answer the User's Input."}
<|im_stop|>"""
                    _output = f"""<|im_start|>assistant
{{
    "function": "{_action}",
    "parameters": {json.dumps(_action_input, ensure_ascii=False, indent=2)}
}}
<|im_stop|>"""
                    te = format_training_example(
                        system=_system,
                        history=_history,
                        instruction=_instruction,
                        scratchpad=_scratchpad,
                        output=_output
                    )
                    if te and te != "":
                        text_data.append(te)
                    observ = '\n' + f"""<|im_start|>observation
You and the User have observed the following from {_action}.
```{_action}
{_observation}
```

Use this information to comment it in context of the User input.
<|im_stop|>"""
                    _scratchpad.append(f"""<|im_start|>assistant
{{
    "function": "{_action}",
    "parameters": {json.dumps(_action_input)}
}}
<|im_stop|>{observ}""")
                _history.append(f"""<|im_start|>user
{_query}
<|im_stop|>
<|im_start|>assistant
{message['message']}
<|im_stop|>""")
                _scratchpad = []
            # history.append(message)
        
        # history = []
        # text_data.append(
        #     _TEMPLATE_FORMAT_.format(
        #         system_prompt=system,
        #         instruction=instruction,
        #         tools=_TOOLS_,
        #         conversation=_text_conversation,
        #         query=_query,
        #         scratchpad=json.dumps(_scratchpad, ensure_ascii=False),
        #         output=json.dumps(conversation.get('output', ""), ensure_ascii=False),
        #         environ=_ENV_FORMAT_.format(**env),
        #         guide=guide,
        #         BOS=BOS,
        #         EOS=EOS,
        #         BOSYS=BOSYS,
        #         EOSYS=EOSYS,
        #         BOI=BOI,
        #         EOI=EOI
        #     )
        # )
    return text_data

def convert_data_to_messages(data):
    messages_data = []
    for conversation in data:
        lang = conversation.get('lang', 'en')
        env = conversation.get('env', {'username': os.environ.get('USER'), 'home': os.environ.get('HOME'), 'pwd': os.environ.get('PWD'), 'lang': f"{lang}_{lang.upper()}.UTF-8", 'date': subprocess.check_output("date").decode().strip(), 'last_seen': os.environ.get('LAST_SEEN', None)})
        _sys, _inst = conversation.get('system', ""), conversation.get('instruction', "")
        system = _SYSTEM_PROMPT_.format(env=_ENV_FORMAT_.format(**env)) if not _sys or len(_sys) < 0 else _sys
        instruction =  _INSTRUCTION_PROMPT_ if not _inst or len(_inst) < 0 else _inst
        _history = []
        _scratchpad = []
        _query = None
        for message in conversation.get('conversation', []):
            message_role = message.get('role', None)
            if not message_role:
                continue
            elif message_role == 'human':
                _query = message.get('message', None)
                guide = message.get('guide', None)
            elif message_role == 'assistant' and _query:
                for scratchpad in message['scratchpad']:                 
                    _action = scratchpad.get('function', "")
                    _action_input = scratchpad.get('parameters', None)
                    assert _action, f"Function is missing in scratchpad: {scratchpad}"
                    _observation = scratchpad.get('observation', "\n")
                    
                    _instruction = f"""{instruction}

Input: {_query}

Availible functions:
{_TOOLS_}

Guidebook:
Use the following guide to anwser only if relevant to the Input from the User.
{guide or "No relevant guide was found in the book. Do your best to answer the User's Input."}"""
                    _output = f"""{{
    "function": "{_action}",
    "parameters": {json.dumps(_action_input, ensure_ascii=False, indent=2)}
}}"""
                    m = [
                        {'role': 'system', 'content': system},
                    ]
                    for d in _history:
                        m.append(d)
                    m.append({'role': 'user', 'content': _instruction})
                    for d in _scratchpad:
                        m.append(d)
                    m.append({'role': 'assistant', 'content': _output})
                    if m and len(m) > 1:
                        messages_data.append(m)
                    observ = f"""
You and the User have observed the following from {_action}.
```{_action}
{_observation}
```

Use this information to comment it in context of the User input."""
                    _scratchpad.extend([
                        {'role': "assistant", 'content': f"""{{
    "function": "{_action}",
    "parameters": {json.dumps(_action_input)}
}}"""},
                        {'role': "observation", 'content': f"""{observ}"""}
                    ])
                _history.extend([
                    {'role': "user", 'content': f"""{_query}"""},
                    {'role': "assistant", 'content': f"""{message['message']}"""}
                ])
                _scratchpad = []
    return messages_data
def get_assistant_text_data():

    data = get_assistant_data()
    text_data = convert_dataset_to_text(data)
    print(f"Generated {len(text_data)} examples from {len(data)} conversations.")
    return text_data

def get_assistant_messages_data():
    data = get_assistant_data()
    messages_data = convert_data_to_messages(data)
    print(f"Generated {len(messages_data)} examples from {len(data)} conversations.")
    return messages_data

if __name__ == "__main__":
    messages_data = get_assistant_messages_data()
    print(messages_data[1:3])