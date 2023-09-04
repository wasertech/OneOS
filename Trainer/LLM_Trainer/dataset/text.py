
from datasets import load_dataset

def create_text_dataset(dataset_name, *args, **kwargs):
    return load_dataset(dataset_name, *args, **kwargs)