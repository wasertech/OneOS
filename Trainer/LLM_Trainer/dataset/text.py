
from datasets import load_dataset

class TextDataLoader:

    def __init__(self, dataset_name, *args, **kwargs):
        return load_dataset(dataset_name, *args, **kwargs)