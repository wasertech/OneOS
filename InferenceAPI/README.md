# vLLM API

Efficiently serving LLMs is a challenging task. I use a custom vLLM server to achive so. It's relatively fast and efficient, specially with AWQ models.

## Installation & Usage

I recommend you use `docker` to serve your model in a contained environment but you can always try to install vLLM with `pip` or from source but results are not given.

### Using docker

You'll need a [working Docker installation with Nvidia Container Toolkit](https://docs.docker.com/config/containers/resource_constraints/#gpu) and at least one [GPU with a CUDA score of 7.0 or more](https://developer.nvidia.com/cuda-gpus) and enough memory to load the model.

You can try using CPU but at the cost of inference speed.

See [vLLM docker installation](https://vllm.readthedocs.io/en/latest/getting_started/installation.html) for more information.

### Build an image

```shell
docker build \
--rm \
-f Dockerfile \
-t vllm-inference-api:latest .
```

### Run your image

Expose port `5085` (or `$PORT`), specify gpus, shared memory size allocation and mount your local HuggingFace cache inside the container so that you don't have to download it everytime.

Use `$MODEL_ID` to set which model to load.

```shell
docker run \
-it \
-p 5085:5085 \
--gpus=all \
--privileged \
--shm-size=8g \
--ulimit memlock=-1 \
--ulimit stack=67108864 \
--mount type=bind,src=`echo ~/.cache/huggingface/hub/`,dst=/root/.cache/huggingface/hub/ \
--env PORT="5085" --env MODEL_ID="wasertech/assistant-llama2-chat-awq" \
--env QUANT="awq" --env DTYPE="half" \
vllm-inference-api:latest
```

### Prompt the model

```shell
curl -N -X POST \
-H "Accept: text/event-stream" -H "Content-Type: application/json" \
-d '{"prompt": "<s>[INST] Greeting Assistant [/INST] ", "temperature": 0.5, "max_tokens": 2, "stop": ["</s>",]}' \
http://0.0.0.0:8000/generate
```
