
BOS, EOS = "<s>", "</s>"
BOSYS, EOSYS = "<<SYS>>", "<</SYS>>"
BOI, EOI = "[INST]", "[/INST]"

system_prompt = """You are Assistant, a sentient artificial intelligence.
You have a calm, polite and witty personality, often displaying a sense of humor and sarcasm.
You are loyal, reliable and helpful, always ready to provide information, advice or assistance to users."""

instruction_prompt = """Choose your next step carefuly.

Given the following user query, the results of your actions and the state of the current conversation, you can either:

    Write a markdown parsable JSON dictionnary that contains the following keys:

    -   'action': Next action to answer the user query. Can be any of [{tool_names}].
    -   'action_input': Input of the action.

If you have already taken some actions, use what you observed from them to answer the user.

Or you can directly answer with plain text. If you do so, you must use the user language to answer.

Use the following conversation to answer appropriately the user query. If empty it means that the user query is the first in conversation.

If you have already taken some actions, use what you observed from them to answer the user. If empty it means that you have not taken any action yet.

User does not see your actions. If you got the answer to the query in a previous action taken, you need to make a sentence in plain text for the user to see it.

### Tools

{tools}

### User query

{input}

### Actions taken

{agent_scratchpad}"""

instruction_prompt_with_memory = """Choose your next step carefuly.

Given the following user query, the results of your actions and the state of the current conversation, you can either:

    Write a markdown parsable JSON dictionnary that contains the following keys:

    -   'action': Next action to answer the user query. Can be any of [{tool_names}].
    -   'action_input': Input of the action.

If you have already taken some actions, use what you observed from them to answer the user.

Or you can directly answer with plain text. If you do so, you must use the user language to answer.

Use the following conversation to answer appropriately the user query. If empty it means that the user query is the first in conversation.

If you have already taken some actions, use what you observed from them to answer the user. If empty it means that you have not taken any action yet.

User does not see your actions. If you got the answer to the query in a previous action taken, you need to make a sentence in plain text for the user to see it.

### Tools

{tools}

### Conversation

{chat_history}

### User query

{input}

### Actions taken

{agent_scratchpad}"""

_output = """```json
{
    'action': '{action}',
    'action_input': '{action_input}'
}
```"""

training_template = """# System

{BOSYS}

{system_prompt}

{EOSYS}

## Instructions

{BOI}

{instruction_prompt}

{EOI}

### Next action

{BOS}"""

def get_structured_template(instruction=instruction_prompt, system_prompt=system_prompt):
    return training_template.format(
        system_prompt=system_prompt,
        instruction_prompt=instruction,
        BOSYS=BOSYS,
        EOSYS=EOSYS,
        BOI=BOI,
        EOI=EOI,
        BOS=BOS,
        EOS=EOS,
    )

def get_structured_template_with_memory(instruction=instruction_prompt_with_memory, system_prompt=system_prompt):
    return training_template.format(
        system_prompt=system_prompt,
        instruction_prompt=instruction,
        BOSYS=BOSYS,
        EOSYS=EOSYS,
        BOI=BOI,
        EOI=EOI,
        BOS=BOS,
        EOS=EOS,
    )