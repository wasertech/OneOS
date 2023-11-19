#!/usr/bin/env bash
set -xe

# Set default value if env var is not set

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-5085}
MODEL_ID=${MODEL_ID:-'TheBloke/Llama-2-7b-chat-fp16'}
TOKENIZER_ID=${TOKENIZER_ID:-'hf-internal-testing/llama-tokenizer'}
DTYPE=${DTYPE:-'auto'} # 'auto', 'half', 'float', 'bfloat16'
QUANT=${QUANT} # None, 'awq'
N_GPUS=${N_GPUS:-1}
GPU_MEM=${GPU_MEM:-0.9}

QUANT_FLAG=""

# Check if $QUANT is defined
if [ -n "$QUANT" ]; then
    QUANT_FLAG="--quantization ${QUANT}"
fi

python app.py --host $HOST --port $PORT --model $MODEL_ID --tokenizer $TOKENIZER_ID --dtype $DTYPE --tensor-parallel-size $N_GPUS --gpu-memory-utilization $GPU_MEM $QUANT_FLAG

# Uncomment to run the OpenAI API server (comment out the line above)
# pydantic==1.10.13
# fschat
# accelerate
# python 
# python -m vllm.entrypoints.openai.api_server --host $HOST --port $PORT --model $MODEL_ID --tokenizer $TOKENIZER_ID --dtype $DTYPE
