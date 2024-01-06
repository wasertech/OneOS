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

cat_examples = {
    'user_ask': {
        'en': [
            "Show me the content of {file_name}.",
            "What's inside {file_name}?",
            "Display {file_name} contents.",
            "Can you print {file_name} for me?",
            "Let me see the file {file_name}.",
            "Open {file_name} and show me.",
            "What does {file_name} contain?",
            "Read {file_name} to me.",
            "Print the content of {file_name}.",
            "I want to see the file {file_name}."
        ],
        'fr': [
            "Affiche-moi le contenu du fichier {file_name}.",
            "Que contient le fichier {file_name}?",
            "Montre le contenu du fichier {file_name}.",
            "{file_name}; Peux-tu imprimer le fichier pour moi ?",
            "Laisse-moi voir le fichier qui s'appelle {file_name}.",
            "Ouvre le fichier {file_name} et montre-le-moi.",
            "Qu'est-ce que le fichier {file_name} contient ?",
            "Lis-moi le contenu du fichier {file_name}.",
            "Afficher le contenu du fichier {file_name}.",
            "Je veux voir le fichier {file_name}."
        ]
    },
    'assistant_response': {
        'en': [
            "Sure, here's the content of the filenamed {file_name}:\n```txt\n{file_content}\n```",
            "The file contains the following:\n```txt\n{file_content}\n```",
            "Here's what's inside the file:\n```csv\n{file_content}\n```",
            "Printing the file content:\n```yml\n{file_content}\n```",
            "File contents displayed below:\n```md\n{file_content}\n```",
            "Opening the file, here's what it says:\n```ini\n{file_content}\n```",
            "The file contains the following data:\n```python\n{file_content}",
            "Reading the file for you:\n```rst\n{file_content}\n```",
            "Here's the content of the file:\n```json\n{file_content}\n```",
            "Displaying the file content:\n```txt\n{file_content}\n```"
        ],
        'fr': [
            "Bien sûr, voici le contenu du fichier {file_name}:\n```txt\n{file_content}\n```",
            "Le fichier contient ceci :\n```txt\n{file_content}\n```",
            "Voici ce qu'il y a dans le fichier {file_name}:\n```csv\n{file_content}\n```",
            "Impression du contenu du fichier {file_name}:\n```yml\n{file_content}\n```",
            "Contenu du fichier {file_name} affiché ci-dessous :\n```md\n{file_content}\n```",
            "Ouverture du fichier {file_name}, voici ce qu'il dit :\n```ini\n{file_content}\n```",
            "Le fichier contient les données suivantes :\n```python\n{file_content}\n```",
            "Je lis le fichier pour vous :\n```rst\n{file_content}\n```",
            "Voici le contenu du fichier :\n```json\n{file_content}\n```",
            "Affichage du contenu du fichier :\n```txt\n{file_content}\n```"
        ]
    }
}

# Add some fake file examples here
file_data = {
    'file1.txt': 'This is the content of file1.txt.',
    'file2.txt': 'Welcome to file2.txt. Have a nice day!',
    'data.csv': 'Name,Age,Occupation\nJohn,30,Engineer\nAlice,25,Teacher\nBob,40,Doctor',
    'config.yml': 'database:\n  host: localhost\n  port: 5432\n  username: admin\n  password: secret',
    'notes.md': '# Meeting Notes\n\n## Agenda\n1. Introduction\n2. Project Updates\n3. Q&A\n',
    'settings.ini': '[General]\nlanguage = en\ntheme = dark\nfont_size = 14',
    'script.py': 'def main():\n    print("Hello, this is script.py")\n\nif __name__ == "__main__":\n    main()',
    'readme.rst': 'Welcome to this project.\nPlease read the instructions carefully.\n',
    'data.json': '{ "name": "John", "age": 30, "occupation": "Engineer" }',
    'README.txt': 'Welcome to this project.\nPlease read the instructions carefully.\n'
}

guides = {
    'en': """# Read a file

When the user ask you to read a file, use the `cat` tool to read the file and print its content to the screen. Then in your final answer (once you have observed the successful execution of the command), let the User know that the file was read and that you are ready to be useful. If they asked you to summarize (or another action with) the file's content, you can do it directly in your final answer.
""",
    'fr': """# Lire un fichier

Lorsque l'utilisateur vous demande de lire un fichier, utilisez l'outil `cat` pour lire le fichier et imprimer son contenu à l'écran. Ensuite, dans votre réponse finale (une fois que vous avez observé l'exécution réussie de la commande), faites savoir à l'utilisateur que le fichier a été lu et que vous êtes prêt à être utile. S'ils vous ont demandé de résumer (ou une autre action avec) le contenu du fichier, vous pouvez le faire directement dans votre réponse finale.
"""
}

def get_cat_examples():
    data = []
    for i, (file_name, file_content) in enumerate(file_data.items()):
        user_ask_en = cat_examples['user_ask']['en'][i].format(file_name=file_name)
        user_ask_fr = cat_examples['user_ask']['fr'][i].format(file_name=file_name)
        assistant_reply_en = cat_examples['assistant_response']['en'][i].format(file_name=file_name, file_content=file_content)
        assistant_reply_fr = cat_examples['assistant_response']['fr'][i].format(file_name=file_name, file_content=file_content)
        data.append({
            'lang': 'en',
            'system': system_prompt.get('en', ""),
            'instruction': intruction_prompt.get('en', ""),
            'conversation': [
                { 'role': "human", 'message': user_ask_en, 'guide': guides.get('en') },
                { 'role': "assistant", 'message': assistant_reply_en,  'scratchpad': [
                        { 'function': 'shell', 'parameters': {'code': f"cat {file_name}"}, 'observation': file_content },
                        { 'function': 'final_answer', 'parameters': {'answer': assistant_reply_en}, 'observation': "" },
                    ]
                },
            ]
        })
        data.append({
            'lang': 'fr',
            'system': system_prompt.get('fr', ""),
            'instruction': intruction_prompt.get('fr', ""),
            'conversation': [
                { 'role': "human", 'message': user_ask_fr, 'guide': guides.get('fr') },
                { 'role': "assistant", 'message': assistant_reply_fr,  'scratchpad': [
                        { 'function': 'shell', 'parameters': {'code': f"cat {file_name}"}, 'observation': file_content },
                        { 'function': 'final_answer', 'parameters': {'answer': assistant_reply_fr}, 'observation': "" },
                    ]
                },
            ]
        })
    return data

