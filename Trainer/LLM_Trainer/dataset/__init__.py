
from LLM_Trainer.dataset.text import create_text_dataset

def create_dataset(dataset_name, *args, **kwargs):
    return create_text_dataset(dataset_name, *args, **kwargs)