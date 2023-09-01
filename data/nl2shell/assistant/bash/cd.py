# Bash: cd
# English: Go to my home directory.
# French: Va dans mon répertoire personnel.

# Bash: cd /
# English: Go to the root directory.
# French: Déplace-toi dans le répertoire racine.

# Bash: cd /home/user/documents
# English: Go to the "documents" folder in the user's home directory.
# French: Va dans le dossier "documents" dans le répertoire personnel de l'utilisateur.

# Bash: cd ../..
# English: Go up two levels in the directory hierarchy.
# French: Remonte de deux niveaux dans la hiérarchie des dossiers.

# Bash: cd ~/Desktop
# English: Go to the "Desktop" folder in your home directory.
# French: Va dans le dossier "Bureau" dans ton répertoire personnel.

# Bash: cd /var/www/html
# English: Go to the "html" folder in the "/var/www" directory.
# French: Déplace-toi dans le dossier "html" dans le répertoire "/var/www".

# Bash: cd /etc
# English: Go to the "/etc" directory.
# French: Va dans le répertoire "/etc".

# Bash: cd ../../shared
# English: Go up two levels and then into the "shared" folder.
# French: Remonte de deux niveaux et entre dans le dossier "shared".

# Bash: cd ~/Documents/Work\ Projects
# English: Go to the "Work Projects" folder inside the "Documents" folder in your home directory.
# French: Va dans le dossier "Projets de travail" dans le dossier "Documents" de ton répertoire personnel.

# Bash: cd -
# English: Go back to the previous directory you were in.
# French: Retourne dans le répertoire précédent où tu étais.

# Examples for the user asking the 'cd' command in a natural way
user_ask_cd_en = [
    "Change the directory to /home/user/documents.",
    "Can you navigate to /var/www/html?",
    "Move to the 'Music' folder in my home directory.",
    "Switch to the parent directory.",
    "Go up two levels.",
    "Take me to /etc.",
    "I want to go to /mnt/external_drive.",
    "Move into the 'Videos' folder inside my 'Documents' directory.",
    "Change the directory to /usr/local/bin.",
    "Can you take me to the 'Pictures' folder?",
    "Go to my home directory.",
    "Go to the root directory.",
    "Go to the 'documents' folder in the user's home directory.",
    "Go up two levels in the directory hierarchy.",
    "Go to the 'Desktop' folder in your home directory.",
    "Go to the 'html' folder in the '/var/www' directory.",
    "Go to the '/etc' directory.",
    "Go up two levels and then into the 'shared' folder.",
    "Go to the 'Work Projects' folder inside the 'Documents' folder in your home directory.",
    "Go back to the previous directory you were in.",
]

user_ask_cd_fr = [
    "Déplace-toi dans le répertoire /home/user/documents.",
    "Peux-tu naviguer vers /var/www/html ?",
    "Va dans le dossier 'Musique' dans mon répertoire personnel.",
    "Retourne au répertoire parent.",
    "Remonte de deux niveaux.",
    "Mène-moi à /etc.",
    "Je veux aller dans /mnt/external_drive.",
    "Dirige-toi vers le dossier 'Vidéos' à l'intérieur de mon dossier 'Documents'.",
    "Déplace-toi dans le répertoire /usr/local/bin.",
    "Peux-tu m'amener dans le dossier 'Images' ?",
    "Va dans mon répertoire personnel.",
    "Va dans le répertoire racine.",
    "Va dans le dossier 'documents' dans le répertoire personnel de l'utilisateur.",
    "Remonte de deux niveaux dans la hiérarchie des dossiers.",
    "Va dans le dossier 'Bureau' dans ton répertoire personnel.",
    "Va dans le dossier 'html' dans le répertoire '/var/www'.",
    "Va dans le répertoire '/etc'.",
    "Remonte de deux niveaux et entre dans le dossier 'shared'.",
    "Va dans le dossier 'Projets de travail' dans le dossier 'Documents' de ton répertoire personnel.",
    "Retourne dans le répertoire précédent où tu étais.",
]

# Examples of sentences responding to the 'cd' command
response_cd_en = [
    "You are now in the /home/user/documents directory.",
    "Sure, you have navigated to /var/www/html.",
    "You have switched to the 'Music' folder in your home directory.",
    "You are now in the parent directory.",
    "You have moved up two levels.",
    "You are now in the /etc directory.",
    "Alright, you are in /mnt/external_drive.",
    "You have moved into the 'Videos' folder inside your 'Documents' directory.",
    "You are now in the /usr/local/bin directory.",
    "Sure, you are in the 'Pictures' folder.",
    "You are now in your home directory.",
    "You are now in the root directory.",
    "You have gone to the 'documents' folder in the user's home directory.",
    "You have gone up two levels in the directory hierarchy.",
    "You arrived at your desk.",
    "You have gone to the 'html' folder in the '/var/www' directory.",
    "Entering '/etc' directory.",
    "You have gone up two levels and then into the 'shared' folder.",
    "Welcome to the 'Work Projects' folder inside the 'Documents' folder in your home directory.",
    "You have gone back to the previous directory you were in.",
]

response_cd_fr = [
    "Vous êtes maintenant dans le répertoire /home/user/documents.",
    "Bien sûr, vous avez navigué vers /var/www/html.",
    "Vous êtes maintenant dans le dossier 'Musique' dans votre répertoire personnel.",
    "Vous êtes maintenant dans le répertoire parent.",
    "Vous avez remonté de deux niveaux.",
    "Vous êtes maintenant dans le répertoire /etc.",
    "D'accord, vous êtes dans /mnt/external_drive.",
    "Vous êtes maintenant dans le dossier 'Vidéos' à l'intérieur de votre dossier 'Documents'.",
    "Vous êtes maintenant dans le répertoire /usr/local/bin.",
    "Bien sûr, vous êtes dans le dossier 'Images'."
    "Vous êtes maintenant dans votre répertoire personnel.",
    "Vous êtes maintenant dans le répertoire racine.",
    "Vous êtes allé dans le dossier 'documents' dans le répertoire personnel de l'utilisateur.",
    "Vous avez remonté de deux niveaux dans la hiérarchie des dossiers.",
    "Vous arrivez au bureau, prêt à travailler.",
    "Vous êtes dans le dossier 'html' dans le répertoire '/var/www'.",
    "Entrée dans le répertoire '/etc'.",
    "Vous avez remonté de deux niveaux et entrez dans le dossier 'shared'.",
    "Bienvenue dans le dossier 'Projets de travail' dans le dossier 'Documents' de votre répertoire personnel.",
    "Vous êtes retourné dans le répertoire précédent où vous étiez.",
]


action_cd = [
    "cd /home/user/documents",
    "cd /var/www/html",
    "cd ~/Music",
    "cd ..",
    "cd ../..",
    "cd /etc",
    "cd /mnt/external_drive",
    "cd ~/Documents/Videos",
    "cd /usr/local/bin",
    "cd ~/Pictures",
    "cd ~",
    "cd /",
    "cd ~/Documents/documents",
    "cd ../..",
    "cd ~/Desktop",
    "cd /var/www/html",
    "cd /etc",
    "cd ../../shared",
    "cd ~/Documents/Work Projects",
    "cd -",
]

data = []

for query, response, action in zip(user_ask_cd_en, response_cd_en, action_cd):
    conversation = [
        {'role': 'human', 'message': query},
        {'role': 'assistant', 'message': response, 'scratchpad': [
                {'action': 'Bash', 'action_input': action, 'observation': ""},
                {'action': 'final_answer', 'action_input': response, 'observation': ""},
            ]
        }
    ]
    data.append({'system': "", 'instruction': "", 'conversation': conversation})

def get_cd_examples(dataset=data):    
    return dataset