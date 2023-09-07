from nl2shell.assistant import get_assistant_text_data
from datasets import Dataset
from huggingface_hub import login

# TODO: Parse aguments
# TODO: Add a flag to push to the hub
# TODO: Add a flag to push to the hub with a specific name
# TODO: Add a flag to save to a local file

def get_text_dataset():
    text_data = {}
    text_data['text'] = []
    text_data['text'].extend(get_assistant_text_data())
    
    return text_data

if __name__ == "__main__":
    
    dataset_dict = get_text_dataset()

    # Create the Hugging Face dataset
    # dataset = Dataset.from_dict(dataset_dict)

    # Push to the hub
    # login()
    # dataset.push_to_hub("OneOS")

    for text_data in dataset_dict['text']:
        print(text_data)
        print()
        print("_"*42)
        print()

