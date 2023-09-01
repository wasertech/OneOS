import os, sys, shutil, psutil
import time
import json, pickle
import subprocess
import requests
import random
from glob import glob
from time import sleep
from tqdm import tqdm
from halo import Halo
from datasets import Dataset
from translator import Translator
from datetime import timedelta
import logging
import locale

logging.getLogger('transformers.pipelines.base').setLevel(logging.ERROR)
logger = logging.Logger(__file__)
locale.setlocale(locale.LC_ALL, '')

translator = Translator("eng_Latn", "fra_Latn", model_id="Helsinki-NLP/opus-mt-en-fr", max_length=2048)

spinner = Halo(text='Translating', spinner='dots12')

def load_translated_conversations():
    data_file = "data/samantha-1.1.fr.json"
    if not os.path.exists(data_file):
        return {}
    else:
        with open(data_file, 'r') as f:
            json_data = json.load(f)
        return {
            conversation.get('id'): conversation.get('conversations')
            for conversation in json_data
        }

def save_translated_conversations(conversations: dict):
    data_file = "data/samantha-1.1.fr.json"
    json_conversations = [{'id': k, 'conversations': v} for k, v in conversations.items()]
    with open(data_file, 'w') as f:
        json.dump(json_conversations, f)
    return json_conversations

def translate_conversation(conversation_data: list):
    translated_conversation = []
    for turn in conversation_data:
        _turn = turn
        sentence = turn.get('value')
        assert sentence, "Nothing to translate!"
        _sentence = sentence.replace(". ", ".<split>")
        _sentence = _sentence.replace("? ", "?<split>")
        _sentence = _sentence.replace("! ", "!<split>")
        translated_lines = []
        for line in _sentence.split("\n"):
            s = line.split("<split>")
            try:
                translated_lines.extend(translator.translate(s))
            except Exception as e:
                translated_lines.extend(s)
        _turn['value'] = "\n".join(translated_lines)
        translated_conversation.append(_turn)
    return translated_conversation

dataset_name = "wasertech/samantha-data-cot-fr" #"ehartford/samantha-data"
data_json_filename = "samantha-1.1.json"

spinner.start()

with open(data_json_filename) as f:
    data = json.load(f)

TOTAL_CONVERSATIONS = len(data)

spinner.info(f"Found {TOTAL_CONVERSATIONS:n} conversation{'s' if TOTAL_CONVERSATIONS > 1 else ''}.")

translated_conversations = load_translated_conversations()

try:
    for conversation in tqdm(data):
        conversation_id = conversation.get('id', None)
        conversation_data = conversation.get('conversations', [])
        assert conversation_id and conversation_data, f"Conversation ID and data must be given; currently {conversation_id=}\n{conversation_data=}"
        
        if conversation_id not in translated_conversations:
            # print(f"Translating Conversation[{conversation_id}]")
            translated_conversations[conversation_id] = translate_conversation(conversation_data)
except (Exception, KeyboardInterrupt) as e:
    spinner.stop()
    #spinner.error(f"{e}")
    spinner.info("saving translated sentences.")
    save_translated_conversations(translated_conversations)
    exit(1)

save_translated_conversations(translated_conversations)