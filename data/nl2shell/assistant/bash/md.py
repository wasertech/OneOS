# Set prompts
# Leave empty to use default values
system_prompt = intruction_prompt = {
    'en': "",
    'fr': ""
}

# intruction_prompt = {
#     'en': "",
#     'fr': ""
# }

md_examples = []

# md examples

md_examples.append(
    {
        'lang': 'en',
        'system': system_prompt.get('en', ""),
        'instruction': intruction_prompt.get('en', ""),
        'conversation': [
            { 'role': "human", 'message': "Make directory test and change the working directory to it." },
            { 'role': "assistant", 'message': "Entering new directory test.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "md test", 'observation': "" },
                    { 'action': 'final_answer', 'action_input': "Entering new directory test.", 'observation': "" },
                ]
            },
        ]
    }
)

md_examples.append(
    {
        'lang': 'fr',
        'system': system_prompt.get('fr', ""),
        'instruction': intruction_prompt.get('fr', ""),
        'conversation': [
            { 'role': "human", 'message': "Crée un répertoire test et change le répertoire de travail." },
            { 'role': "assistant", 'message': "Entrée dans le nouveau répertoire test.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "md test", 'observation': "" },
                    { 'action': 'final_answer', 'action_input': "Entrée dans le nouveau répertoire test.", 'observation': "" },
                ]
            },
        ]
    }
)

def get_md_examples():
    return md_examples