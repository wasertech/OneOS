import os, shutil
import questionary
from glob import glob
from pathlib import Path
from huggingface_hub import HfApi, Repository
from datasets import Dataset, DatasetInfo, SplitInfo, load_dataset, concatenate_datasets
from rich.console import Console
from rich.markdown import Markdown


console = Console()

BANNER = Markdown("# Data Manager")
BANNER_HIGHLIGHT = "Welcome to the data manager for LLMs!"
console.print(BANNER)
console.print(BANNER_HIGHLIGHT, justify="center", style="italic")

def featurize(example):
    _input = example["input"]
    _output = example["output"]

    _query = _input.split("Question: ")

    if len(_query) < 3:
        _query = ""
    else:
        _query = _query[2].split("Thought: ")[0].strip()
    question = _query
    if _output.startswith("Thought: "):
        thought = _output.split("Thought: ")[1].split("Final Answer: ")[0].split("Action: ")[0].strip()
    else:
        thought = _output.split("Action: ")[0].split("Final Answer: ")[0].strip()
    if "Final Answer: " in _output:
        final_answer = _output.split("Final Answer: ")[1].split("Thought: ")[0].strip()
    else:
        final_answer = "N/A"
    if "Action: " in _output:
        action = _output.split("Action: ")[1].split("Action Input:")[0].strip()
        _action_input = _output.split("Action Input: ")
        if len(_action_input) > 1:
            action_input = _action_input[1].strip()
        else:
            action_input = "N/A"
    else:
        action = "N/A"
        action_input = "N/A"
    example["human"] = question
    example["machine"] = thought
    example["action"] = action
    example["action_input"] = action_input
    example["final_answer"] = final_answer
    return example

def load_data(data_path):
    # Get all input files
    input_files = glob(os.path.join(data_path, "*-*[!_output].txt"))

    # Initialize the result dictionary
    result = {'human': [], 'input': [], 'output': [], 'machine': [], 'action': [], 'action_input': [], 'final_answer': []}

    # Iterate over the input files
    for input_file in input_files:
        # Get the corresponding output file
        output_file = input_file.replace(".txt", "_output.txt")

        # Check if the output file exists
        if os.path.isfile(output_file):
            # Read the input and output files
            with open(input_file, 'r') as f:
                input_text = f.read().strip()
            with open(output_file, 'r') as f:
                output_text = f.read().strip()

            data = featurize({"input": input_text, "output": output_text})

            # Add the input and output to the result dictionary
            result['input'].append(data['input'])
            result['output'].append(data['output'])
            result['human'].append(data['human'])
            result['machine'].append(data['machine'])
            result['action'].append(data['action'])
            result['action_input'].append(data['action_input'])
            result['final_answer'].append(data['final_answer'])

    return result

def main():
    dataset_path = Path(questionary.path("Where are the text files located?", default="../Console/data/").ask())
    to_hub = questionary.confirm("Do you want to push to/pull from the HuggingFace Hub?").ask()
    if to_hub:
        dataset_repo_name = questionary.text("What is the name repository of the dataset?", default="wasertech/NL2Shell").ask()
        user, repo = dataset_repo_name.split("/")
        console.print("Loading data...", end="")
        data_dict = load_data(Path("../Console/data/"))
        console.print("Done.")
        
        api = HfApi()
        
        _results = api.list_datasets(search=repo, author=user)

        if len(list(_results)) > 0:
            console.print("Repository already exists. Updating existing dataset.")

            nl2shell = load_dataset(dataset_repo_name, use_auth_token=True, cache_dir="./cache", ignore_verifications=True, download_mode="force_redownload")
            _nl2shell = Dataset.from_dict(data_dict)
            nl2shell['train'] = concatenate_datasets([nl2shell['train'], _nl2shell])
            _pd_nl2shell = nl2shell['train'].to_pandas()
            _pd_nl2shell.drop_duplicates(subset=["input", "output"], inplace=True)
            _pd_nl2shell.reset_index(inplace=True)
            nl2shell['train'] = Dataset.from_pandas(_pd_nl2shell).map(lambda x: x, batched=True, remove_columns=["index", "level_0"])
            nl2shell.push_to_hub(dataset_repo_name)
            shutil.rmtree("./cache")
        else:
            console.print("Repository does not exist. Creating a new dataset.")
            # dataset_description = questionary.text("What is the description of the dataset?", default="Natural Language to Shell").ask()
            # dataset_version = questionary.text("What is the version of the dataset?", default="1.0.0").ask()
            # # dataset_author = questionary.text("Who is the author of the dataset?", default="Danny Waser").ask()
            # dataset_licence = questionary.text("What is the licence of the dataset?", default="cc0-1.0").ask()
            # dataset_homepage = questionary.text("What is the homepage of the dataset?", default="https://github.com/wasertech/NL2Shell").ask()
            # dataset_citation = questionary.text("What is the citation of the dataset?", default="").ask()
            # dataset_info = DatasetInfo(
            #     description=dataset_description,
            #     version=dataset_version,
            #     license=dataset_licence,
            #     homepage=dataset_homepage,
            #     citation=dataset_citation,
            #     features={
            #         "input": {"description": "Input given to the model.", "type": "string"},
            #         "output": {"description": "Output of the model.", "type": "string"},
            #     },
            # )
            nl2shell = Dataset.from_dict(data_dict) #, info=dataset_info)      
            nl2shell.push_to_hub(dataset_repo_name)
        console.print("Everything is done. The model has been pushed to HuggingFace Hub!")
    else:
        raise NotImplementedError("Not implemented yet")
        # dataset_path = questionary.text("What is the local path of the dataset?", default="./NL2Shell").ask()
        nl2shell.save_to_disk("dataset/")

if __name__ == "__main__":
    main()