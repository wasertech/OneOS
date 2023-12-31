# Gestion des conteneurs et des images Docker.
#   Certaines commandes comme `docker run` ont leur propre documentation.
#   Plus d'informations : <https://docs.docker.com/engine/reference/commandline/cli/>.

_docker_data = []

_base_data = {
    'system': "",
    'instruction': "",
}

#   Liste tous les conteneurs Docker (en cours d'exécution ou arrêtés) :

#       docker ps --all

_docker_data.append({
    **_base_data,
    'lang': "fr",
    'conversation': [
        { 'role': "human", 'message': "Liste tous les conteneurs Docker (en cours d'exécution ou arrêtés)." },
        { 'role': "assistant", 'message': "Voici la liste de tous les conteneurs Docker (en cours d'exécution ou arrêtés) :",  'scratchpad': [
                { 'function': 'shell', 'parameters': {'code': "docker ps --all", 'observation': "CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES\n" +
                                                                                        "e7c9e4f5a5b0   ubuntu    \"bash\"    2 days    Up 2 days            ubuntu\n" +
                                                                                        "e7c9e4f5a5b0   ubuntu    \"bash\"    2 days    Up 2 days            ubuntu\n" +
                                                                                        "e7c9e4f5a5b0   ubuntu    \"bash\"    2 days    Up 2 days            ubuntu\n" +
                                                                                        "e7c9e4f5a5b0   ubuntu    \"bash\"    2 days    Up 2 days            ubuntu\n" +
                                                                                        "e7c9e4f5a5b0   ubuntu    \"bash\"    2 days    Up 2 days            ubuntu\n" +
                                                                                        "e7c9e4f5a5b0   ubuntu    \"bash\"    2 days    Up 2 days            ubuntu\n" +
                                                                                        "e7c9e4f5a5b0   ubuntu    \"bash\"    2 days    Up 2 days            ubuntu\n" +
                                                                                        "e7c9e4f5a5b0   ubuntu    \"bash\"    2 days    Up 2 days            ubuntu\n" +
                                                                                        "e7c9e4f5a5b0   ubuntu    \"bash\"    2 days    Up 2 days            ubuntu"} },
                { 'function': 'final_answer', 'parameters': {'answer': "Voici la liste de tous les conteneurs Docker (en cours d'exécution ou arrêtés)."}, 'observation': "" },
            ]
        },
    ]
})


#   Démarre un conteneur à partir d'une image, avec un nom personnalisé :

#       docker run --name custom-freqtrade-container freqtrade/freqtrade:stable

_docker_data.append({
    **_base_data,
    'lang': 'fr',
    'conversation': [
        { 'role': "human", 'message': "Démarre un conteneur custom-frerade-container à partir de l'image freqtrade/freqtrade:stable." },
        { 'role': "assistant", 'message': "Le conteneur custom-frerade-container a été démarré avec succès.",  'scratchpad': [
                { 'function': 'shell', 'parameters': {'code': "docker run -d --name custom-freqtrade-container freqtrade/freqtrade:stable"}, 'observation': "2021-08-02 04:00:00,000 - freqtrade - INFO - Starting FreqTrade 2021.8.0\n"},
                { 'function': 'final_answer', 'parameters': {'answer': "Le conteneur custom-frerade-container a été démarré avec succès."}, 'observation': "" },
            ]
        },
    ]
})
                                                                                                                                                

#   Démarre ou arrête un conteneur existant :

#       docker start|stop nom_conteneur

_docker_data.append({
    **_base_data,
    'lang': 'fr',
    'conversation': [
        { 'role': "human", 'message': "Démarre le conteneur custom-frerade-container." },
        { 'role': "assistant", 'message': "Le conteneur custom-frerade-container a été démarré avec succès.",  'scratchpad': [
                { 'function': 'shell', 'parameters': {'code': "docker start custom-freqtrade-container"}, 'observation': "2021-08-02 04:00:00,000 - freqtrade - INFO - Starting FreqTrade 2021.8.0\n"},
                { 'function': 'final_answer', 'parameters': {'answer': "Le conteneur custom-frerade-container a été démarré avec succès."}, 'observation': "" },
            ]
        },
    ]
})


#   Télécharge une image depuis un registre Docker :

#       docker pull image

_docker_data.append({
    **_base_data,
    'lang': 'fr',
    'conversation': [
        { 'role': "human", 'message': "Télécharge l'image freqtrade/freqtrade:stable depuis le registre Docker." },
        { 'role': "assistant", 'message': "L'image freqtrade/freqtrade:stable a été téléchargée avec succès.",  'scratchpad': [
                { 'function': 'shell', 'parameters': {'code': "docker pull freqtrade/freqtrade:stable"}, 'observation': "stable: Pulling from freqtrade/freqtrade\n"},
                { 'function': 'final_answer', 'parameters': {'answer': "L'image freqtrade/freqtrade:stable a été téléchargée avec succès."}, 'observation': "" },
            ]
        },
    ]
})

#   Affiche les images déjà téléchargées :

#       docker images

_docker_data.append({
    **_base_data,
    'lang': 'fr',
    'conversation': [
        { 'role': "human", 'message': "Affiche les images déjà téléchargées." },
        { 'role': "assistant", 'message': "Voici la liste des images déjà téléchargées.",  'scratchpad': [
                { 'function': 'shell', 'parameters': {'code': "docker images"}, 'observation': "REPOSITORY          TAG       IMAGE ID       CREATED       SIZE\n" +
                                                                                    "freqtrade/freqtrade stable    1234567890ab   2 days ago    1.23GB\n" +
                                                                                    "freqtrade/freqtrade stable    1234567890ab   2 days ago    1.23GB\n" +
                                                                                    "freqtrade/freqtrade stable    1234567890ab   2 days ago    1.23GB\n" +
                                                                                    "freqtrade/freqtrade stable    1234567890ab   2 days ago    1.23GB\n" +
                                                                                    "freqtrade/freqtrade stable    1234567890ab   2 days ago    1.23GB\n" +
                                                                                    "freqtrade/freqtrade stable    1234567890ab   2 days ago    1.23GB\n" +
                                                                                    "freqtrade/freqtrade stable    1234567890ab   2 days ago    1.23GB\n" +
                                                                                    "freqtrade/freqtrade stable    1234567890ab   2 days ago    1.23GB\n" +
                                                                                    "freqtrade/freqtrade stable    1234567890ab   2 days ago    1.23GB" },
                { 'function': 'final_answer', 'parameters': {'answer': "Voici la liste des images déjà téléchargées."}, 'observation': "" },
            ]
        },
    ]
})

#   Ouvre un shell dans un conteneur déjà en cours d'exécution :

#       docker exec -it nom_conteneur sh

_docker_data.append({
    **_base_data,
    'lang': 'fr',
    'conversation': [
        { 'role': "human", 'message': "Ouvre un shell dans le conteneur custom-freqtrade-container." },
        { 'role': "assistant", 'message': "Un shell a été ouvert dans le conteneur custom-freqtrade-container.",  'scratchpad': [
                { 'function': 'shell', 'parameters': {'code': "docker exec -it custom-freqtrade-container sh"}, 'observation': "root@e7c9e4f5a5b0:/freqtrade# "},
                { 'function': 'final_answer', 'parameters': {'answer': "Un shell a été ouvert dans le conteneur custom-freqtrade-container."}, 'observation': "" },
            ]
        },
    ]
})

#   Supprime un conteneur arrêté :

#       docker rm nom_conteneur --force

_docker_data.append({
    **_base_data,
    'lang': 'fr',
    'conversation': [
        { 'role': "human", 'message': "Supprime le conteneur custom-freqtrade-container." },
        { 'role': "assistant", 'message': "Le conteneur custom-freqtrade-container a été supprimé avec succès.",  'scratchpad': [
                { 'function': 'shell', 'parameters': {'code': "docker rm custom-freqtrade-container --force"}, 'observation': "custom-freqtrade-container\n"},
                { 'function': 'final_answer', 'parameters': {'answer': "Le conteneur custom-freqtrade-container a été supprimé avec succès."}, 'observation': "" },
            ]
        },
    ]
})

#   Récupère et suit les journaux de message d'un conteneur :

#       docker logs -f nom_conteneur

_docker_data.append({
    **_base_data,
    'lang': 'fr',
    'conversation': [
        { 'role': "human", 'message': "Récupère et suit les journaux de message du conteneur custom-freqtrade-container." },
        { 'role': "assistant", 'message': "Voici les journaux de message du conteneur custom-freqtrade-container :",  'scratchpad': [
                { 'function': 'shell', 'parameters': {'code': "docker logs -f custom-freqtrade-container"}, 'observation': "2021-08-02 04:00:00,000 - freqtrade - INFO - Starting FreqTrade 2021.8.0\n"},
                { 'function': 'final_answer', 'parameters': {'answer': "Voici les journaux de message du conteneur."}, 'observation': "" },
            ]
        },
    ]
})

#   Supprime une image :

#       docker rmi image --force

_docker_data.append({
    **_base_data,
    'lang': 'fr',
    'conversation': [
        { 'role': "human", 'message': "Supprime l'image freqtrade/freqtrade:stable." },
        { 'role': "assistant", 'message': "L'image freqtrade/freqtrade:stable a été supprimée avec succès.",  'scratchpad': [
                { 'function': 'shell', 'parameters': {'code': "docker rmi freqtrade/freqtrade:stable --force"}, 'observation': "Deleted: sha256:1234567890ab\n"},
                { 'function': 'final_answer', 'parameters': {'answer': "L'image freqtrade/freqtrade:stable a été supprimée avec succès."}, 'observation': "" },
            ]
        },
    ]
})


#   Supprime toutes les images non utilisées :

#       docker image prune --force

_docker_data.append({
    **_base_data,
    'lang': 'fr',
    'conversation': [
        { 'role': "human", 'message': "Supprime toutes les images non utilisées." },
        { 'role': "assistant", 'message': "Toutes les images non utilisées ont été supprimées avec succès.",  'scratchpad': [
                { 'function': 'shell', 'parameters': {'code': "docker image prune --force", 'observation': "Deleted Images:\n" +
                                                                                                "deleted: sha256:1234567890ab\n" +
                                                                                                "deleted: sha256:1234567890ab\n" +
                                                                                                "deleted: sha256:1234567890ab\n" +
                                                                                                "deleted: sha256:1234567890ab\n" +
                                                                                                "deleted: sha256:1234567890ab\n" +
                                                                                                "deleted: sha256:1234567890ab\n" +
                                                                                                "deleted: sha256:1234567890ab\n" +
                                                                                                "deleted: sha256:1234567890ab\n" +
                                                                                                "deleted: sha256:1234567890ab\n" +
                                                                                                "Total reclaimed space: 1.23GB\n"}},
                { 'function': 'final_answer', 'parameters': {'answer': "Toutes les images non utilisées ont été supprimées avec succès."}, 'observation': "" },
            ]
        },
    ]
})

#   Supprime tous les conteneurs arrêtés :

#       docker container prune --force

_docker_data.append({
    **_base_data,
    'lang': 'fr',
    'conversation': [
        { 'role': "human", 'message': "Supprime tous les conteneurs arrêtés." },
        { 'role': "assistant", 'message': "Tous les conteneurs arrêtés ont été supprimés avec succès.",  'scratchpad': [
                { 'function': 'shell', 'parameters': {'code': "docker container prune --force", 'observation': "Deleted Containers:\n" +
                                                                                                "e7c9e4f5a5b0\n" +
                                                                                                "e7c9e4f5a5b0\n" +
                                                                                                "e7c9e4f5a5b0\n" +
                                                                                                "e7c9e4f5a5b0\n" +
                                                                                                "e7c9e4f5a5b0\n" +
                                                                                                "e7c9e4f5a5b0\n" +
                                                                                                "e7c9e4f5a5b0\n" +
                                                                                                "e7c9e4f5a5b0\n" +
                                                                                                "Total reclaimed space: 1.23GB\n"}},
                { 'function': 'final_answer', 'parameters': {'answer': "Tous les conteneurs arrêtés ont été supprimés avec succès."}, 'observation': "" },
            ]
        },
    ]
})

#   Supprime tous les conteneurs et toutes les images non utilisées :

#       docker system prune --force

_docker_data.append({
    **_base_data,
    'lang': 'fr',
    'conversation': [
        { 'role': "human", 'message': "Supprime tous les conteneurs et toutes les images non utilisées." },
        { 'role': "assistant", 'message': "Tous les conteneurs et toutes les images non utilisées ont été supprimés avec succès.",  'scratchpad': [
                { 'function': 'shell', 'parameters': {'code': "docker system prune --force"}, 'observation': "Deleted Containers:\n" +
                                                                                                "e7c9e4f5a5b0\n" +
                                                                                                "e7c9e4f5a5b0\n" +
                                                                                                "e7c9e4f5a5b0\n" +
                                                                                                "e7c9e4f5a5b0\n" +
                                                                                                "Deleted Images:\n" +
                                                                                                "deleted: sha256:1234567890ab\n" +
                                                                                                "deleted: sha256:1234567890ab\n" +
                                                                                                "deleted: sha256:1234567890ab\n" +
                                                                                                "deleted: sha256:1234567890ab\n" +
                                                                                                "Total reclaimed space: 1.23GB\n"},
                { 'function': 'final_answer', 'parameters': {'answer': "Tous les conteneurs et toutes les images non utilisées ont été supprimés avec succès."}, 'observation': "" },
            ]
        },
    ]
})

#   Supprime tous les conteneurs, toutes les images et tous les volumes non utilisés, sans confirmation :

#       docker system prune --all --volumes --force

_docker_data.append({
    **_base_data,
    'lang': 'fr',
    'conversation': [
        { 'role': "human", 'message': "Supprime tous les conteneurs, toutes les images et tous les volumes non utilisés, sans confirmation." },
        { 'role': "assistant", 'message': "Tous les conteneurs, toutes les images et tous les volumes non utilisés ont été supprimés avec succès.",  'scratchpad': [
                { 'function': 'shell', 'parameters': {'code': "docker system prune --all --volumes --force", 'observation': "Deleted Containers:\n" +
                                                                                                "e7c9e4f5a5b0\n" +
                                                                                                "Deleted Images:\n" +
                                                                                                "deleted: sha256:1234567890ab\n" +
                                                                                                "Total reclaimed space: 1.23GB\n"}},
                { 'function': 'final_answer', 'parameters': {'answer': "Tous les conteneurs, toutes les images et tous les volumes non utilisés ont été supprimés avec succès."}, 'observation': "" },
            ]
        },
    ]
})


def get_docker_examples():
    return _docker_data
