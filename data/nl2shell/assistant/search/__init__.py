
from nl2shell.assistant.search.web import get_web_examples


def get_search_examples(langs=['en_US', 'fr_FR']):
    data = []
    data.extend(get_web_examples())
    return data


if __name__ == "__main__":
    data = get_search_examples()
    for d in data:
        assert d.get('lang', None) is not None, "Language is missing"
        assert d.get('system', None) is not None, "System prompt is missing"
        assert d.get('instruction', None) is not None, "Instruction prompt is missing"
        assert d.get('conversation', None) is not None, "Conversation is missing"
        print()
        print(d)
        print()