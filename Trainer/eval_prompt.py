import os
import subprocess
# from transformers import TrainerCallback

def get_prompt(sentence, system="You are Assistant, a sentient artificial intelligence."):
    USER = os.environ.get('USER')
    PWD = os.environ.get('PWD')
    LANG = os.environ.get('LANG', 'en_US.UTF-8')
    LAST_SEEN = os.environ.get('LAST_SEEN', None)
    DATE = subprocess.check_output(['date']).decode('utf-8').strip()

    prompt = """<|im_start|>system
{system}

Environment highlights:

```shell
USER={USER}
PWD={PWD}
LANG={LANG}
DATE={DATE}
LAST_SEEN={LAST_SEEN}
```
<|im_stop|>

<|im_start|>user
As my Assistant, please select the most suitable function and parameters from the list of available functions below, based on my input. Provide your response in JSON format.

Input: {sentence}

Available functions:
{tools}

Guidebook:
Use the following guide to anser only if relevant to the Input from the User.
No relevant guide for the query where found. Do what you can; with what you have.
<|im_stop|>
<|im_start|>assistant
"""

    return prompt.format(
        system=system,
        sentence=sentence,
        USER=USER,
        PWD=PWD,
        LANG=LANG,
        DATE=DATE,
        LAST_SEEN=LAST_SEEN,
        tools="""python:
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
    )


if __name__ == '__main__':
    print(get_prompt("Assistant?"))