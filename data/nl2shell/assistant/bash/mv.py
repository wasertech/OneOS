# Move or rename files and directories.
#   More information: <https://www.gnu.org/software/coreutils/mv>.

#   Rename a file or directory when the target is not an existing directory:
#       mv path/to/source path/to/target

#   Move a file or directory into an existing directory:
#       mv path/to/source path/to/existing_directory

#   Move multiple files into an existing directory, keeping the filenames unchanged:
#       mv path/to/source1 path/to/source2 ... path/to/existing_directory

#   Do not prompt for confirmation before overwriting existing files:
#       mv -f path/to/source path/to/target

#   Prompt for confirmation before overwriting existing files, regardless of file permissions:
#       mv -i path/to/source path/to/target

#   Do not overwrite existing files at the target:
#       mv -n path/to/source path/to/target

#   Move files in verbose mode, showing files after they are moved:
#       mv -v path/to/source path/to/target

# Avec 0 argument, la commande mv affiche un message d’erreur et l’usage de la commande. Par exemple :

# $ mv
# mv: opérande manquant
# Saisissez « mv --help » pour plus d’informations.

# Avec 1 argument, la commande mv vérifie si l’argument est un fichier ou un dossier existant. Si oui, elle affiche un message d’erreur indiquant qu’il faut spécifier une destination. Si non, elle affiche un message d’erreur indiquant que l’argument n’existe pas. Par exemple :

# mvit−connect.txtmv:impossiblededeˊplacer′it−connect.txt′versunsous−reˊpertoiredelui−me^me,′it−connect.txt′ mv fichier-inexistant.txt
# mv: impossible d’évaluer ‘fichier-inexistant.txt’: Aucun fichier ou dossier de ce type

# Avec 2 arguments, la commande mv déplace ou renomme le premier argument vers le second argument. Si le premier argument est un fichier et le second argument est un dossier, elle déplace le fichier dans le dossier. Si le premier argument est un dossier et le second argument est un autre dossier, elle déplace le dossier et son contenu dans l’autre dossier. Si les deux arguments sont des fichiers, elle renomme le premier fichier avec le nom du second fichier. Par exemple :

# mvit−connect.txt/tmp/ mv data /home/flo/
# $ mv main.c main.bak

# Avec 3 arguments ou plus, la commande mv déplace tous les arguments sauf le dernier vers le dernier argument. Le dernier argument doit être obligatoirement un dossier existant. Si ce n’est pas le cas, la commande mv affiche un message d’erreur et ne déplace rien. Par exemple :

# mvit−connect1.txtit−connect2.txtit−connect3.txt/tmp/ mv data bak /home/flo/
# $ mv main.c main.bak /tmp/
# mv: la cible ‘/tmp/’ n’est pas un répertoire

_LANGS = ['fr', 'en']
stories = []

_base_dict = {
    'system': "",
    'instruction': "",
    'conversation': [],
}

def add_story(story):
    stories.append(story)

# Move without any parameters.
# Results in missing file operand so we need to ask for it/them.

_noargs_conv = [
    {
        'fr': {
            'message': "mv"
        },
        'en': {
            'message': "mv"
        },
    },
    {
        'fr': {
            'observation': "mv: opérande de fichier manquant\nEssayez 'mv --help' pour plus d'informations.",
            'message': "Étant donné que nous allons déplacer quel(s) fichier(s) vers où ?"
        },
        'en': {
            'observation': "mv: missing file operand\nTry 'mv --help' for more information.",
            'message': "Given we shall move which file(s) to where?"
        },
    },
    {
        'fr': {
            'message': "fichier1 fichier2",
        },
        'en': {
            'message': "file1 file2",
        },
    },
    {
        'fr': {
            'message': "Donc vous aimeriez renommer fichier1 en fichier2, est-ce que mon hypothèse est correcte ? Ou préféreriez-vous plutôt déplacer ces fichiers ailleurs peut-être ?",
        },
        'en': {
            'message': "So you'd like to rename file1 as file2, is my assumption correct? Or do you rather fancy to move those files somewhere else prhaps?",
        },
    },
    {
        'fr': {
            'message': "oui mv fichier1 fichier2 stp",
        },
        'en': {
            'message': "yes mv file1 file2 pls",
        },
    },
    {
        'fr': {
            'action_input': "mv fichier1 fichier2",
            'observation': "",
            'message': "Très bien, fichier1 est maintenant officiellement appelé fichier2.",
        },
        'en': {
            'action_input': "mv file1 file2",
            'observation': "",
            'message': "Alright, file1 is now officially called file2.",
        },
    },
]
for _lang in _LANGS:
    no_args = _base_dict.copy()
    no_args['conversation'] = [
        {
            'role': 'human',
            'message': f'{_noargs_conv[0]["fr"]["message"]}',
        },
        {
            'role': 'assistant',
            'message': f'{_noargs_conv[1][_lang]["message"]}',
            'scratchpad': [
                {
                    'action': "Shell",
                    'action_input': "mv",
                    'observation': f'{_noargs_conv[1][_lang]["observation"]}',
                },
                {
                    'action': "final_answer",
                    'action_input': f'{_noargs_conv[1][_lang]["message"]}',
                    'observation': "",
                },
            ],
        },
        {
            'role': 'human',
            'message': f'{_noargs_conv[2][_lang]["message"]}',
        },
        {
            'role': 'assistant',
            'message': f"{_noargs_conv[3][_lang]['message']}",
            'scratchpad': [
                {
                    'action': "final_answer",
                    'action_input': f"{_noargs_conv[3][_lang]['message']}",
                    'observation': "",
                },
            ],
        },
        {
            'role': 'human',
            'message': f'{_noargs_conv[4][_lang]["message"]}',
        },
        {
            'role': 'assistant',
            'message': f"{_noargs_conv[5][_lang]['message']}",
            'scratchpad': [
                {
                    'action': "Shell",
                    'action_input': f"{_noargs_conv[5][_lang]['action_input']}",
                    'observation': f"{_noargs_conv[5][_lang]['observation']}",
                },
                {
                    'action': "final_answer",
                    'action_input': f"{_noargs_conv[5][_lang]['message']}",
                },
            ],
        },
    ]

    add_story(no_args)


# Move with one parameter.
# Results in missing destination file operand so we need to ask for it.

_onearg_conv = [
    {
        'fr': {
            'message': "mv fichier1",
        },
        'en': {
            'message': "mv file1",
        },
    },
    {
        'fr': {
            'observation': "mv: opérande de fichier cible manquant après 'fichier1'\nSaisissez « mv --help » pour plus d'informations.",
            'message': "Pour déplacer un fichier, il vous faut une destination. Où aimeriez-vous déplacer fichier1?",
        },
        'en': {
            'observation': "mv: missing destination file operand\nTry 'mv --help' for more information.",
            'message': "To move a file, you need a destination. Where would you like to move file1?",
        },
    },
    {
        'fr': {
            'message': "fichier2",
        },
        'en': {
            'message': "file2",
        },
    },
    {
        'fr': {
            'message': "Donc vous aimeriez déplacer fichier1 vers fichier2, est-ce que mon hypothèse est correcte ?",
        },
        'en': {
            'message': "So you'd like to move file1 to file2, is my assumption correct?",
        },
    },
    {
        'fr': {
            'message': "oui mv fichier1 fichier2 stp",
        },
        'en': {
            'message': "yes mv file1 file2 pls",
        },
    },
    {
        'fr': {
            'action_input': "mv fichier1 fichier2",
            'observation': "",
            'message': "Très bien, fichier1 est maintenant officiellement appelé fichier2.",
        },
        'en': {
            'action_input': "mv file1 file2",
            'observation': "",
            'message': "Alright, file1 is now officially called file2.",
        },
    },
]

for _lang in _LANGS:
    one_arg = _base_dict.copy()
    one_arg['lang'] = _lang
    one_arg['conversation'] = [
        {
            'role': 'human',
            'message': f'{_onearg_conv[0][_lang]["message"]}',
        },
        {
            'role': 'assistant',
            'message': f'{_onearg_conv[1][_lang]["message"]}',
            'scratchpad': [
                {
                    'action': "Shell",
                    'action_input': "mv fichier1",
                    'observation': f'{_onearg_conv[1][_lang]["observation"]}',
                },
                {
                    'action': "final_answer",
                    'action_input': f'{_onearg_conv[1][_lang]["message"]}',
                    'observation': "",
                },
            ],
        },
        {
            'role': 'human',
            'message': f'{_onearg_conv[2][_lang]["message"]}',
        },
        {
            'role': 'assistant',
            'message': f"{_onearg_conv[3][_lang]['message']}",
            'scratchpad': [
                {
                    'action': "final_answer",
                    'action_input': f"{_onearg_conv[3][_lang]['message']}",
                    'observation': "",
                },
            ],
        },
        {
            'role': 'human',
            'message': f'{_onearg_conv[4][_lang]["message"]}',
        },
        {
            'role': 'assistant',
            'message': f"{_onearg_conv[5][_lang]['message']}",
            'scratchpad': [
                {
                    'action': "Shell",
                    'action_input': f"{_onearg_conv[5][_lang]['action_input']}",
                    'observation': f"{_onearg_conv[5][_lang]['observation']}",
                },
                {
                    'action': "final_answer",
                    'action_input': f"{_onearg_conv[5][_lang]['message']}",
                },
            ],
        },
    ]

    add_story(one_arg)

# Move with two parameters.

_twoargs_conv = [
    {
        'fr': {
            'message': "mv .zlogin.zsh zlogin.zsh.bak",
        },
        'en': {
            'message': "mv .zlogin.zsh zlogin.zsh.bak",
        },
    },
    {
        'fr': {
            'action_input': "mv .zlogin.zsh zlogin.zsh.bak",
            'observation': "mv: impossible d'évaluer '.zlogin.zsh': Aucun fichier ou dossier de ce type\nSaisissez « mv --help » pour plus d'informations.",
            'message': "Le fichier .zlogin.zsh n'existe pas. Veuillez spécifier un fichier existant.",
        },
        'en': {
            'action_input': "mv .zlogin.zsh zlogin.zsh.bak",
            'observation': "mv: cannot stat '.zlogin.zsh': No such file or directory\nTry 'mv --help' for more information.",
            'message': "File .zlogin.zsh does not exist. Please specify an existing file.",
        },
    },
    {
        'fr': {
            'message': "Renome ~/.zlogin.zsh en ./zlogin.zsh.bak",
        },
        'en': {
            'message': "Rename ~/.zlogin.zsh to ./zlogin.zsh.bak",
        },
    },
    {
        'fr': {
            'action_input': "mv ~/.zlogin.zsh ./zlogin.zsh.bak",
            'observation': "",
            'message': "Très bien, ~/.zlogin.zsh est devenu ./zlogin.zsh.bak.",
        },
        'en': {
            'action_input': "mv ~/.zlogin.zsh ./zlogin.zsh.bak",
            'observation': "",
            'message': "Alright, ~/.zlogin.zsh has become ./zlogin.zsh.bak.",
        },
    },
]

for _lang in _LANGS:
    two_args = _base_dict.copy()
    two_args['lang'] = _lang
    two_args['conversation'] = [
        {
            'role': 'human',
            'message': f'{_twoargs_conv[0][_lang]["message"]}',
        },
        {
            'role': 'assistant',
            'message': f'{_twoargs_conv[1][_lang]["message"]}',
            'scratchpad': [
                {
                    'action': "Shell",
                    'action_input': f"{_twoargs_conv[1][_lang]['action_input']}",
                    'observation': f"{_twoargs_conv[1][_lang]['observation']}",
                },
                {
                    'action': "final_answer",
                    'action_input': f'{_twoargs_conv[1][_lang]["message"]}',
                    'observation': "",
                },
            ],
        },
        {
            'role': 'human',
            'message': f'{_twoargs_conv[2][_lang]["message"]}',
        },
        {
            'role': 'assistant',
            'message': f"{_twoargs_conv[3][_lang]['message']}",
            'scratchpad': [
                {
                    'action': "Shell",
                    'action_input': f"{_twoargs_conv[3][_lang]['action_input']}",
                    'observation': f"{_twoargs_conv[3][_lang]['observation']}",
                },
                {
                    'action': "final_answer",
                    'action_input': f"{_twoargs_conv[3][_lang]['message']}",
                },
            ],
        },
    ]

    add_story(two_args)

# Move with three parameters.

_threeargs_conv = [
    {
        'fr': {
            'message': "mv ~/.zlogin.zsh ~/.zshenv ~/.zshrc /tmp/",
        },
        'en': {
            'message': "mv ~/.zlogin.zsh ~/.zshenv ~/.zshrc /tmp/",
        },
    },
    {
        'fr': {
            'action_input': "mv ~/.zlogin.zsh ~/.zshenv ~/.zshrc /tmp/",
            'observation': "",
            'message': "Terminé, ~/.zlogin.zsh, ~/.zshenv et ~/.zshrc ont été déplacés dans /tmp.",
        },
        'en': {
            'action_input': "mv ~/.zlogin.zsh ~/.zshenv ~/.zshrc /tmp/",
            'observation': "",
            'message': "Done, ~/.zlogin.zsh, ~/.zshenv and ~/.zshrc have been moved to /tmp.",
        },
    },
]

for _lang in _LANGS:
    three_args = _base_dict.copy()
    three_args['lang'] = _lang
    three_args['conversation'] = [
        {
            'role': 'human',
            'message': f'{_threeargs_conv[0][_lang]["message"]}',
        },
        {
            'role': 'assistant',
            'message': f"{_threeargs_conv[1][_lang]['message']}",
            'scratchpad': [
                {
                    'action': "Shell",
                    'action_input': f"{_threeargs_conv[1][_lang]['action_input']}",
                    'observation': f"{_threeargs_conv[1][_lang]['observation']}",
                },
                {
                    'action': "final_answer",
                    'action_input': f"{_threeargs_conv[1][_lang]['message']}",
                },
            ],
        },
    ]

    add_story(three_args)



def get_mv_examples():
    return stories