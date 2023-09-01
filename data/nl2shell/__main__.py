
from nl2shell import LANGS
from nl2shell.assistant.bash import get_bash_examples

if __name__ == "__main__":
    data = get_bash_examples(langs=LANGS)
    for d in data:
        print()
        print(d)
        print()
