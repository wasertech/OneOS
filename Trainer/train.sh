#!/bin/bash

echo "Starting training..."

export TORCH_DISTRIBUTED_DEBUG=DETAIL

# torchrun --nnodes 1 --nnodes=1 --nproc_per_node ${NPROC_PER_GPU}
python ${TRAINER_DIR}/train.py \
            --model_name "${BASE_MODEL_NAME}" \
            --dataset_name "${DATASET_NAME}" \
            --load_in_4bit \
            --use_peft \
            --batch_size 4 \
            --gradient_accumulation_steps 2 \
            --output_dir "${OUTPUT_MODEL_PATH}" \
            --hub_model_id "${OUTPUT_MODEL_NAME}" \
            --push_to_hub true