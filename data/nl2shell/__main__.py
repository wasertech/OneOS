
from nl2shell import LANGS
from nl2shell.assistant import get_assistant_text_data
from datasets import Dataset

if __name__ == "__main__":
    
    text_data = get_assistant_text_data()

    dataset_dict = {"text": text_data}

    # Create the Hugging Face dataset
    dataset = Dataset.from_dict(dataset_dict)

    # Push to the hub
    dataset.push_to_hub("OneOS")


    # for text_data in text_data:
    #     print(text_data)
    #     print()
    #     print()
    #     print()

