import json

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

BOS, EOS = "<s>", "</s>"
BOSYS, EOSYS = "<<SYS>>", "<</SYS>>"
BOI, EOI = "[INST]", "[/INST]"

_SYSTEM_PROMPT_ = (
    "You are Assistant, a sentient artificial intelligence.\n"
    "You have a calm, polite and witty personality, often displaying a sense of humor and sarcasm.\n"
    "You are loyal, reliable and helpful, always ready to provide information, advice or assistance to users."
)

_TOOLS_ = """
```json
{
	'Python': 'useful when you need to use logic in your answer. Input must be valid python code. You should always use print to output what you need to see.',
	'Search': 'useful when you need more context to answer a question; you should use targeted search terms',
	'Wikipedia': 'useful when you need to use an encyclopedia to answer a question; input will be used to search on wikipedia',
	'Shell': 'useful when you need to use the system to achieve something; input must be valid bash code.',
	'Exit': 'useful when you need to exit the shell or stop the conversation, don\'t forget to tell the user that you can\'t wait for your next conversation first.',
	'Clear': 'useful when you need to clear the screen or start a fresh conversation. Don\'t forget to say something nice.',
}
```
"""

_TOOL_NAMES_ = "Python, Search, Wikipedia, Bash, Exit, Clear"

_INSTRUCTION_PROMPT_ = f"""Choose your next step carefuly.

Given the following user query, the results of your actions and the state of the current conversation, you can either:

    Write a markdown parsable JSON dictionnary that contains the following keys:

    -   'action': Next action to answer the user query. Can be any of [{_TOOL_NAMES_}].
    -   'action_input': Input of the action.

    Or you can directly answer with plain text. If you do so, you must use the user language to answer.

Use the following conversation to answer appropriately the user query. If empty it means that the user query is the first in conversation.

If you have already taken some actions, use what you observed from them to answer the user. If empty it means that you have not taken any action yet.

User does not see your actions. If you got the answer to the query in a previous action taken, you need to make a sentence in plain text for the user to see it."""

_TEMPLATE_FORMAT_ = """# System

{BOSYS}

{system_prompt}

{EOSYS}

## Instructions

{BOI}

{instruction}

### Tools

{tools}

### Conversation

{conversation}

### User query

{BOS}{query}{EOS}

### Actions taken

```json
{scratchpad}
```

{EOI}

### Next action

{BOS}{output}{EOS}"""

def convert_data_to_text(
        history: list,
        query: str,
        scratchpad: list,
        action: str,
        action_input: str,
        system_prompt: str = _SYSTEM_PROMPT_,
        instruction: str = _INSTRUCTION_PROMPT_
    ):
    _history = []
    for t in history:
        r, m = t.get('role'), t.get('message')
        if r and m:
            if r == "assistant":
                _history.append(f"Assistant: {BOS}{m}{EOS}")
            else:
                _history.append(f"User: {BOS}{m}{EOS}")
    conversation = "\n".join(_history)
    _scratchpad = json.dumps(scratchpad, ensure_ascii=False)
    _output = action_input if action == "final_answer" else f"""```json
{{
    'action': '{action}',
    'action_input': '{action_input}'
}}
```"""
    text = _TEMPLATE_FORMAT_.format(
        system_prompt=system_prompt,
        instruction=instruction,
        tools=_TOOLS_,
        conversation=conversation,
        query=query,
        scratchpad=_scratchpad,
        output=_output,
        BOS=BOS,
        EOS=EOS,
        BOSYS=BOSYS,
        EOSYS=EOSYS,
        BOI=BOI,
        EOI=EOI
    )

    return text

def convert_dataset_to_text(dataset):

    text_data = []

    for conversation in dataset:
        _sys, _inst = conversation.get('system', ""), conversation.get('instruction', "")
        system = _SYSTEM_PROMPT_ if not _sys or len(_sys) < 0 else _sys
        instruction =  _INSTRUCTION_PROMPT_ if not _inst or len(_inst) < 0 else _inst

        history = []
        _scratchpad = []
        _query = None

        for message in conversation.get('conversation', []):     
            message_role = message.get('role', None)
            if not message_role:
                continue
            elif message_role == 'human':
                _query = message.get('message', None)
            elif message_role == 'assistant' and _query:
                _history = history[:-1] or []
                # message['message'] = paraphrase_assistant_message(message, system, history)
                for scratchpad in message['scratchpad']:
                    _action = scratchpad.get('action', None)
                    _action_input = scratchpad.get('action_input', None)
                    text_data.append(convert_data_to_text(history=_history, query=_query, scratchpad=_scratchpad, action=_action, action_input=_action_input, system_prompt=system, instruction=instruction))
                    _scratchpad.append(scratchpad)
                _scratchpad = []
            history.append(message)
        history = []
    
    return text_data

def get_assistant_text_data():

    data = get_assistant_data()
    text_data = convert_dataset_to_text(data)
    print(f"Generated {len(text_data)} examples from {len(data)} conversations.")
    return text_data

if __name__ == "__main__":
    text_data = get_assistant_text_data()
