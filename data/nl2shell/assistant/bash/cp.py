# Copier fichiers et répertoires.
#   Plus d'informations : <https://www.gnu.org/software/coreutils/cp>.

#   Copier un fichier vers un autre emplacement:

#       cp chemin/vers/fichier_original.ext chemin/vers/fichier_cible.ext

#   Copier un ficher d'un répertoire vers un autre en conservant le nom du fichier :

#       cp chemin/vers/fichier_original.ext chemin/vers/repertoire_cible

#   Copier récursivement le contenu d'un répertoire vers un autre emplacement (si la destination existe, le répertoire est copié dans celle-ci) :

#       cp -r chemin/vers/repertoire_source chemin/vers/repertoire_cible

#   Copier récursivement le contenu d'un répertoire vers un autre emplacement en mode verbeux (affichage des noms fichiers à mesure de leur copie) :

#       cp -vr chemin/vers/repertoire_source chemin/vers/repertoire_cible

#   Copier les fichiers textes vers un autre emplacement, en mode interactive (demande une confirmation avant d'écrire par dessus un fichier du même nom) :

#       cp -i *.txt chemin/vers/repertoire_cible

#   Suivre le lien symbolique avant de copier (copie le fichier lié, et non le lien) :

#       cp -L link chemin/vers/repertoire_cible

#   Utiliser le chemin complet du fichier source, créant tout répertoire manquant lors de la copie :

#       cp --parents chemin/vers/fichier_source chemin/vers/fichier_cible

# Avec 0 argument, la commande cp affiche un message d’erreur et l’usage de la commande. Par exemple :

# $ cp
# cp: opérande manquant
# Saisissez « cp --help » pour plus d’informations.

# Avec 1 argument, la commande cp vérifie si l’argument est un fichier ou un dossier existant. Si oui, elle affiche un message d’erreur indiquant qu’il faut spécifier une destination. Si non, elle affiche un message d’erreur indiquant que l’argument n’existe pas. Par exemple :

# cp it−connect.txt cp:impossibledecopier′it−connect.txt′versunsous−reˊpertoiredelui−me^me,′it−connect.txt′ cp fichier-inexistant.txt
# cp: impossible d’évaluer ‘fichier-inexistant.txt’: Aucun fichier ou dossier de ce type

# Avec 2 arguments, la commande cp copie le premier argument vers le second argument. Si le premier argument est un fichier et le second argument est un dossier, elle copie le fichier dans le dossier. Si le premier argument est un dossier et le second argument est un autre dossier, elle copie le dossier et son contenu dans l’autre dossier. Si les deux arguments sont des fichiers, elle copie le premier fichier avec le nom du second fichier. Par exemple :

# cp it−connect.txt /backup/newf​ile.txt cp data /home/flo/
# $ cp main.c main.bak

# Avec 3 arguments ou plus, la commande cp copie tous les arguments sauf le dernier vers le dernier argument. Le dernier argument doit être obligatoirement un dossier existant. Si ce n’est pas le cas, la commande cp affiche un message d’erreur et ne copie rien. Par exemple :

# cp it−connect1.txt it−connect2.txt it−connect3.txt /backup/ cp data bak /home/flo/
# $ cp main.c main.bak /tmp/
# cp: la cible ‘/tmp/’ n’est pas un répertoire

_LANGS = ['fr', 'en']
stories = []

_base_dict = {
    'system': "",
    'instruction': "",
    'conversation': [],
}

def add_story(story):
    stories.append(story)

# copy without any parameters.
# Results in missing file operand so we need to ask for it/them.

_noargs_conv = [
    {
        'fr': {
            'message': "cp"
        },
        'en': {
            'message': "cp"
        },
    },
    {
        'fr': {
            'observation': "cp: opérande de fichier manquant\nEssayez 'cp --help' pour plus d'informations.",
            'message': "Étant donné que nous allons copier quel(s) fichier(s) vers où ?"
        },
        'en': {
            'observation': "cp: missing file operand\nTry 'cp --help' for more information.",
            'message': "Given we shall copy which file(s) to where?"
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
            'message': "Donc vous aimeriez copier fichier1 pour créer fichier2, est-ce que mon hypothèse est correcte ? Ou préféreriez-vous plutôt copier ces fichiers ailleurs peut-être ?",
        },
        'en': {
            'message': "So you'd like to copy file1 to create file2, is my assumption correct? Or do you rather fancy to copy those files somewhere else prhaps?",
        },
    },
    {
        'fr': {
            'message': "oui cp fichier1 fichier2 stp",
        },
        'en': {
            'message': "yes cp file1 file2 pls",
        },
    },
    {
        'fr': {
            'action_input': "cp fichier1 fichier2",
            'observation': "",
            'message': "Très bien, j'ai copié fichier1 vers fichier2.",
        },
        'en': {
            'action_input': "cp file1 file2",
            'observation': "",
            'message': "Alright, I've copied file1 to file2.",
        },
    },
]
for _lang in _LANGS:
    no_args = _base_dict.copy()
    no_args['lang'] = _lang
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
                    'action_input': "cp",
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


# copy with one parameter.
# Results in missing destination file operand so we need to ask for it.

_onearg_conv = [
    {
        'fr': {
            'message': "cp fichier1",
        },
        'en': {
            'message': "cp file1",
        },
    },
    {
        'fr': {
            'observation': "cp: opérande de fichier cible manquant après 'fichier1'\nSaisissez « cp --help » pour plus d'informations.",
            'message': "Pour copier un fichier, il vous faut une destination. Où aimeriez-vous copier fichier1?",
        },
        'en': {
            'observation': "cp: missing destination file operand\nTry 'cp --help' for more information.",
            'message': "To copy a file, you need a destination. Where would you like to copy file1?",
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
            'message': "Donc vous aimeriez copier fichier1 vers fichier2, est-ce que mon hypothèse est correcte ?",
        },
        'en': {
            'message': "So you'd like to copy file1 to file2, is my assumption correct?",
        },
    },
    {
        'fr': {
            'message': "oui cp fichier1 fichier2 stp",
        },
        'en': {
            'message': "yes cp file1 file2 pls",
        },
    },
    {
        'fr': {
            'action_input': "cp fichier1 fichier2",
            'observation': "",
            'message': "Très bien, fichier1 à été copié vers fichier2.",
        },
        'en': {
            'action_input': "cp file1 file2",
            'observation': "",
            'message': "Alright, file1 has been copied at file2.",
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
                    'action_input': "cp fichier1",
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

# copy with two parameters.

_twoargs_conv = [
    {
        'fr': {
            'message': "cp .zlogin.zsh zlogin.zsh.bak",
        },
        'en': {
            'message': "cp .zlogin.zsh zlogin.zsh.bak",
        },
    },
    {
        'fr': {
            'action_input': "cp .zlogin.zsh zlogin.zsh.bak",
            'observation': "cp: impossible d'évaluer '.zlogin.zsh': Aucun fichier ou dossier de ce type\nSaisissez « cp --help » pour plus d'informations.",
            'message': "Le fichier .zlogin.zsh n'existe pas. Veuillez spécifier un fichier existant.",
        },
        'en': {
            'action_input': "cp .zlogin.zsh zlogin.zsh.bak",
            'observation': "cp: cannot stat '.zlogin.zsh': No such file or directory\nTry 'cp --help' for more information.",
            'message': "File .zlogin.zsh does not exist. Please specify an existing file.",
        },
    },
    {
        'fr': {
            'message': "Copie ~/.zlogin.zsh et colle le là: ./zlogin.zsh.bak",
        },
        'en': {
            'message': "Copy ~/.zlogin.zsh to ./zlogin.zsh.bak",
        },
    },
    {
        'fr': {
            'action_input': "cp ~/.zlogin.zsh ./zlogin.zsh.bak",
            'observation': "",
            'message': "Très bien, ~/.zlogin.zsh a été copié vers ./zlogin.zsh.bak.",
        },
        'en': {
            'action_input': "cp ~/.zlogin.zsh ./zlogin.zsh.bak",
            'observation': "",
            'message': "Alright, ~/.zlogin.zsh was copied at ./zlogin.zsh.bak.",
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

# copy with three parameters.

_threeargs_conv = [
    {
        'fr': {
            'message': "cp ~/.zlogin.zsh ~/.zshenv ~/.zshrc /tmp/",
        },
        'en': {
            'message': "cp ~/.zlogin.zsh ~/.zshenv ~/.zshrc /tmp/",
        },
    },
    {
        'fr': {
            'action_input': "cp ~/.zlogin.zsh ~/.zshenv ~/.zshrc /tmp/",
            'observation': "",
            'message': "Terminé, ~/.zlogin.zsh, ~/.zshenv et ~/.zshrc ont été copiés dans /tmp.",
        },
        'en': {
            'action_input': "cp ~/.zlogin.zsh ~/.zshenv ~/.zshrc /tmp/",
            'observation': "",
            'message': "Done, ~/.zlogin.zsh, ~/.zshenv and ~/.zshrc have been copied to /tmp.",
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



def get_cp_examples():
    return stories