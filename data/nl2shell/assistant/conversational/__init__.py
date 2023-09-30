from nl2shell.assistant.conversational.greet import get_greet_examples
from nl2shell.assistant.conversational.misc import get_misc_examples
from nl2shell.assistant.conversational.sam_en import get_sam_en_examples
# from nl2shell.assistant.conversational.sam_fr import get_sam_fr_examples # Do not use. Fix translations first

def get_conversational_examples(langs=['en_US', 'fr_FR']):
    data = []

    data.extend(get_greet_examples())
    data.extend(get_misc_examples())
    # data.extend(get_sam_en_examples())
    # data.extend(get_sam_fr_examples())
    
    return data


if __name__ == "__main__":
    data = get_conversational_examples()
    for d in data:
        assert d.get('lang', None) is not None, "Language is missing"
        assert d.get('system', None) is not None, "System prompt is missing"
        assert d.get('instruction', None) is not None, "Instruction prompt is missing"
        assert d.get('conversation', None) is not None, "Conversation is missing"
        print()
        print(d)
        print()
