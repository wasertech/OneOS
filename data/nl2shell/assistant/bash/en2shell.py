# data = [
#     {
#         'system': "",
#         'instruction': "",
#         'conversation': [
#             { 'role': "human", 'message': "Bonjour" },
#             { 'role': "assistant", 'message': "Bonjour! Vous êtes bien matinal aujourd'hui.",  'scratchpad': [
#                     { 'action': 'Shell', 'action_input': "date", 'observation': "mer 02 aoû 2023 03:59:15 CEST" },
#                     { 'action': 'final_answer', 'action_input': "Bonjour! Vous êtes bien matinal aujourd'hui.", 'observation': "" },
#                 ]
#             },
#             { 'role': "human", 'message': "Quel jour sommes-nous?" },
#             { 'role': "assistant", 'message': "mer 02 aoû 2023 03:59:15 CEST",  'scratchpad': [
#                     { 'action': 'Shell', 'action_input': "date", 'observation': "mer 02 aoû 2023 03:59:15 CEST" },
#                     { 'action': 'final_answer', 'action_input': "Nous sommes le mercredi 2 août 2023.", 'observation': "" },
#                 ]
#             },
#         ]
#     }
# ]

def get_nl2shell_english_examples():
    data = []

    with open('nl2shell.en.nl', 'r') as nl_file, open('nl2shell.cm', 'r') as cm_file:
        for nl_line, cm_line in zip(nl_file, cm_file):
            
            query = nl_line.strip()
            output = cm_line.strip()

            if query.startswith('('):
                continue
            elif "exit" in output:
                continue
            else:
                data.append({
                    'lang': 'en',
                    'system': "",
                    'instruction': "",
                    'conversation': [
                        { 'role': "human", 'message': query },
                        { 'role': "assistant", 'message': "",  'scratchpad': [
                                { 'function': 'shell', 'parameters': {'code': output}, 'observation': "" },
                            ]
                        },
                    ]
                })
    
    return data