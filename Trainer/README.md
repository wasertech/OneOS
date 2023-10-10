
Build and start training using docker.

```shell
docker build \
--rm \
--build-arg uid=1018 \
--build-arg gid=1018 \
-f Dockerfile.train \
-t llm-train:latest . && \
docker run \
-it \
--env HUB_API_TOKEN="${HUB_API_TOKEN}" \
--env PUSH_TO_HUB=0 \
--env LOG_TO_WANDB=1 \
--env DISTRIBUTE_TRAIN=1 \
--env NPROC_PER_GPU=2 \
--env BASE_MODEL_NAME="Photolens/llama-2-7b-langchain-chat" \
--env OUTPUT_MODEL_NAME="assistant-llama2-7b-chat" \
--env BATCH_SIZE=4 \
--env GAS=8 \
--env SEQENCE_LENGTH=4096 \
--env USE_PEFT=1 \
--env USE_4BIT=1 \
--gpus=all \
--privileged \
--shm-size=1g \
--ulimit memlock=-1 \
--ulimit stack=67108864 \
--mount type=bind,src=`echo ~/.cache/huggingface/`,dst=/home/trainer/.cache/huggingface/ \
--mount type=bind,src="${DATA_VOLUME_PATH}",dst=/mnt \
llm-train:latest && \
docker container prune || docker container prune -f
```
