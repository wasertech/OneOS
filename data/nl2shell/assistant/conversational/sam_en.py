import json
import random

# Set prompts
# Leave empty to use default values
system_prompt = intruction_prompt= {
    'en': "",
    'fr': ""
}

# intruction_prompt = {
#     'en': "",
#     'fr': ""
# }

def load_sam_en_dataset(ds_path='sam/samantha-1.1.json'):
    with open(ds_path) as f:
        sam = json.load(f)
    return sam

def as_assistant(from_samantha):
    to_assistant = from_samantha
    to_assistant = to_assistant.replace('Samantha', 'Assistant')

    return to_assistant

def get_random_name(names=[
    "Samantha",
    "Theodore",
    "Danny",
    "James",
    "John",
    "Robert", 
    "Michael", 
    "William", 
    "David", 
    "Richard", 
    "Joseph", 
    "Thomas", 
    "Charles",
    "Jean", 
    "Pierre", 
    "Marie", 
    "Claude", 
    "André", 
    "Jacques", 
    "Michel", 
    "Alain", 
    "Daniel", 
    "Philippe",
]):
    name = random.choice(names)

    return name.capitalize()

def as_random_user(from_theodore):
    to_user = from_theodore
    random_user_name = get_random_name()
    to_user = to_user.replace('Theodore', random_user_name)
    return to_user

def get_sam_en_examples():
    sam = load_sam_en_dataset()

    sam_en = []
    for conv in sam:

        conversation = []
        for message in conv.get('conversations'):
            if message.get('from') == 'human':
                _message = as_random_user(message.get('value'))
                conversation.append({
                    'role': "human",
                    'message': _message
                })
            elif message.get('from') == 'gpt':
                _message = as_assistant(message.get('value'))
                conversation.append({
                    'role': "assistant",
                    'message': _message,
                    'scratchpad': [
                        { 'action': 'final_answer', 'action_input': _message, 'observation': "" },
                    ]
                })
            else:
                continue
        
        sam_en.append({
            'lang': 'en',
            'system': system_prompt.get('en', ""),
            'instruction': intruction_prompt.get('en', ""),
            'conversation': conversation
        })

    return sam_en