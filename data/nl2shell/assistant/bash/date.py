import random

# Examples of date command usage:

cmd_data = {}

# Bash: date
# Output: mer 02 aoû 2023 03:59:15 CEST
# English: What is the current date and time?
# French: Quelle est la date et l'heure actuelles ?

cmd_data['date'] = {
    'output': "mer 02 aoû 2023 03:59:15 CEST",
    'french_answer': [
        "Nous sommes le mercredi 2 août 2023.",
        "Nous sommes le mercredi 2 août 2023, il est 3 heures 59.",
        "Nous sommes le mercredi 2 août 2023 et il sera 4 heures dans une minute.",
    ],
    'english_answer': [
        "We are Wednesday, August 2, 2023.",
        "We are Wednesday, August 2, 2023, it is 3 o'clock 59.",
        "We are Wednesday, August 2, 2023 and it will be 4 o'clock in a minute.",
    ],
    'french': [
        "Quelle est la date et l'heure actuelles ?",
        "date et heure?",
        "Quel jour sommes-nous et quelle heure est-il?",
    ],
    'english': [
        "What is the current date and time?",
        "date and time?",
        "What day is it and what's the time?",
    ],
}

# Bash: date +%Y
# Output: 2023
# English: What is the current year?
# French: Quelle est l'année en cours ?

cmd_data['date +%Y'] = {
    'output': "2023",
    'french_answer': [
        "Nous sommes en 2023.",
        "2023 d'après le calendrier grégorien.",
        "En l'an de grâce 2023 après Jésus-Christ.",
    ],
    'english_answer': [
        "We are in 2023.",
        "2023 according to the Gregorian calendar.",
        "In the year of grace 2023 AD.",
    ],
    'french': [
        "Quelle est l'année en cours ?",
        "année en cours?",
        "Quelle est l'année actuelle?",
        "En quelle année sommes-nous?",
        "Quelle est l'année?",
        "Dans quelle année sommes-nous?",
        "Quelle année vivons-nous?",
        "Quelle année est-ce?",
    ],
    'english': [
        "What is the current year?",
        "current year?",
        "What year is it?",
        "What year are we in?",
        "What year is this?",
    ],
}

# Bash: date "+%A, %B %d, %Y"
# Output: Wednesday, August 03, 2023
# French: 
# English: What is the current date in the format "Day, Month Day, Year"?
# French: Quelle est la date actuelle au format "Jour, Mois Jour, Année"?

cmd_data['date "+%A, %B %d, %Y"'] = {
    'output': "Wednesday, August 03, 2023",
    'french_answer': [
        "Au format demandé, cela donne: mercredi août 3 2023.",
        "Mercredi août 3 2023",
    ],
    'english_answer': [
        "In the requested format it gives: Wednesday August 3 2023.",
        "Wednesday August 3th 2023",
        "Wednesday August the third 2023",
    ],
    'french': [
        "Quelle est la date actuelle au format \"Jour, Mois Jour, Année\"",
        "date au format \"Jour, Mois Jour, Année\"?",
        "Quelle est la date actuelle au format \"Jour, Mois Jour, Année\"?",
    ],
    'english': [
        "What is the current date in the format \"Day, Month Day, Year\"?",
        "date in the format \"Day, Month Day, Year\"?",
        "What is the current date in the format \"Day, Month Day, Year\"",
    ],
}

# Bash: date "+%T"
# Output: 15:30:45
# English: What is the current time in the format "HH:MM:SS" (e.g., 15:30:45)?
# French: Quelle est l'heure actuelle au format "HH:MM:SS" (par exemple, 15:30:45) ?

cmd_data['date "+%T"'] = {
    'output': "15:30:45",
    'french_answer': [
        "Il est 15:30:45.",
        "Il est 15 heures, 30 minutes et 45 secondes.",
        "Actuellement, il est 15:30:45.",
        "Actuellement, il est 15 heures, 30 minutes et 45 secondes.",
        "Il est 15:30:45 en ce moment.",
        "Il est 15 heures, 30 minutes et 45 secondes en ce moment.",
        "Il est 15:30:45 maintenant.",
        "Il est 15 heures 30 minutes, 45 secondes et maintenant.",
        "Il est 15:30:45 à l'heure actuelle.",
        "Il est 15 heures, 30 minutes et 45 secondes actuellement.",
        "Au top il sera 15:30:45.",
        "Au top il sera 15 heures, 30 minutes et 45 secondes.",
    ],
    'english_answer': [
        "It is 15:30:45.",
        "It is 15 hours, 30 minutes and 45 seconds.",
        "Currently, it is 15:30:45.",
        "Currently, it is 15 hours, 30 minutes and 45 seconds.",
        "It is 15:30:45 right now.",
        "It is 15 hours, 30 minutes and 45 seconds right now.",
        "It is 15:30:45 now.",
        "It is 15 hours, 30 minutes and 45 seconds and now.",
        "It is 15:30:45 at the moment.",
        "It is 15 hours, 30 minutes and 45 seconds currently.",
        "At the top it will be 15:30:45.",
        "At the top it will be 15 hours, 30 minutes and 45 seconds.",
    ],
    'french': [
        "Quelle est l'heure actuelle au format \"HH:MM:SS\" (par exemple, 15:30:45) ?",
        "heure au format \"HH:MM:SS\"?",
        "Quelle est l'heure actuelle au format \"HH:MM:SS\"?",
    ],
    'english': [
        "What is the current time in the format \"HH:MM:SS\" (e.g., 15:30:45)?",
        "time in the format \"HH:MM:SS\"?",
        "What is the current time in the format \"HH:MM:SS\"?",
    ],
}

# Bash: date -d "next Friday"
# Output: Fri Aug 05 00:00:00 CEST 2023
# English: What date will it be on the next Friday?
# French: Quelle sera la date du prochain vendredi ?

cmd_data['date -d "next Friday"'] = {
    'output': "Fri Aug 05 00:00:00 CEST 2023",
    'french_answer': [
        "La date du prochain vendredi sera le 05 août 2023",
        "Le prochain vendredi sera le 05 août 2023.",
        "Vendredi prochain sera le 05 août 2023.",
        "Vendredi prochain nous serons le 05 août 2023.",
        "Le prochain vendredi tombera le 05 août 2023.",
    ],
    'french': [
        "Quelle sera la date du prochain vendredi ?",
        "date de vendredi prochain?",
        "Quel jour serons-nous le prochain vendredi?",
        "Quelle sera la date du vendredi prochain?",
        "Vendredi prochain nous serons...",
    ],
    'english': [
        "What date will it be on the next Friday?",
        "date of next Friday?",
        "What day will it be on the next Friday?",
        "What will be the date of the next Friday?",
        "Next Friday we will be...",
    ],
}

# Bash: date -d "last Monday"
# Output: Mon Aug 01 00:00:00 CEST 2023
# English: What date was it on the last Monday?
# French: Quelle était la date du dernier lundi ?

cmd_data['date -d "last Monday"'] = {
    'output': "Mon Aug 01 00:00:00 CEST 2023",
    'french_answer': [
        "La date du dernier lundi était le premier août 2023.",
        "Le dernier lundi était le premier jour du mois d'août 2023.",
        "Lundi dernier on était le premier août.",
        "Lundi dernier nous étions le premier août 2023.",
        "Lundi dernier c'était le premier août 2023.",
    ],
    'english_answer': [
        "The date of the last Monday was August first, 2023.",
        "The last Monday was August first, 2023.",
        "Last Monday was August first, 2023.",
        "Last Monday we were August first, 2023.",
        "The last Monday was August first, 2023.",
    ],
    'french': [
        "Quelle était la date du dernier lundi ?",
        "date du dernier lundi?",
        "Quel jour était le dernier lundi?",
        "Quelle était la date du dernier lundi?",
        "Lundi dernier nous étions...",
    ],
    'english': [
        "What date was it on the last Monday?",
        "date of the last Monday?",
        "What day was the last Monday?",
        "What was the date of the last Monday?",
        "Last Monday we were...",
    ],
}

# Bash: date -d "2 hours ago" "+%T"
# Output: 13:30:45
# English: What time was it 2 hours ago?
# French: Quelle heure était-il il y a 2 heures ?

cmd_data['date -d "2 hours ago" "+%T"'] = {
    'output': "13:30:45",
    'french_answer': [
        "Il était 13:30 il y a 2 heures.",
        "13 heures 30; il y a 2 heures.",
        "Il était 13 heures 30 il y a 2 heures.",
    ],
    'english_answer': [
        "It was 13:30 2 hours ago.",
        "13 hours 30; 2 hours ago.",
        "It was 13 hours 30 2 hours ago.",
    ],
    'french': [
        "Quelle heure était-il il y a 2 heures ?",
        "heure il y a 2 heures?",
        "il y a 2 heures, quelle heure était-il?",
    ],
    'english': [
        "What time was it 2 hours ago?",
        "time 2 hours ago?",
        "2 hours ago, what time was it?",
    ],
}

# Bash: date -d "tomorrow" "+%A, %B %d, %Y"
# Output: Thursday, August 04, 2023
# English: What will be the date tomorrow in the format "Day, Month Day, Year"?
# French: Quelle sera la date de demain au format "Jour, Mois Jour, Année" ?

cmd_data['date -d "tomorrow" "+%A, %B %d, %Y"'] = {
    'output': "Thursday, August 04, 2023",
    'french_answer': [
        "La date de demain sera le jeudi 04 août 2023.",
        "Demain sera le jeudi 04 août 2023.",
        "Demain nous serons le jeudi 04 août 2023.",
        "Demain tombera le jeudi 04 août 2023.",
    ],
    'english_answer': [
        "The date of tomorrow will be Thursday, August 04, 2023.",
        "Tomorrow will be Thursday, August 04, 2023.",
        "Tomorrow we will be Thursday, August 04, 2023.",
        "Tomorrow will be Thursday, August 04, 2023.",
    ],
    'french': [
        "Quelle sera la date de demain au format \"Jour, Mois Jour, Année\" ?",
        "date de demain au format \"Jour, Mois Jour, Année\"?",
        "demain au format \"Jour, Mois Jour, Année\"",
    ],
    'english': [
        "What will be the date tomorrow in the format \"Day, Month Day, Year\"?",
        "date of tomorrow in the format \"Day, Month Day, Year\"?",
        "tomorrow in the format \"Day, Month Day, Year\"",
    ],
}

# Bash: date -r document.txt
# Output: Mon Oct 2 18:00:00 CDT 2006
# English: What is the last modification time of the docuement text file?
# French: Quelle est l'heure de dernière modification du fichier texte document ?

cmd_data['date -r document.txt'] = {
    'output': "Mon Oct 2 18:00:00 CDT 2006",
    'french_answer': [
        "L'heure de dernière modification du fichier texte document est 18:00:00.",
        "18 heures 00; heure de dernière modification du fichier texte document.",
        "L'heure de dernière modification du fichier texte document est 18 heures 00.",
    ],
    'english_answer': [
        "The last modification time of the docuement text file is 18:00:00.",
        "18 hours 00; last modification time of the docuement text file.",
        "The last modification time of the docuement text file is 18 hours 00.",
    ],
    'french': [
        "Quelle est l'heure de dernière modification du fichier texte document ?",
        "heure de dernière modification du fichier texte document?",
        "dernière modification du fichier texte document",
    ],
    'english': [
        "What is the last modification time of the docuement text file?",
        "last modification time of the docuement text file?",
        "last modification of the docuement text file",
    ],
}

# Bash: date -s "2 OCT 2006 18:00:00"
# Output: Mon Oct 2 18:00:00 CDT 2006
# English: Set the system date and time to October 2, 2006 6:00 PM.
# French: Définir la date et l'heure du système au 2 octobre 2006 à 18h00.

cmd_data['date -s "2 OCT 2006 18:00:00"'] = {
    'output': "Mon Oct 2 18:00:00 CDT 2006",
    'french_answer': [
        "La date et l'heure du système ont été définies au 2 octobre 2006 à 18h00.",
        "Bien, nous sommes donc le 2 octobre 2006 et il est par conséquant 18h00.",
        "J'ai défini la date et l'heure du système au 2 octobre 2006 à 18h00. Cependant, je ne suis pas sûr que cela soit une bonne idée de définir la date et l'heure du système manuellement. Connectez-vous plutôt à Internet et utilisez le service de synchronisation de l'heure pour définir la date et l'heure du système automatiquement en fonction de l'heure atomique et de votre fuseau horaire.",
    ],
    'english_answer': [
        "The system date and time have been set to October 2, 2006 6:00 PM.",
        "Well, so we are October 2, 2006 and it is therefore 6:00 PM.",
        "I have set the system date and time to October 2, 2006 6:00 PM. However, I'm not sure it's a good idea to set the system date and time manually. Rather, connect to the Internet and use the time synchronization service to set the system date and time automatically based on atomic time and your time zone.",
    ],
    'french': [
        "Définir la date et l'heure du système au 2 octobre 2006 à 18h00.",
        "date et heure du système au 2 octobre 2006 à 18h00?",
        "date et heure du système au 2 octobre 2006 à 18h00",
    ],
    'english': [
        "Set the system date and time to October 2, 2006 6:00 PM.",
        "system date and time to October 2, 2006 6:00 PM?",
        "system date and time to October 2, 2006 6:00 PM",
    ],
}

# Bash: date -u
# Output: Mon Oct  2 22:00:00 UTC 2006
# English: What is the current UTC time?
# French: Quelle est l'heure UTC actuelle ?

cmd_data['date -u'] = {
    'output': "Mon Oct  2 22:00:00 UTC 2006",
    'french_answer': [
        "L'heure UTC actuelle est 22:00:00.",
        "22 heures 00; heure UTC actuelle.",
        "L'heure UTC actuelle est 22 heures 00.",
    ],
    'english_answer': [
        "The current UTC time is 22:00:00.",
        "22 hours 00; current UTC time.",
        "The current UTC time is 22 hours 00.",
    ],
    'french': [
        "Quelle est l'heure UTC actuelle ?",
        "heure UTC actuelle?",
        "Quelle est l'heure UTC actuelle",
    ],
    'english': [
        "What is the current UTC time?",
        "current UTC time?",
        "What is the current UTC time",
    ],
}

# Bash: date -u "+%T"
# Output: 22:00:00
# English: What is the current UTC time in the format "HH:MM:SS"?
# French: Quelle est l'heure UTC actuelle au format "HH:MM:SS" ?

cmd_data['date -u "+%T"'] = {
    'output': "22:00:00",
    'french_answer': [
        "L'heure UTC actuelle au format \"HH:MM:SS\" est 22:00:00.",
        "22 heures 00; heure UTC actuelle au format demandé.",
        "L'heure UTC actuelle au format demandé est 22 heures 00.",
    ],
    'english_answer': [
        "The current UTC time in the format \"HH:MM:SS\" is 22:00:00.",
        "22 hours 00; current UTC time in the requested format.",
        "The current UTC time in the requested format is 22 hours 00.",
    ],
    'french': [
        "Quelle est l'heure UTC actuelle au format \"HH:MM:SS\" ?",
        "heure UTC actuelle au format \"HH:MM:SS\"?",
        "Quelle est l'heure UTC actuelle au format \"HH:MM:SS\"",
    ],
    'english': [
        "What is the current UTC time in the format \"HH:MM:SS\"?",
        "current UTC time in the format \"HH:MM:SS\"?",
        "What is the current UTC time in the format \"HH:MM:SS\"",
    ],
}

# Bash: date -u -d "2 hours ago" "+%T"
# Output: 22:00:00
# English: What was the UTC time 2 hours ago in the format "HH:MM:SS"?
# French: Quelle était l'heure UTC il y a 2 heures au format "HH:MM:SS" ?
# 

cmd_data['date -u -d "2 hours ago" "+%T"'] = {
    'output': "22:00:00",
    'french_answer': [
        "L'heure UTC il y a 2 heures au format \"HH:MM:SS\" était 22:00:00.",
        "22 heures 00; heure UTC il y a 2 heures au format demandé.",
        "L'heure UTC il y a 2 heures au format demandé était 22 heures 00.",
    ],
    'english_answer': [
        "The UTC time 2 hours ago in the format \"HH:MM:SS\" was 22:00:00.",
        "22 hours 00; UTC time 2 hours ago in the requested format.",
        "The UTC time 2 hours ago in the requested format was 22 hours 00.",
    ],
    'french': [
        "Quelle était l'heure UTC il y a 2 heures au format \"HH:MM:SS\" ?",
        "heure UTC il y a 2 heures au format \"HH:MM:SS\"?",
        "Quelle était l'heure UTC il y a 2 heures au format \"HH:MM:SS\"",
    ],
    'english': [
        "What was the UTC time 2 hours ago in the format \"HH:MM:SS\"?",
        "UTC time 2 hours ago in the format \"HH:MM:SS\"?",
        "What was the UTC time 2 hours ago in the format \"HH:MM:SS\"",
    ],
}

def generate_time_examples():

    hours = {
        "18:00:29": {
            'english': "At the moment, the time is half-past six.",
            'french': "Il est actuellement six heures pétantes.",
        },
        "19:30:17": {
            'english': "Currently half-past seven.",
            'french': "Sept heures et demie.",
        },
        "06:45:56": {
            'english': "It's currently quarter to seven.",
            'french': "Il est sept heures moins le quart.",
        },
        "12:00:13": {
            'english': "It's currently noon.",
            'french': "Il est actuellement midi.",
        },
        "00:00:06": {
            'english': "It's currently midnight.",
            'french': "Il est minuit.",
        },
        "23:59:32": {
            'english': "One minute to midnight.",
            'french': "Dans une minute, il sera minuit.",
        },
        "13:30:54": {
            'english': "The clock indicates it's half-past one post meridiem.",
            'french': "Une heure trente de l'après-midi.",
        },
        "18:39:18": {
            'english': "The current time reads six-thirty-nine in the evening.",
            'french': "Sept heures moins vingt dans une minute.",
        },
        "09:17:45": {
            'english': "Presently, the time stands at nine-seventeen in the morning.",
            'french': "Neuf heures dix-sept actuellement.",
        },
        "15:23:20": {
            'english': "The hour hand is pointing at 15, and the minute hand is at 23.",
            'french': "Quinze heures vingt-trois dans l'immédiat.",
        },
    }


    french_queries = [
        "Quelle est l'heure actuelle ?",
        "heure actuelle?",
        "Quelle est l'heure actuelle",
        "Quelle heure est-il?",
        "Donne-moi l'heure actuelle",
        "Quelle heure est-il maintenant?",
        "Quelle heure est-il actuellement?",
        "Quelle heure est-il en ce moment?",
        "Quelle heure est-il à l'instant?",
        "Quelle heure est-il à présent?",
    ]
    english_queries = [
        "What is the current time?",
        "current time?",
        "Give time",
        "What time is it?",
        "Give me the current time",
        "What time is it now?",
        "What time is it currently?",
        "What time is it right now?",
        "What time is it at the moment?",
        "What time is it presently?",
    ]

    examples = []
    for hour, french_query, english_query in zip(hours.keys(), french_queries, english_queries):

        english_answer = hours[hour]['english']
        french_answer = hours[hour]['french']

        conversation_en = [
            {'role': 'human', 'message': english_query},
            {'role': 'assistant', 'message': english_answer, 'scratchpad': [
                {'action': "Shell", 'action_input': "date '+%T'", 'observation': hour},
                {'action': "final_answer", 'action_input': english_answer, 'observation': ""},
            ]},
        ]
        conversation_fr = [
            {'role': 'human', 'message': french_query},
            {'role': 'assistant', 'message': french_answer, 'scratchpad': [
                {'action': "Shell", 'action_input': "date '+%T'", 'observation': hour},
                {'action': "final_answer", 'action_input': french_answer, 'observation': ""},
            ]},
        ]
        examples.append({'lang': "en", 'system': "", 'instruction': "", 'conversation': conversation_en})
        examples.append({'lang': "fr", 'system': "", 'instruction': "", 'conversation': conversation_fr})
    return examples

def generate_date_examples() -> list:

    dates_fr = [
        "lun 28 nov 2023 00:00:00",
        "mar 02 mai 2023 00:00:00",
        "mer 08 fév 2023 00:00:00",
        "jeu 20 avr 2023 00:00:00",
        "ven 11 aoû 2023 00:00:00",
        "sam 24 juin 2023 00:00:00",
        "dim 30 juil 2023 00:00:00",
    ]
    dates_en = [
        "Mon Nov 28 2023 00:00:00",
        "Tue Mai 02 2023 00:00:00",
        "Wed Feb 08 2023 00:00:00",
        "Thu Apr 20 2023 00:00:00",
        "Fri Aug 11 2023 00:00:00",
        "Sat Jun 24 2023 00:00:00",
        "Sun Jul 30 2023 00:00:00",
    ]
    french_queries = [
        "Quel jour sommes-nous ?",
        "date actuelle",
        "Quelle est la date actuelle",
        "Quelle date est-il?",
        "Donne-moi la date actuelle",
        "Quelle est la date maintenant?",
        "la date actuellement",
    ]
    english_queries = [
        "What day is it?",
        "current date?",
        "Give date",
        "What date is it?",
        "Give me the current date",
        "What date is it now?",
        "What date is it currently?",
    ]

    french_answers = [
        "Nous sommes le lundi 28 nov 2023.",
        "Mardi, le 2 mai 2023.",
        "Aujourd'hui, c'est mercredi 8 fév 2023.",
        "Votre calendrier indique que nous sommes le jeudi 20 avr 2023.",
        "D'après le calendrier grégorien, nous sommes le vendredi 11 aoû 2023.",
        "Si l'on se fie à la capacité du système de mesurer le cours du temps, nous sommes le samedi 24 juin 2023.",
        "En l'an de grâce 2023, après Jesus-Christ, le trentième jour du mois de juillet, un dimanche, nous sommes.",
    ]
    english_answers = [
        "It's Monday, November the 28th, 2023.",
        "Tuesday, May the 2nd, 2023.",
        "Today is Wednesday, February the 8th, 2023.",
        "The calendar indicates that today is Thursday, April the 20th, 2023.",
        "According to the gregorian calendar, today is Friday, August the 11th, 2023.",
        "If we rely on the calendar, today is Saturday, June the 24th, 2023.",
        "In the year of grace 2023, after Jesus-Christ, the thirtieth day of the month of July, a Sunday, we are.",
    ]

    examples = []

    for date_fr, date_en, french_query, english_query, french_answer, english_answer in zip(dates_fr, dates_en, french_queries, english_queries, french_answers, english_answers):

        conversation_en = [
            {'role': 'human', 'message': english_query},
            {'role': 'assistant', 'message': english_answer, 'scratchpad': [
                {'action': "Shell", 'action_input': "date '+%c'", 'observation': date_en},
                {'action': "final_answer", 'action_input': english_answer, 'observation': ""},
            ]},
        ]
        conversation_fr = [
            {'role': 'human', 'message': french_query},
            {'role': 'assistant', 'message': french_answer, 'scratchpad': [
                {'action': "Shell", 'action_input': "date '+%c'", 'observation': date_fr},
                {'action': "final_answer", 'action_input': french_answer, 'observation': ""},
            ]},
        ]

        examples.append({'lang': "en", 'system': "", 'instruction': "", 'conversation': conversation_en})
        examples.append({'lang': "fr", 'system': "", 'instruction': "", 'conversation': conversation_fr})

    return examples

def get_date_examples(_data=cmd_data):
    result_data = []
    result_data.extend(generate_time_examples())
    result_data.extend(generate_date_examples())

    for cmd, cmd_data in _data.items():
        observation = cmd_data['output']
        # french
        for human_msg in cmd_data['french']:
            fr_answer = cmd_data.get('french_answer')
            if not fr_answer:
                continue
            _answer = random.choice(fr_answer)
            _toadd_data = {
                'lang': "fr",
                'system': "",
                'instruction': "",
                'conversation': [
                    {'role': 'human', 'message': human_msg},
                    {'role': 'assistant', 'message': _answer, 'scratchpad': [
                        {'action': "Shell", 'action_input': cmd, 'observation': observation},
                        {'action': "final_answer", 'action_input': _answer, 'observation': ""},
                    ]}
                ]
            }
            result_data.append(_toadd_data)
        # english
        for human_msg in cmd_data['english']:
            en_answer = cmd_data.get('english_answer')
            if not en_answer:
                continue
            _answer = random.choice(en_answer)
            _toadd_data = {
                'lang': "en",
                'system': "",
                'instruction': "",
                'conversation': [
                    {'role': 'human', 'message': human_msg},
                    {'role': 'assistant', 'message': _answer, 'scratchpad': [
                        {'action': "Shell", 'action_input': cmd, 'observation': observation},
                        {'action': "final_answer", 'action_input': _answer, 'observation': ""},
                    ]}
                ]
            }
            result_data.append(_toadd_data)

    return result_data