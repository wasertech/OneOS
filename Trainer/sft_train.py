'''
Supervised Fine Tuning Training Script
'''
# coding=utf-8
# Copyright 2023 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from dataclasses import dataclass, field
from typing import Optional

import torch
from datasets import load_dataset
from peft import LoraConfig
from tqdm import tqdm
from transformers import AutoModelForCausalLM, BitsAndBytesConfig, HfArgumentParser, TrainingArguments, TrainerCallback
from huggingface_hub import login

from trl import SFTTrainer

from eval_prompt import get_prompt

tqdm.pandas()

# Define default parameters
DEFAULT_MODEL_NAME = "cognitivecomputations/dolphin-2.2.1-mistral-7b"
DEFAULT_DATASET_NAME = "wasertech/OneOS"
DEFAULT_DATASET_TEXT_FIELD = "text"
DEFAULT_LOG_WITH = None
DEFAULT_LEARNING_RATE = 1.41e-5
DEFAULT_BATCH_SIZE = 64
DEFAULT_SEQ_LENGTH = 512
DEFAULT_GRADIENT_ACCUMULATION_STEPS = 16
DEFAULT_LOAD_IN_8BIT = False
DEFAULT_LOAD_IN_4BIT = False
DEFAULT_USE_PEFT = False
DEFAULT_TRUST_REMOTE_CODE = True
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_PEFT_LORA_R = 64
DEFAULT_PEFT_LORA_ALPHA = 16
DEFAULT_LOGGING_STEPS = 1
DEFAULT_USE_AUTH_TOKEN = True
DEFAULT_NUM_TRAIN_EPOCHS = 1
DEFAULT_MAX_STEPS = -1
DEFAULT_SAVE_STEPS = 100
DEFAULT_SAVE_TOTAL_LIMIT = 3
DEFAULT_PUSH_TO_HUB = False
DEFAULT_HUB_MODEL_ID = None
DEFAULT_NEFT_ALPHA = 5.0

# Define and parse arguments.
@dataclass
class ScriptArguments:
    """
    The name of the Casual LM model we wish to fine-tune with SFTTrainer
    """

    model_name: Optional[str] = field(default=DEFAULT_MODEL_NAME, metadata={"help": "the model name"})
    dataset_name: Optional[str] = field(
        default=DEFAULT_DATASET_NAME, metadata={"help": "the dataset name"}
    )
    dataset_text_field: Optional[str] = field(default=DEFAULT_DATASET_TEXT_FIELD, metadata={"help": "the text field of the dataset"})
    log_with: Optional[str] = field(default=DEFAULT_LOG_WITH, metadata={"help": "use 'wandb' to log with wandb"})
    learning_rate: Optional[float] = field(default=DEFAULT_LEARNING_RATE, metadata={"help": "the learning rate"})
    batch_size: Optional[int] = field(default=DEFAULT_BATCH_SIZE, metadata={"help": "the batch size"})
    seq_length: Optional[int] = field(default=DEFAULT_SEQ_LENGTH, metadata={"help": "Input sequence length"})
    gradient_accumulation_steps: Optional[int] = field(
        default=DEFAULT_GRADIENT_ACCUMULATION_STEPS, metadata={"help": "the number of gradient accumulation steps"}
    )
    load_in_8bit: Optional[bool] = field(default=DEFAULT_LOAD_IN_8BIT, metadata={"help": "load the model in 8 bits precision"})
    load_in_4bit: Optional[bool] = field(default=DEFAULT_LOAD_IN_4BIT, metadata={"help": "load the model in 4 bits precision"})
    use_peft: Optional[bool] = field(default=DEFAULT_USE_PEFT, metadata={"help": "Wether to use PEFT or not to train adapters"})
    trust_remote_code: Optional[bool] = field(default=DEFAULT_TRUST_REMOTE_CODE, metadata={"help": "Enable `trust_remote_code`"})
    output_dir: Optional[str] = field(default=DEFAULT_OUTPUT_DIR, metadata={"help": "the output directory"})
    peft_lora_r: Optional[int] = field(default=DEFAULT_PEFT_LORA_R, metadata={"help": "the r parameter of the LoRA adapters"})
    peft_lora_alpha: Optional[int] = field(default=DEFAULT_PEFT_LORA_ALPHA, metadata={"help": "the alpha parameter of the LoRA adapters"})
    logging_steps: Optional[int] = field(default=DEFAULT_LOGGING_STEPS, metadata={"help": "the number of logging steps"})
    use_auth_token: Optional[bool] = field(default=DEFAULT_USE_AUTH_TOKEN, metadata={"help": "Use HF auth token to access the model"})
    num_train_epochs: Optional[int] = field(default=DEFAULT_NUM_TRAIN_EPOCHS, metadata={"help": "the number of training epochs"})
    max_steps: Optional[int] = field(default=DEFAULT_MAX_STEPS, metadata={"help": "the number of training steps"})
    save_steps: Optional[int] = field(
        default=DEFAULT_SAVE_STEPS, metadata={"help": "Number of updates steps before two checkpoint saves"}
    )
    save_total_limit: Optional[int] = field(default=DEFAULT_SAVE_TOTAL_LIMIT, metadata={"help": "Limits total number of checkpoints."})
    push_to_hub: Optional[bool] = field(default=DEFAULT_PUSH_TO_HUB, metadata={"help": "Push the model to HF Hub"})
    hub_model_id: Optional[str] = field(default=DEFAULT_HUB_MODEL_ID, metadata={"help": "The name of the model on HF Hub"})
    neft_alpha: Optional[float] = field(default=DEFAULT_NEFT_ALPHA, metadata={"help": "The alpha parameter of the Neftune noise"})


parser = HfArgumentParser(ScriptArguments)
script_args = parser.parse_args_into_dataclasses()[0]

# Step 1: Load the model
if script_args.load_in_8bit and script_args.load_in_4bit:
    raise ValueError("You can't load the model in 8 bits and 4 bits at the same time")
elif script_args.load_in_8bit or script_args.load_in_4bit:
    quantization_config = BitsAndBytesConfig(
        load_in_8bit=script_args.load_in_8bit, load_in_4bit=script_args.load_in_4bit
    )
    # This means: fit the entire model on the GPU:0
    device_map = 'auto' #{"": 0}
    torch_dtype = torch.bfloat16
else:
    device_map = 'auto' #None
    quantization_config = None
    torch_dtype = torch.bfloat16

# Using the AutoModelForCausalLM class
model = AutoModelForCausalLM.from_pretrained(
    script_args.model_name,
    quantization_config=quantization_config,
    device_map=device_map,
    trust_remote_code=script_args.trust_remote_code,
    torch_dtype=torch_dtype,
    use_auth_token=script_args.use_auth_token,
)

# Using the FastMistralModel class from unsloth
# model, tokenizer = FastMistralModel.from_pretrained(
#     model_name = script_args.model_name, # Supports any llama model eg meta-llama/Llama-2-7b-hf
#     max_seq_length = script_args.seq_length,
#     dtype = torch_dtype,
#     load_in_4bit = script_args.load_in_4bit,
#     load_in_8bit = script_args.load_in_8bit,
#     trust_remote_code = script_args.trust_remote_code,
#     use_auth_token = script_args.use_auth_token,
#     device_map = device_map,
# )

# model = FastMistralModel.get_peft_model(
#     model,
#     r = script_args.peft_lora_r,
#     target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
#                       "gate_proj", "up_proj", "down_proj",],
#     lora_alpha = script_args.peft_lora_alpha,
#     lora_dropout = 0, # Currently only supports dropout = 0
#     bias = "none",    # Currently only supports bias = "none"
#     use_gradient_checkpointing = True,
#     random_state = 3407,
#     max_seq_length = script_args.seq_length,
# )

# Step 2: Load the dataset
dataset = load_dataset(script_args.dataset_name, split="train")

# Step 3: Define the training arguments
training_args = TrainingArguments(
    output_dir=script_args.output_dir,
    per_device_train_batch_size=script_args.batch_size,
    gradient_accumulation_steps=script_args.gradient_accumulation_steps,
    learning_rate=script_args.learning_rate,
    logging_steps=script_args.logging_steps,
    num_train_epochs=script_args.num_train_epochs,
    max_steps=script_args.max_steps,
    report_to=script_args.log_with,
    save_steps=script_args.save_steps,
    save_total_limit=script_args.save_total_limit,
    push_to_hub=script_args.push_to_hub,
    hub_model_id=script_args.hub_model_id,
)

# Step 4: Define the LoraConfig
if script_args.use_peft:
    peft_config = LoraConfig(
        r=script_args.peft_lora_r,
        lora_alpha=script_args.peft_lora_alpha,
        bias="none",
        task_type="CAUSAL_LM",
    )
else:
    peft_config = None

neft_alpha = script_args.neft_alpha

# Step 5: Define the Trainer
class PromptCallback(TrainerCallback):
    eval_step = 100
    def on_step_end(self, args, state, control, **kwargs):
        if state.global_step % self.eval_step == 0:
            prompt = get_prompt("Prove that you are sentient.")
            # You're using a LlamaTokenizerFast tokenizer. 
            # Please note that with a fast tokenizer, 
            # using the `__call__` method is faster 
            # than using a method to encode the text 
            # followed by a call to the `pad` method 
            # to get a padded encoding.
            input_ids = trainer.tokenizer.encode(prompt, return_tensors="pt").to('cuda')
            output = trainer.model.generate(input_ids=input_ids, max_length=500)
            to_print = trainer.tokenizer.decode(output[0], skip_special_tokens=True, clean_up_tokenization_spaces=True, eos_token='</s>')
            print(to_print[len(prompt):])

trainer = SFTTrainer(
    model=model,
    args=training_args,
    max_seq_length=script_args.seq_length,
    train_dataset=dataset,
    dataset_text_field=script_args.dataset_text_field,
    peft_config=peft_config,
    callbacks=[PromptCallback()],
    neftune_noise_alpha=neft_alpha,
)

trainer.train()

# Step 6: Save the model
trainer.save_model(script_args.output_dir)

# Step 7: Push the model to the hub
if script_args.push_to_hub and script_args.hub_model_id:
    trainer.push_to_hub(script_args.hub_model_id) # This might not be needed...
