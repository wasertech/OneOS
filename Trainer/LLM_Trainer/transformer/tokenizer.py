from transformers import AutoTokenizer

def create_tokenizer(
        model_name, 
        trust_remote_code=True, 
        *args,
        **kwargs
    ):
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=trust_remote_code,
        *args,
        **kwargs
    )
    tokenizer.pad_token = tokenizer.eos_token
    return tokenizer