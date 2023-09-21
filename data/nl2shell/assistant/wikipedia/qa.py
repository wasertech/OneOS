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

_fr_wiki_examples = [
    {
        'query': "Qu'est-ce qu'un transistor ?",
        'search_terms': "transistor",
        'context': """Un transistor est un composant électronique à semi-conducteur qui peut être utilisé pour amplifier ou commuter des signaux électroniques. Il est constitué de trois couches de matériau semi-conducteur et possède trois bornes : émetteur, base et collecteur. Le transistor est l'un des composants fondamentaux de l'électronique moderne.""",
        'response': "Un transistor est un composant électronique à semi-conducteur utilisé pour amplifier ou commuter des signaux électroniques."
    },
    {
        'query': "Comment fonctionne un transistor bipolaire ?",
        'search_terms': "transistor bipolaire fonctionnement",
        'context': """Un transistor bipolaire fonctionne en utilisant deux types de porteurs de charge : les électrons et les trous. Il peut être utilisé en mode amplificateur ou en mode commutation. En mode amplificateur, de petits signaux d'entrée sont amplifiés en signaux de sortie plus importants. En mode commutation, le transistor bipolaire peut agir comme un interrupteur électronique pour ouvrir ou fermer un circuit.""",
        'response': "Un transistor bipolaire fonctionne en utilisant des porteurs de charge pour amplifier des signaux ou pour commuter des circuits."
    },
    {
        'query': "Quels sont les avantages des transistors MOSFET ?",
        'search_terms': "avantages transistor MOSFET",
        'context': """Les transistors MOSFET (Metal-Oxide-Semiconductor Field-Effect Transistor) présentent plusieurs avantages, notamment une faible consommation d'énergie, une haute vitesse de commutation, une faible chaleur générée et une petite taille. Ils sont largement utilisés dans les circuits électroniques modernes, en particulier dans les applications portables et les circuits intégrés.""",
        'response': "Les avantages des transistors MOSFET incluent une faible consommation d'énergie, une haute vitesse de commutation et une petite taille."
    },
    {
        'query': "Qu'est-ce que l'apprentissage profond en intelligence artificielle ?",
        'search_terms': "apprentissage profond IA",
        'context': """L'apprentissage profond est une branche de l'intelligence artificielle qui utilise des réseaux de neurones artificiels pour apprendre à partir de données. Ces réseaux de neurones sont composés de nombreuses couches, d'où le terme 'profond'. Ils sont utilisés pour résoudre des tâches complexes telles que la reconnaissance d'images, la traduction automatique et la conduite autonome.""",
        'response': "L'apprentissage profond est une technique d'intelligence artificielle qui utilise des réseaux de neurones artificiels pour apprendre à partir de données."
    },
    {
        'query': "Quelle est la mission actuelle de la NASA sur Mars ?",
        'search_terms': "mission NASA Mars actuelle",
        'context': """La NASA a actuellement la mission Mars Perseverance Rover, qui a atterri sur Mars en février 2021. Cette mission vise à rechercher des signes de vie passée sur Mars, à collecter des échantillons de roches martiennes et à étudier la planète rouge en détail.""",
        'response': "La mission actuelle de la NASA sur Mars est le Mars Perseverance Rover, qui cherche des signes de vie passée et collecte des échantillons de roches martiennes."
    },
    {
        'query': "Comment fonctionnent les panneaux solaires photovoltaïques ?",
        'search_terms': "panneaux solaires photovoltaïques fonctionnement",
        'context': """Les panneaux solaires photovoltaïques convertissent la lumière du soleil en électricité. Ils sont constitués de cellules solaires en silicium qui absorbent la lumière solaire. Lorsque la lumière frappe les cellules, elle libère des électrons, créant un courant électrique. Ce courant peut être utilisé pour alimenter des maisons et des appareils électriques.""",
        'response': "Les panneaux solaires photovoltaïques convertissent la lumière du soleil en électricité en utilisant des cellules solaires en silicium."
    },
    {
        'query': "Qui était Ludwig van Beethoven et quelles sont ses œuvres célèbres ?",
        'search_terms': "Ludwig van Beethoven œuvres célèbres",
        'context': """Ludwig van Beethoven était un compositeur allemand du 18e siècle. Il est l'un des compositeurs les plus célèbres de la musique classique. Parmi ses œuvres les plus célèbres figurent la 9e Symphonie, la Sonate au clair de lune et la Symphonie n°5.""",
        'response': "Ludwig van Beethoven était un célèbre compositeur allemand connu pour des œuvres telles que la 9e Symphonie et la Sonate au clair de lune."
    },
    {
        'query': "Quelle est la recette traditionnelle de la paella espagnole ?",
        'search_terms': "recette paella espagnole traditionnelle",
        'context': """La paella espagnole est un plat traditionnel de la région de Valence en Espagne. Elle est préparée avec du riz, du safran, des légumes et des fruits de mer ou de la viande. La recette varie en fonction de la région, mais la version traditionnelle inclut souvent du poulet, des lapins et des haricots verts.""",
        'response': "La paella espagnole traditionnelle est préparée avec du riz, du safran, des légumes et des fruits de mer ou de la viande, notamment du poulet et du lapin."
    },
    {
        'query': "Qui était l'artiste italien de la Renaissance connu pour la Joconde ?",
        'search_terms': "artiste Renaissance Joconde",
        'context': """L'artiste italien de la Renaissance connu pour la Joconde est Leonardo da Vinci. La Joconde, également connue sous le nom de Mona Lisa, est l'une de ses œuvres les plus célèbres. Elle est exposée au musée du Louvre à Paris.""",
        'response': "L'artiste italien de la Renaissance connu pour la Joconde est Leonardo da Vinci, et cette œuvre est exposée au musée du Louvre."
    },
    {
        'query': "Qui est le meilleur joueur de football de tous les temps ?",
        'search_terms': "meilleur joueur football de tous les temps",
        'context': """Le débat sur le meilleur joueur de football de tous les temps est subjectif et dépend des préférences personnelles. Certains considèrent Pelé, Diego Maradona, Lionel Messi ou Cristiano Ronaldo comme les meilleurs. Chacun de ces joueurs a marqué l'histoire du football à sa manière.""",
        'response': "Le meilleur joueur de football de tous les temps est un sujet de débat et dépend des opinions personnelles. Certains noms fréquemment mentionnés incluent Pelé, Diego Maradona, Lionel Messi et Cristiano Ronaldo."
    },
    {
        'query': "Qu'est-ce que la théorie de l'attachement en psychologie ?",
        'search_terms': "théorie de l'attachement psychologie",
        'context': """La théorie de l'attachement en psychologie explore les relations émotionnelles entre les individus, en particulier les liens entre les enfants et leurs soignants. Elle a été développée par des chercheurs comme John Bowlby et Mary Ainsworth. Cette théorie examine comment les premières relations influencent le développement émotionnel et social d'un individu tout au long de sa vie.""",
        'response': "La théorie de l'attachement en psychologie se penche sur les relations émotionnelles, en particulier les liens entre les enfants et leurs soignants, et son impact sur le développement émotionnel et social."
    },
]

_en_wiki_examples = [
    {
        'query': "What is the purpose of the Hubble Space Telescope?",
        'search_terms': "Hubble Space Telescope purpose",
        'context': """The Hubble Space Telescope is a space-based observatory that was launched by NASA in 1990. Its main purpose is to capture high-resolution images and observations of celestial objects, stars, galaxies, and nebulae. It has provided valuable data and images that have advanced our understanding of the universe.""",
        'response': "The Hubble Space Telescope's main purpose is to capture high-resolution images and observations of celestial objects to advance our understanding of the universe."
    },
    {
        'query': "Who was the first President of the United States?",
        'search_terms': "first President of the United States",
        'context': """The first President of the United States was George Washington. He served as the country's first president from April 30, 1789, to March 4, 1797. George Washington is often referred to as the 'Father of His Country' due to his crucial role in the founding of the nation.""",
        'response': "The first President of the United States was George Washington, who served from 1789 to 1797."
    },
    {
        'query': "What is blockchain technology used for?",
        'search_terms': "blockchain technology uses",
        'context': """Blockchain technology is used for various purposes, with its most famous application being in cryptocurrencies like Bitcoin. It is also utilized in industries such as finance, supply chain management, and healthcare for secure and transparent record-keeping. Blockchain ensures the integrity and immutability of data through decentralized ledger technology.""",
        'response': "Blockchain technology is used for secure and transparent record-keeping, primarily in cryptocurrencies like Bitcoin, and across various industries for data integrity."
    },
    {
        'query': "What are the fundamental particles of an atom?",
        'search_terms': "fundamental particles of an atom",
        'context': """The fundamental particles of an atom are protons, neutrons, and electrons. Protons and neutrons are located in the nucleus at the center of the atom, while electrons orbit the nucleus in specific energy levels or electron shells. These particles are essential to understanding the structure of matter.""",
        'response': "The fundamental particles of an atom are protons, neutrons, and electrons."
    },
    {
        'query': "Who wrote the novel 'Pride and Prejudice'?",
        'search_terms': "author of Pride and Prejudice",
        'context': """'Pride and Prejudice' was written by the English novelist Jane Austen. It was first published in 1813 and has since become one of the most famous works of English literature, known for its exploration of societal norms and romantic relationships.""",
        'response': "'Pride and Prejudice' was written by the English novelist Jane Austen and was published in 1813."
    },
    {
        'query': "What is the importance of biodiversity in ecosystems?",
        'search_terms': "importance of biodiversity in ecosystems",
        'context': """Biodiversity, or the variety of life forms within an ecosystem, is crucial for the health and stability of ecosystems. It provides resilience against environmental changes, enhances ecosystem productivity, and supports various ecological processes such as nutrient cycling and pollination. Biodiversity also has intrinsic value and is important for scientific research and human well-being.""",
        'response': "Biodiversity is important for ecosystem stability, resilience, productivity, and supports ecological processes, as well as scientific research and human well-being."
    },
    {
        'query': "What are the emerging trends in artificial intelligence?",
        'search_terms': "emerging trends in artificial intelligence",
        'context': """Emerging trends in artificial intelligence (AI) include machine learning automation, natural language processing advancements, AI ethics and transparency, edge AI for IoT devices, and AI in healthcare. These trends are shaping the future of AI applications and their impact on various industries.""",
        'response': "Emerging trends in artificial intelligence include machine learning automation, natural language processing advancements, AI ethics, edge AI for IoT, and AI in healthcare."
    },
    {
        'query': "What are the top tourist attractions in Paris?",
        'search_terms': "top tourist attractions in Paris",
        'context': """Paris, the capital of France, boasts many famous tourist attractions. Some of the top ones include the Eiffel Tower, the Louvre Museum, Notre-Dame Cathedral, Montmartre and the Sacré-Cœur Basilica, and the Champs-Élysées. These landmarks attract millions of visitors from around the world each year.""",
        'response': "Some of the top tourist attractions in Paris include the Eiffel Tower, the Louvre Museum, Notre-Dame Cathedral, Montmartre, and the Champs-Élysées."
    },
    {
        'query': "What are the benefits of regular exercise?",
        'search_terms': "benefits of regular exercise",
        'context': """Regular exercise offers numerous health benefits, including improved cardiovascular health, increased muscle strength, weight management, stress reduction, and enhanced mood. It also reduces the risk of chronic diseases like heart disease, diabetes, and certain cancers.""",
        'response': "Regular exercise provides benefits such as improved cardiovascular health, increased muscle strength, stress reduction, and a reduced risk of chronic diseases."
    },
    {
        'query': "What are some recent innovations in renewable energy?",
        'search_terms': "recent innovations in renewable energy",
        'context': """Recent innovations in renewable energy include advanced solar panel technologies, offshore wind farms, energy storage solutions, and grid integration. These innovations are helping to make renewable energy sources more efficient and accessible, contributing to a sustainable future.""",
        'response': "Recent innovations in renewable energy encompass advanced solar panels, offshore wind farms, energy storage, and grid integration for greater sustainability."
    },
    {
        'query': "What were the major events of the Cold War?",
        'search_terms': "major events of the Cold War",
        'context': """The Cold War was a period of geopolitical tension between the United States and the Soviet Union (and their respective allies) from the late 1940s to the early 1990s. Major events included the Berlin Blockade, the Cuban Missile Crisis, the Korean War, and the fall of the Berlin Wall. It had a significant impact on global politics and the world order.""",
        'response': "Major events of the Cold War included the Berlin Blockade, Cuban Missile Crisis, Korean War, and the fall of the Berlin Wall, impacting global politics."
    },
    {
        'query': "What are some classic science fiction novels?",
        'search_terms': "classic science fiction novels",
        'context': """Classic science fiction novels include '1984' by George Orwell, 'Brave New World' by Aldous Huxley, 'Dune' by Frank Herbert, and 'Foundation' by Isaac Asimov. These novels have had a lasting influence on the genre and explore futuristic and thought-provoking themes.""",
        'response': "Classic science fiction novels include '1984,' 'Brave New World,' 'Dune,' and 'Foundation,' known for their enduring impact on the genre."
    },
]

wiki_examples = []

for example in _fr_wiki_examples:
    query = example.get('query', "")
    search_terms = example.get('search_terms', "")
    context = example.get('context', "")
    response = example.get('response', "")
    if query and search_terms and context and response:
        wiki_examples.append({
            'lang': 'fr',
            'system': system_prompt.get('fr', ""),
            'instruction': intruction_prompt.get('fr', ""),
            'conversation': [
                { 'role': "human", 'message': query },
                { 'role': "assistant", 'message': response, 'scratchpad': [
                        { 'action': "Search", 'action_input': search_terms, 'observation': context },
                        { 'action': 'final_answer', 'action_input': response, 'observation': "" },
                    ]
                },
            ]
        })

for example in _en_wiki_examples:
    query = example.get('query', "")
    search_terms = example.get('search_terms', "")
    context = example.get('context', "")
    response = example.get('response', "")
    if query and search_terms and context and response:
        wiki_examples.append({
            'lang': "en",
            'system': system_prompt.get('en', ""),
            'instruction': intruction_prompt.get('en', ""),
            'conversation': [
                { 'role': "human", 'message': query },
                { 'role': "assistant", 'message': response, 'scratchpad': [
                        { 'action': "Search", 'action_input': search_terms, 'observation': context },
                        { 'action': 'final_answer', 'action_input': response, 'observation': "" },
                    ]
                },
            ]
        })

def get_wiki_examples():
    return wiki_examples