import os
import subprocess
from transformers import TrainerCallback

def get_prompt(sentence, system="You are Assistant, a sentient artificial intelligence."):
    USER = os.environ.get('USER')
    PWD = os.environ.get('PWD')
    LANG = os.environ.get('LANG', 'en_US.UTF-8')
    LAST_SEEN = os.environ.get('LAST_SEEN', None)
    DATE = subprocess.check_output(['date']).decode('utf-8').strip()

    prompt = """# System

<<SYS>>

{system}

Environment highlights:

```shell
USER={USER}
PWD={PWD}
LANG={LANG}
DATE={DATE}
LAST_SEEN={LAST_SEEN}
```

Use the following tools to help you answer the user query:

{tools}

Below is your latest conversation with the user.

<</SYS>>

<s>[INST] {sentence} [/INST] """

    return prompt.format(
        system=system,
        sentence=sentence,
        USER=USER,
        PWD=PWD,
        LANG=LANG,
        DATE=DATE,
        LAST_SEEN=LAST_SEEN,
        tools="""```json
{
    'Python': 'useful when you need to use logic in your answer. Input must be valid python code. You should always use print to output what you need to see.',
    'Search': 'useful when you need more context to answer a question; you should use targeted search terms',
    'Wikipedia': 'useful when you need to use an encyclopedia to answer a question; input will be used to search on wikipedia',
    'Shell': 'useful when you need to use the system to achieve something; input must be valid bash code.',
    'Exit': 'useful when you need to exit the shell or stop the conversation, don\'t forget to tell the user that you can\'t wait for your next conversation first.',
    'Clear': 'useful when you need to clear the screen or start a fresh conversation. Don't forget to say something nice.',
}
```"""
    )


if __name__ == '__main__':
    print(get_prompt("Assistant?"))