import random

pwd_data = {}

# Bash Output: /
# English: You are at the root of your directories.
# French: Vous êtes à la racine de vos dossiers.

path = "/"

pwd_data[path] = {
    'en': [
        "You are at the root of your directories.",
        "You are in the top-level directory.",
        "You are at the starting point of your file system.",
        "You are in the root directory.",
        "You are at the highest level of your folder structure.",
        "Your current location is the root folder.",
        "You are in the main directory.",
        "You are at the base of your file system.",
        "Your working directory is the root.",
        "You are in the primary directory.",
    ],
    'fr': [
        "Vous êtes à la racine de vos dossiers.",
        "Vous êtes dans le répertoire de niveau supérieur.",
        "Vous êtes au point de départ de votre système de fichiers.",
        "Vous êtes dans le répertoire racine.",
        "Vous êtes au niveau le plus élevé de votre structure de dossiers.",
        "Votre emplacement actuel est le dossier racine.",
        "Vous êtes dans le répertoire principal.",
        "Vous êtes à la base de votre système de fichiers.",
        "Votre répertoire de travail est la racine.",
        "Vous êtes dans le répertoire principal.",
    ]
}

# Bash Output: /home/user/documents
# English: You are in the "documents" folder in your home directory.
# French: Vous êtes dans le dossier "documents" de votre répertoire personnel.

pwd_data["/home/user/documents"] = {
    "en": [
        "You are in the 'documents' folder in your home directory.",
        "You are currently located in the 'documents' directory in your home folder.",
        "Your current location is inside the 'documents' folder within your home directory.",
        "You have navigated to the 'documents' folder in your home path.",
        "You are currently in the 'documents' directory within your home directory.",
        "Your current working directory is the 'documents' folder in your home directory.",
        "You are at '/home/user/documents'.",
        "Your current location is '/home/user/documents'.",
        "You have navigated to '/home/user/documents'.",
        "You are currently at '/home/user/documents'.",
    ],
    "fr": [
        "Vous êtes dans le dossier 'documents' de votre répertoire personnel.",
        "Vous vous trouvez actuellement dans le répertoire 'documents' de votre dossier personnel.",
        "Votre emplacement actuel se trouve à l'intérieur du dossier 'documents' de votre répertoire personnel.",
        "Vous avez navigué jusqu'au dossier 'documents' de votre répertoire personnel.",
        "Vous êtes actuellement dans le répertoire 'documents' de votre dossier personnel.",
        "Votre répertoire de travail actuel est le dossier 'documents' de votre répertoire personnel.",
        "Vous êtes à '/home/user/documents'.",
        "Votre emplacement actuel est '/home/user/documents'.",
        "Vous avez navigué jusqu'à '/home/user/documents'.",
        "Vous êtes actuellement à '/home/user/documents'.",
    ]
}

# Bash Output: /var/www/html
# English: You are in the "html" folder inside the "/var/www" directory.
# French: Vous êtes dans le dossier "html" dans le répertoire "/var/www".

pwd_data["/var/www/html"] = {
    'en': [
        "You are currently in the '/var/www/html' directory.",
        "The current working directory is '/var/www/html'.",
        "Your current location is '/var/www/html'.",
        "You have navigated to '/var/www/html'.",
        "You are inside the '/var/www/html' folder.",
        "Currently, you are at '/var/www/html'.",
        "Your present working directory is '/var/www/html'.",
        "You have changed to '/var/www/html'.",
        "Now, you are in the '/var/www/html' directory.",
        "The current path is '/var/www/html'.",
    ],
    'fr': [
        "Vous êtes actuellement dans le répertoire '/var/www/html'.",
        "Le répertoire de travail actuel est '/var/www/html'.",
        "Votre emplacement actuel est '/var/www/html'.",
        "Vous avez navigué vers '/var/www/html'.",
        "Vous êtes à l'intérieur du dossier '/var/www/html'.",
        "Actuellement, vous êtes à '/var/www/html'.",
        "Votre répertoire de travail présent est '/var/www/html'.",
        "Vous avez changé pour '/var/www/html'.",
        "Maintenant, vous vous trouvez dans le répertoire '/var/www/html'.",
        "Le chemin actuel est '/var/www/html'.",
    ]
}

# Bash Output: /etc
# English: You are in the "/etc" directory.
# French: Vous êtes dans le répertoire "/etc".

pwd_data["/etc"] = {
    'en': [
        "You are in the /etc directory.",
        "Currently, you are located in the /etc folder.",
        "The current working directory is /etc.",
        "You have navigated to /etc.",
        "Your current location is the /etc directory.",
        "The present directory is /etc.",
        "You are inside the /etc folder.",
        "You have changed to the /etc directory.",
        "You are at /etc in the directory tree.",
        "Your current path is /etc.",
    ],
    'fr': [
        "Vous êtes dans le répertoire /etc.",
        "Actuellement, vous vous trouvez dans le dossier /etc.",
        "Le répertoire de travail actuel est /etc.",
        "Vous êtes arrivé(e) à /etc.",
        "Votre emplacement actuel est le répertoire /etc.",
        "Le répertoire courant est /etc.",
        "Vous vous trouvez à l'intérieur du dossier /etc.",
        "Vous avez changé pour le répertoire /etc.",
        "Vous êtes à /etc dans l'arborescence des dossiers.",
        "Votre chemin actuel est /etc.",
    ]
}

# Bash Output: /home/user/Pictures/Family\ Vacation
# English: You are in the "Family Vacation" folder inside the "Pictures" folder in your home directory.
# French: Vous êtes dans le dossier "Vacances en famille" dans le dossier "Images" de votre répertoire personnel.

pwd_data["/home/user/Pictures/Family\\ Vacation"] = {
    'en': [
        "You are in the 'Family Vacation' folder inside the 'Pictures' folder in your home directory.",
        "You are currently at '/home/user/Pictures/Family Vacation'.",
        "Your current location is '/home/user/Pictures/Family Vacation'.",
        "You are in the 'Family Vacation' folder inside the 'Pictures' directory in your home folder.",
        "You are located at '/home/user/Pictures/Family Vacation'.",
        "You are inside the 'Family Vacation' folder within the 'Pictures' folder in your home directory.",
        "You are at '/home/user/Pictures/Family Vacation'.",
        "You are currently in the 'Family Vacation' folder inside the 'Pictures' folder in your home directory.",
        "You are presently at '/home/user/Pictures/Family Vacation'.",
        "You have navigated to the 'Family Vacation' folder inside the 'Pictures' directory in your home folder.",
    ],
    'fr': [
        "Vous êtes dans le dossier 'Vacances en famille' dans le dossier 'Images' de votre répertoire personnel.",
        "Vous êtes actuellement dans '/home/user/Pictures/Family Vacation'.",
        "Votre emplacement actuel est '/home/user/Pictures/Family Vacation'.",
        "Vous êtes dans le dossier 'Vacances en famille' dans le répertoire 'Images' de votre répertoire personnel.",
        "Vous êtes situé(e) à '/home/user/Pictures/Family Vacation'.",
        "Vous vous trouvez dans le dossier 'Vacances en famille' à l'intérieur du dossier 'Images' de votre répertoire personnel.",
        "Vous êtes à '/home/user/Pictures/Family Vacation'.",
        "Vous êtes actuellement dans le dossier 'Vacances en famille' à l'intérieur du dossier 'Images' de votre répertoire personnel.",
        "Vous êtes actuellement à '/home/user/Pictures/Family Vacation'.",
        "Vous avez navigué jusqu'au dossier 'Vacances en famille' à l'intérieur du dossier 'Images' de votre répertoire personnel.",
    ]
}

# Bash Output: /usr/local/bin
# English: You are in the "bin" folder inside the "/usr/local" directory.
# French: Vous êtes dans le dossier "bin" dans le répertoire "/usr/local".

pwd_data["/usr/local/bin"] = {
    'en': [
        "You are currently in the '/usr/local/bin' directory.",
        "Your current location is '/usr/local/bin'.",
        "You have navigated to '/usr/local/bin'.",
        "The working directory is set to '/usr/local/bin'.",
        "You are inside the '/usr/local/bin' folder.",
        "Your current path is '/usr/local/bin'.",
        "You have changed to the '/usr/local/bin' directory.",
        "You are at '/usr/local/bin' now.",
        "The present directory is '/usr/local/bin'.",
        "Your current working directory is '/usr/local/bin'.",
    ],
    'fr': [
        "Vous êtes actuellement dans le répertoire '/usr/local/bin'.",
        "Votre emplacement actuel est '/usr/local/bin'.",
        "Vous vous trouvez dans le dossier '/usr/local/bin'.",
        "Le répertoire de travail est défini sur '/usr/local/bin'.",
        "Vous êtes à l'intérieur du dossier '/usr/local/bin'.",
        "Votre chemin actuel est '/usr/local/bin'.",
        "Vous avez changé pour le répertoire '/usr/local/bin'.",
        "Vous êtes maintenant dans '/usr/local/bin'.",
        "Le répertoire présent est '/usr/local/bin'.",
        "Votre répertoire de travail actuel est '/usr/local/bin'.",
    ]
}

# Bash Output: /mnt/external_drive
# English: You are in the "external_drive" folder inside the "/mnt" directory.
# French: Vous êtes dans le dossier "external_drive" dans le répertoire "/mnt".

pwd_data["/mnt/external_drive"] = {
    "en": [
        "You are currently in the '/mnt/external_drive' directory.",
        "Your current working directory is '/mnt/external_drive'.",
        "You have navigated to '/mnt/external_drive'.",
        "You are located at '/mnt/external_drive'.",
        "You are inside the '/mnt/external_drive' folder.",
        "You have reached the '/mnt/external_drive' directory.",
        "The present working directory is '/mnt/external_drive'.",
        "You are exploring the '/mnt/external_drive' directory.",
        "Your current location is '/mnt/external_drive'.",
        "You are at '/mnt/external_drive'.",
    ],
    "fr": [
        "Vous êtes actuellement dans le répertoire '/mnt/external_drive'.",
        "Votre répertoire de travail actuel est '/mnt/external_drive'.",
        "Vous avez navigué jusqu'au répertoire '/mnt/external_drive'.",
        "Vous vous trouvez à '/mnt/external_drive'.",
        "Vous êtes à l'intérieur du dossier '/mnt/external_drive'.",
        "Vous avez atteint le répertoire '/mnt/external_drive'.",
        "Le répertoire de travail actuel est '/mnt/external_drive'.",
        "Vous explorez le répertoire '/mnt/external_drive'.",
        "Votre emplacement actuel est '/mnt/external_drive'.",
        "Vous êtes à '/mnt/external_drive'.",
    ]
}

# Bash Output: /home/user/Downloads/../Videos
# English: You are in the "Videos" folder inside your home directory, regardless of the current location.
# French: Vous êtes dans le dossier "Vidéos" de votre répertoire personnel, peu importe l'emplacement actuel.

pwd_data["/home/user/Videos"] = {
    'en': [
        "You are in the 'Videos' folder inside your home directory.",
        "You are currently in the 'Videos' folder inside your home directory.",
        "Your current location is the 'Videos' folder in your home directory.",
        "You have navigated to the 'Videos' folder in your home directory.",
        "Your present working directory is the 'Videos' folder in your home directory.",
        "You are currently located in the 'Videos' folder inside your home directory.",
        "You are in the 'Videos' folder in your home directory, regardless of previous location.",
        "You have arrived at the 'Videos' folder inside your home directory.",
        "Your current working directory is the 'Videos' folder in your home directory.",
        "You are currently at the 'Videos' folder inside your home directory.",
    ],
    'fr': [
        "Vous êtes dans le dossier 'Vidéos' de votre répertoire personnel.",
        "Vous vous trouvez actuellement dans le dossier 'Vidéos' de votre répertoire personnel.",
        "Votre emplacement actuel est le dossier 'Vidéos' de votre répertoire personnel.",
        "Vous avez navigué jusqu'au dossier 'Vidéos' de votre répertoire personnel.",
        "Votre répertoire de travail actuel est le dossier 'Vidéos' de votre répertoire personnel.",
        "Vous êtes actuellement situé dans le dossier 'Vidéos' de votre répertoire personnel.",
        "Vous êtes dans le dossier 'Vidéos' de votre répertoire personnel, peu importe l'emplacement précédent.",
        "Vous êtes arrivé(e) dans le dossier 'Vidéos' de votre répertoire personnel.",
        "Votre répertoire de travail actuel est le dossier 'Vidéos' de votre répertoire personnel.",
        "Vous êtes actuellement au niveau du dossier 'Vidéos' de votre répertoire personnel.",
    ]
}

# Bash Output: /var/log/apache2
# English: You are in the "apache2" folder inside the "/var/log" directory.
# French: Vous êtes dans le dossier "apache2" dans le répertoire "/var/log".

pwd_data["/var/log/apache2"] = {
    'en': [
        "You are currently in the '/var/log/apache2' directory.",
        "The current working directory is '/var/log/apache2'.",
        "You have navigated to '/var/log/apache2'.",
        "Your current location is '/var/log/apache2'.",
        "The path '/var/log/apache2' points to your current directory.",
        "You are in the '/var/log/apache2' folder.",
        "Your present working directory is '/var/log/apache2'.",
        "You have changed to the '/var/log/apache2' directory.",
        "You are inside '/var/log/apache2' now.",
        "Your current directory is '/var/log/apache2'.",
    ],
    'fr': [
        "Vous êtes actuellement dans le répertoire '/var/log/apache2'.",
        "Le répertoire de travail actuel est '/var/log/apache2'.",
        "Vous avez navigué jusqu'à '/var/log/apache2'.",
        "Votre emplacement actuel est '/var/log/apache2'.",
        "Le chemin '/var/log/apache2' pointe vers votre répertoire actuel.",
        "Vous êtes dans le dossier '/var/log/apache2'.",
        "Votre répertoire de travail présent est '/var/log/apache2'.",
        "Vous avez changé pour le répertoire '/var/log/apache2'.",
        "Vous êtes maintenant à l'intérieur de '/var/log/apache2'.",
        "Votre répertoire actuel est '/var/log/apache2'.",
    ]
}

# Bash Output: /home/user
# English: You are in your home directory.
# French: Vous êtes dans votre répertoire personnel.

pwd_data["/home/user"] = {
    'en': [
        "You are in your home directory.",
        "You are currently at /home/user.",
        "Your current working directory is /home/user.",
        "You are located in the /home/user directory.",
        "You have navigated to /home/user.",
        "Your current location is in the /home/user folder.",
        "You are at the path /home/user.",
        "The present working directory is /home/user.",
        "You have landed in /home/user.",
        "You are in the user's home directory (/home/user).",
    ],
    'fr': [
        "Vous êtes dans votre répertoire personnel.",
        "Vous êtes actuellement dans /home/user.",
        "Votre répertoire de travail actuel est /home/user.",
        "Vous êtes situé dans le répertoire /home/user.",
        "Vous avez navigué vers /home/user.",
        "Votre emplacement actuel est le dossier /home/user.",
        "Vous êtes au chemin /home/user.",
        "Le répertoire de travail actuel est /home/user.",
        "Vous avez atterri dans /home/user.",
        "Vous êtes dans le répertoire personnel de l'utilisateur (/home/user).",
    ]
}

# Example of pwd intents
trigger_sentences = {}
trigger_sentences['en'] = [
    "What is the current directory?",
    "Show me the present working directory.",
    "Print the current path.",
    "Display the current folder.",
    "What folder am I in right now?",
    "Tell me the path of the current directory.",
    "What is my current location?",
    "Show the full path.",
    "Print the absolute path.",
    "What directory is this?",
    "Show the current working directory.",
    "Display the full path of the current directory.",
    "What is the current location?",
    "Where am I right now?",
    "Tell me the present working directory.",
    "Show the absolute path.",
    "Display the full path.",
    "What is my current working folder?",
    "What directory am I in?",
    "Tell me the absolute path.",
]


trigger_sentences['fr'] = [
    "Quel est le répertoire courant ?",
    "Affiche-moi le répertoire de travail actuel.",
    "Afficher le chemin actuel.",
    "Montre le dossier courant.",
    "Dans quel dossier suis-je actuellement ?",
    "Donne-moi le chemin du répertoire courant.",
    "Quel est mon emplacement actuel ?",
    "Affiche le chemin complet.",
    "Donne le chemin absolu.",
    "Quel répertoire est-ce ?",
    "Montre le répertoire de travail actuel.",
    "Afficher le chemin complet du répertoire courant.",
    "Quel est l'emplacement actuel ?",
    "Où suis-je en ce moment ?",
    "Dis-moi le répertoire de travail actuel.",
    "Montre le chemin absolu.",
    "Affiche le chemin complet.",
    "Quel est mon répertoire de travail actuel ?",
    "Dans quel répertoire suis-je ?",
    "Dis-moi le chemin absolu.",
]


def get_pwd_data():
    data = []
    for path in pwd_data:
        for lang in pwd_data[path]:
            for assistant_reply in pwd_data[path][lang]:
                user_msg = random.choice(trigger_sentences[lang])
                
                conversation = [
                    { 'role': 'human', 'message': user_msg },
                    {
                        'role': 'assistant',
                        'message': assistant_reply,
                        'scratchpad': [
                            { 'action': 'Bash', 'action_input': 'pwd', 'observation': path },
                            { 'action': 'final_answer', 'action_input': assistant_reply, 'observation': "" }
                        ]
                    }
                ]
                data.append({'system': "", 'instruction': "", 'conversation': conversation})

    return data