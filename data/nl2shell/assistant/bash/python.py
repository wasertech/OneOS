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
                    { 'function': 'shell', 'parameters': {'code': "python -m listen.Wav2Vec.as_service"}, 'observation': "...\nStarting FastAPI server\n..." },
                    { 'function': 'final_answer', 'parameters': {'answer': "Python module is running."}, 'observation': "" },
                ]
            },
        ]
    }
)

def get_python_examples():
    return py_examples