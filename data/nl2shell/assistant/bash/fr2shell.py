from nl2shell.assistant.bash.en2shell import get_nl2shell_english_examples
from translator import Translator
from functools import lru_cache

translator = Translator("eng_Latn", "fra_Latn", model_id="Helsinki-NLP/opus-mt-en-fr", max_length=2048)
# data = [
#     {
#         'system': "",
#         'instruction': "",
#         'conversation': [
#             { 'role': "human", 'message': "Bonjour" },
#             { 'role': "assistant", 'message': "Bonjour! Vous êtes bien matinal aujourd'hui.",  'scratchpad': [
#                     { 'action': 'Bash', 'action_input': "date", 'observation': "mer 02 aoû 2023 03:59:15 CEST" },
#                     { 'action': 'final_answer', 'action_input': "Bonjour! Vous êtes bien matinal aujourd'hui.", 'observation': "" },
#                 ]
#             },
#             { 'role': "human", 'message': "Quel jour sommes-nous?" },
#             { 'role': "assistant", 'message': "mer 02 aoû 2023 03:59:15 CEST",  'scratchpad': [
#                     { 'action': 'Bash', 'action_input': "date", 'observation': "mer 02 aoû 2023 03:59:15 CEST" },
#                     { 'action': 'final_answer', 'action_input': "Nous sommes le mercredi 2 août 2023.", 'observation': "" },
#                 ]
#             },
#         ]
#     }
# ] 

@lru_cache(maxsize=128)
def translate(utterance):
    return translator.translate(utterance)

def get_nl2shell_french_examples():
    data = get_nl2shell_english_examples()
    _data = []

    for example in data:
        try:
            example['conversation'][0]['message'] = translate(example['conversation'][0]['message'])
            example['lang'] = 'fr'
            _data.append(example)
        except Exception as e:
            print(f"Error: {e}")
            print("Skipping...")
            continue

    return _data