from transformers import (
    AutoModelForCausalLM,
    TrainingArguments,
)

def create_training_args(
        output_dir = "./results",
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 8,
        optim = "paged_adamw_32bit",
        save_steps = 100,
        logging_steps = 10,
        learning_rate = 2e-4,
        max_grad_norm = 0.3,
        max_steps = 100,
        warmup_ratio = 0.03,
        lr_scheduler_type = "constant",
        group_by_length=True,
        fp16=True,
    ):
    return TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=per_device_train_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        optim=optim,
        save_steps=save_steps,
        logging_steps=logging_steps,
        learning_rate=learning_rate,
        fp16=fp16,
        max_grad_norm=max_grad_norm,
        max_steps=max_steps,
        warmup_ratio=warmup_ratio,
        group_by_length=group_by_length,
        lr_scheduler_type=lr_scheduler_type,
    )

def create_model(
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
