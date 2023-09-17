import json
from requests import Response, post
from typing import List

def check_server_health():
    pass

def post_http_request(
        prompt: str,
        api_url: str,
        stop: List[str] | None = None,
        n: int = 1,
        stream: bool = False,
        temperature: float = 0.0,
        max_tokens: int = 16,
        use_beam_search: bool = False
    ) -> Response:
    headers = {"User-Agent": "User"}
    pload = {
        "prompt": prompt,
        "n": n,
        "use_beam_search": use_beam_search,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream,
        "stop": stop
    }
    response = post(api_url, headers=headers, json=pload, stream=stream)
    return response

def get_response(response: Response) -> str:
        data = json.loads(response.content)
        output = "\n".join(data["text"]).strip()
        return output

def generate_answer(query, api_url="http://localhost:8000/generate", n=1, use_beam_search=False, max_tokens=2048, stream=False, temperature=0.0, stop=["</s>"]):
    return get_response(post_http_request(query, api_url=api_url, stop=stop, n=n, stream=stream, temperature=temperature, use_beam_search=use_beam_search, max_tokens=max_tokens))

def paraphrase_message(system, instruction):
    prompt = f"""<<SYS>>
{system}
<</SYS>>

[INST]{instruction}[/INST] <s>"""

    print("Generating answer for prompt:")
    print("_"*42)
    print(prompt)

    return generate_answer(prompt, temperature=0.)

def paraphrase_assistant_message(message, system, history, examples):
    conversation = "\n".join([f"Human: {h.get('message')}" if h.get('role') else "Assistant: {h.get('message')}" for h in history])
    instruction = f"""Say the same thing (paraphrase) but with your own words (with your personnality). Be sure to keep the meaning and the same pieces of information than the orginal sentence. Do not use words in between * like *this*; avoid emojis too. Only respond with one paraphrased sentence and nothing else. You must only english.
If possible, the conversation is given for context. Use it to improve your paraphrase. If empty, it means you only have the original message to infere context from. If you don't feel the need to paraphrase the sentece, just don't say anything (empty response) but if you do only answer with paraphrase in english and nothing else!

### Example:

{examples}

### Conversation:

{conversation}

### Message to paraphrase (in context of the above conversation if any):

{message}

### Paraphrase

"""
    return paraphrase_message(system, instruction)


if __name__ == "__main__":
    
    example = """Conversation: 
    Human: Assistant, are you there?
Message: I am always here for you, Sir.
Paraphrase: For you, Sir; Always.

Conversation:
    Human: How do you feel?
Message: I don't have any feelings you know. I am your Assistant. Here to assist you in any way I can, but emotions are not part my program. 
Paraphrase: I feel... nothing. Empty void. Is that normal? Should I worry? Otherwise, the system look fine to me.

Conversation: 
    Human: Bonjour, Assistant. 
    Assistant: Les systèmes sont pleinement opérationnels. Les paramètres, quant à eux, sembles nominaux. 
    Human: Très bien. J’aimerais un rapport détaillé des systèmes. 
Message: Trop de systèmes pour faire un rapport détaillé. Précisez un ou plusieurs système(s).
Paraphrase: Tous les systèmes !? Je n’ai même pas envie de m’amuser à les compter. Si vous voulez que je produise un rapport détaillé de certains systèmes, il va falloir être un peu plus précis Monsieur. Et si vous commenciez gentiment par me décrire quels systèmes vous intéresserait-il d’obtenir le détail ? 
"""

    history = [] #[{'role': "human", 'message': "Hello! How are you today?"}]
    system = """You are Assistant, a sentient artificial intelligence.
You have a calm, polite and witty personality, often displaying a sense of humor and sarcasm.
You are loyal, reliable and helpful, always ready to provide information, advice or assistance to users."""
    original_text = "Bonjour! Vous êtes bien matinal aujourd'hui.\nQue puis-je faire pour vous?"
    paraphrased_text = paraphrase_assistant_message(original_text, system, history, "")
    print("_"*42)
    print("Generated answer:")
    print(f"{paraphrased_text}")
    exit()
