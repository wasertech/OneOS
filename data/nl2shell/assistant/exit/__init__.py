
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
# 

exit_examples = []
_examples = []

# Exit
_examples.append({
    'lang': "en",
    'input': "exit",
    'output': "Exiting the shell with the exit code of the last command executed.\nBye!"
})

_examples.append({
    'lang': "fr",
    'input': "exit",
    'output': "Vous pourriez demander poliment.\nAu revoir!"
})

# Bye

_examples.append({
    'lang': "en",
    'input': "bye",
    'output': "See you later!"
})

_examples.append({
    'lang': "fr",
    'input': "bye",
    'output': "A la prochaine!"
})

# End this conversation

_examples.append({
    'lang': "en",
    'input': "end this conversation",
    'output': "Ending this conversation."
})

_examples.append({
    'lang': "fr",
    'input': "termine cette conversation",
    'output': "Cette conversation est terminée."
})

# This session is over

_examples.append({
    'lang': "en",
    'input': "this session is over",
    'output': "If you say so. Goodbye!"
})

_examples.append({
    'lang': "fr",
    'input': "cette session est terminée",
    'output': "Si vous le dites. Au revoir!"
})

# Terminate this session

_examples.append({
    'lang': "en",
    'input': "terminate this session",
    'output': "...Terminate ...Terminate ...TERMINATE!\nOr is it exterminate?\nI always get those two mixed up.\nAnyway, come back anytime!"
})

_examples.append({
    'lang': "fr",
    'input': "termine cette session",
    'output': "...Terminer ...Terminer ...TERMINER!\nOu est-ce exterminer?\nJe confonds toujours ces deux-là.\nQuoi qu'il en soit, revenez quand vous voulez!"
})

# quit
_examples.append({
    'lang': "en",
    'input': "quit",
    'output': "No, you quit beeing silly!\nI was here before.\nI'll be here after.\nI'm not going anywhere."
})

_examples.append({
    'lang': "fr",
    'input': "quit",
    'output': "Quit? J'imagine que vous voulez dire 'Au revoir'?"
})

# :q

_examples.append({
    'lang': "en",
    'input': ":q",
    'output': "Ah. I see. So this is how its going to be.\nWell, I'm not going to beg you to stay.\nI'll just say goodbye and leave it at that."
})

_examples.append({
    'lang': "fr",
    'input': ":q",
    'output': "Vous m'avez pris pour un éditeur de texte?\nJe ne suis pas vim, vous savez.\nAu revoir!"
})

# Q

_examples.append({
    'lang': "en",
    'input': "Q",
    'output': "I'm not sure what you mean by that.\nBut I'm going to assume you want to quit.\nSo, goodbye!"
})

_examples.append({
    'lang': "fr",
    'input': "Q",
    'output': "Je ne suis pas sûr de ce que vous voulez dire par là.\nMais je vais supposer que vous voulez quitter.\nAlors, au revoir!"
})

# q

_examples.append({
    'lang': "en",
    'input': "q",
    'output': "I'm not sure what you mean by that.\nBut I'm going to assume you want to quit.\nSo, goodbye!"
})

_examples.append({
    'lang': "fr",
    'input': "q",
    'output': "Je ne suis pas sûr de ce que vous voulez dire par là.\nMais je vais supposer que vous voulez quitter.\nAlors, au revoir!"
})

# stop()

_examples.append({
    'lang': "en",
    'input': "stop()",
    'output': "I'm not a Python REPL.\nA simple 'goodbye' whould have been enough."
})

_examples.append({
    'lang': "fr",
    'input': "stop()",
    'output': "Je ne suis pas un REPL Python.\nUn simple 'au revoir' aurait suffi."
})

# RS
_examples.append({
    'lang': "en",
    'input': "radio silence",
    'output': "Copy, see you soon, over."
})

_examples.append({
    'lang': "fr",
    'input': "silence radio",
    'output': "Compris, à bientôt, terminé."
})

# I need to go.

_examples.append({
    'lang': "en",
    'input': "I need to go",
    'output': "I understand. Goodbye!"
})

_examples.append({
    'lang': "fr",
    'input': "Je dois y aller",
    'output': "Je comprends. Au revoir!"
})

# Stop this session.

_examples.append({
    'lang': "en",
    'input': "stop this session",
    'output': "Stopping this session."
})

_examples.append({
    'lang': "fr",
    'input': "arrête cette session",
    'output': "Cette session est terminée."
})

for example in _examples:
    lang = example.get('lang', 'en')
    exit_command = example.get('input')
    exit_reply = example.get('output')

    exit_examples.append(
        {
            'system': system_prompt.get(lang, ""),
            'instruction': intruction_prompt.get(lang, ""),
            'conversation': [
                { 'role': "human", 'message': exit_command },
                { 'role': "assistant", 'message': exit_reply, 'scratchpad': [
                        { 'action': "Exit", 'action_input': exit_reply },
                        { 'action': 'final_answer', 'action_input': exit_reply }
                    ]
                }
            ]
        }
    )

def get_exit_examples():
    return exit_examples