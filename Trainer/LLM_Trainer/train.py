import sys
import argparse
import torch
from pathlib import Path
from huggingface_hub import login

from LLM_Trainer.dataset import create_dataset
from LLM_Trainer.transformer import create_trainer
from LLM_Trainer.transformer.tokenizer import create_tokenizer
from LLM_Trainer.transformer.model import create_model, create_training_args
from LLM_Trainer.transformer.config import create_bnb_config, create_lora_config

def parse_arguments():
    parse = argparse.ArgumentParser(description="Training script for LLM")
    parse.add_argument('-v', '--version', action='store_true', help="shows the current version")
    parse.add_argument('-d', '--dataset_name', required=True, help='Path or name of the dataset to use')
    parse.add_argument('-m', '--foundation_model', default="TinyPixel/Llama-2-7B-bf16-sharded", help="Base model to use as foundation for fine-tuning the LLM")
    parse.add_argument('-s', '--max_seq_length', default=4096, help="Maximum sequence length to use for training")
    parse.add_argument('-o', '--output_dir', default="outputs", help="Path to save the model")
    parse.add_argument('-n', '--model_name', default="assistant-llama2-7b-qlora-fp16", help="Name of the model to save")
    parse.add_argument('-p', '--push', action='store_true', help="Push the model to the hub")

    return parse.parse_args()

def model_preprocessing(trainer):
    '''
    Pre-process the model by upcasting the layer norms in float 32 for more stable training
    '''
    for name, module in trainer.model.named_modules():
        if "norm" in name:
            module = module.to(torch.float32)

def main():
    args = parse_arguments()

    if args.version:
        from LLM_Trainer import __version__
        from transformers import __version__ as __trans_version__
        print(f"LLM Trainer: {__version__}")
        print(f"Transformer: {__trans_version__}")
        sys.exit(0)

    
    dataset_name = args.dataset_name
    foundation_model = args.foundation_model
    max_seq_length = args.max_seq_length
    output_dir = args.output_dir
    model_name = args.model_name
    is_push = args.push
    
    # Load dataset
    dataset = create_dataset(dataset_name)
    
    # Load the model and tokenizer
    bnb_config = create_bnb_config()
    lora_config = create_lora_config()
    training_args = create_training_args()

    model = create_model(foundation_model, bnb_config=bnb_config)
    tokenizer = create_tokenizer(foundation_model)
    
    # Load the trainer
    trainer = create_trainer(model, tokenizer, dataset, peft_config=lora_config, training_arguments=training_args, max_seq_length=max_seq_length)

    # Preprocess the model
    model_preprocessing(trainer)
    
    # Train the model
    try:
        trainer.train()
    except KeyboardInterrupt:
        print("Training interrupted")
    finally:
        # Save the model
        model_to_save = trainer.model.module if hasattr(trainer.model, 'module') else trainer.model  # Take care of distributed/parallel training
        model_to_save.save_pretrained(output_dir)
        
        # Publish the model on the hub
        if is_push:
            login()
            model_to_save.push_to_hub(model_name)
            print(f"Model {model_name} pushed to the hub")

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(1)
