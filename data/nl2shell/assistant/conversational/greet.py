_SYS_GREET_MSG = """This is the System, letting you know that the user has just entered a new shell session.
You should probably take this opportunity to greet the user and ask them how can you be useful.
User uses the following environment variables:

```env
{env}
```

Be sure to use the appropriate (iternationalized and localized) language for the user during the conversation."""

_env = """LANG={LANG}.UTF-8
DATE={DATE}
LAST_SEEN={LAST_SEEN}
USER={USERNAME}
PWD={PWD}"""

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

greet_examples = []

_greets = []

_greets.append({
    'env': {
        'LANG': "fr_CH",
        'DATE': "Sat Sep  2 03:07:36 CEST 2023",
        'LAST_SEEN': "Fri Sep 1 23:21:05 2023",
        'USER': "waser",
        'PWD': "/home/waser",
        },
    'final_answer': "Ravis de vous revoir si tôt!\nNe devriez-vous pas dormir à cette heure si tardive?\nQui qu'il en soit, je suis à votre entière disposition."
})

greet_examples.append(
    {
        'system': system_prompt.get('en', ""),
        'instruction': intruction_prompt.get('en', ""),
        'conversation': [
            { 'role': "human", 'message': _SYS_GREET_MSG.format(env="LANG=en_US.UTF-8") },
            { 'role': "assistant", 'message': "Hello, how can I help you?",  'scratchpad': [
                    { 'action': 'final_answer', 'action_input': "Hello, how can I help you?", 'observation': "" },
                ]
            },
        ]
    }
)

def get_greet_examples():
    pass