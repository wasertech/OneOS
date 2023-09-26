import os
from time import sleep
from glob import glob
from huggingface_hub import HfApi

repo_user = os.environ.get('REPO_USER', "wasertech")

OUTPUT_MODEL_NAME = os.environ.get('OUTPUT_MODEL_NAME', "assistant-llama2-7b-merge-bf16")

HUB_API_TOKEN = os.environ.get('HUB_API_TOKEN', None)

api = HfApi(token=HUB_API_TOKEN)

def push_file(path_or_fileobj, path_in_repo, repo_id):
    attempt_count = 1
    t = 10
    while True:
        try:
            api.upload_file(
                path_or_fileobj=path_or_fileobj,
                path_in_repo=path_in_repo,
                repo_id=repo_id,
            )
            print(f"Pushed {path_or_fileobj} on {repo_id} after {attempt_count} attempts")
            break
        except (Exception, RuntimeError) as e:
            print("\n"*5)
            print(e)
            print(f"Waiting {t} seconds...")
            sleep(t)
            attempt_count += 1
            print("Trying again...")

found_artefacts = glob(f"{OUTPUT_MODEL_NAME}/*")

print("Found Artefacts:\n" + "\n".join(found_artefacts) + "\n")

t = 10
for artefact in found_artefacts:
    path_or_fileobj = artefact
    path_in_repo = f"{artefact.split('/')[-1]}"
    repo_id = f"{repo_user}/{OUTPUT_MODEL_NAME}"
    print(f"Pushing {artefact} on {repo_id}...")
    push_file(path_or_fileobj, path_in_repo, repo_id)
    print(f"{artefact}: Pushed on {repo_id}")
    print("Waiting {t} seconds to publish next file...")
    sleep(10)

# upload_folder(
#     folder_path="local/checkpoints",
#     repo_id="username/my-dataset",
#     repo_type="dataset",
#     multi_commits=True,
#     multi_commits_verbose=True,
# )