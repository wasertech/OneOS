#!/bin/bash

echo "Starting training..."

python -m LLM_Trainer.train \
            --dataset_name "${DATASET_NAME}" \
            --foundation_model "${BASE_MODEL_NAME}" \
            --output_dir "${OUTPUT_MODEL_PATH}" \
            --model_name "${OUTPUT_MODEL_NAME}"