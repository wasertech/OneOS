import os, shutil
import re
import json
import questionary
import requests
import pickle
import subprocess
from glob import glob
from pathlib import Path
from huggingface_hub import HfApi, Repository
from datasets import Dataset, DatasetInfo, SplitInfo, load_dataset, concatenate_datasets
from rich.console import Console
from rich.markdown import Markdown
from pprint import pprint
import argparse

BANNER = Markdown("# Data Manager")
BANNER_HIGHLIGHT = (
    "Welcome to the Data Manager for Reinforcement Learning with Human Feedback!"
)


class Tool:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return f"'{self.name}': '{self.description}'"

    def __repr__(self):
        return f"'{self.name}': '{self.description}'"


standard_tools_list = [
    Tool(
        "Python",
        "useful when you need to use logic in your answer. Input must be valid python code.",
    ),
    Tool(
        "Search",
        "useful when you need more context to answer a question; you should use targeted search terms",
    ),
    Tool(
        "Wikipedia",
        "useful when you need to use an encyclopedia to answer a question; input will be used to search on wikipedia",
    ),
    Tool(
        "Shell",
        "useful when you need to use the system to achieve something; input must be valid bash code; implemented using subprocess so no tty support.",
    ),
    Tool(
        "Exit",
        "useful when you need to exit the shell or stop the conversation, dont forget to tell the user that you can't wait for your next conversation first.",
    ),
    Tool(
        "Clear",
        "useful when you need to clear the screen or start a fresh conversation. Don't forget to say something nice.",
    ),
]


def serialize(item, location):
    # if not os.path.exists(os.path.dirname(location)):
    #     os.makedirs(os.path.dirname(location))
    with open(location, "wb") as f:
        pickle.dump(item, f)


def deserialize(location, default=None):
    if not os.path.exists(location):
        return default
    with open(location, "rb") as f:
        return pickle.load(f)


def get_users():
    return deserialize("users.pkl", default={})


def save_users(users):
    serialize(users, "users.pkl")


def create_user(username):
    print(f"Creating user {username}")
    user = User(username)

    if not user._check_attr("first_name"):
        first_name = questionary.text("First name: ").ask()
        if first_name:
            user.set_first_name(first_name)
            user.save()

    if not user._check_attr("last_name"):
        last_name = questionary.text("Last name: ").ask()
        if last_name:
            user.set_last_name(last_name)
            user.save()

    if not user._check_attr("gender"):
        user_gender = questionary.select(
            "What is your gender?",
            choices=["man", "woman", "none"],
        ).ask()
        # print(f"You selected {user_gender}")
        if user_gender in ["man", "woman", "none"]:
            # print("Setting gender")
            user.set_gender(user_gender)
            user.save()
    
    if not user._check_attr("surnames"):
        add_surname = True
        while add_surname:
            surname = questionary.text("Surname: ").ask()
            if surname is not None:
                if user._check_attr("surnames"):
                    user.surnames.append(surname)
                else:
                    user.surnames = [surname]
                user.save()
                add_surname = questionary.confirm(
                    "Would you like to add another surname?", default=False
                ).ask()
            else:
                add_surname = False

    user.save()

    return user


def get_usernames():
    users = get_users()
    list_users = list(users.keys())
    current_user = os.environ.get("USER")

    if current_user not in list_users:
        list_users.append(current_user)
        create_user(current_user)
    return list_users


class User:
    username: str
    first_name: str | None = None
    last_name: str | None = None
    gender: str | None = None
    surnames: list | None = None

    def __init__(self, username: str | None = os.environ.get("USER")):
        if not username:
            raise ValueError("You need to provide a username")
        self.username = username
        self.load_from_disk()

    def load_from_disk(self):
        user = get_users().get(self.username)
        if user is None:
            user = {}

        if user.get("first_name"):
            self.set_first_name(user.get("first_name"))
        if user.get("last_name"):
            self.set_last_name(user.get("last_name"))
        if user.get("gender"):
            self.set_gender(user.get("gender"))
        if user.get("surnames"):
            self.set_surnames(user.get("surnames"))

    def __str__(self):
        if self._check_attr("first_name") and self._check_attr("last_name"):
            name = f"{self.first_name.capitalize()} {self.last_name.capitalize()}"
        elif self._check_attr("first_name"):
            name = f"{self.first_name.capitalize()}"
        elif self._check_attr("last_name"):
            name = f"{self.last_name.capitalize()}"
        else:
            name = f"{self.username}"
        return name

    def __repr__(self):
        return self.describe()

    def _get_attr(self, attr):
        if self._check_attr(attr):
            return getattr(self, attr)
        return None

    def _set_attr(self, attr, value):
        setattr(self, attr, value)

    def _check_attr(self, attr):
        if hasattr(self, attr) and getattr(self, attr) is not None:
            return True
        return False

    def set_first_name(self, first_name: str):
        self._set_attr("first_name", first_name)

    def set_last_name(self, last_name: str):
        self._set_attr("last_name", last_name)

    def set_gender(self, gender: str):
        gender = gender.lower()
        if gender in ["man", "woman", "none"]:
            self._set_attr("gender", gender)
            assert (
                self._check_attr("gender") and self._get_attr("gender") == gender
            ), f"Could not set gender to {gender}"

    def set_surnames(self, surnames: list):
        self._set_attr("surnames", surnames)

    def describe(self):
        if self._check_attr("gender"):
            gender = self.gender
        else:
            gender = "person"
        if self._check_attr("surnames"):
            if len(self._get_attr("surnames")) > 1:
                surnames = (
                    "either "
                    + ", ".join(self.surnames[:-1])
                    + " or "
                    + self.surnames[-1]
                )
            else:
                surnames = self.surnames[0]
        else:
            surnames = self.username
        if self._check_attr("first_name") and self._check_attr("last_name"):
            name = f"My firstname is {self.first_name.capitalize()} and my lastname is {self.last_name.capitalize()}."
        elif self._check_attr("first_name"):
            name = f"My firstname is {self.first_name.capitalize()}."
        elif self._check_attr("last_name"):
            name = f"My lastname is {self.last_name.capitalize()}."
        else:
            name = f"My username is {self.username}."

        description = f"""I am the user. {name}
I am a {gender}. You should address me as {surnames}."""
        return description

    def save(self):
        users = get_users()
        if self.username not in users:
            users[self.username] = {}
        if hasattr(self, "first_name"):
            users[self.username]["first_name"] = self.first_name
        if hasattr(self, "last_name"):
            users[self.username]["last_name"] = self.last_name
        if hasattr(self, "gender"):
            users[self.username]["gender"] = self.gender
        if hasattr(self, "surnames"):
            users[self.username]["surnames"] = self.surnames

        save_users(users)


class Environment:
    owner: str
    language: str | None = None
    pwd: str | None = None
    home: str | None = None
    date: str | None = None
    last_seen: str | None = None

    def __init__(
        self, owner: str = os.environ.get("USER"), last_seen: str | None = None
    ):
        if not owner:
            raise ValueError("You need to provide an owner")

        self.owner = owner
        self.last_seen = last_seen

    def load_from_environment(self):
        self.pwd = os.environ.get("PWD")
        self.home = os.environ.get("HOME")
        self.language = os.environ.get("LANG")
        self.date = subprocess.check_output(["date"]).decode("utf-8").strip()

    def __str__(self):
        return self.describe()

    def __repr__(self) -> str:
        return self.describe()

    def describe(self):
        return f"""```env
USER={self.owner}
HOME={self.home}
PWD={self.pwd}
LANG={self.language}
DATE={self.date}
LAST_SEEN={self.last_seen}
```"""


class Tools:
    def __init__(self, tools):
        self.tools = tools

    def __getitem__(self, key):
        return self.tools[key]

    def __setitem__(self, key, value):
        self.tools[key] = value

    def __delitem__(self, key):
        del self.tools[key]

    def __iter__(self):
        return iter(self.tools)

    def __len__(self):
        return len(self.tools)

    def __contains__(self, item):
        return item in self.tools

    def __add__(self, other):
        return self.tools + other

    def list_str(self):
        tools_list_str = ",\n    ".join([str(tool) for tool in self.tools])
        return f"""```tools
{{
    {tools_list_str}
}}
```"""

    def __str__(self):
        return self.list_str()

    def __repr__(self):
        return self.list_str()


def get_agents():
    return deserialize("agents.pkl", default={})


def save_agents(agents):
    serialize(agents, "agents.pkl")


def get_agentnames():
    agents = get_agents()
    list_agents = list(agents.keys())
    if not list_agents:
        agents["system"] = {
            "name": "system",
            "description": None,
            "personality": None,
            "traits": None,
            "adjectives": None,
            "role": None,
            "user_seen": None,
        }
        agents["assistant"] = {
            "name": "assistant",
            "description": "a sentient artificial intelligence",
            "personality": ["calm", "polite", "witty"],
            "traits": ["a sense of humor", "sarcasm"],
            "adjectives": ["loyal", "reliable", "helpful"],
            "role": "provide information, advice or assistance to users",
            "user_seen": None,
        }
        save_agents(agents)
        list_agents.extend(["system", "assistant"])
    return list_agents


class Agent:
    name: str
    description: str | None = None
    personality: list | None = None
    traits: list | None = None
    ajectives: list | None = None
    role: str | None = None
    user_seen: dict = {}

    def __init__(self, name: str | None = None):
        if not name:
            raise ValueError("You need to provide a name")
        self.name = name
        self.load_from_disk()

    def load_from_disk(self):
        agents = get_agents()
        agent = agents.get(self.name)
        if agent is None:
            agent = {}
        if agent.get("description"):
            self.set_description(agent.get("description"))
        if agent.get("personality"):
            self.set_personality(agent.get("personality"))
        if agent.get("traits"):
            self.set_traits(agent.get("traits"))
        if agent.get("adjectives"):
            self.set_adjectives(agent.get("adjectives"))
        if agent.get("role"):
            self.set_role(agent.get("role"))
        if agent.get("user_seen"):
            self.set_user_seen(agent.get("user_seen"))

    def __str__(self):
        if hasattr(self, "name"):
            return self.name.capitalize()
        return None

    def __repr__(self):
        return self.describe()

    def _get_attr(self, attr):
        if self._check_attr(attr):
            return getattr(self, attr)
        return None

    def _set_attr(self, attr, value):
        setattr(self, attr, value)

    def _check_attr(self, attr):
        if hasattr(self, attr) and getattr(self, attr) is not None:
            return True
        return False

    def set_description(self, description: str):
        self._set_attr("description", description)

    def set_personality(self, personality: list):
        self._set_attr("personality", personality)

    def set_traits(self, traits: list):
        self._set_attr("traits", traits)

    def set_adjectives(self, adjectives: list):
        self._set_attr("adjectives", adjectives)

    def set_role(self, role: str):
        self._set_attr("role", role)

    def set_user_seen(self, user_seen: dict):
        self._set_attr("user_seen", user_seen)

    def get_personality(self):
        if self._check_attr("personality"):
            if len(self.personality) > 1:
                return ", ".join(self.personality[:-1]) + " and " + self.personality[-1]
            else:
                return self.personality[0]
        return None

    def get_traits(self):
        if self._check_attr("traits"):
            if len(self.traits) > 1:
                return ", ".join(self.traits[:-1]) + " and " + self.traits[-1]
            else:
                return self.traits[0]
        return None

    def get_adjectives(self):
        if self._check_attr("adjectives"):
            if len(self.adjectives) > 1:
                return ", ".join(self.adjectives[:-1]) + " and " + self.adjectives[-1]
            else:
                return self.adjectives[0]
        return None

    def describe(self):
        agent_system_description = []
        if self._check_attr("description"):
            agent_system_description.append(
                f"You are {self.name.capitalize()}, {self.description}.\n"
            )
        else:
            agent_system_description.append(f"You are {self.name.capitalize()}.\n")

        personality = self.get_personality()
        if personality:
            agent_system_description.append(f"You are {personality}")

        traits = self.get_traits()
        if traits:
            if self._check_attr("personality"):
                agent_system_description.append(f", often displaying {traits}.\n")
            else:
                agent_system_description.append(f"You are {traits}.\n")

        adjectives = self.get_adjectives()
        if adjectives:
            agent_system_description.append(f"You are {adjectives}")

        if self._check_attr("role"):
            if self._check_attr("adjectives"):
                agent_system_description.append(f", always ready to {self.role}.\n")
            else:
                agent_system_description.append(
                    f"You are always ready to {self.role}.\n"
                )

        return "".join(agent_system_description).strip()

    def save(self):
        agents = get_agents()
        if self.name not in agents:
            agents[self.name] = {}
        if hasattr(self, "description"):
            agents[self.name]["description"] = self.description
        if hasattr(self, "personality"):
            agents[self.name]["personality"] = self.personality
        if hasattr(self, "traits"):
            agents[self.name]["traits"] = self.traits
        if hasattr(self, "adjectives"):
            agents[self.name]["adjectives"] = self.adjectives
        if hasattr(self, "role"):
            agents[self.name]["role"] = self.role
        if hasattr(self, "user_seen"):
            agents[self.name]["user_seen"] = self.user_seen

        save_agents(agents)


class SystemPrompt:
    def __init__(
        self, user: User, agent: Agent, environment: Environment, tools: Tools
    ):
        self.user = user
        self.agent = agent
        self.environment = environment
        self.tools = tools

    def __str__(self):
        return self.describe()

    def describe(self):
        return f"""<<SYS>>

{self.agent.describe()}

{self.user.describe()}

Environment highlights:

{self.environment}

Use the following tools to help you answer the user query:

{self.tools}

Below is our latest conversation.

<</SYS>>"""


class Conversation:
    def __init__(self, turns: list, system: SystemPrompt):
        self.turns = turns
        self.system = system

    def __getitem__(self, key):
        return self.turns[key]

    def __setitem__(self, key, value):
        self.turns[key] = value

    def __delitem__(self, key):
        del self.turns[key]

    def __iter__(self):
        return iter(self.turns)

    def __len__(self):
        return len(self.turns)

    def __contains__(self, item):
        return item in self.turns

    def __add__(self, other):
        return self.turns + other

    def __str__(self):
        return self.describe()

    def __repr__(self) -> str:
        return "\n".join(
            [f"{t.get('human')}: {t.get('final_answer')}" for t in self.turns]
        )

    def as_list(self):
        return self.turns

    def add_turn(self, turn):
        self.turns.append(turn)

    def add_reply(self, action, action_input, observation):
        if not self.turns[-1].get("scratchpad"):
            self.turns[-1]["scratchpad"] = []
        self.turns[-1]["scratchpad"].append(
            {"action": action, "action_input": action_input, "observation": observation}
        )

    def add_final_answer(self, final_answer):
        self.turns[-1]["final_answer"] = final_answer

    def add_prompt(self, prompt):
        if not self.turns[-1].get("scratchpad"):
            raise ValueError("You need to add a scratchpad before adding a prompt")
        self.turns[-1]["scratchpad"][-1]["prompt"] = prompt

    def add_model_output(self, model_output):
        if not self.turns[-1].get("scratchpad"):
            raise ValueError(
                "You need to add a scratchpad before adding a model output"
            )
        self.turns[-1]["scratchpad"][-1]["model_output"] = model_output

    def describe(self):
        return f"""{self.system}

{self.get_history()}{self.get_scratchpad()}"""

    def get_scratchpad(self):
        turn = self.turns[-1]
        scratchpad = turn.get("scratchpad", [])
        agent_output = []
        for scratchpad_item in scratchpad:
            agent_action = scratchpad_item.get("action")
            agent_action_input = scratchpad_item.get("action_input")
            agent_observation = scratchpad_item.get("observation")
            agent_output.append(
                f"""```json
{{"action": "{agent_action}",
"action_input": "{agent_action_input}",
"observation": "{agent_observation}"}}
```"""
            )
        return " | ".join(agent_output) + " | " if agent_output else ""

    def get_history(self):
        history = ""

        for t, turn in enumerate(self.turns):
            user_input = turn.get("human")
            # scratchpad = turn.get("scratchpad")
            agent_answer = turn.get("final_answer")
            if agent_answer:
                history += f"""[INST] {user_input} [/INST] {agent_answer} / """
            elif user_input:
                history += f"""<s>[INST] {user_input} [/INST] """

        return history


def get_conversations():
    return deserialize("conversations.pkl", default=[])


def save_conversations(conversations):
    serialize(conversations, "conversations.pkl")


class Conversations:
    def __init__(self, file_path: str = "conversations.pkl"):
        self.file_path = file_path
        self.load_from_disk()

    def load_from_disk(self):
        self.conversations = get_conversations()

    def save(self):
        save_conversations(self.conversations)

    def __getitem__(self, key):
        return self.conversations[key]

    def __setitem__(self, key, value):
        self.conversations[key] = value

    def __delitem__(self, key):
        del self.conversations[key]
    
    def __iter__(self):
        return iter(self.conversations)
    
    def __len__(self):
        return len(self.conversations)
    
    def __contains__(self, item):
        return item in self.conversations
    
    def __add__(self, other):
        return self.conversations + other
    
    def __str__(self):
        return self.describe()
    
    def __repr__(self) -> str:
        return self.describe()
    
    def describe(self):
        return "\n".join([str(c) for c in self.conversations])

    def add_conversation(self, conversation):
        self.conversations.append(conversation)
        self.save()

    def to_list(self):
        return self.conversations

    def to_dict(self):
        data = {
            "prompt": [],
            "chosen": [],
            "rejected": [],
        }

        for conversation in self.conversations:
            for turn in conversation:
                scratchpad = turn.get("scratchpad")
                if scratchpad:
                    for scratchpad_item in scratchpad:
                        prompt = scratchpad_item.get("prompt")
                        rejected = scratchpad_item.get("model_output")
                        rejected = rejected[:min(500, len(rejected))]
                        action, action_input, observation = (
                            scratchpad_item.get("action"),
                            scratchpad_item.get("action_input"),
                            scratchpad_item.get("observation"),
                        )
                        if (
                            prompt
                            and rejected
                            and action
                            and action_input
                            and observation
                        ):
                            data["prompt"].append(prompt)
                            data["rejected"].append(rejected)
                            action = (
                                "Final Answer"
                                if action == "final_answer"
                                else action.capitalize()
                            )
                            data["chosen"].append(
                                f"""```json
{{"action": "{action}",
"action_input": "{action_input}",
"observation": "{observation}"}}
```"""
                            )
        return data


def list_items():
    # Code to list items
    conversations = Conversations()
    if len(conversations) == 0:
        print("No conversation found.")
    elif len(conversations) == 1:
        print("1 conversaiton found.")
        print(f"ID")
        print(f"0")
    else:
        print(
            f"{len(conversations)} conversation{'s' if len(conversations) > 1 else ''} found."
        )
        print(f"ID")
        print(f"0")
        print(f".")
        print(f".")
        print(f".")
        print(f"{len(conversations) - 1}")


def show_item(id_int: int):
    # Code to show item by ID
    print(f"Showing conversation with ID: {id_int}")
    conversations = Conversations()
    if id_int < len(conversations):
        pprint(conversations[id_int])
    else:
        print("ID not found in converations.")


def save_conversation(conversation):
    print("Saving conversation")
    conversations = Conversations()
    conversations.add_conversation(conversation)
    print("Conversation saved")


def is_base_model_loaded(host: str = "localhost", port: str = "5085"):
    try:
        r = requests.get(f"http://{host}:{port}")
        if r.status_code == 200:
            return True
        else:
            raise Exception()
    except Exception as e:
        return False


def select_user():
    username_select = questionary.select(
        "Which user is having the conversation?",
        choices=get_usernames() + ["add"],
    ).ask()
    if username_select == "add":
        username = None
        while username is None:
            username = questionary.text("Username: ").ask()
            if username:
                user = create_user(username)
    else:
        user = User(username_select)

    return user


def select_agent():
    agentname = questionary.select(
        "Who is the user's interlocutor?",
        choices=get_agentnames() + ["add"],
    ).ask()
    if agentname == "add":
        agentname = questionary.text("Agentname: ").ask()
        agent = Agent(agentname)

        if not agent._check_attr("description"):
            add_description = questionary.confirm(
                "Would you like to add a description?", default=False
            ).ask()
            if add_description:
                agent.set_description(questionary.text("Description: ").ask())
                agent.save()

        if not agent._check_attr("personality"):
            add_personality = questionary.confirm(
                "Would you like to add a personality?", default=False
            ).ask()
            if add_personality:
                add_trait = True
                while add_trait:
                    trait = questionary.text("Personality trait: ").ask()
                    if trait is not None:
                        if agent._check_attr("personality"):
                            agent.personality.append(trait)
                        else:
                            agent.personality = [trait]
                        agent.save()
                    add_trait = questionary.confirm(
                        "Would you like to add another trait?", default=False
                    ).ask()

        if not agent._check_attr("traits"):
            add_traits = questionary.confirm(
                "Would you like to add traits?", default=False
            ).ask()
            if add_traits:
                add_trait = True
                while add_trait:
                    trait = questionary.text("Trait: ").ask()
                    if trait is not None:
                        if agent._check_attr("traits"):
                            agent.traits.append(trait)
                        else:
                            agent.traits = [trait]
                        agent.save()
                    add_trait = questionary.confirm(
                        "Would you like to add another trait?", default=False
                    ).ask()

        if not agent._check_attr("adjectives"):
            add_adjectives = questionary.confirm(
                "Would you like to add adjectives?", default=False
            ).ask()
            if add_adjectives:
                add_adjective = True
                while add_adjective:
                    adjective = questionary.text("Adjective: ").ask()
                    if adjective is not None:
                        if agent._check_attr("adjectives"):
                            agent.adjectives.append(adjective)
                        else:
                            agent.adjectives = [adjective]
                        agent.save()
                    add_adjective = questionary.confirm(
                        "Would you like to add another adjective?", default=False
                    ).ask()

        if not agent._check_attr("role"):
            add_role = questionary.confirm(
                "Would you like to add a role?", default=False
            ).ask()
            if add_role:
                agent.set_role(questionary.text("Role: ").ask())
                agent.save()
    else:
        agent = Agent(agentname)

    return agent


def select_environment(user, agent):
    username = user.username
    last_seen = agent.user_seen.get(username)
    environment = Environment(username, last_seen)
    env_choice = questionary.select(
        "In which environment is the conversation happening?",
        choices=["current", "custom"],
    ).ask()
    if env_choice == "current":
        environment.load_from_environment()
    elif env_choice == "custom":
        environment.pwd = questionary.text("PWD=").ask()
        environment.home = questionary.text("HOME=").ask()
        environment.date = questionary.text("DATE=").ask()
        environment.language = questionary.text("LANG=").ask()

    return environment


def select_tools():
    define_tools_manualy = questionary.confirm(
        "Would you like to define the tools yourself?", default=False
    ).ask()

    if not define_tools_manualy:
        return Tools(standard_tools_list)
    else:
        add_tool = True
        tools = []
        while add_tool:
            tool_name = questionary.text("Tool name: ").ask()
            tool_description = questionary.text("Tool description: ").ask()
            tools.append(Tool(tool_name, tool_description))
            add_tool = questionary.confirm(
                "Would you like to add another tool?", default=False
            ).ask()
        return Tools(tools)


def get_model_output(
    prompt,
    host="localhost",
    port="5085",
    max_tokens: int = 1000,
    stop: list | None = ["</s>"],
):
    headers = {"User-Agent": "data_manager"}
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "stop": stop,
        "temperature": 0.0,
    }
    try:
        r = requests.post(
            f"http://{host}:{port}/generate", json=payload, headers=headers
        )
        if r.status_code == 200:
            j = r.json()
            if j:
                return j["text"][0]
    except Exception:
        pass
    return None


def parse_json_markdown(json_string: str) -> dict:
    """
    Parse a JSON string from a Markdown string.

    Args:
        json_string: The Markdown string.

    Returns:
        The parsed JSON object as a Python dictionary.
    """
    # Try to find JSON string within triple backticks
    match = re.search(r"```(json)?(.*)```", json_string, re.DOTALL)

    # If no match found, assume the entire string is a JSON string
    if match is None:
        json_str = json_string
    else:
        # If match found, use the content within the backticks
        json_str = match.group(2)

    # Strip whitespace and newlines from the start and end
    json_str = json_str.strip()

    # handle newlines and other special characters inside the returned value
    # json_str = _custom_parser(json_str)

    # Parse the JSON string into a Python dictionary
    parsed = json.loads(json_str)

    return parsed


def handle_model_specifics(text):
    # text = text.split("\n\n### ")[0]
    text = text.split("<s>[INST]")[0]
    text = text.split("</s>")[0]
    text = (
        text.replace(
            "```\n\n```",
            "```</s> | <s>[INST] This hallucination will be discarded [/INST] ```",
        )
        .split(" | ")[0]
        .removesuffix("<s>")
    )
    text = text.split("[/INST]")[0].strip()
    text = text.split("[INST]")[0].strip()
    # text = text.replace("""</s>""", "")
    # text = text.replace("\n", '')
    # text = text.replace("\t", '')
    # text = text.replace("\r", '')
    # text = text.replace(" ", '')
    # text = text.replace("```json", '')
    # text = text.replace("```", '')
    text = text.strip("\n")
    return text


def get_action(text):
    _text = handle_model_specifics(text)
    try:
        return parse_json_markdown(_text)
    except Exception:
        return None


def add_item():
    # Code to add an item
    print("Adding a conversation")
    assert (
        is_base_model_loaded()
    ), "You need to load the base model before adding a conversation"
    add_conversation = True
    add_turn = True
    while add_conversation:
        # Define the user
        user = select_user()
        print(f"Your username is {user.username}")

        if user._check_attr("first_name"):
            print("Your first name is " + user._get_attr("first_name"))
        if user._check_attr("last_name"):
            print("Your last name is " + user._get_attr("last_name"))
        if user._check_attr("gender") and user.gender != "none":
            print(
                "You are a " + user._get_attr("gender")
                if user._get_attr("gender") != "none"
                else "person" + "."
            )
        if user._check_attr("surnames"):
            print("You should be called " + ", ".join(user._get_attr("surnames")))

        # Define the agent

        agent = select_agent()
        print(f"Interlocutor is {agent}")
        if agent._check_attr("description"):
            print(f"{agent} is {agent.description}.")
        if agent._check_attr("personality"):
            print(f"It has a {agent.get_personality()} personality.")
        if agent._check_attr("traits"):
            print(f"It often display {agent.get_traits()}.")
        if agent._check_attr("adjectives") and agent._check_attr("role"):
            print(f"It is {agent.get_adjectives()}, always ready to {agent.role}.")
        elif agent._check_attr("adjectives"):
            print(f"It is {agent.get_adjectives()}.")
        elif agent._check_attr("role"):
            print(f"It is always ready to {agent.role}.")

        agent_last_seen_user = agent.user_seen.get(user.username)
        if agent_last_seen_user:
            print(f"{agent} last saw {user} on {agent_last_seen_user}.")
        else:
            print(f"{agent} has never seen {user}.")

        # Define the environment

        environment = select_environment(user, agent)
        print(environment)

        # Define the tools

        tools = select_tools()
        print(tools)

        # Define the system prompt
        print("System prompt:")
        system_prompt = SystemPrompt(user, agent, environment, tools)
        print(system_prompt)

        # Define the conversation

        conversation = Conversation([], system=system_prompt)
        user_input = None

        while add_turn:
            while user_input is None:
                user_input = questionary.text("User input: ").ask()
                conversation.add_turn({"human": user_input})

            # Get the prompt
            conversation.system.environment.date = subprocess.check_output( 
                "date", shell=True, text=True
            ).strip()
            conversation.system.environment.pwd = questionary.text(
                "PWD=", default=conversation.system.environment.pwd
            ).ask()
            prompt = conversation.describe()
            print(prompt)

            # Get the model output
            print("Getting the model output")
            model_output = get_model_output(prompt)
            print(model_output)

            # get the action and input from the model output
            action_dict = get_action(model_output)
            if action_dict:
                action = action_dict.get("action")
                action_input = action_dict.get("action_input")
            else:
                action = None
                action_input = None

            if action and action_input:
                print(f"Model has chosen action {action} with input {action_input}")

                # Correct the output if necessary
                is_action_correct = questionary.confirm(
                    "Is the action correct?", default=True
                ).ask()
                if not is_action_correct:
                    correct_action = None
                    # while correct_action != "final_answer":
                    correct_action = questionary.select(
                        f"Which action should {agent} have taken:",
                        choices=[
                            "final_answer",
                            "shell",
                            "python",
                            "search",
                            "wikipedia",
                            "clear",
                            "exit",
                        ],
                    ).ask()  # TODO;: Use Tools.as_list() instead
                    if correct_action == "final_answer":
                        correct_action_input = questionary.text(
                            f"What should {agent} have answered: "
                        ).ask()
                        observation = "User has seen this message."
                    else:
                        correct_action_input = questionary.text(
                            f"What input should {agent} have given to action {correct_action}: "
                        ).ask()
                        observation = questionary.text(
                            f"What did {agent} observed from this action: "
                        ).ask()
                else:
                    correct_action = action
                    correct_action_input = action_input
                    observation = questionary.text(
                        f"What did {agent} observed from this action: "
                    ).ask()
            else:
                print("Model failed to output an action and input.")
                correct_action = questionary.select(
                    f"Which action should {agent} have taken:",
                    choices=[
                        "final_answer",
                        "shell",
                        "python",
                        "search",
                        "wikipedia",
                        "clear",
                        "exit",
                    ],
                ).ask()
                if correct_action == "final_answer":
                    correct_action_input = questionary.text(
                        f"What should {agent} have answered: "
                    ).ask()
                    observation = "User has seen this message."
                else:
                    correct_action_input = questionary.text(
                        f"What input should {agent} have given to action {correct_action}: "
                    ).ask()
                    observation = questionary.text(
                        f"What did {agent} observed from this action: "
                    ).ask()
            # Update the conversation
            conversation.add_reply(
                correct_action, correct_action_input or "", observation or ""
            )

            if correct_action in ["exit", "clear"]:
                add_turn = False
                conversation.add_final_answer(correct_action_input)
                print(
                    f"{agent} ended the conversation by saying '{correct_action_input or ''}'."
                )
            elif correct_action == "final_answer":
                user_input = None
                conversation.add_final_answer(correct_action_input)
                print(f"{agent} said '{correct_action_input or ''}'.")

            conversation.add_model_output(model_output)
            conversation.add_prompt(prompt)

        save_conversation(conversation)
        agent.user_seen[user.username] = subprocess.check_output(
            "date", shell=True, text=True
        ).strip()
        agent.save()
        add_conversation = questionary.confirm(
            "Would you like to add another conversation?", default=False
        ).ask()


def remove_item(id_int: int):
    # Code to remove an item
    print("Removing a conversation")
    conversations = Conversations()
    if id_int < len(conversations):
        del conversations[id_int]
        conversations.save()
        print("Conversation removed.")
    else:
        print("ID not found in converations.")



def push(dataset_name):
    assert (
        len(dataset_name.split("/")) == 2
    ), "Dataset name must be of the form <user>/<dataset>"
    print(f"Pushing {dataset_name}")
    conversations = Conversations()
    data_dict = conversations.to_dict()
    # create hf dataset
    dataset = Dataset.from_dict(data_dict)
    dataset.push_to_hub(dataset_name)


def parse_args():
    parser = argparse.ArgumentParser(description="Data Manager for RLHF")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subparser for 'list' command
    list_parser = subparsers.add_parser("list", help="List items")

    # Subparser for 'show' command
    show_parser = subparsers.add_parser("show", help="Show an item by ID")
    show_parser.add_argument(
        "id_int", nargs="*", default=None, help="ID of the item to show"
    )

    # Subparser for 'add' command
    add_parser = subparsers.add_parser("add", help="Add an item")

    # Subparser for 'remove' command
    remove_parser = subparsers.add_parser("remove", help="Remove an item")
    remove_parser.add_argument(
        "id_int", nargs="*", default=None, help="ID of the item to show"
    )

    # Subparser for 'push' command
    push_parser = subparsers.add_parser("push", help="Push the dataset")
    push_parser.add_argument(
        "dataset_name",
        nargs="?",
        default=None,
        help="Name of the dataset to publish. (be sure to be logged into the hub)",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    console = Console()

    console.print(BANNER)
    console.print(BANNER_HIGHLIGHT, justify="center", style="italic")

    if args.command == "list":
        list_items()
    elif args.command == "show":
        id_int = args.id_int
        if id_int is None:
            id_int = questionary.text(
                "Enter the ID of the conversation to show: "
            ).ask()
            if id_int is not None:
                show_item(int(id_int))
            else:
                print("No ID entered.")
        else:
            for id in id_int:
                show_item(int(id))
    elif args.command == "add":
        add_item()
    elif args.command == "remove":
        id_int = args.id_int
        if id_int is None:
            id_int = questionary.text("Enter the ID of the item to remove: ").ask()
            if id_int is not None:
                remove_item(int(id_int))
            else:
                print("No ID entered.")
        else:
            for id in id_int:
                remove_item(int(id))
    elif args.command == "push":
        if args.dataset_name is None:
            dataset_name = questionary.text(
                "Enter the name of the dataset to push: "
            ).ask()
        else:
            dataset_name = args.dataset_name
        push(dataset_name)
    else:
        choice = questionary.select(
            "Please select a command:",
            choices=["list", "show", "add", "remove", "push"],
        ).ask()

        if choice == "list":
            list_items()
        elif choice == "show":
            id_str = questionary.text("Enter the ID of the item to show: ").ask()
            show_item(id_str)
        elif choice == "add":
            add_item()
        elif choice == "remove":
            id_str = questionary.text("Enter the ID of the item to remove: ").ask()
            remove_item(id_str)
        elif choice == "push":
            dataset_name = questionary.text(
                "Enter the name of the dataset to push: "
            ).ask()
            push(dataset_name)


if __name__ == "__main__":
    main()
