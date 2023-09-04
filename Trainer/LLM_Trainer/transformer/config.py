import torch
from transformers import BitsAndBytesConfig
from peft import LoraConfig


def create_bnb_config(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    ):
    return BitsAndBytesConfig(
        load_in_4bit=load_in_4bit,
        bnb_4bit_quant_type=bnb_4bit_quant_type,
        bnb_4bit_compute_dtype=bnb_4bit_compute_dtype,
    )

def create_lora_config(
        lora_alpha = 16,
        lora_dropout = 0.1,
        lora_r = 64,
        bias="none",
        task_type="CAUSAL_LM",
    ):
    return LoraConfig(
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        r=lora_r,
        bias=bias,
        task_type=task_type,
    )
