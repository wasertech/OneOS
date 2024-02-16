"""Large language model inference API for generation and embedding."""
import sys
import argparse
import json
import logging
import uvicorn

from typing import AsyncGenerator
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse

from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.sampling_params import SamplingParams
from vllm.utils import random_uuid

import sentence_transformers
# from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

logging.basicConfig(level=logging.DEBUG)

TIMEOUT_KEEP_ALIVE = 5  # seconds.
TIMEOUT_TO_PREVENT_DEADLOCK = 1  # seconds.
app = FastAPI()

# Helth check endpoint.
@app.get("/")
async def health_check() -> Response:
    return Response(status_code=200)

@app.get("/embeding/model/name")
async def get_embedding_model_name() -> Response:
    return Response(status_code=200, content=emmbeding_engine.model_name)

@app.post("/embed")
async def emmbed(request: Request) -> Response:
    """Generate embeddings for the request.

    The request should be a JSON object with the following fields:
    - prompt: the prompt to use for the generation.
    """
    request_dict = await request.json()
    prompt = request_dict.pop("prompt")
    # stream = request_dict.pop("stream", False)
    # request_id = random_uuid()
    #results_generator = emmbeding_engine.embed_query(prompt)
    results_generator = emmbeding_engine.client.encode_multi_process([prompt] if isinstance(prompt, str) else prompt if isinstance(prompt, list) else [], emmbeding_engine_pool)
    
    # Streaming case
    # async def stream_results() -> AsyncGenerator[bytes, None]:
    #     async for request_output in results_generator.tolist()[0]:
    #         ret = {"emmbedings": request_output}
    #         yield (json.dumps(ret) + "\0").encode("utf-8")
    
    # async def abort_request() -> None:
    #     sentence_transformers.SentenceTransformer.stop_multi_process_pool(pool)
    
    # if stream:
    #     background_tasks = BackgroundTasks()
    #     # Abort the request if the client disconnects.
    #     background_tasks.add_task(abort_request)
    #     return StreamingResponse(stream_results(), background=background_tasks)
    
    # Non-streaming case
    final_output = []
    #for request_output in results_generator.tolist():
    if await request.is_disconnected():
        # Abort the request if the client disconnects.
        sentence_transformers.SentenceTransformer.stop_multi_process_pool(emmbeding_engine_pool)
        return Response(status_code=499)
    final_output = results_generator.tolist() if isinstance(prompt, list) else results_generator.tolist()[0] if isinstance(prompt, str) else []

    assert final_output
    ret = {"embeddings": final_output}
    return JSONResponse(ret)

@app.post("/generate")
async def generate(request: Request) -> Response:
    """Generate completion for the request.

    The request should be a JSON object with the following fields:
    - prompt: the prompt to use for the generation.
    - stream: whether to stream the results or not.
    - other fields: the sampling parameters (See `SamplingParams` for details).
    """
    request_dict = await request.json()
    prompt = request_dict.pop("prompt")
    stream = request_dict.pop("stream", False)
    sampling_params = SamplingParams(**request_dict)
    request_id = random_uuid()
    results_generator = engine.generate(prompt, sampling_params, request_id)
    
    # Streaming case
    async def stream_results() -> AsyncGenerator[bytes, None]:
        text_buffer = ""
        async for request_output in results_generator:
            # prompt = request_output.prompt
            # text_outputs = [
            #     prompt + output.text for output in request_output.outputs
            # ]
            
            text_outputs = []
            for output in request_output.outputs:
                text_outputs.append(output.text.removeprefix(text_buffer))
                text_buffer = output.text
            
            ret = {"text": text_outputs[-1]}
            yield (json.dumps(ret) + "\0").encode("utf-8")

    async def abort_request() -> None:
        await engine.abort(request_id)

    if stream:
        background_tasks = BackgroundTasks()
        # Abort the request if the client disconnects.
        background_tasks.add_task(abort_request)
        return StreamingResponse(stream_results(), background=background_tasks)

    # Non-streaming case
    final_output = None
    async for request_output in results_generator:
        if await request.is_disconnected():
            # Abort the request if the client disconnects.
            await engine.abort(request_id)
            return Response(status_code=499)
        final_output = request_output

    assert final_output is not None
    # prompt = final_output.prompt
    # text_outputs = [prompt + output.text for output in final_output.outputs]
    text_outputs = [output.text for output in final_output.outputs]
    ret = {"text": text_outputs}
    return JSONResponse(ret)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--embed", type=str, default="intfloat/e5-large-v2", help="Embedding model to use")
    parser.add_argument("--embed-device", type=str, default="cuda", help="Embedding model device")
    parser.add_argument("--embed-norm", type=bool, default=True, help="Normalize embeddings")
    vllm_parser = AsyncEngineArgs.add_cli_args(parser)
    vllm_args = vllm_parser.parse_args()

    engine_args = AsyncEngineArgs.from_cli_args(vllm_args)
    engine = AsyncLLMEngine.from_engine_args(engine_args)
    
    print("Loading embedding model...")
    args = parser.parse_args()
    emmbeding_engine_model = args.embed
    emmbeding_engine_model_kwargs = {'device': args.embed_device}
    emmbeding_engine_encode_kwargs = {'normalize_embeddings': args.embed_norm}
    emmbeding_engine = HuggingFaceEmbeddings(model_name=emmbeding_engine_model, model_kwargs=emmbeding_engine_model_kwargs, encode_kwargs=emmbeding_engine_encode_kwargs, cache_folder="/root/.cache/huggingface/hub/")
    emmbeding_engine_pool = emmbeding_engine.client.start_multi_process_pool()
    
    try:
        uvicorn.run(app,
                    host=args.host,
                    port=args.port,
                    log_level="debug",
                    timeout_keep_alive=TIMEOUT_KEEP_ALIVE)
    except KeyboardInterrupt:
        print("Shutting down...")
        

    emmbeding_engine.client.stop_multi_process_pool(emmbeding_engine_pool)
    
