from .vllm import vLLM

def get_llm(max_tokens=500, temperature=0.0, streaming=False, callbacks=[]):
    return vLLM(max_tokens=max_tokens, temperature=temperature, streaming=streaming, callbacks=callbacks)