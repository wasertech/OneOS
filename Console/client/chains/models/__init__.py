from .vllm import vLLM
# from .hf import get_hf_llm

def get_llm(max_tokens=500, temperature=0.0, streaming=False, callbacks=[]):
    vllm = vLLM(max_tokens=max_tokens, temperature=temperature, streaming=streaming, callbacks=callbacks)
    # if vllm.is_nlp_server_up():
    return vllm
    # else:
    #     print("Warning: Could not reach internal service!")
    #     print("Falling back to loading the language model now...")
    #     print("This is slow and will happen every time the service is unreachable (downloading will only happen once).")
    #     print("Consider running the assistant as a service to greatly improve loading times.")
    #     print()
    #     print("systemctl enbale --user --now assistant.service")
    #     print()
    #     print("Or manually from python in another process.")
    #     print()
    #     print("python -m assistant.as_service")
    #     print()
    #     return get_hf_llm(max_tokens=max_tokens)
