#!/usr/bin/env bash
set -xe

# Set default value if env var is not set

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
MODEL_ID=${MODEL_ID:-'wasertech/assistant-llama2-7b-qlora-bf16'}
TOKENIZER_ID=${TOKENIZER_ID:-'hf-internal-testing/llama-tokenizer'}
DTYPE=${DTYPE:-'half'} # 'auto', 'half', 'float', 'bfloat16'

python app.py --host $HOST --port $PORT --model $MODEL_ID --tokenizer $TOKENIZER_ID --dtype $DTYPE

# Uncomment to run the OpenAI API server (comment out the line above)
# python -m vllm.entrypoints.openai.api_server --host $HOST --port $PORT --model $MODEL_ID --tokenizer $TOKENIZER_ID --dtype $DTYPE