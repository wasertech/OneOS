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

_fr_search_examples = [
    {
        'query': "Qu'est-ce que le traitement du langage naturel (NLP) ?",
        'search_terms': "Traitement du langage naturel définition",
        'context': """Le traitement du langage naturel (NLP) est un domaine de l'intelligence artificielle qui se concentre sur l'interaction entre les ordinateurs et le langage humain.
Il vise à permettre aux machines de comprendre, d'analyser et de générer un langage humain de manière naturelle.
Le NLP est utilisé dans de nombreuses applications, telles que la traduction automatique, l'analyse des sentiments, la génération de texte et les chatbots.""",
        'response': "Le traitement du langage naturel (NLP) est un domaine de l'intelligence artificielle qui vise à permettre aux machines de comprendre et de générer un langage humain de manière naturelle."
    },
    {
        'query': "Comment fonctionne la reconnaissance vocale ?",
        'search_terms': "Fonctionnement de la reconnaissance vocale",
        'context': """La reconnaissance vocale est une technologie qui permet à un ordinateur de convertir la parole humaine en texte.
Elle repose sur des modèles de langage et des réseaux neuronaux profonds qui analysent les caractéristiques vocales et les transforment en mots écrits.
Les systèmes de reconnaissance vocale sont utilisés dans les assistants virtuels, les systèmes de transcription, et bien d'autres applications.""",
        'response': "La reconnaissance vocale fonctionne en utilisant des modèles de langage et des réseaux neuronaux pour convertir la parole en texte écrit."
    },
    {
        'query': "Quels sont les principaux domaines de l'apprentissage automatique ?",
        'search_terms': "Domaines de l'apprentissage automatique",
        'context': """L'apprentissage automatique (Machine Learning) est un domaine de l'intelligence artificielle qui se décline en plusieurs sous-domaines spécialisés.
Certains des principaux domaines de l'apprentissage automatique comprennent l'apprentissage supervisé, l'apprentissage non supervisé, l'apprentissage par renforcement, et l'apprentissage profond (Deep Learning).
Chacun de ces domaines a ses propres techniques et applications spécifiques.""",
        'response': "Les principaux domaines de l'apprentissage automatique incluent l'apprentissage supervisé, l'apprentissage non supervisé, l'apprentissage par renforcement, et l'apprentissage profond (Deep Learning). Chacun a ses propres applications spécifiques."
    },
    {
        'query': "Qu'est-ce que la synthèse vocale ?",
        'search_terms': "Synthèse vocale définition",
        'context': """La synthèse vocale est une technologie qui permet à un ordinateur de générer une voix humaine artificielle à partir de texte écrit.
Elle utilise des modèles linguistiques et des paramètres vocaux pour produire un discours fluide et naturel.
La synthèse vocale est utilisée dans les systèmes de navigation, les assistants vocaux et d'autres applications pour fournir des informations parlées aux utilisateurs.""",
        'response': "La synthèse vocale est une technologie qui permet à un ordinateur de générer une voix humaine artificielle à partir de texte écrit."
    },
    {
        'query': "Comment fonctionne un agent conversationnel intelligent ?",
        'search_terms': "Fonctionnement des chatbots",
        'context': """Un agent conversationnel intelligent, également appelé chatbot, fonctionne en utilisant des algorithmes d'intelligence artificielle pour interpréter les messages entrants et générer des réponses appropriées.
Il peut s'appuyer sur des modèles de langage pré-entraînés, des bases de connaissances et des règles définies pour comprendre le contexte et formuler des réponses pertinentes.
Les chatbots sont utilisés dans le service client, la réponse aux questions fréquentes et d'autres interactions automatisées.""",
        'response': "Un agent conversationnel intelligent fonctionne en utilisant des algorithmes d'intelligence artificielle pour comprendre les messages et générer des réponses appropriées."
    },
    {
        'query': "Quels sont les avantages de l'interaction humain-machine ?",
        'search_terms': "Avantages de l'interaction humain-machine",
        'context': """L'interaction humain-machine (IHM) présente de nombreux avantages, notamment l'amélioration de l'efficacité, la réduction des erreurs humaines, et l'accès à des informations en temps réel.
Elle permet également une meilleure accessibilité pour les personnes handicapées et facilite la communication dans divers domaines, tels que la santé, l'éducation et l'industrie.""",
        'response': "Les avantages de l'interaction humain-machine comprennent l'amélioration de l'efficacité, la réduction des erreurs humaines, et l'accès à des informations en temps réel, entre autres."
    },
    {
        'query': "Qu'est-ce que la modélisation mathématique ?",
        'search_terms': "Modélisation mathématique définition",
        'context': """La modélisation mathématique est un processus qui consiste à représenter un phénomène du monde réel à l'aide d'équations mathématiques.
Elle permet de comprendre, de prédire et de simuler le comportement de systèmes complexes, qu'ils soient naturels ou artificiels.
La modélisation mathématique est largement utilisée dans les sciences, l'ingénierie, l'économie et d'autres domaines pour résoudre des problèmes complexes.""",
        'response': "La modélisation mathématique consiste à représenter un phénomène du monde réel à l'aide d'équations mathématiques pour en comprendre le comportement."
    },
    {
        'query': "Quelles sont les applications de l'innovation technologique ?",
        'search_terms': "Applications de l'innovation technologique",
        'context': """L'innovation technologique trouve des applications dans de nombreux domaines, y compris la santé, les transports, les communications, l'énergie et l'industrie.
Elle permet de développer de nouveaux produits, de créer des processus plus efficaces et de résoudre des problèmes complexes.
Les innovations technologiques peuvent améliorer la qualité de vie, stimuler la croissance économique et favoriser le progrès global.""",
        'response': "L'innovation technologique trouve des applications dans divers domaines, améliorant la vie quotidienne et stimulant la croissance économique."
    },
    {
        'query': "Comment fonctionne la communication multimodale ?",
        'search_terms': "Fonctionnement de la communication multimodale",
        'context': """La communication multimodale implique l'utilisation de plusieurs modes de communication, tels que la parole, les gestes, les expressions faciales et les médias visuels.
    Elle permet une communication plus riche et expressive en combinant ces différents canaux.
    La communication multimodale est utilisée dans la publicité, l'enseignement en ligne et d'autres contextes où la compréhension claire est essentielle.""",
        'response': "La communication multimodale combine différents modes de communication, tels que la parole, les gestes et les médias visuels, pour une communication plus riche."
    },
    {
        'query': "Comment cuisiner un risotto au champignon ?",
        'search_terms': "Recette risotto champignon",
        'context': """Pour cuisiner un risotto au champignon, vous aurez besoin d'ingrédients tels que du riz arborio, des champignons, du bouillon de légumes, de l'oignon, du vin blanc, du beurre, du parmesan, et des herbes.
Il faut d'abord faire revenir les champignons et l'oignon dans du beurre, puis ajouter le riz et le vin blanc.
Ensuite, ajoutez progressivement le bouillon tout en remuant jusqu'à ce que le riz soit crémeux et cuit.
Terminez en ajoutant du parmesan râpé et des herbes fraîches.""",
        'response': "Pour cuisiner un risotto au champignon, suivez ces étapes : faites revenir les champignons et l'oignon, ajoutez le riz et le vin blanc, puis le bouillon jusqu'à ce que le riz soit crémeux, et terminez avec du parmesan et des herbes."
    },
    {
        'query': "Quels sont les symptômes du rhume des foins ?",
        'search_terms': "Symptômes rhume des foins",
        'context': """Le rhume des foins, également connu sous le nom de rhinite allergique saisonnière, est une réaction allergique aux pollens.
Ses symptômes courants comprennent l'écoulement nasal, les éternuements, les démangeaisons au niveau du nez et des yeux, et la congestion nasale.
Dans les cas graves, il peut également provoquer de la toux, de la fatigue, et des maux de tête.""",
        'response': "Les symptômes du rhume des foins incluent l'écoulement nasal, les éternuements, les démangeaisons au nez et aux yeux, et la congestion nasale, ainsi que d'autres symptômes dans les cas graves."
    },
    {
        'query': "Quels sont les meilleurs conseils pour économiser de l'argent ?",
        'search_terms': "Conseils pour économiser de l'argent",
        'context': """Il existe de nombreux conseils pour économiser de l'argent, notamment :
    1. Établir un budget.
    2. Réduire les dépenses superflues.
    3. Économiser régulièrement.
    4. Investir judicieusement.
    5. Comparer les prix avant d'acheter.
    6. Rembourser les dettes rapidement.
    7. Éviter les achats impulsifs.
    8. Utiliser des coupons et des remises.
    9. Planifier les repas à l'avance.
    10. Économiser sur les frais de transport.""",
        'response': "Pour économiser de l'argent, suivez ces conseils : établissez un budget, réduisez les dépenses inutiles, économisez régulièrement, investissez judicieusement, et ainsi de suite."
    },
    {
        'query': "Comment prendre soin d'une plante d'intérieur ?",
        'search_terms': "Conseils entretien plante d'intérieur",
        'context': """Pour prendre soin d'une plante d'intérieur, il est essentiel de :
    1. Arroser régulièrement, mais ne pas trop.
    2. Fournir suffisamment de lumière.
    3. Éviter les températures extrêmes.
    4. Fertiliser périodiquement.
    5. Vérifier les signes de maladie ou de parasites.
    6. Rempoter si nécessaire.
    7. Nettoyer les feuilles.
    8. Prévenir l'accumulation de poussière.""",
        'response': "Pour prendre soin d'une plante d'intérieur, suivez ces conseils : arrosez régulièrement, assurez-vous de la lumière, évitez les températures extrêmes, et ainsi de suite."
    },
    {
        'query': "Quelle est l'histoire de la Tour Eiffel ?",
        'search_terms': "Histoire de la Tour Eiffel",
        'context': """La Tour Eiffel, construite en 1889 à Paris, France, pour l'Exposition universelle, est l'une des structures emblématiques du monde.
Conçue par l'ingénieur Gustave Eiffel, elle était à l'origine controversée mais est devenue un symbole de la France.
        La tour mesure 324 mètres de hauteur et était la plus haute structure du monde à l'époque de sa construction.""",
        'response': "La Tour Eiffel a été construite en 1889 pour l'Exposition universelle de Paris par l'ingénieur Gustave Eiffel et mesure 324 mètres de hauteur."
    },
    {
        'query': "Quelles sont les principales attractions touristiques de Tokyo ?",
        'search_terms': "Attractions touristiques Tokyo",
        'context': """Tokyo, la capitale du Japon, regorge d'attractions touristiques, notamment :
    1. Le temple Senso-ji à Asakusa.
    2. La tour de Tokyo avec une vue panoramique.
    3. Le quartier animé de Shibuya.
    4. Le parc Ueno avec son zoo et ses musées.
    5. Le quartier de Shinjuku avec ses gratte-ciels.
    6. Le sanctuaire Meiji-jingu à Harajuku.
    7. Le palais impérial et ses jardins.
    8. Le quartier de Ginza pour le shopping de luxe.
    9. Le parc d'attractions Tokyo Disneyland.
    10. Le marché aux poissons de Tsukiji.""",
        'response': "Les principales attractions touristiques de Tokyo incluent le temple Senso-ji, la tour de Tokyo, Shibuya, et bien d'autres lieux fascinants."
    },
    {
        'query': "Comment choisir le bon vélo de montagne ?",
        'search_terms': "Conseils choix vélo de montagne",
        'context': """Le choix d'un vélo de montagne dépend de plusieurs facteurs, notamment :
    1. Le type de terrain sur lequel vous allez rouler (sentiers, montagnes, etc.).
    2. Votre niveau d'expérience en cyclisme.
    3. Votre budget.
    4. La taille du cadre du vélo.
    5. Le type de suspension (rigide, à suspension avant ou intégrale).
    6. Les composants (freins, dérailleurs, pneus, etc.).
Il est recommandé de consulter un expert en magasin pour des conseils personnalisés.""",
        'response': "Pour choisir le bon vélo de montagne, tenez compte du terrain, de votre expérience, de votre budget, de la taille du cadre, de la suspension et des composants."
    },
    {
        'query': "Quelles sont les étapes pour rédiger un CV efficace ?",
        'search_terms': "Conseils rédaction CV",
        'context': """La rédaction d'un CV efficace implique les étapes suivantes :
    1. Inclure les informations de contact et un titre professionnel.
    2. Résumer vos compétences et expériences clés.
    3. Énumérer votre expérience de travail de manière chronologique.
    4. Mettre en avant vos réalisations spécifiques.
    5. Inclure des compétences pertinentes.
    6. Mentionner votre formation académique.
    7. Personnaliser le CV en fonction de l'emploi visé.
    8. Relire et corriger les erreurs grammaticales.""",
        'response': "Pour rédiger un CV efficace, suivez ces étapes : incluez les informations de contact, résumez vos compétences, énumérez l'expérience de travail, et ainsi de suite."
    },
    {
        'query': "Comment fonctionne la cryptomonnaie Bitcoin ?",
        'search_terms': "Fonctionnement Bitcoin",
        'context': """Le Bitcoin est une cryptomonnaie basée sur la technologie blockchain.
Son fonctionnement repose sur des transactions décentralisées enregistrées dans un grand livre public.
Les mineurs résolvent des problèmes mathématiques pour valider les transactions et ajouter des blocs à la chaîne.
Le Bitcoin peut être utilisé pour des transactions en ligne, mais sa valeur est volatile sur les marchés financiers.""",
        'response': "Le Bitcoin fonctionne grâce à la technologie blockchain, avec des transactions décentralisées validées par des mineurs, mais sa valeur peut être volatile."
    }
]

_en_search_examples = [
    {
        'query': "How to make homemade pizza?",
        'search_terms': "Homemade pizza recipe",
        'context': """Making homemade pizza is a fun and delicious activity. Here are the basic steps:
    1. Prepare pizza dough or buy pre-made dough.
    2. Roll out the dough into your desired shape and thickness.
    3. Add tomato sauce, cheese, and your favorite toppings.
    4. Bake in a preheated oven until the crust is golden and the cheese is bubbly.
    5. Enjoy your homemade pizza!""",
        'response': "To make homemade pizza, prepare dough, add sauce, cheese, toppings, and bake until golden brown."
    },
    {
        'query': "What are the symptoms of COVID-19?",
        'search_terms': "COVID-19 symptoms",
        'context': """COVID-19, caused by the coronavirus, can have various symptoms, including:
    1. Fever or chills
    2. Cough
    3. Shortness of breath or difficulty breathing
    4. Fatigue
    5. Muscle or body aches
    6. Headache
    7. Sore throat
    8. Loss of taste or smell
    9. Congestion or runny nose
    10. Nausea or vomiting
    11. Diarrhea
It's important to get tested if you experience any of these symptoms.""",
        'response': "COVID-19 symptoms include fever, cough, shortness of breath, fatigue, loss of taste or smell, and more."
    },
    {
        'query': "How to start a successful online business?",
        'search_terms': "Starting a successful online business tips",
        'context': """Starting a successful online business requires careful planning and execution. Here are some tips:
    1. Identify a niche or product that has demand.
    2. Create a business plan and set clear goals.
    3. Build a professional website and online presence.
    4. Develop a marketing strategy, including social media and SEO.
    5. Offer excellent customer service.
    6. Monitor your finances and adjust your strategy as needed.
    7. Stay up-to-date with industry trends.
    8. Be persistent and adaptable.""",
        'response': "To start a successful online business, identify a niche, create a plan, build a website, and focus on marketing and customer service."
    },
    {
        'query': "How to grow tomatoes in a garden?",
        'search_terms': "Growing tomatoes in a garden tips",
        'context': """Growing tomatoes in a garden can be rewarding. Here are some tips:
    1. Choose a sunny spot with well-drained soil.
    2. Plant tomato seedlings or seeds after the last frost.
    3. Water consistently, keeping the soil evenly moist.
    4. Support the plants with stakes or cages as they grow.
    5. Prune the plants to encourage air circulation.
    6. Fertilize with a balanced fertilizer.
    7. Watch for pests and diseases and take action if needed.
    8. Harvest when the tomatoes are ripe and enjoy!""",
        'response': "To grow tomatoes in a garden, choose a sunny spot, plant seedlings, water consistently, support the plants, and watch for pests."
    },
    {
        'query': "What is climate change?",
        'search_terms': "Climate change definition",
        'context': """Climate change refers to long-term shifts in global weather patterns. It is primarily driven by human activities, such as the burning of fossil fuels and deforestation, which release greenhouse gases into the atmosphere.
        These gases trap heat and lead to rising temperatures, altered weather patterns, and various environmental impacts, including more frequent and severe extreme weather events.""",
        'response': "Climate change is the long-term alteration of global weather patterns due to human activities that release greenhouse gases, causing rising temperatures and environmental impacts."
    },
    {
        'query': "How to improve time management skills?",
        'search_terms': "Tips for improving time management",
        'context': """Improving time management skills is essential for productivity. Here are some tips:
    1. Prioritize tasks and set clear goals.
    2. Use time management tools like calendars and to-do lists.
    3. Eliminate distractions during focused work periods.
    4. Break tasks into smaller, manageable steps.
    5. Learn to say no to non-essential commitments.
    6. Delegate tasks when possible.
    7. Take regular breaks to recharge.
    8. Reflect on your time management habits and make adjustments as needed.""",
        'response': "To improve time management skills, prioritize tasks, use tools, eliminate distractions, and take breaks to recharge."
    },
    {
        'query': "How to start a vegetable garden?",
        'search_terms': "Starting a vegetable garden for beginners",
        'context': """Starting a vegetable garden can be a rewarding experience. Here are some beginner's tips:
    1. Choose a sunny location with well-draining soil.
    2. Decide on the vegetables you want to grow.
    3. Prepare the soil by adding compost or organic matter.
    4. Plant your chosen vegetables according to spacing guidelines.
    5. Water consistently and mulch to retain moisture.
    6. Keep an eye out for pests and diseases.
    7. Harvest when the vegetables are ripe and enjoy fresh produce!""",
        'response': "To start a vegetable garden, choose a sunny spot, prepare the soil, plant your chosen vegetables, water consistently, and watch for pests."
    },
    {
        'query': "What is artificial intelligence (AI)?",
        'search_terms': "Artificial intelligence definition",
        'context': """Artificial intelligence (AI) refers to the simulation of human intelligence in machines. It involves programming computers to perform tasks that typically require human intelligence, such as problem-solving, decision-making, and learning.
AI is used in various applications, including natural language processing, computer vision, and robotics.""",
        'response': "Artificial intelligence (AI) simulates human intelligence in machines and is used in tasks like problem-solving and natural language processing."
    },
    {
        'query': "How to write a compelling cover letter?",
        'search_terms': "Tips for writing a compelling cover letter",
        'context': """Writing a compelling cover letter is essential for job applications. Here are some tips:
    1. Address it to the hiring manager if possible.
    2. Customize the letter for the specific job.
    3. Highlight your relevant skills and experiences.
    4. Use clear and concise language.
    5. Explain why you're a good fit for the company.
    6. Proofread for grammar and spelling errors.
    7. Keep it brief and focused on your qualifications.""",
        'response': "To write a compelling cover letter, customize it, highlight skills, use clear language, and explain why you're a good fit for the job."
    },
]

search_examples = []

for example in _fr_search_examples:
    query = example.get('query', "")
    search_terms = example.get('search_terms', "").lower()
    context = example.get('context', "")
    response = example.get('response', "")
    if query and search_terms and context and response:
        search_examples.append({
            'lang': 'fr',
            'system': system_prompt.get('fr', ""),
            'instruction': intruction_prompt.get('fr', ""),
            'conversation': [
                { 'role': "human", 'message': query },
                { 'role': "assistant", 'message': response, 'scratchpad': [
                        { 'function': "search_web", 'parameters': {'terms': search_terms}, 'observation': context },
                        { 'function': 'final_answer', 'parameters': {'answer': response}, 'observation': "" },
                    ]
                },
            ]
        })

for example in _en_search_examples:
    query = example.get('query', "")
    search_terms = example.get('search_terms', "").lower()
    context = example.get('context', "")
    response = example.get('response', "")
    if query and search_terms and context and response:
        search_examples.append({
            'lang': 'en',
            'system': system_prompt.get('en', ""),
            'instruction': intruction_prompt.get('en', ""),
            'conversation': [
                { 'role': "human", 'message': query },
                { 'role': "assistant", 'message': response, 'scratchpad': [
                        { 'function': "search_web", 'parameters': {'terms': search_terms}, 'observation': context },
                        { 'function': 'final_answer', 'parameters': {'answer': response}, 'observation': "" },
                    ]
                },
            ]
        })

def get_web_examples():
    return search_examples
