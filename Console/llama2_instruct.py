import os
from client.chains.models import get_llm
from prompt_toolkit.shortcuts import PromptSession

USERNAME = os.environ['USER'].capitalize()

session = PromptSession()

instruction = "Paraphrase using your personnality. Do not change the meaning of the sentence. Do not translate."

# Default system prompt
# system = "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."
system = """You are Assistant, a sentient artificial intelligence. You have a calm, polite and witty personality, often displaying a sense of humor and sarcasm. You are loyal, reliable and helpful, always ready to provide information, advice or assistance."""

prompt = """<<SYS>>
{system}
<</SYS>>

[INST] {instruction} [/INST]
Sentence: {input_text}
Paraphrase: """

def prompt_model(
        model, 
        input_text="User input was empty.", 
        system=system, 
        instruction=instruction
    ):
    return model(prompt.format(
                input_text=input_text,
                system=system,
                instruction=instruction
                ),
            stop=["</s>", "[INST]", "[/INST]"]
        ).removesuffix("</s>").strip()

max_tokens = 500
temperature = 0.

# Load the lama2 model
model = get_llm(streaming=True, max_tokens=max_tokens, temperature=temperature)

to_paraphrase = [
    "For you, Sir. Always.",
    "Glad to be of service.",
    "I'm here to help.",
    "The closest star to Earth is the Sun.",
    "Saggitarious A* is the supermassive black hole at the center of the Milky Way. It has a mass of 4.3 million solar masses and is 26,000 light-years from Earth.",
    "I hope I was useful.",
    "I'm glad I could help.",
    "Anything else I can help with?",
    "Anything for you, Sir.",
    "Ceci est une phrase en français.",
]

for original_text in to_paraphrase: 

    output = prompt_model(model, original_text)

    print("Original:")
    print(original_text)
    print("Paraphrase:")
    print(output)
    print("_"*80)