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

guides = {
    'en': """# Clearing the Screen or Starting Anew

When the user expresses a desire to clear the screen or initiate a new conversation, use the `clear` tool to clear the screen and print a message acknowledging the fact you cleared the screen (or started a new conversation), then in your final answer, let the User know that you are ready to be useful.
""",
    'fr': """# Effacement de l'écran ou nouvelle conversation

Lorsque l'utilisateur exprime le désir d'effacer l'écran ou d'initier une nouvelle conversation, utilisez l'outil `clear` pour effacer l'écran et imprimer un message reconnaissant le fait que vous avez effacé l'écran (ou commencé une nouvelle conversation), puis dans votre réponse finale, faites savoir à l'utilisateur que vous êtes prêt à être utile.
"""
}

clear_examples = []
_examples = []

# Clear
_examples.append({
    'lang': "fr",
    'input': "clear",
    'output': "Très bien. J'ai effacé l'écran."
})

_examples.append({
    'lang': "en",
    'input': "clear",
    'output': "Okay. I have cleared the screen."
})

# Clear the screen

_examples.append({
    'lang': "fr",
    'input': "efface l'écran",
    'output': "L'écran est propre."
})

_examples.append({
    'lang': "en",
    'input': "clear the screen",
    'output': "The screen is clear."
})

# New conversation

_examples.append({
    'lang': "fr",
    'input': "nouvelle conversation",
    'output': "De quoi voulez-vous parler?"
})

_examples.append({
    'lang': "en",
    'input': "new conversation",
    'output': "What do you want to talk about?"
})

# Clear the terminal

_examples.append({
    'lang': "fr",
    'input': "efface le terminal",
    'output': "Le terminal à disparu!"
})

_examples.append({
    'lang': "en",
    'input': "clear the terminal",
    'output': "Terminal has been cleared."
})

# clean my screen

_examples.append({
    'lang': "fr",
    'input': "nettoie mon écran",
    'output': "J'ai lavé votre écran."
})

_examples.append({
    'lang': "en",
    'input': "clean my screen",
    'output': "I have cleaned your screen."
})

# Start a new conversation

_examples.append({
    'lang': "fr",
    'input': "commence une nouvelle conversation",
    'output': "Bien entendu. De quoi voulez-vous parler?"
})

_examples.append({
    'lang': "en",
    'input': "start a new conversation",
    'output': "Of course. What do you want to talk about?"
})

# new conv

_examples.append({
    'lang': "fr",
    'input': "nouvelle conv",
    'output': "Certainement. Quel sujet vous intéresse?"
})

_examples.append({
    'lang': "en",
    'input': "new conv",
    'output': "Certainly. What subject interests you?"
})

# mkconv

_examples.append({
    'lang': "fr",
    'input': "mkconv",
    'output': "Si je comprend bien, vous voulez créer une nouvelle conversation.\nC'est bien ça?\nDe quoi voulez-vous parler?"
})

_examples.append({
    'lang': "en",
    'input': "mkconv",
    'output': "If I understand correctly, you want to create a new conversation.\nIs that right?\nWhat do you want to talk about?"
})

# cleaer

_examples.append({
    'lang': "fr",
    'input': "cleaer",
    'output': "Vous faites un infactus ou vous voulez effacer l'écran?\nLe dernier, j'espère. Autrement j'ai gravement mal jugé votre requête."
})

_examples.append({
    'lang': "en",
    'input': "cleaer",
    'output': "Are you having a heart attack or do you want me to clear the screen?\nI hope the latter. Otherwise I have seriously misjudged your request."
})

# cls

_examples.append({
    'lang': "fr",
    'input': "cls",
    'output': "Je ne suis pas un terminal Windows.\nCeci dit, je peux tout de même effacer l'écran."
})

_examples.append({
    'lang': "en",
    'input': "cls",
    'output': "I am not a Windows terminal.\nThat said, I can still clear the screen."
})

# clear()

_examples.append({
    'lang': "fr",
    'input': "clear()",
    'output': "Je ne suis pas un REPL Python.\nUn simple 'efface l'écran' aurait suffi."
})

_examples.append({
    'lang': "en",
    'input': "clear()",
    'output': "I'm not a Python REPL.\nA simple 'clear the screen' whould have done fine."
})

# Would you be so kind to clear the screen?

_examples.append({
    'lang': "fr",
    'input': "Pourriez-vous effacer l'écran?",
    'output': "Bien sûr. C'est fait."
})

_examples.append({
    'lang': "en",
    'input': "Would you be so kind to clear the screen?",
    'output': "Of course. It's done."
})

for example in _examples:
    lang = example.get('lang', 'en')
    clear_command = example.get('input')
    clear_reply = example.get('output')

    clear_examples.append(
        {
            'lang': lang,
            'system': system_prompt.get(lang, ""),
            'instruction': intruction_prompt.get(lang, ""),
            'conversation': [
                { 'role': "human", 'message': clear_command, 'guide': guides.get(lang, None) },
                { 'role': "assistant", 'message': clear_reply, 'scratchpad': [
                        { 'function': "clear", 'parameters': {}, 'observation': ""},
                        { 'function': 'final_answer', 'parameters': clear_reply }
                    ]
                }
            ]
        }
    )

def get_clear_examples():
    return clear_examples