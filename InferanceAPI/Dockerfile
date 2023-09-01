FROM nvcr.io/nvidia/pytorch:22.12-py3
#FROM nvcr.io/nvidia/pytorch:23.04-py3
RUN apt-get update && apt-get install -y git
RUN pip install --upgrade --no-input pip
RUN pip uninstall -y torch
RUN pip install --no-input vllm

WORKDIR /app

ARG host=""
ENV HOST=${host}

ARG port=""
ENV PORT=${port}

ARG model_id=""
ENV MODEL_ID=${model_id}

ARG tokenizer_id=""
ENV TOKENIZER_ID=${tokenizer_id}

ENTRYPOINT ["bash", "app.sh"]

COPY app.py app.py
COPY app.sh app.sh
