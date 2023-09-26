#!/usr/bin/env bash
set -xe

# Set default value if env var is not set

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-5085}
MODEL_ID=${MODEL_ID:-'TheBloke/Llama-2-7b-chat-fp16'}
TOKENIZER_ID=${TOKENIZER_ID:-'hf-internal-testing/llama-tokenizer'}
DTYPE=${DTYPE:-'auto'} # 'auto', 'half', 'float', 'bfloat16'

python app.py --host $HOST --port $PORT --model $MODEL_ID --tokenizer $TOKENIZER_ID --dtype $DTYPE

# Uncomment to run the OpenAI API server (comment out the line above)
# python -m vllm.entrypoints.openai.api_server --host $HOST --port $PORT --model $MODEL_ID --tokenizer $TOKENIZER_ID --dtype $DTYPE
