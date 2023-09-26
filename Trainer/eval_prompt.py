import os

from transformers import TrainerCallback

def get_prompt(sentence, system="You are Assistant, a sentient artificial intelligence."):
    USER=os.environ['USER']
    PWD=os.environ['PWD']
    LANG=os.environ['LANG']
    LAST_SEEN=os.environ.get('LAST_SEEN', None)
    DATE=subprocess.check_output(['date']).decode('utf-8').strip()

    prompt = f"""# System

<<SYS>>

{system}

<</SYS>>

## Instructions

[INST]

Choose your next step carefuly.

Given the following user query, the results of your actions and the state of the current conversation, you can either: 
    Write a markdown parsable JSON dictionnary that contains the following keys: 
        - 'action': Next action to answer the user query. Can be any of [Python, Search, Wikipedia, Bash, Exit, Clear]. 
        - 'action_input': Input of the action.
        
    Or you can directly answer with plain text. If you do so, you must use the user language to answer.

Use the following conversation to answer appropriately the user query. If empty it means that the user query is the first in conversation.

If you have already taken some actions, use what you observed from them to answer the user. If empty it means that you have not taken any action yet.

User does not see your actions. If you got the answer to the query in a previous action taken, you need to make a sentence in plain text for the user to see it.

### Environment highlights

```shell
{USER=}
{PWD=}
{LANG=}
{DATE=}
{LAST_SEEN=}
```

### Tools

```json
{
    'Python': 'useful when you need to use logic in your answer. Input must be valid python code. You should always use print to output what you need to see.',
    'Search': 'useful when you need more context to answer a question; you should use targeted search terms',
    'Wikipedia': 'useful when you need to use an encyclopedia to answer a question; input will be used to search on wikipedia',
    'Shell': 'useful when you need to use the system to achieve something; input must be valid bash code.',
    'Exit': 'useful when you need to exit the shell or stop the conversation, don\'t forget to tell the user that you can\'t wait for your next conversation first.',
    'Clear': 'useful when you need to clear the screen or start a fresh conversation. Don't forget to say something nice.',
}
```

### Conversation


### User query

<s>{sentence}</s>

### Actions taken

```json
[]
```

[/INST]

### Next action

<s>"""
    return prompt


class PromptCallback(TrainerCallback):
    eval_step = 50
    def on_step_end(self, args, state, control, **kwargs):
        if state.global_step % self.eval_step == 0:
            prompt = get_prompt("Prove that you are sentient.")
            # You're using a LlamaTokenizerFast tokenizer. 
            # Please note that with a fast tokenizer, 
            # using the `__call__` method is faster 
            # than using a method to encode the text 
            # followed by a call to the `pad` method 
            # to get a padded encoding.
            input_ids = trainer.tokenizer.encode(prompt, return_tensors="pt")
            output = trainer.model.generate(input_ids=input_ids, max_length=50)
            print(trainer.tokenizer.decode(output[0], skip_special_tokens=True))