from nl2shell.assistant.bash.en2shell import get_nl2shell_english_examples
from nl2shell.assistant.bash.fr2shell import get_nl2shell_french_examples
from nl2shell.assistant.bash.date import get_date_examples
from nl2shell.assistant.bash.cd import get_cd_examples
from nl2shell.assistant.bash.ls import get_ls_data
from nl2shell.assistant.bash.pwd import get_pwd_data
from nl2shell.assistant.bash.cat import get_cat_examples

def get_bash_examples():
    data = []
    data.extend(get_nl2shell_english_examples())
    #data.extend(get_nl2shell_french_examples())
    #data.extend(get_date_examples())
    #data.extend(get_cd_examples())
    #data.extend(get_ls_data())
    #data.extend(get_pwd_data())
    #data.extend(get_cat_examples())
    return data


if __name__ == "__main__":
    data = get_bash_examples()
    for d in data:
        assert d.get('system', None) is not None, "System prompt is missing"
        assert d.get('instruction', None) is not None, "Instruction prompt is missing"
        assert d.get('conversation', None) is not None, "Conversation is missing"
        print()
        print(d)
        print()