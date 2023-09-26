#!/bin/bash

set -xe

echo "Starting training..."


# Use PEFT or not? That is the question.
PEFT_PARAMS=""
if [ "$USE_PEFT" = 1 ] ; then
    PEFT_PARAMS="--use_peft"
fi

# Use 4-bit or 8-bit LORA? That is the other question.
LORA_PARAMS=""
if [ "$USE_4BIT" = 1 ] ; then
    LORA_PARAMS="--load_in_4bit"
elif [ "$USE_8BIT" = 1 ] ; then
    LORA_PARAMS="--load_in_8bit"
fi

HUB_PARAMS=""
if [ "$PUSH_TO_HUB" = 1 ] ; then
    HUB_PARAMS="--push_to_hub --hub_model_id ${OUTPUT_MODEL_NAME}"
fi

WANDB_LOG_PARAMS=""
if [ "$LOG_TO_WANDB" = 1 ] ; then
    WANDB_LOG_PARAMS="--log_with wandb"
fi

BATCH_SIZE="${BATCH_SIZE:-4}"
GAS="${GAS:-2}"
EPOCHS="${EPOCHS:-1}"
LEARNING_RATE="${LEARNING_RATE:-1.41e-5}"
SEQENCE_LENGTH="${SEQENCE_LENGTH:-512}"

python ${HOMEDIR}/sft_train.py \
            --model_name "${BASE_MODEL_NAME}" \
            --dataset_name "${DATASET_NAME}" \
            ${LORA_PARAMS} \
            ${PEFT_PARAMS} \
            --batch_size ${BATCH_SIZE} \
            --num_train_epochs ${EPOCHS} \
            --learning_rate ${LEARNING_RATE} \
            --gradient_accumulation_steps ${GAS} \
            --seq_length ${SEQENCE_LENGTH} \
            --output_dir "${OUTPUT_MODEL_PATH}" \
            ${WANDB_LOG_PARAMS} \
            ${HUB_PARAMS} && \
${HOMEDIR}/export.sh || echo "Training failed." && exit 1