from transformers import AutoModelForCausalLM, AutoTokenizer

class LLModel:
    def __init__(
            self, 
            model_name, 
            bnb_config, 
            trust_remote_code=True, 
            use_cache=False
        ):
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            trust_remote_code=trust_remote_code
        )
        model.config.use_cache = use_cache
        return model
