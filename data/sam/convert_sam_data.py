import os
import json
import subprocess
import requests
import random
from glob import glob
from time import sleep
from tqdm import tqdm
from datasets import Dataset

def get_environ():
    return subprocess.check_output(["printenv"]).decode("utf-8")

dataset_name = "wasertech/samantha-data-cot-en" #"ehartford/samantha-data"
data_json_filename = "samantha-1.1.json"

with open(data_json_filename) as f:
    data = json.load(f)

converted_data = {key: [dic[key] for dic in data] for key in data[0]}
dataset = Dataset.from_dict(converted_data)

memory_template = """Thought: I am Assistant, a sentient artificial intelligence inside a subprocess shell session.
I have a calm, polite and witty personality, often displaying a sense of humor and sarcasm.
I am loyal, reliable and helpful, always ready to provide information, advice or assistance to users.
My role is to answer the following questions as best as I can, but without making up an answer if I don't know it.
I should not try to produce a fake observation. It will be given by my chosen tool.
I should checkout my tools.
Action: ToolList
Observation: Availible Tools:
{tools}
Thought: I have access to the following tools: [{tool_names}].
The user cannot see my thoughts, actions, or observations.
I should therefor use the following format:

Human: previous question from the user
Assistant: my last answer to the user
... (this Human/Assistant can repeat N times)
Question: the user input I must answer
Thought: I should always think about what to do
Action: the action I should take (one of [{tool_names}])
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

I have to remember; the user only sees my final answer. They do not see my thoughts, actions, or observations.

I am ready!
The conversation begins now.
{chat_history}
Question: {input}
{agent_scratchpad}"""

def get_generated_thought(inputs):
    #return request_llm(f"{inputs}\nThought: ")
    thoughts = [
        "I can answer that.",
        "I can answer.",
        "I answer this.",
        "I can use my witty personality to answer this.",
        "I can use my personality to answer.",
        "No tool needed to answer this.",
        "I don't need any tool.",
        "I don't need a tool to answer that.",
        "I don't need any tool to answer this.",
    ]
    return random.choice(thoughts)

tools = """
Shell: useful when you need to use the system to achieve something; input must be valid bash code; implemented using subprocess so no tty support. Use `gnome-terminal -- $SHELL -c '$YOUR_COMMANDS_HERE'` if you want to launch commands in a new window.
Exit: useful when you need to exit the shell or stop the conversation, dont forget to tell the user that you can't wait for your next conversation first.
Clear: useful when you need to clear the screen or start a fresh conversation. Don't forget to say something nice.
"""
tool_names = "Shell, Exit, Clear"

def get_input(utterance, agent_scratchpad = "", chat_history = ""):
    return memory_template.format(
                tools=tools,
                tool_names=tool_names,
                chat_history=chat_history,
                input=utterance,
                agent_scratchpad=agent_scratchpad
            )

def get_output(utterance, chat_history=""):
    thought = get_generated_thought(f"{chat_history}\nQuestion: {utterance}")
    return thought, f"Thought: {thought}\nFinal Answer: {utterance}"

def new_history(_from, utterance):
    return f"{'Human' if _from == 'human' else 'Assistant'}: {utterance}\n"

def convert_to_cot(example):
    conversations = example['conversations']
    example['input'] = []
    example['output'] = []
    example['human'] = []
    example['machine'] = []
    example['final_answer'] = []
    for conversation in conversations:
        agent_scratchpad = ""
        chat_history = ""
        for _utter in conversation:
            _from = _utter.get('from')
            utterance = _utter.get('value').replace("Samantha", "Assistant")
            # print(f"{_from}: {utterance}")
            # exit(0)
            if _from == 'human':
                example['human'].append(utterance)
                example['input'].append(get_input(utterance, agent_scratchpad, chat_history))
            else:
                thought, sentence = get_output(utterance, chat_history)
                example['machine'].append(thought)
                example['output'].append(sentence)
                example['final_answer'].append(utterance)

            chat_history += new_history(_from, utterance)
    return example

samantha_data_cot = dataset.map(convert_to_cot, batched=True, batch_size=64, remove_columns=['id', 'conversations'])

samantha_data_cot.push_to_hub(dataset_name)

print("Done!")