
```shell
python -m LLM_Train.train --help
usage: train.py [-h] [-v] -d DATASET_NAME [-m FOUNDATION_MODEL] [-s MAX_SEQ_LENGTH] [-o OUTPUT_DIR] [-n MODEL_NAME] [-p]

Training script for LLM

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         shows the current version
  -d DATASET_NAME, --dataset_name DATASET_NAME
                        Path or name of the dataset to use
  -m FOUNDATION_MODEL, --foundation_model FOUNDATION_MODEL
                        Base model to use as foundation for fine-tuning the LLM
  -s MAX_SEQ_LENGTH, --max_seq_length MAX_SEQ_LENGTH
                        Maximum sequence length to use for training
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        Path to save the model
  -n MODEL_NAME, --model_name MODEL_NAME
                        Name of the model to save
  -p, --push            Push the model to the hub
```