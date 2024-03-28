from nl2shell.assistant import get_assistant_text_data, get_assistant_messages_data
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

def get_messages_dataset():
    messages_data = {}
    messages_data['messages'] = []
    messages_data['messages'].extend(get_assistant_messages_data())
    
    return messages_data

def print_head_tail(dataset_dict):
    for data in dataset_dict['messages'][:10]:
        print(data)
        print()
        print("_"*42)
        print()
    print("-"*42)
    for data in dataset_dict['messages'][:10]:
        print(data)
        print()
        print("_"*42)
        print()

if __name__ == "__main__":
    
    # dataset_dict = get_text_dataset()
    dataset_dict = get_messages_dataset()

    # print_head_tail(dataset_dict)

    # Create the Hugging Face dataset
    dataset = Dataset.from_dict(dataset_dict)

    # Push to the hub
    # login()
    dataset.push_to_hub("OneOS")



