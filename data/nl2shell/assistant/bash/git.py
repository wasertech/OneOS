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

git_examples = []

# Git examples

git_examples.append(
    {
        'system': "",
        'instruction': "",
        'conversation': [
            { 'role': "human", 'message': "Which version of git am I using?" },
            { 'role': "assistant", 'message': "You are using version 2.42.0 of Git.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "git --version", 'observation': "git version 2.42.0" },
                    { 'action': 'final_answer', 'action_input': "You are using Git version 2.42.0.", 'observation': "" },
                ]
            },
        ]
    }
)

git_examples.append(
    {
        'system': "",
        'instruction': "",
        'conversation': [
            { 'role': "human", 'message': "Quelle version de git est-ce que j'utilise?" },
            { 'role': "assistant", 'message': "Vous utilisez la version 2.42.0 de Git.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "git --version", 'observation': "git version 2.42.0" },
                    { 'action': 'final_answer', 'action_input': "Vous utilisez la version 2.42.0 de Git.", 'observation': "" },
                ]
            },
        ]
    }
)

git_examples.append(
    {
        'system': "",
        'instruction': "",
        'conversation': [
            { 'role': "human", 'message': "What is the current branch?" },
            { 'role': "assistant", 'message': "You are on the main branch.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "git branch", 'observation': "* main" },
                    { 'action': 'final_answer', 'action_input': "You are on the main branch.", 'observation': "" },
                ]
            },
        ]
    }
)

git_examples.append(
    {
        'system': "",
        'instruction': "",
        'conversation': [
            { 'role': "human", 'message': "Quelle est la branche actuelle?" },
            { 'role': "assistant", 'message': "Vous êtes sur la branche main.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "git branch", 'observation': "* main" },
                    { 'action': 'final_answer', 'action_input': "Vous êtes sur la branche main.", 'observation': "" },
                ]
            },
        ]
    }
)

# Git status

git_examples.append(
    {
        'system': "",
        'instruction': "",
        'conversation': [
            { 'role': "human", 'message': "What is the status of my repository?" },
            { 'role': "assistant", 'message': "You are on the main branch and there are no commits yet.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "git status", 'observation': "On branch main\n\nNo commits yet\n\nnothing to commit (create/copy files and use \"git add\" to track)" },
                    { 'action': 'final_answer', 'action_input': "You are on the main branch and there are no commits yet.", 'observation': "" },
                ]
            },
        ]
    }
)

git_examples.append(
    {
        'system': "",
        'instruction': "",
        'conversation': [
            { 'role': "human", 'message': "Quel est l'état de mon dépôt?" },
            { 'role': "assistant", 'message': "Vous êtes sur la branche main et il n'y a pas encore de commits.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "git status", 'observation': "On branch main\n\nNo commits yet\n\nnothing to commit (create/copy files and use \"git add\" to track)" },
                    { 'action': 'final_answer', 'action_input': "Vous êtes sur la branche main et il n'y a pas encore de commits.", 'observation': "" },
                ]
            },
        ]
    }
)

# Git clone

git_examples.append(
    {
        'system': "",
        'instruction': "",
        'conversation': [
            { 'role': "human", 'message': "Clone Django's repository in my local projects directory." },
            { 'role': "assistant", 'message': "",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "git clone git@github.com:django/django.git ~/Projects/Django", 'observation': "Clonage dans '/home/username/Projects/Django'...\nremote: Enumerating objects: 516486, done.\nremote: Counting objects: 100% (120/120), done.\nremote: Compressing objects: 100% (79/79), done.\nremote: Total 516486 (delta 49), reused 93 (delta 41), pack-reused 516366\nRéception d'objets: 100% (516486/516486), 234.75 Mio | 2.96 Mio/s, fait.\nRésolution des deltas: 100% (379934/379934), fait." },
                    { 'action': 'final_answer', 'action_input': "I have cloned Django's respository under Projects.", 'observation': "" },
                ]
            },
        ]
    }
)

git_examples.append(
    {
        'system': "",
        'instruction': "",
        'conversation': [
            { 'role': "human", 'message': "Clone le dépôt de Django dans mon répertoire de projets local." },
            { 'role': "assistant", 'message': "",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "git clone git@github.com:django/django.git ~/Projects/Django", 'observation': "Clonage dans '/home/username/Projects/Django'...\nremote: Enumerating objects: 516486, done.\nremote: Counting objects: 100% (120/120), done.\nremote: Compressing objects: 100% (79/79), done.\nremote: Total 516486 (delta 49), reused 93 (delta 41), pack-reused 516366\nRéception d'objets: 100% (516486/516486), 234.75 Mio | 2.96 Mio/s, fait.\nRésolution des deltas: 100% (379934/379934), fait." },
                    { 'action': 'final_answer', 'action_input': "J'ai cloné le dépôt de Django sous Projets.", 'observation': "" },
                ]
            },
        ]
    }
)

# Git add

git_examples.append(
    {
        'system': "",
        'instruction': "",
        'conversation': [
            { 'role': "human", 'message': "Add the file 'README.md' to the staging area." },
            { 'role': "assistant", 'message': "The file 'README.md' has been added to the staging area.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "git add README.md", 'observation': "" },
                    { 'action': 'final_answer', 'action_input': "The file 'README.md' has been added to the staging area.", 'observation': "" },
                ]
            },
        ]
    }
)

git_examples.append(
    {
        'system': "",
        'instruction': "",
        'conversation': [
            { 'role': "human", 'message': "Ajoute le fichier 'README.md' à la zone de transit." },
            { 'role': "assistant", 'message': "Le fichier 'README.md' a été ajouté à la zone de transit.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "git add README.md", 'observation': "" },
                    { 'action': 'final_answer', 'action_input': "Le fichier 'README.md' a été ajouté à la zone de transit.", 'observation': "" },
                ]
            },
        ]
    }
)

# git commit

git_examples.append(
    {
        'system': "",
        'instruction': "",
        'conversation': [
            { 'role': "human", 'message': "Commit the changes with the message 'Add README.md'." },
            { 'role': "assistant", 'message': "The changes have been committed with the message 'Add README.md'.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "git commit -m 'Add README.md'", 'observation': "[main (root-commit) 0b8a1b7] Add README.md\n 1 file changed, 1 insertion(+)\n create mode 100644 README.md" },
                    { 'action': 'final_answer', 'action_input': "The changes have been committed with the message 'Add README.md'.", 'observation': "" },
                ]
            },
        ]
    }
)

git_examples.append(
    {
        'system': "",
        'instruction': "",
        'conversation': [
            { 'role': "human", 'message': "Commit les changements avec le message 'Ajouter README.md'." },
            { 'role': "assistant", 'message': "Les changements ont été validés avec le message 'Ajouter README.md'.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "git commit -m 'Ajouter README.md'", 'observation': "[main (root-commit) 0b8a1b7] Ajouter README.md\n 1 file changed, 1 insertion(+)\n create mode 100644 README.md" },
                    { 'action': 'final_answer', 'action_input': "Les changements ont été validés avec le message 'Ajouter README.md'.", 'observation': "" },
                ]
            },
        ]
    }
)

# git push

git_examples.append(
    {
        'system': "",
        'instruction': "",
        'conversation': [
            { 'role': "human", 'message': "Push the changes to the remote repository." },
            { 'role': "assistant", 'message': "The changes have been pushed to the remote repository.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "git push", 'observation': "Décompte des objets: 3, fait.\nÉcriture des objets: 100% (3/3), 225 bytes | 225.00 KiB/s, fait.\nTotal 3 (delta 0), reused 0 (delta 0), pack-reused 0\nTo github.com:username/repo.git\n * [new branch]      main -> main" },
                    { 'action': 'final_answer', 'action_input': "The changes have been pushed to the remote repository.", 'observation': "" },
                ]
            },
        ]
    }
)

git_examples.append(
    {
        'system': "",
        'instruction': "",
        'conversation': [
            { 'role': "human", 'message': "Pousse les changements vers le dépôt distant." },
            { 'role': "assistant", 'message': "Les changements ont été poussés vers le dépôt distant.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "git push", 'observation': "Décompte des objets: 3, fait.\nÉcriture des objets: 100% (3/3), 225 bytes | 225.00 KiB/s, fait.\nTotal 3 (delta 0), reused 0 (delta 0), pack-reused 0\nTo github.com:username/repo.git\n * [new branch]      main -> main" },
                    { 'action': 'final_answer', 'action_input': "Les changements ont été poussés vers le dépôt distant.", 'observation': "" },
                ]
            },
        ]
    }
)

# git pull

git_examples.append(
    {
        'system': "",
        'instruction': "",
        'conversation': [
            { 'role': "human", 'message': "Pull the changes from the remote repository." },
            { 'role': "assistant", 'message': "The changes have been pulled from the remote repository.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "git pull", 'observation': "Décompte des objets: 3, fait.\nÉcriture des objets: 100% (3/3), 225 bytes | 225.00 KiB/s, fait.\nTotal 3 (delta 0), reused 0 (delta 0), pack-reused 0\nTo github.com:username/repo.git\n * [new branch]      main -> main" },
                    { 'action': 'final_answer', 'action_input': "The changes have been pulled from the remote repository.", 'observation': "" },
                ]
            },
        ]
    }
)

git_examples.append(
    {
        'system': "",
        'instruction': "",
        'conversation': [
            { 'role': "human", 'message': "Tire les changements du dépôt distant." },
            { 'role': "assistant", 'message': "Les changements ont été tirés du dépôt distant.",  'scratchpad': [
                    { 'action': 'Bash', 'action_input': "git pull", 'observation': "Décompte des objets: 3, fait.\nÉcriture des objets: 100% (3/3), 225 bytes | 225.00 KiB/s, fait.\nTotal 3 (delta 0), reused 0 (delta 0), pack-reused 0\nTo github.com:username/repo.git\n * [new branch]      main -> main" },
                    { 'action': 'final_answer', 'action_input': "Les changements ont été tirés du dépôt distant.", 'observation': "" },
                ]
            },
        ]
    }
)

def get_git_examples():
    return git_examples
