from trl import SFTTrainer

def create_trainer(
        model,
        tokenizer,
        dataset,
        peft_config,
        training_arguments,
        max_seq_length = 512,
        dataset_text_field="text"
    ):
    return SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        dataset_text_field=dataset_text_field,
        max_seq_length=max_seq_length,
        tokenizer=tokenizer,
        args=training_arguments,
    )