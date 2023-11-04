#!/usr/bin/env bash
python ${HOMEDIR}/dpo_train.py --max_length 8192 --max_prompt_length 4096 --per_device_train_batch_size 1 --per_device_eval_batch_size 1 --gradient_accumulation_steps 2
