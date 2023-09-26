'''
Merge the lora adapter back into the base model
'''

print("Loading libraries...", end="")
import os
import time
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM
from requests.exceptions import ConnectionError

print("Done.")

hub_user = "wasertech"
base_model = os.environ.get("BASE_MODEL_NAME")
#adapter_model_name = "assistant-llama2-7b-qlora-bf16"
merged_model_name = os.environ.get('OUTPUT_MODEL_NAME', "assistant-llama2-7b-merge-bf16")

print("Loading the base model and the LoRA adapter...")

OUTPUT_MODEL_PATH = os.environ.get("OUTPUT_MODEL_PATH", "./output")

config = PeftConfig.from_pretrained(f"{OUTPUT_MODEL_PATH}")
model = AutoModelForCausalLM.from_pretrained(base_model)
model = PeftModel.from_pretrained(model, f"{OUTPUT_MODEL_PATH}")

print("Loading the base model and the LoRA adapter...Done.")

print("Merging the LoRA adapter back into the base model...", end="")

# Merge the LoRA weights into the base model
merged_model = model.merge_and_unload()

print("Done.")

print("Saving the merged model...", end="")

# Save the merged model
merged_model.save_pretrained(merged_model_name)

print("Done.")

# Push the merged model to the Hub
# print("Pushing the merged model to the Hub...")

# while True:
#     try:
#         merged_model.push_to_hub(merged_model_name)
#         print("Pushing the merged model to the Hub...Done!")
#         print("Model merged and pushed to the Hub!")
#         break
#     except (RuntimeError, ConnectionError) as e:
#         print(f"Error while uploading to the Hub: {e}")
#         print("Retrying in 10 seconds...", end="")
#         time.sleep(10)
#         print("Done.")
#         print("Retrying...", end="")

