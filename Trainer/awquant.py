"""
Activation-aware Weight Quantization (AWQ) algorithm for quantizing LLMs
"""
import os

from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

from llmcompressor import oneshot
from llmcompressor.modifiers.awq import AWQModifier
from llmcompressor.utils import dispatch_for_generation


MODEL_ID = os.environ.get('OUTPUT_MODEL_NAME', "swiss-ai/Apertus-8B-Instruct-2509")

model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype="auto")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
print(f"Taking full precision weigths and biases from {MODEL_ID}.")

# DATASET_ID = os.environ.get('CALIBRATION_DATASET_NAME', "swiss-ai/apertus-sft-mixture") 
# DATASET_SPLIT = "train"

# NUM_CALIBRATION_SAMPLES = 256
# MAX_SEQUENCE_LENGTH = 1024

# ds = load_dataset(DATASET_ID, split=f"{DATASET_SPLIT}[:{NUM_CALIBRATION_SAMPLES}]")
# ds = ds.shuffle(seed=42)

# def preprocess(example):
#     conv = example["messages"]
#     c = []
#     for msg in conv:
#         if msg['role'] not in ['user', 'assistant', 'system', 'tool']:
#             continue
#         c.append(msg)

#     assert len(c) > 0, f"Empty messages in {example}"
    
#     try:
#         t = tokenizer.apply_chat_template(
#             c,
#             tokenize=False,
#         )
#     except Exception as x:
#         print(f"Error in template application: {c}")
#         raise Exception(f"Error in template application: {c}\n{x}")
    
#     assert t, "Empty text"
    
#     return { "text": t }


# ds = ds.map(preprocess)


# # Tokenize inputs.
# def tokenize(sample):
#     return tokenizer(
#         sample["text"],
#         padding=False,
#         max_length=MAX_SEQUENCE_LENGTH,
#         truncation=True,
#         add_special_tokens=False,
#     )


# recipe = [
#     AWQModifier(
#         ignore=[
#             "lm_head",
#             # gates/router/expert selectors
#             "re:.*mlp.gate$",
#             "re:.*mlp.shared_expert_gate$",
#             "re:.*router",
#             "re:.*gate",
#             "re:.*expert",
#             "re:.*experts",
#         ],
#         scheme="W4A16_ASYM",
#         targets=["Linear"],
#     ),
# ]

# # Apply algorithms.
# oneshot(
#     model=model,
#     dataset=ds,
#     recipe=recipe,
#     max_seq_length=MAX_SEQUENCE_LENGTH,
#     num_calibration_samples=NUM_CALIBRATION_SAMPLES,
    
# )

# Confirm generations of the quantized model look sane.
print("\n\n")
print("========== SAMPLE GENERATION ==============")
dispatch_for_generation(model)

prompt = tokenizer.apply_chat_template(
    [{'role': "user", 'content': "Present yourself."}],
    tokenize=False,
)
input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(
    model.device
)
output = model.generate(input_ids, max_new_tokens=100)
print(tokenizer.decode(output[0]))
print("==========================================\n\n")

# Save to disk compressed.
SAVE_DIR = MODEL_ID.rstrip("/").split("/")[-1] + "-awq"
model.save_pretrained(SAVE_DIR, save_compressed=True)
tokenizer.save_pretrained(SAVE_DIR)

print("Done.")