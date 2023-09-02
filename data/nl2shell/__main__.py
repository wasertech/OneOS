
from nl2shell import LANGS
from nl2shell.assistant.bash import get_bash_examples
from nl2shell.assistant.conversational import get_conversational_examples

if __name__ == "__main__":
    data = []
    
    data.extend(get_bash_examples(langs=LANGS))
    data.extend(get_conversational_examples(langs=LANGS)


    for d in data:
        print()
        print(d)
        print()
