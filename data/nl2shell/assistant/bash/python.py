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

py_examples = []

py_examples.append(
    {
        'lang': 'en',
        'system': system_prompt.get('en', ""),
        'instruction': intruction_prompt.get('en', ""),
        'conversation': [
            { 'role': "human", 'message': "Run python module listen.Wav2Vec.as_service." },
            { 'role': "assistant", 'message': "Python module is running.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "python -m listen.Wav2Vec.as_service", 'observation': "Starting FastAPI server..." },
                    { 'action': 'final_answer', 'action_input': "Python module is running.", 'observation': "" },
                ]
            },
        ]
    }
)

def get_python_examples():
    return py_examples