import sys
import argparse
from pathlib import Path

from LLM_Trainer.dataset import DataLoader

def parse_arguments():
    parse = argparse.ArgumentParser(description="Training script for LLM")
    parse.add_argument('-v', '--version', action='store_true', help="shows the current version")
    parse.add_argument('-d', '--dataset_name', required=True, help='Path or name of the dataset to use')
    parse.add_argument('-m', '--foundation_model', default="TinyPixel/Llama-2-7B-bf16-sharded", help="Base model to use as foundation for fine-tuning the LLM")

    return parse.parse_args()

def main():
    args = parse_arguments()

    accoustic_model_name, language_model_name = args.accoustic_model, args.language_model

    if args.version:
        from LLM_Trainer import __version__
        from transformers import __version__ as __trans_version__
        print(f"LLM Trainer: {__version__}")
        print(f"Transformer: {__trans_version__}")
        sys.exit(0)

    
    dataset_name = args.dataset_name
    foundation_model = args.foundation_model
    
    # Load dataset
    dataset = DataLoader(dataset_name)
    # Load the model
    
    # Laod the trainer
    # Train the model
    # Save the model
    # Publish the model

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(1)