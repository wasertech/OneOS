# Gestion des conteneurs et des images Docker.
#   Certaines commandes comme `docker run` ont leur propre documentation.
#   Plus d'informations : <https://docs.docker.com/engine/reference/commandline/cli/>.

_doker_data = []

_base_data = {
    'system': "",
    'instruction': "",
    'image': "",
}

#   Liste tous les conteneurs Docker (en cours d'exécution ou arrêtés) :

#       docker ps --all

#   Démarre un conteneur à partir d'une image, avec un nom personnalisé :

#       docker run --name nom_conteneur image

#   Démarre ou arrête un conteneur existant :

#       docker start|stop nom_conteneur

#   Télécharge une image depuis un registre Docker :

#       docker pull image

#   Affiche les images déjà téléchargées :

#       docker images

#   Ouvre un shell dans un conteneur déjà en cours d'exécution :

#       docker exec -it nom_conteneur sh

#   Supprime un conteneur arrêté :

#       docker rm nom_conteneur --force

#   Récupère et suit les journaux de message d'un conteneur :

#       docker logs -f nom_conteneur

#   Supprime une image :

#       docker rmi image --force

#   Supprime toutes les images non utilisées :

#       docker image prune --force

#   Supprime tous les conteneurs arrêtés :

#       docker container prune --force

#   Supprime tous les conteneurs et toutes les images non utilisées :

#       docker system prune --force

#   Supprime tous les conteneurs, toutes les images et tous les volumes non utilisés, sans confirmation :

#       docker system prune --all --volumes --force


