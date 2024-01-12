"""
Activation-aware Weight Quantization (AWQ) algorithm for quantizing LLMs
"""
import os
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

model_path = os.environ.get('OUTPUT_MODEL_NAME', "assistant-mistral-7b-dolphin-2.2.1")
tokenizer_path = model_path #os.environ.get('BASE_MODEL_NAME', "hf-internal-testing/llama-tokenizer")
print(f"Taking full precision weigths and biases from {model_path}.")

quant_path = f'{model_path}-awq'

quant_config = { "zero_point": True, "q_group_size": 128, "w_bit": 4 }

print("Exporting:")
print(f"{quant_config=}")
print(f"{quant_path=}")

# Load model
print("Loading model")
model = AutoAWQForCausalLM.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True)

# Quantize
model.quantize(tokenizer, quant_config=quant_config)

# Save quantized model
model.save_quantized(quant_path)
tokenizer.save_pretrained(quant_path)

model.push_to_hub(f"{quant_path}")
print("Done.")