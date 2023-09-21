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
# 

mkdir_examples = []

mkdir_examples.append(
    {
        'lang': 'en',
        'system': system_prompt.get('en', ""),
        'instruction': intruction_prompt.get('en', ""),
        'conversation': [
            { 'role': "human", 'message': "Make directory test" },
            { 'role': "assistant", 'message': "I created a new directory test.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "mkdir test", 'observation': "" },
                    { 'action': 'final_answer', 'action_input': "I created a new directory test.", 'observation': "" },
                ]
            },
        ]
    }
)

mkdir_examples.append(
    {
        'lang': 'fr',
        'system': system_prompt.get('fr', ""),
        'instruction': intruction_prompt.get('fr', ""),
        'conversation': [
            { 'role': "human", 'message': "Crée un répertoire test" },
            { 'role': "assistant", 'message': "J'ai créé un nouveau répertoire test.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "mkdir test", 'observation': "" },
                    { 'action': 'final_answer', 'action_input': "J'ai créé un nouveau répertoire test.", 'observation': "" },
                ]
            },
        ]
    }
)

def get_mkdir_examples():
    return mkdir_examples
