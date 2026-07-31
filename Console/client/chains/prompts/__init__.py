# import subprocess
from langchain.prompts import StringPromptTemplate, ChatPromptTemplate, PromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from typing import Callable

from Console.client.chains.tools import get_all_tools
from Console.client.chains.prompts.markdown import get_structured_template, get_structured_template_with_memory
# from Console.client.chains.tools.retriever import get_relevant_tools_from_query

class MarkdownPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools_getter: Callable

    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        
        if intermediate_steps:
            thoughts = "```json\n[\n"
            for action, observation in intermediate_steps:
                thoughts += f"\t{{ 'action': '{action.tool}',  'action_input': '{action.tool_input}', 'observation': '{observation}' }},\n"
            thoughts += "]\n```"
        else:
            thoughts = "```json\n[]\n```"

        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts

        tools = self.tools_getter()
        # tools = self.tools_getter(kwargs["input"])
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "```json\n{\n" + "".join(
            [f"\t'{tool.name}': '{tool.description}',\n" for tool in tools]
        ) + "}\n```"
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in tools])

        # # Add environment variables from printenv
        # kwargs["env"] = self.get_environ()

        # Format the template
        return self.template.format(**kwargs)

    # def get_environ(self):
    #     # Get the environment variables from printenv
    #     return subprocess.check_output(["printenv"]).decode("utf-8")

template = get_structured_template()
memory_template = get_structured_template_with_memory()

def get_prompt(template=template):
    return MarkdownPromptTemplate(
        template=template,
        tools_getter=get_all_tools,
        #tools_getter=get_relevant_tools_from_query,
        # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
        # This includes the `intermediate_steps` variable because that is needed
        input_variables=["input", "intermediate_steps"],
    )

def get_prompt_with_memory(template=memory_template, memory_key="chat_history"):
    return MarkdownPromptTemplate(
        template=template,
        tools_getter=get_all_tools,
        #tools_getter=get_relevant_tools_from_query,
        # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
        # This includes the `intermediate_steps` variable because that is needed
        input_variables=[memory_key, "input", "intermediate_steps"],
    )